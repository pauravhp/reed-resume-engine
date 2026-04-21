"""
Resume generation engine.

Flow for POST /resumes/generate:
  1. Validate user has a Groq API key stored
  2. Decrypt the key
  3. Optionally cache/retrieve the job posting by URL
  4. Fetch all user data (experiences, education, projects, skills, leadership)
  5. Run 3 Groq calls in parallel: summary, experiences, projects+skills
  6. Assemble the LaTeX template with the results
  7. Save Application row and return
"""

import asyncio
import json
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
    ApplicationPublic,
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
    application_id: uuid.UUID
    generated_json: dict
    generated_latex: str
    match_score: int
    reasoning: str


# ─── LaTeX escape ─────────────────────────────────────────────────────────────


def _latex_escape(s: str) -> str:
    if not s:
        return ""
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for char, replacement in replacements:
        s = s.replace(char, replacement)
    return s


# ─── URL normalization ────────────────────────────────────────────────────────


def _normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    normalized = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        "",   # params
        "",   # query
        "",   # fragment
    ))
    return normalized


# ─── Job posting cache ────────────────────────────────────────────────────────


def _get_jd(session: Any, source_url: str, jd_text: str) -> tuple[JobPosting, str]:
    normalized = _normalize_url(source_url)
    statement = select(JobPosting).where(JobPosting.url == normalized)
    existing = session.exec(statement).first()

    now = datetime.now(timezone.utc)
    seven_days_seconds = 7 * 24 * 3600

    if existing:
        age = (now - existing.scraped_at.replace(tzinfo=timezone.utc)).total_seconds()
        if age < seven_days_seconds:
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


# ─── Template assembly ────────────────────────────────────────────────────────


def _assemble_latex(
    template_str: str,
    summary_r: dict,
    exp_r: dict,
    proj_r: dict,
    profile: Profile,
    current_user_email: str,
    experiences: list[Experience],
    projects: list[Project],
    leadership: list[Leadership],
) -> str:
    exp_by_company = {e.company: e for e in experiences}

    class _ExpContext:
        def __init__(self, exp: Experience, selected_bullets: list[str]) -> None:
            self.company = exp.company
            self.role = exp.role
            self.start_date = exp.start_date
            self.end_date = exp.end_date
            self.location = exp.location
            self.selected_bullets = selected_bullets

    selected_experiences = []
    for item in exp_r.get("experiences", []):
        exp = exp_by_company.get(item["company"])
        if exp:
            selected_experiences.append(
                _ExpContext(exp, item.get("selected_bullets", []))
            )

    proj_by_id = {str(p.id): p for p in projects}
    selected_projects = [
        proj_by_id[pid]
        for pid in proj_r.get("selected_project_ids", [])
        if pid in proj_by_id
    ]

    skills = proj_r.get("skills", {})

    env = Environment(
        variable_start_string="{{",
        variable_end_string="}}",
        block_start_string="{%",
        block_end_string="%}",
        comment_start_string="{#",
        comment_end_string="#}",
        autoescape=False,
    )
    env.filters["latex_escape"] = _latex_escape

    template = env.from_string(template_str)

    return template.render(
        email=current_user_email,
        phone=profile.phone or "",
        linkedin_url=profile.linkedin_url or "",
        github_url=profile.github_url or "",
        summary=summary_r.get("summary", ""),
        include_coursework=exp_r.get("include_coursework", False),
        coursework_items=exp_r.get("coursework_items", []),
        selected_experiences=selected_experiences,
        selected_projects=selected_projects,
        skills_languages=skills.get("languages", ""),
        skills_frameworks=skills.get("frameworks", ""),
        skills_tools=skills.get("tools", ""),
        leadership=leadership,
    )


# ─── Groq LLM calls ───────────────────────────────────────────────────────────


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=8),
    retry=retry_if_exception_type(groq.RateLimitError),
)
async def _call_groq_summary(client: groq.AsyncGroq, jd_text: str, bio_context: str) -> dict:
    """Call A: Generate a 2-3 sentence tailored professional summary.

    Returns: {"summary": str}
    """
    prompt = f"""You are a professional resume writer.

Given the job description and bio context below, write a 2-3 sentence professional summary tailored to this specific role.
Rules:
- Be specific to the role and company, not generic
- No buzzwords like "passionate", "results-driven", "dynamic"
- Write in first person without using the word "I"
- Do not mention the company name explicitly

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
    experiences: list[Experience],
    education: Education | None,
) -> dict:
    """Call B: Select relevant bullets from each experience; decide on coursework.

    Returns: {
      "experiences": [{"company": str, "selected_bullets": [str]}],
      "match_score": int,
      "reasoning": str,
      "include_coursework": bool,
      "coursework_items": [str]
    }
    """
    exp_data = [
        {
            "company": e.company,
            "role": e.role,
            "start_date": e.start_date,
            "end_date": e.end_date,
            "bullets": [b["text"] if isinstance(b, dict) else b for b in (e.bullets or [])],
        }
        for e in experiences
    ]

    coursework = []
    field_of_study = ""
    if education:
        coursework = education.coursework or []
        field_of_study = education.field_of_study

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
- Include coursework ONLY if the JD explicitly requires academic background in that area, OR the user has 1 or fewer work experience entries
- Provide a match_score (0-100) reflecting how well the candidate's background fits this role
- Provide brief reasoning (2-3 sentences) explaining the score

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
  "reasoning": "...",
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
    projects: list[Project],
    skills: Skills | None,
) -> dict:
    """Call C: Select 2 most relevant projects; reorder skills to front-load JD matches.

    Returns: {
      "selected_project_ids": [str, str],
      "skills": {"languages": str, "frameworks": str, "tools": str}
    }
    """
    proj_data = [
        {
            "id": str(p.id),
            "name": p.name,
            "tech_stack": p.tech_stack or "",
            "bullets": [b["text"] if isinstance(b, dict) else b for b in (p.bullets or [])],
        }
        for p in projects
    ]

    languages = ", ".join(skills.languages) if skills else ""
    frameworks = ", ".join(skills.frameworks) if skills else ""
    tools = ", ".join(skills.tools) if skills else ""

    prompt = f"""You are a resume tailoring expert.

Select the 2 most relevant projects for this job description and reorder skill lists to front-load JD-relevant technologies.

Rules:
- Select exactly 2 project IDs (use the "id" field from the input)
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
    # 1. Validate Groq key exists
    profile = session.get(Profile, current_user.id)
    if not profile or profile.groq_api_key is None:
        raise HTTPException(status_code=400, detail="No Groq API key configured")

    # 2. Decrypt key
    try:
        api_key = decrypt_api_key(profile.groq_api_key)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt Groq API key")

    # 3. Build Groq client
    client = groq.AsyncGroq(api_key=api_key)

    # 4. Handle job posting cache
    jd_text = request.jd_text
    job_posting_id: uuid.UUID | None = None

    if request.source_url:
        posting, jd_text = _get_jd(session, request.source_url, request.jd_text)
        job_posting_id = posting.id

    # 5. Fetch all user data
    experiences = list(
        session.exec(
            select(Experience)
            .where(Experience.user_id == current_user.id)
            .order_by(Experience.display_order.asc())
        ).all()
    )
    education = session.get(Education, current_user.id)
    projects = list(
        session.exec(
            select(Project)
            .where(Project.user_id == current_user.id)
            .order_by(Project.display_order.asc())
        ).all()
    )
    skills_row = session.get(Skills, current_user.id)
    leadership = list(
        session.exec(
            select(Leadership)
            .where(Leadership.user_id == current_user.id)
            .order_by(Leadership.display_order.asc())
        ).all()
    )

    # 6. Run all 3 Groq calls in parallel
    bio_context = profile.bio_context or ""
    try:
        summary_r, exp_r, proj_r = await asyncio.gather(
            _call_groq_summary(client, jd_text, bio_context),
            _call_groq_experiences(client, jd_text, experiences, education),
            _call_groq_projects(client, jd_text, projects, skills_row),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Resume generation failed — please retry",
        ) from exc

    # 7. Load template from disk
    template_str = Path("app/templates/resume.tex.jinja2").read_text()

    # 8. Render LaTeX
    latex = _assemble_latex(
        template_str=template_str,
        summary_r=summary_r,
        exp_r=exp_r,
        proj_r=proj_r,
        profile=profile,
        current_user_email=current_user.email,
        experiences=experiences,
        projects=projects,
        leadership=leadership,
    )

    # 9. Merge all Groq outputs into generated_json
    generated_json = {
        "summary": summary_r.get("summary", ""),
        "experiences": exp_r.get("experiences", []),
        "include_coursework": exp_r.get("include_coursework", False),
        "coursework_items": exp_r.get("coursework_items", []),
        "selected_project_ids": proj_r.get("selected_project_ids", []),
        "skills": proj_r.get("skills", {}),
    }

    # 10. Save Application row
    application = Application(
        user_id=current_user.id,
        job_posting_id=job_posting_id,
        generated_json=generated_json,
        generated_latex=latex,
        match_score=exp_r.get("match_score"),
    )
    session.add(application)
    session.commit()
    session.refresh(application)

    return GenerateResponse(
        application_id=application.id,
        generated_json=generated_json,
        generated_latex=latex,
        match_score=exp_r.get("match_score", 0),
        reasoning=exp_r.get("reasoning", ""),
    )


@router.get("/{application_id}", response_model=ApplicationPublic)
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
    return application
