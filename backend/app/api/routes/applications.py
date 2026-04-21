import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    APPLICATION_STATUSES,
    Application,
    ApplicationPublic,
    ApplicationUpdate,
    JobPosting,
)

router = APIRouter(prefix="/applications", tags=["applications"])


class ApplicationListItem(SQLModel):
    """Application summary row — includes job posting metadata from the join."""

    id: uuid.UUID
    job_posting_id: uuid.UUID | None
    company: str | None
    role_title: str | None
    match_score: int | None
    status: str
    notes: str | None
    created_at: datetime


class ApplicationsListPublic(SQLModel):
    data: list[ApplicationListItem]
    count: int


@router.get("/", response_model=ApplicationsListPublic)
def read_applications(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    count_statement = (
        select(func.count())
        .select_from(Application)
        .where(Application.user_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    # Left-join jobposting to pull company + role_title into the response
    statement = (
        select(Application, JobPosting)
        .join(JobPosting, Application.job_posting_id == JobPosting.id, isouter=True)
        .where(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    rows = session.exec(statement).all()

    data = [
        ApplicationListItem(
            id=app.id,
            job_posting_id=app.job_posting_id,
            company=jp.company if jp else None,
            role_title=jp.role_title if jp else None,
            match_score=app.match_score,
            status=app.status,
            notes=app.notes,
            created_at=app.created_at,
        )
        for app, jp in rows
    ]
    return ApplicationsListPublic(data=data, count=count)


@router.patch("/{id}", response_model=ApplicationPublic)
def update_application(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    application_in: ApplicationUpdate,
) -> Any:
    application = session.get(Application, id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if (
        application_in.status is not None
        and application_in.status not in APPLICATION_STATUSES
    ):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status. Must be one of: {sorted(APPLICATION_STATUSES)}",
        )
    update_dict = application_in.model_dump(exclude_unset=True)
    application.sqlmodel_update(update_dict)
    session.add(application)
    session.commit()
    session.refresh(application)
    return application
