"""
Tailored answer generation.

POST /answers/generate — single Groq call using JD + question + user bio context.
Stateless: no Application row is created.
"""

import json
from typing import Any

import groq
from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.api.deps import CurrentUser, SessionDep
from app.core.security import decrypt_api_key
from app.models import Profile

router = APIRouter(prefix="/answers", tags=["answers"])


class AnswerRequest(SQLModel):
    jd_text: str
    question: str


class AnswerResponse(SQLModel):
    answer: str


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=8),
    retry=retry_if_exception_type(groq.RateLimitError),
)
async def _call_groq_answer(
    client: groq.AsyncGroq,
    jd_text: str,
    question: str,
    bio_context: str,
) -> dict:
    """Generate a personalised answer to an application question.

    Returns: {"answer": str}
    """
    prompt = f"""You are an expert career coach helping a candidate write compelling job application answers.

Using the candidate's background and the job description below, write a strong, specific answer to the application question.

ABSOLUTE RULE — NO HALLUCINATION:
- The Candidate Background is the ONLY source of truth about the candidate. Use ONLY facts literally present in it.
- Do NOT invent, imply, or infer any credentials, degrees, program names, schools, employers, job titles, years of experience, technologies, frameworks, languages, certifications, publications, or achievements that are not explicitly stated in the Candidate Background.
- If the Candidate Background does not mention a specific tool, framework, or skill that would be useful for this answer, DO NOT claim the candidate has it — just work with what is actually there.
- If the Candidate Background does not specify degree level (bachelor's / master's / PhD), DO NOT assert one.
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
{bio_context}

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

    client = groq.AsyncGroq(api_key=api_key)

    try:
        result = await _call_groq_answer(
            client,
            request.jd_text,
            request.question,
            profile.bio_context or "",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Answer generation failed — please retry",
        ) from exc

    return {"answer": result.get("answer", "")}
