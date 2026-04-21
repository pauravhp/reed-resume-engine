from fastapi import APIRouter

from app.api.routes import (
    applications,
    education,
    experiences,
    items,
    leadership,
    login,
    private,
    profile,
    projects,
    skills,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(profile.router)
api_router.include_router(education.router)
api_router.include_router(projects.router)
api_router.include_router(experiences.router)
api_router.include_router(skills.router)
api_router.include_router(leadership.router)
api_router.include_router(applications.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
