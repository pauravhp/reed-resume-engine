from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.models import Skills, SkillsPublic, SkillsUpdate

router = APIRouter(prefix="/skills", tags=["skills"])

_EMPTY = SkillsPublic(languages=[], frameworks=[], tools=[])


@router.get("/", response_model=SkillsPublic)
def read_skills(session: SessionDep, current_user: CurrentUser) -> Any:
    db_row = session.get(Skills, current_user.id)
    if not db_row:
        return _EMPTY
    return SkillsPublic(
        languages=db_row.languages or [],
        frameworks=db_row.frameworks or [],
        tools=db_row.tools or [],
    )


@router.put("/", response_model=SkillsPublic)
def upsert_skills(
    *, session: SessionDep, current_user: CurrentUser, skills_in: SkillsUpdate
) -> Any:
    db_row = session.get(Skills, current_user.id)
    if not db_row:
        db_row = Skills(user_id=current_user.id)
    # Full-replace: always overwrite all three arrays
    db_row.languages = skills_in.languages
    db_row.frameworks = skills_in.frameworks
    db_row.tools = skills_in.tools
    session.add(db_row)
    session.commit()
    session.refresh(db_row)
    return SkillsPublic(
        languages=db_row.languages or [],
        frameworks=db_row.frameworks or [],
        tools=db_row.tools or [],
    )
