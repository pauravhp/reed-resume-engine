import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# ─── Profile ──────────────────────────────────────────────────────────────────

class Profile(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    bio_context: str | None = Field(default=None)
    groq_api_key: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    linkedin_url: str | None = Field(default=None)
    github_url: str | None = Field(default=None)


class ProfileUpdate(SQLModel):
    bio_context: str | None = None
    groq_api_key: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None


class ProfilePublic(SQLModel):
    bio_context: str | None = None
    groq_api_key_set: bool
    phone: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None


# ─── Education ────────────────────────────────────────────────────────────────

class Education(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    institution: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: str
    location: str | None = Field(default=None)
    gpa: str | None = Field(default=None)
    coursework: list = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default="[]"))
    display_order: int = Field(default=0)


class EducationCreate(SQLModel):
    institution: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: str
    location: str | None = None
    gpa: str | None = None
    coursework: list[str] = []
    display_order: int = 0


class EducationUpdate(SQLModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    location: str | None = None
    gpa: str | None = None
    coursework: list[str] | None = None
    display_order: int | None = None


class EducationPublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    institution: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: str
    location: str | None
    gpa: str | None
    coursework: list[str]
    display_order: int


class EducationsPublic(SQLModel):
    data: list[EducationPublic]
    count: int


# ─── Leadership ───────────────────────────────────────────────────────────────

class Leadership(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    organization: str
    role: str
    start_date: str
    end_date: str
    location: str | None = Field(default=None)
    bullets: list = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default="[]"))
    display_order: int = Field(default=0)


class LeadershipCreate(SQLModel):
    organization: str
    role: str
    start_date: str
    end_date: str
    location: str | None = None
    bullets: list = []
    display_order: int = 0


class LeadershipUpdate(SQLModel):
    organization: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    location: str | None = None
    bullets: list | None = None
    display_order: int | None = None


class LeadershipPublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    organization: str
    role: str
    start_date: str
    end_date: str
    location: str | None
    bullets: list
    display_order: int


class LeadershipListPublic(SQLModel):
    data: list[LeadershipPublic]
    count: int


# ─── Project ──────────────────────────────────────────────────────────────────

class Project(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    name: str
    tech_stack: str | None = Field(default=None)
    bullets: list = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default="[]"))
    display_order: int = Field(default=0)
    github_url: str | None = Field(default=None)
    live_url: str | None = Field(default=None)


class ProjectCreate(SQLModel):
    name: str
    tech_stack: str | None = None
    bullets: list = []
    display_order: int = 0
    github_url: str | None = None
    live_url: str | None = None


class ProjectUpdate(SQLModel):
    name: str | None = None
    tech_stack: str | None = None
    bullets: list | None = None
    display_order: int | None = None
    github_url: str | None = None
    live_url: str | None = None


class ProjectPublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    tech_stack: str | None
    bullets: list
    display_order: int
    github_url: str | None
    live_url: str | None


class ProjectsPublic(SQLModel):
    data: list[ProjectPublic]
    count: int


# ─── Experience ───────────────────────────────────────────────────────────────

class Experience(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    company: str
    role: str
    start_date: str
    end_date: str
    location: str | None = Field(default=None)
    bullets: list = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default="[]"))
    display_order: int = Field(default=0)


class ExperienceCreate(SQLModel):
    company: str
    role: str
    start_date: str
    end_date: str
    location: str | None = None
    bullets: list = []
    display_order: int = 0


class ExperienceUpdate(SQLModel):
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    location: str | None = None
    bullets: list | None = None
    display_order: int | None = None


class ExperiencePublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    company: str
    role: str
    start_date: str
    end_date: str
    location: str | None
    bullets: list
    display_order: int


class ExperiencesPublic(SQLModel):
    data: list[ExperiencePublic]
    count: int


# ─── Skills ───────────────────────────────────────────────────────────────────

class Skills(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    languages: list = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default="[]"))
    frameworks: list = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default="[]"))
    tools: list = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default="[]"))


class SkillsUpdate(SQLModel):
    languages: list[str] = []
    frameworks: list[str] = []
    tools: list[str] = []


class SkillsPublic(SQLModel):
    languages: list[str]
    frameworks: list[str]
    tools: list[str]


# ─── JobPosting ───────────────────────────────────────────────────────────────

class JobPosting(SQLModel, table=True):
    __tablename__ = "jobposting"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url: str = Field(unique=True, index=True)
    jd_text: str
    company: str | None = Field(default=None)
    role_title: str | None = Field(default=None)
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobPostingPublic(SQLModel):
    id: uuid.UUID
    url: str
    company: str | None
    role_title: str | None
    scraped_at: datetime


# ─── Application ──────────────────────────────────────────────────────────────

APPLICATION_STATUSES = {
    "not_applied",
    "applied",
    "response_received",
    "interview",
    "rejected",
    "offer",
}


class Application(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    job_posting_id: uuid.UUID | None = Field(default=None, foreign_key="jobposting.id")
    generated_json: dict = Field(default={}, sa_column=Column(JSONB, nullable=False, server_default="{}"))
    generated_latex: str
    match_score: int | None = Field(default=None)
    status: str = Field(default="not_applied")
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    jd_text: str | None = Field(default=None)


class ApplicationCreate(SQLModel):
    job_posting_id: uuid.UUID | None = None
    generated_json: dict = {}
    generated_latex: str
    match_score: int | None = None


class ApplicationUpdate(SQLModel):
    status: str | None = None
    notes: str | None = None


class ApplicationPublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_posting_id: uuid.UUID | None
    generated_json: dict
    generated_latex: str
    match_score: int | None
    status: str
    notes: str | None
    created_at: datetime


class ApplicationsPublic(SQLModel):
    data: list[ApplicationPublic]
    count: int
