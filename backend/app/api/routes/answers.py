"""
Tailored answer generation.

POST /answers/generate — single Groq call using JD + question + user profile
(bio_context, experiences, projects, skills, education, leadership).
Stateless: no Application row is created.
"""

import json
from typing import Any

import groq
from fastapi import APIRouter, HTTPException
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
    Education,
    Experience,
    Leadership,
    Profile,
    Project,
    Skills,
)

router = APIRouter(prefix="/answers", tags=["answers"])


class AnswerRequest(SQLModel):
    jd_text: str
    question: str


class AnswerResponse(SQLModel):
    answer: str


def _build_candidate_background(
    bio_context: str,
    experiences: list,
    projects: list,
    skills: Any,
    educations: list,
    leadership: list,
) -> str:
    """Render a plain-text summary of everything the LLM is allowed to draw on."""
    parts: list[str] = []

    if bio_context:
        parts.append(f"Bio:\n{bio_context}")

    if educations:
        edu_lines = []
        for e in educations:
            line = f"- {e.degree} in {e.field_of_study}, {e.institution} ({e.start_date} – {e.end_date})"
            edu_lines.append(line)
        parts.append("Education:\n" + "\n".join(edu_lines))

    if experiences:
        exp_lines = []
        for e in experiences:
            bullets = [b["text"] if isinstance(b, dict) else b for b in (e.bullets or [])]
            bullet_str = "".join(f"\n    • {b}" for b in bullets)
            exp_lines.append(f"- {e.role} at {e.company} ({e.start_date} – {e.end_date}){bullet_str}")
        parts.append("Work Experience:\n" + "\n".join(exp_lines))

    if projects:
        proj_lines = []
        for p in projects:
            bullets = [b["text"] if isinstance(b, dict) else b for b in (p.bullets or [])]
            bullet_str = "".join(f"\n    • {b}" for b in bullets)
            tech = f" (tech: {p.tech_stack})" if p.tech_stack else ""
            proj_lines.append(f"- {p.name}{tech}{bullet_str}")
        parts.append("Projects:\n" + "\n".join(proj_lines))

    if leadership:
        lead_lines = []
        for l in leadership:
            bullets = [b["text"] if isinstance(b, dict) else b for b in (l.bullets or [])]
            bullet_str = "".join(f"\n    • {b}" for b in bullets)
            lead_lines.append(f"- {l.role} at {l.organization} ({l.start_date} – {l.end_date}){bullet_str}")
        parts.append("Leadership:\n" + "\n".join(lead_lines))

    if skills:
        skill_bits = []
        if skills.languages:
            skill_bits.append(f"Languages: {', '.join(skills.languages)}")
        if skills.frameworks:
            skill_bits.append(f"Frameworks: {', '.join(skills.frameworks)}")
        if skills.tools:
            skill_bits.append(f"Tools: {', '.join(skills.tools)}")
        if skill_bits:
            parts.append("Skills:\n" + "\n".join(skill_bits))

    return "\n\n".join(parts) if parts else "(The candidate has not filled in any profile information.)"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=8),
    retry=retry_if_exception_type(groq.RateLimitError),
)
async def _call_groq_answer(
    client: groq.AsyncGroq,
    jd_text: str,
    question: str,
    candidate_background: str,
) -> dict:
    """Generate a personalised answer to an application question.

    Returns: {"answer": str}
    """
    prompt = f"""You are an expert career coach helping a candidate write compelling job application answers.

ABSOLUTE RULE — NO HALLUCINATION:
- The Candidate Background below is the COMPLETE and ONLY source of truth about the candidate. Use ONLY facts literally present in it.
- Do NOT invent, imply, or infer any credentials, degrees, program names, schools, employers, job titles, years of experience, technologies, frameworks, languages, certifications, publications, or achievements that are not explicitly stated.
- If the Candidate Background does not mention a specific tool, framework, or skill that would be useful for this answer, DO NOT claim the candidate has it — work with what is actually there.
- If the Candidate Background does not specify degree level (bachelor's / master's / PhD), DO NOT assert one.
- If the Candidate Background is effectively empty, write a short, honest answer that talks about general interest in the role and the candidate's stated bio, without inventing any concrete facts. Do NOT make up a degree, school, or tool stack to pad the answer.
- When in doubt about any fact, omit it. A shorter, truthful answer is strictly better than a longer, fabricated one.

Style rules:
- Be specific — reference concrete things from the Candidate Background
- Avoid generic filler phrases like "I am passionate about..." or "I have always been..."
- Write in first person
- Keep the answer to 3-5 sentences unless the question clearly warrants more
- Match the tone to a professional job application

Job Description:
{jd_text}

Candidate Background:
{candidate_background}

Application Question:
{question}

Respond with JSON only, exactly this shape: {{"answer": "..."}}"""

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    return json.loads(response.choices[0].message.content)


@router.post("/generate", response_model=AnswerResponse)
async def generate_answer(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    request: AnswerRequest,
) -> Any:
    profile = session.get(Profile, current_user.id)
    if not profile or profile.groq_api_key is None:
        raise HTTPException(status_code=400, detail="No Groq API key configured")
    try:
        api_key = decrypt_api_key(profile.groq_api_key)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt Groq API key")

    experiences = list(
        session.exec(
            select(Experience)
            .where(Experience.user_id == current_user.id)
            .order_by(Experience.display_order.asc())
        ).all()
    )
    projects = list(
        session.exec(
            select(Project)
            .where(Project.user_id == current_user.id)
            .order_by(Project.display_order.asc())
        ).all()
    )
    educations = list(
        session.exec(
            select(Education)
            .where(Education.user_id == current_user.id)
            .order_by(Education.display_order.asc())
        ).all()
    )
    leadership = list(
        session.exec(
            select(Leadership)
            .where(Leadership.user_id == current_user.id)
            .order_by(Leadership.display_order.asc())
        ).all()
    )
    skills = session.get(Skills, current_user.id)

    candidate_background = _build_candidate_background(
        profile.bio_context or "",
        experiences,
        projects,
        skills,
        educations,
        leadership,
    )

    client = groq.AsyncGroq(api_key=api_key)

    try:
        result = await _call_groq_answer(
            client,
            request.jd_text,
            request.question,
            candidate_background,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Answer generation failed — please retry",
        ) from exc

    return {"answer": result.get("answer", "")}
