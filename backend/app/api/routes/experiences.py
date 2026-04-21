import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Experience,
    ExperienceCreate,
    ExperiencePublic,
    ExperiencesPublic,
    ExperienceUpdate,
    Message,
)

router = APIRouter(prefix="/experiences", tags=["experiences"])


@router.get("/", response_model=ExperiencesPublic)
def read_experiences(session: SessionDep, current_user: CurrentUser) -> Any:
    count_statement = (
        select(func.count())
        .select_from(Experience)
        .where(Experience.user_id == current_user.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Experience)
        .where(Experience.user_id == current_user.id)
        .order_by(Experience.display_order.asc())
    )
    experiences = session.exec(statement).all()
    return ExperiencesPublic(data=experiences, count=count)


@router.post("/", response_model=ExperiencePublic)
def create_experience(
    *, session: SessionDep, current_user: CurrentUser, experience_in: ExperienceCreate
) -> Any:
    experience = Experience.model_validate(
        experience_in, update={"user_id": current_user.id}
    )
    session.add(experience)
    session.commit()
    session.refresh(experience)
    return experience


@router.put("/{id}", response_model=ExperiencePublic)
def update_experience(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    experience_in: ExperienceUpdate,
) -> Any:
    experience = session.get(Experience, id)
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    if experience.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = experience_in.model_dump(exclude_unset=True)
    experience.sqlmodel_update(update_dict)
    session.add(experience)
    session.commit()
    session.refresh(experience)
    return experience


@router.delete("/{id}", response_model=Message)
def delete_experience(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    experience = session.get(Experience, id)
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    if experience.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(experience)
    session.commit()
    return Message(message="Experience deleted successfully")
