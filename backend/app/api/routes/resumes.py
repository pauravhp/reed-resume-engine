"""
Resume generation engine.

Flow for POST /resumes/generate:
  1. Validate user has a Groq API key stored
  2. Decrypt the key
  3. Optionally cache/retrieve the job posting by URL
  4. Fetch all user data from DB
  5. Run 3 Groq calls in parallel via asyncio.gather
  6. Build enriched response dict + render LaTeX
  7. Save Application row and return
"""

import asyncio
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import groq
from fastapi import APIRouter, HTTPException
from jinja2 import Environment
from sqlmodel import SQLModel, select
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.api.deps import CurrentUser, SessionDep
from app.core.security import decrypt_api_key
from app.models import (
    Application,
    Education,
    Experience,
    JobPosting,
    Leadership,
    Profile,
    Project,
    Skills,
)

router = APIRouter(prefix="/resumes", tags=["resumes"])


# ─── Request / Response models ────────────────────────────────────────────────


class GenerateRequest(SQLModel):
    jd_text: str
    source_url: str | None = None


class GenerateResponse(SQLModel):
    id: uuid.UUID
    match_score: int
    match_reasoning: str
    summary: str
    include_coursework: bool = False
    coursework_items: list[str] = []
    experiences: list[dict]
    projects: list[dict]
    skills: dict


class RegenerateSummaryResponse(SQLModel):
    summary: str


class RegenerateExperiencesRequest(SQLModel):
    excluded_bullets: list[str] = []


class RegenerateExperiencesResponse(SQLModel):
    experiences: list[dict]


class RegenerateProjectsRequest(SQLModel):
    excluded_project_ids: list[str] = []


class RegenerateProjectsResponse(SQLModel):
    projects: list[dict]
    skills: dict


# ─── LaTeX escape ─────────────────────────────────────────────────────────────


_LATEX_ESCAPE_MAP = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _latex_escape(s: str) -> str:
    """Escape LaTeX special characters in user-supplied strings."""
    if not s:
        return ""
    return "".join(_LATEX_ESCAPE_MAP.get(c, c) for c in s)


# ─── URL normalization ────────────────────────────────────────────────────────


def _normalize_url(url: str) -> str:
    """Strip query string + fragment; lowercase scheme + host + path."""
    parsed = urlparse(url.strip())
    return urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        "",   # params  discard
        "",   # query   discard
        "",   # fragment  discard
    ))


# ─── Job posting cache ────────────────────────────────────────────────────────


def _get_jd(session: Any, source_url: str, jd_text: str) -> tuple["JobPosting", str]:
    """Fetch or upsert a JobPosting row; return (posting, effective_jd_text).

    Cache hit (< 7 days old): returns cached jd_text.
    Cache miss or stale: upserts with new jd_text.
    """
    normalized = _normalize_url(source_url)
    existing = session.exec(
        select(JobPosting).where(JobPosting.url == normalized)
    ).first()

    now = datetime.now(timezone.utc)

    if existing:
        age_seconds = (now - existing.scraped_at.replace(tzinfo=timezone.utc)).total_seconds()
        if age_seconds < 7 * 24 * 3600:
            return existing, existing.jd_text
        existing.jd_text = jd_text
        existing.scraped_at = now
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing, jd_text

    posting = JobPosting(url=normalized, jd_text=jd_text)
    session.add(posting)
    session.commit()
    session.refresh(posting)
    return posting, jd_text


# ─── Response builder ─────────────────────────────────────────────────────────


def _build_generate_response(
    summary_r: dict,
    exp_r: dict,
    proj_r: dict,
    experiences_db: list,
    projects_db: list,
) -> dict:
    """Convert raw Groq output into the frontend-facing response dict.

    Does NOT include 'id' — the route handler adds that after saving.
    Converts 'Present' end_date strings to None (frontend convention).
    """
    exp_by_company = {e.company: e for e in experiences_db}
    enriched_experiences = []
    for item in exp_r.get("experiences", []):
        db_exp = exp_by_company.get(item.get("company"))
        if db_exp:
            enriched_experiences.append({
                "company": db_exp.company,
                "role_title": db_exp.role,
                "start_date": db_exp.start_date,
                "end_date": None if db_exp.end_date == "Present" else db_exp.end_date,
                "location": db_exp.location,
                "bullets": item.get("selected_bullets", []),
            })

    proj_by_id = {str(p.id): p for p in projects_db}
    enriched_projects = []
    for pid in proj_r.get("selected_project_ids", []):
        db_proj = proj_by_id.get(pid)
        if db_proj:
            enriched_projects.append({
                "id": str(db_proj.id),
                "name": db_proj.name,
                "tech_stack": db_proj.tech_stack,
                "bullets": [
                    b["text"] if isinstance(b, dict) else b
                    for b in (db_proj.bullets or [])
                ],
                "github_url": db_proj.github_url,
            })

    return {
        "summary": summary_r.get("summary", ""),
        "match_score": exp_r.get("match_score", 0),
        "match_reasoning": exp_r.get("match_reasoning", ""),
        "include_coursework": exp_r.get("include_coursework", False),
        "coursework_items": exp_r.get("coursework_items", []),
        "experiences": enriched_experiences,
        "projects": enriched_projects,
        "skills": proj_r.get("skills", {}),
    }


# ─── LaTeX assembly ───────────────────────────────────────────────────────────


def _assemble_latex(
    template_str: str,
    response_dict: dict,
    profile: "Profile",
    email: str,
    leadership: list,
    educations: list,
) -> str:
    """Render the Jinja2 LaTeX template from the enriched response dict."""
    leadership_ctx = [
        {
            "organization": entry.organization,
            "role": entry.role,
            "start_date": entry.start_date,
            "end_date": entry.end_date,
            "location": entry.location,
            "bullets": [
                b["text"] if isinstance(b, dict) else b
                for b in (entry.bullets or [])
            ],
        }
        for entry in leadership
    ]

    education_ctx = [
        {
            "institution": e.institution,
            "degree": e.degree,
            "field_of_study": e.field_of_study,
            "start_date": e.start_date,
            "end_date": e.end_date,
            "location": e.location or "",
        }
        for e in educations
    ]

    env = Environment(autoescape=False)
    env.filters["latex_escape"] = _latex_escape
    template = env.from_string(template_str)

    return template.render(
        email=email,
        phone=profile.phone or "",
        linkedin_url=profile.linkedin_url or "",
        github_url=profile.github_url or "",
        summary=response_dict.get("summary", ""),
        include_coursework=response_dict.get("include_coursework", False),
        coursework_items=response_dict.get("coursework_items", []),
        selected_experiences=response_dict.get("experiences", []),
        selected_projects=response_dict.get("projects", []),
        skills_languages=response_dict.get("skills", {}).get("languages", ""),
        skills_frameworks=response_dict.get("skills", {}).get("frameworks", ""),
        skills_tools=response_dict.get("skills", {}).get("tools", ""),
        leadership=leadership_ctx,
        education_list=education_ctx,
    )


# ─── Groq LLM calls ───────────────────────────────────────────────────────────


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=8),
    retry=retry_if_exception_type(groq.RateLimitError),
)
async def _call_groq_summary(
    client: groq.AsyncGroq, jd_text: str, bio_context: str
) -> dict:
    """Call A: Generate a 2-3 sentence tailored professional summary.

    Returns: {"summary": str}
    """
    import json

    prompt = f"""You are a professional resume writer helping a student tailor their resume.

Write a resume summary in exactly this structure:
1. 1-2 sentences describing who the candidate is and what they bring — grounded in the bio context only.
2. Final sentence: "Seeking [role] in [specific field] for [term(s)] [year]." — extract the role type, field, term(s), and year from the job description. Be specific (e.g. "AI/ML Engineering", "Software Engineering", not just "engineering").

Rules:
- Total length: 2-3 sentences, tight and direct
- The bio context is the source of truth for what the candidate brings — do NOT mirror, paraphrase, or echo language from the job description
- Do NOT name specific projects, companies, awards, or bullet-point achievements — those appear elsewhere in the resume
- No buzzwords ("passionate", "results-driven", "dynamic", "transformative", "cutting-edge")
- Write in first person without the word "I"
- Describe who the candidate IS, not what they want to do or what the company does

Job Description:
{jd_text}

Bio Context:
{bio_context}

Respond with JSON only, exactly this shape: {{"summary": "..."}}"""

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    return json.loads(response.choices[0].message.content)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=8),
    retry=retry_if_exception_type(groq.RateLimitError),
)
async def _call_groq_experiences(
    client: groq.AsyncGroq,
    jd_text: str,
    experiences: list,
    educations: list,
    excluded_bullets: list[str] | None = None,
) -> dict:
    """Call B: Select relevant bullets from each experience; decide on coursework.

    excluded_bullets: bullet text strings to omit from the candidate set.

    Returns: {
      "experiences": [{"company": str, "selected_bullets": [str]}],
      "match_score": int,
      "match_reasoning": str,
      "include_coursework": bool,
      "coursework_items": [str]
    }
    """
    import json

    if excluded_bullets is None:
        excluded_bullets = []

    exp_data = [
        {
            "company": e.company,
            "role": e.role,
            "start_date": e.start_date,
            "end_date": e.end_date,
            "bullets": [
                b["text"] if isinstance(b, dict) else b
                for b in (e.bullets or [])
                if (b["text"] if isinstance(b, dict) else b) not in excluded_bullets
            ],
        }
        for e in experiences
    ]

    coursework: list = []
    field_of_study = ""
    for edu in educations:
        coursework.extend(edu.coursework or [])
        if not field_of_study:
            field_of_study = edu.field_of_study

    num_experiences = len(experiences)
    bullets_guidance = (
        "Select 3-4 bullets per experience."
        if num_experiences >= 2
        else "Select 5-6 bullets (only one experience entry)."
    )

    prompt = f"""You are a resume tailoring expert.

Select the most relevant bullet points from each work experience for this job description.

Rules:
- {bullets_guidance}
- NEVER fabricate or modify bullet text — copy exactly from the provided list
- Match company names exactly as provided in the input
- Include coursework ONLY if the JD explicitly requires academic background in that area, OR the candidate has 1 or fewer work experience entries
- Provide a match_score (0-100) reflecting how well the candidate's background fits this role
- Provide brief match_reasoning (2-3 sentences) explaining the score

Job Description:
{jd_text}

Education field: {field_of_study}
Coursework available: {json.dumps(coursework)}

Work Experiences:
{json.dumps(exp_data, indent=2)}

Respond with JSON only, exactly this shape:
{{
  "experiences": [{{"company": "...", "selected_bullets": ["..."]}}],
  "match_score": 75,
  "match_reasoning": "...",
  "include_coursework": false,
  "coursework_items": []
}}"""

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=8),
    retry=retry_if_exception_type(groq.RateLimitError),
)
async def _call_groq_projects(
    client: groq.AsyncGroq,
    jd_text: str,
    projects: list,
    skills: Any,
    excluded_project_ids: list[str] | None = None,
) -> dict:
    """Call C: Select 2 most relevant projects; reorder skills to front-load JD matches.

    excluded_project_ids: project UUID strings to exclude from selection.

    Returns: {
      "selected_project_ids": [str, str],
      "skills": {"languages": str, "frameworks": str, "tools": str}
    }
    """
    import json

    if excluded_project_ids is None:
        excluded_project_ids = []

    filtered_projects = [p for p in projects if str(p.id) not in excluded_project_ids]

    proj_data = [
        {
            "id": str(p.id),
            "name": p.name,
            "tech_stack": p.tech_stack or "",
            "bullets": [b["text"] if isinstance(b, dict) else b for b in (p.bullets or [])],
        }
        for p in filtered_projects
    ]

    languages = ", ".join(skills.languages) if skills else ""
    frameworks = ", ".join(skills.frameworks) if skills else ""
    tools = ", ".join(skills.tools) if skills else ""

    prompt = f"""You are a resume tailoring expert.

Select the 2 most relevant projects for this job description and reorder skill lists to front-load JD-relevant technologies.

Project selection — for each project, use its description (if present), tech stack, and bullet points to evaluate:
1. Domain alignment: does the project operate in a domain that matches the role (e.g. same industry, same problem space, same type of system)?
2. Technical alignment: does the project demonstrate skills, tools, or concepts the JD explicitly requires or values?
3. Depth: does the project show real technical substance (complex problem solved, notable outcome, meaningful scope) rather than surface-level work?

Pick the 2 projects that score highest across all three dimensions for this specific JD. Do not apply assumptions about which domains or technologies are universally "stronger" — evaluate purely based on fit with this particular role.

Rules:
- Select exactly 2 project IDs (use the "id" field from the input). If fewer than 2 projects are provided, select all of them.
- Reorder skills within each category to put JD-relevant technologies first
- NEVER add or remove items from the skill lists — only reorder them
- Return skills as comma-separated strings (not arrays)

Job Description:
{jd_text}

Projects:
{json.dumps(proj_data, indent=2)}

Current Skills:
Languages: {languages}
Frameworks: {frameworks}
Tools: {tools}

Respond with JSON only, exactly this shape:
{{
  "selected_project_ids": ["uuid1", "uuid2"],
  "skills": {{
    "languages": "Python, TypeScript, ...",
    "frameworks": "FastAPI, React, ...",
    "tools": "Docker, Git, ..."
  }}
}}"""

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)


# ─── Route endpoints ──────────────────────────────────────────────────────────


@router.post("/generate", response_model=GenerateResponse)
async def generate_resume(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    request: GenerateRequest,
) -> Any:
    # 1. Validate + decrypt Groq key
    profile = session.get(Profile, current_user.id)
    if not profile or profile.groq_api_key is None:
        raise HTTPException(status_code=400, detail="No Groq API key configured")
    try:
        api_key = decrypt_api_key(profile.groq_api_key)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt Groq API key")

    client = groq.AsyncGroq(api_key=api_key)

    # 2. Handle job posting cache
    jd_text = request.jd_text
    job_posting_id: uuid.UUID | None = None
    if request.source_url:
        posting, jd_text = _get_jd(session, request.source_url, request.jd_text)
        job_posting_id = posting.id

    # 3. Fetch all user data (sync DB reads before entering async block)
    experiences = list(
        session.exec(
            select(Experience)
            .where(Experience.user_id == current_user.id)
            .order_by(Experience.display_order.asc())
        ).all()
    )
    educations = list(
        session.exec(
            select(Education)
            .where(Education.user_id == current_user.id)
            .order_by(Education.display_order.asc())
        ).all()
    )
    projects = list(
        session.exec(
            select(Project)
            .where(Project.user_id == current_user.id)
            .order_by(Project.display_order.asc())
        ).all()
    )
    skills = session.get(Skills, current_user.id)
    leadership = list(
        session.exec(
            select(Leadership)
            .where(Leadership.user_id == current_user.id)
            .order_by(Leadership.display_order.asc())
        ).all()
    )

    # 4. Run all 3 Groq calls in parallel
    try:
        summary_r, exp_r, proj_r = await asyncio.gather(
            _call_groq_summary(client, jd_text, profile.bio_context or ""),
            _call_groq_experiences(client, jd_text, experiences, educations),
            _call_groq_projects(client, jd_text, projects, skills),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Resume generation failed — please retry",
        ) from exc

    # 5. Build enriched response dict + render LaTeX
    response_dict = _build_generate_response(summary_r, exp_r, proj_r, experiences, projects)
    template_str = Path("app/templates/resume.tex.jinja2").read_text()
    latex = _assemble_latex(template_str, response_dict, profile, current_user.email, leadership, educations)

    # 6. Save Application row
    application = Application(
        user_id=current_user.id,
        job_posting_id=job_posting_id,
        generated_json=response_dict,
        generated_latex=latex,
        match_score=response_dict.get("match_score"),
        jd_text=jd_text,
    )
    session.add(application)
    session.commit()
    session.refresh(application)

    return {**response_dict, "id": application.id}


@router.get("/{application_id}", response_model=GenerateResponse)
def read_resume(
    session: SessionDep,
    current_user: CurrentUser,
    application_id: uuid.UUID,
) -> Any:
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return {**application.generated_json, "id": application.id}


@router.post("/{application_id}/regenerate/summary", response_model=RegenerateSummaryResponse)
async def regenerate_summary(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    application_id: uuid.UUID,
) -> Any:
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not application.jd_text:
        raise HTTPException(status_code=400, detail="No JD text stored for this application")

    profile = session.get(Profile, current_user.id)
    if not profile or profile.groq_api_key is None:
        raise HTTPException(status_code=400, detail="No Groq API key configured")
    try:
        api_key = decrypt_api_key(profile.groq_api_key)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt Groq API key")

    client = groq.AsyncGroq(api_key=api_key)

    try:
        summary_r = await _call_groq_summary(client, application.jd_text, profile.bio_context or "")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Regeneration failed — please retry") from exc

    leadership = list(
        session.exec(
            select(Leadership)
            .where(Leadership.user_id == current_user.id)
            .order_by(Leadership.display_order.asc())
        ).all()
    )
    educations = list(
        session.exec(
            select(Education)
            .where(Education.user_id == current_user.id)
            .order_by(Education.display_order.asc())
        ).all()
    )
    updated_json = {**application.generated_json, "summary": summary_r["summary"]}
    template_str = Path("app/templates/resume.tex.jinja2").read_text()
    latex = _assemble_latex(template_str, updated_json, profile, current_user.email, leadership, educations)

    application.generated_json = updated_json
    application.generated_latex = latex
    session.add(application)
    session.commit()

    return {"summary": summary_r["summary"]}


@router.post(
    "/{application_id}/regenerate/experiences",
    response_model=RegenerateExperiencesResponse,
)
async def regenerate_experiences(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    application_id: uuid.UUID,
    request: RegenerateExperiencesRequest,
) -> Any:
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not application.jd_text:
        raise HTTPException(status_code=400, detail="No JD text stored for this application")

    profile = session.get(Profile, current_user.id)
    if not profile or profile.groq_api_key is None:
        raise HTTPException(status_code=400, detail="No Groq API key configured")
    try:
        api_key = decrypt_api_key(profile.groq_api_key)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt Groq API key")

    client = groq.AsyncGroq(api_key=api_key)

    experiences = list(
        session.exec(
            select(Experience)
            .where(Experience.user_id == current_user.id)
            .order_by(Experience.display_order.asc())
        ).all()
    )
    educations = list(
        session.exec(
            select(Education)
            .where(Education.user_id == current_user.id)
            .order_by(Education.display_order.asc())
        ).all()
    )

    try:
        exp_r = await _call_groq_experiences(
            client,
            application.jd_text,
            experiences,
            educations,
            excluded_bullets=request.excluded_bullets,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Regeneration failed — please retry") from exc

    exp_by_company = {e.company: e for e in experiences}
    enriched_experiences = []
    for item in exp_r.get("experiences", []):
        db_exp = exp_by_company.get(item.get("company"))
        if db_exp:
            enriched_experiences.append({
                "company": db_exp.company,
                "role_title": db_exp.role,
                "start_date": db_exp.start_date,
                "end_date": None if db_exp.end_date == "Present" else db_exp.end_date,
                "location": db_exp.location,
                "bullets": item.get("selected_bullets", []),
            })

    leadership = list(
        session.exec(
            select(Leadership)
            .where(Leadership.user_id == current_user.id)
            .order_by(Leadership.display_order.asc())
        ).all()
    )
    regen_educations = list(
        session.exec(
            select(Education)
            .where(Education.user_id == current_user.id)
            .order_by(Education.display_order.asc())
        ).all()
    )
    updated_json = {
        **application.generated_json,
        "experiences": enriched_experiences,
        "include_coursework": exp_r.get("include_coursework", False),
        "coursework_items": exp_r.get("coursework_items", []),
    }
    template_str = Path("app/templates/resume.tex.jinja2").read_text()
    latex = _assemble_latex(template_str, updated_json, profile, current_user.email, leadership, regen_educations)

    application.generated_json = updated_json
    application.generated_latex = latex
    session.add(application)
    session.commit()

    return {"experiences": enriched_experiences}


@router.post(
    "/{application_id}/regenerate/projects",
    response_model=RegenerateProjectsResponse,
)
async def regenerate_projects(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    application_id: uuid.UUID,
    request: RegenerateProjectsRequest,
) -> Any:
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if not application.jd_text:
        raise HTTPException(status_code=400, detail="No JD text stored for this application")

    profile = session.get(Profile, current_user.id)
    if not profile or profile.groq_api_key is None:
        raise HTTPException(status_code=400, detail="No Groq API key configured")
    try:
        api_key = decrypt_api_key(profile.groq_api_key)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt Groq API key")

    client = groq.AsyncGroq(api_key=api_key)

    projects = list(
        session.exec(
            select(Project)
            .where(Project.user_id == current_user.id)
            .order_by(Project.display_order.asc())
        ).all()
    )
    skills = session.get(Skills, current_user.id)

    try:
        proj_r = await _call_groq_projects(
            client,
            application.jd_text,
            projects,
            skills,
            excluded_project_ids=request.excluded_project_ids,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Regeneration failed — please retry") from exc

    proj_by_id = {str(p.id): p for p in projects}
    enriched_projects = []
    for pid in proj_r.get("selected_project_ids", []):
        db_proj = proj_by_id.get(pid)
        if db_proj:
            enriched_projects.append({
                "id": str(db_proj.id),
                "name": db_proj.name,
                "tech_stack": db_proj.tech_stack,
                "bullets": [
                    b["text"] if isinstance(b, dict) else b
                    for b in (db_proj.bullets or [])
                ],
                "github_url": db_proj.github_url,
            })

    new_skills = proj_r.get("skills", {})

    leadership = list(
        session.exec(
            select(Leadership)
            .where(Leadership.user_id == current_user.id)
            .order_by(Leadership.display_order.asc())
        ).all()
    )
    proj_educations = list(
        session.exec(
            select(Education)
            .where(Education.user_id == current_user.id)
            .order_by(Education.display_order.asc())
        ).all()
    )
    updated_json = {
        **application.generated_json,
        "projects": enriched_projects,
        "skills": new_skills,
    }
    template_str = Path("app/templates/resume.tex.jinja2").read_text()
    latex = _assemble_latex(template_str, updated_json, profile, current_user.email, leadership, proj_educations)

    application.generated_json = updated_json
    application.generated_latex = latex
    session.add(application)
    session.commit()

    return {"projects": enriched_projects, "skills": new_skills}
