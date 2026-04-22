import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Education, EducationCreate, EducationPublic, EducationsPublic, EducationUpdate

router = APIRouter(prefix="/education", tags=["education"])


@router.get("/", response_model=EducationsPublic)
def list_education(session: SessionDep, current_user: CurrentUser) -> Any:
    rows = session.exec(
        select(Education)
        .where(Education.user_id == current_user.id)
        .order_by(Education.display_order.asc())
    ).all()
    return EducationsPublic(data=list(rows), count=len(rows))


@router.post("/", response_model=EducationPublic)
def create_education(
    *, session: SessionDep, current_user: CurrentUser, edu_in: EducationCreate
) -> Any:
    row = Education(user_id=current_user.id, **edu_in.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.patch("/{education_id}", response_model=EducationPublic)
def update_education(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    education_id: uuid.UUID,
    edu_in: EducationUpdate,
) -> Any:
    row = session.get(Education, education_id)
    if not row:
        raise HTTPException(status_code=404, detail="Education entry not found")
    if row.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = edu_in.model_dump(exclude_unset=True)
    row.sqlmodel_update(update_dict)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.delete("/{education_id}")
def delete_education(
    *, session: SessionDep, current_user: CurrentUser, education_id: uuid.UUID
) -> Any:
    row = session.get(Education, education_id)
    if not row:
        raise HTTPException(status_code=404, detail="Education entry not found")
    if row.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(row)
    session.commit()
    return {"message": "Education entry deleted"}
