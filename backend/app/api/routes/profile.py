from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.core.security import decrypt_api_key, encrypt_api_key
from app.models import Profile, ProfilePublic, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=ProfilePublic)
def read_profile(session: SessionDep, current_user: CurrentUser) -> Any:
    db_row = session.get(Profile, current_user.id)
    if not db_row:
        return ProfilePublic(groq_api_key_set=False)
    return ProfilePublic(
        bio_context=db_row.bio_context,
        groq_api_key_set=db_row.groq_api_key is not None,
        phone=db_row.phone,
        linkedin_url=db_row.linkedin_url,
        github_url=db_row.github_url,
    )


@router.put("/", response_model=ProfilePublic)
def upsert_profile(
    *, session: SessionDep, current_user: CurrentUser, profile_in: ProfileUpdate
) -> Any:
    db_row = session.get(Profile, current_user.id)
    if not db_row:
        db_row = Profile(user_id=current_user.id)

    update_dict = profile_in.model_dump(exclude_unset=True)

    # Fernet-encrypt the key before storing; never persist plaintext
    if "groq_api_key" in update_dict and update_dict["groq_api_key"] is not None:
        update_dict["groq_api_key"] = encrypt_api_key(update_dict["groq_api_key"])

    db_row.sqlmodel_update(update_dict)
    session.add(db_row)
    session.commit()
    session.refresh(db_row)

    return ProfilePublic(
        bio_context=db_row.bio_context,
        groq_api_key_set=db_row.groq_api_key is not None,
        phone=db_row.phone,
        linkedin_url=db_row.linkedin_url,
        github_url=db_row.github_url,
    )
