from typing import Any

from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Education, EducationPublic, EducationUpdate

router = APIRouter(prefix="/education", tags=["education"])

_EMPTY = EducationPublic(
    institution="",
    degree="",
    field_of_study="",
    start_date="",
    end_date="",
    location=None,
    gpa=None,
    coursework=[],
)


@router.get("/", response_model=EducationPublic)
def read_education(session: SessionDep, current_user: CurrentUser) -> Any:
    db_row = session.get(Education, current_user.id)
    if not db_row:
        return _EMPTY
    return EducationPublic(
        institution=db_row.institution,
        degree=db_row.degree,
        field_of_study=db_row.field_of_study,
        start_date=db_row.start_date,
        end_date=db_row.end_date,
        location=db_row.location,
        gpa=db_row.gpa,
        coursework=db_row.coursework or [],
    )


@router.put("/", response_model=EducationPublic)
def upsert_education(
    *, session: SessionDep, current_user: CurrentUser, education_in: EducationUpdate
) -> Any:
    db_row = session.get(Education, current_user.id)
    if not db_row:
        db_row = Education(
            user_id=current_user.id,
            institution=education_in.institution or "",
            degree=education_in.degree or "",
            field_of_study=education_in.field_of_study or "",
            start_date=education_in.start_date or "",
            end_date=education_in.end_date or "",
        )
    update_dict = education_in.model_dump(exclude_unset=True)
    db_row.sqlmodel_update(update_dict)
    session.add(db_row)
    session.commit()
    session.refresh(db_row)
    return EducationPublic(
        institution=db_row.institution,
        degree=db_row.degree,
        field_of_study=db_row.field_of_study,
        start_date=db_row.start_date,
        end_date=db_row.end_date,
        location=db_row.location,
        gpa=db_row.gpa,
        coursework=db_row.coursework or [],
    )
