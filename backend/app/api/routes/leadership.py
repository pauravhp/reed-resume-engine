import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Leadership,
    LeadershipCreate,
    LeadershipListPublic,
    LeadershipPublic,
    LeadershipUpdate,
    Message,
)

router = APIRouter(prefix="/leadership", tags=["leadership"])


@router.get("/", response_model=LeadershipListPublic)
def read_leadership(session: SessionDep, current_user: CurrentUser) -> Any:
    count_statement = (
        select(func.count())
        .select_from(Leadership)
        .where(Leadership.user_id == current_user.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Leadership)
        .where(Leadership.user_id == current_user.id)
        .order_by(Leadership.display_order.asc())
    )
    entries = session.exec(statement).all()
    return LeadershipListPublic(data=entries, count=count)


@router.post("/", response_model=LeadershipPublic)
def create_leadership(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    entry_in: LeadershipCreate,
) -> Any:
    entry = Leadership.model_validate(entry_in, update={"user_id": current_user.id})
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.put("/{id}", response_model=LeadershipPublic)
def update_leadership(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    entry_in: LeadershipUpdate,
) -> Any:
    entry = session.get(Leadership, id)
    if not entry:
        raise HTTPException(status_code=404, detail="Leadership entry not found")
    if entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = entry_in.model_dump(exclude_unset=True)
    entry.sqlmodel_update(update_dict)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.delete("/{id}", response_model=Message)
def delete_leadership(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    entry = session.get(Leadership, id)
    if not entry:
        raise HTTPException(status_code=404, detail="Leadership entry not found")
    if entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(entry)
    session.commit()
    return Message(message="Leadership entry deleted successfully")
