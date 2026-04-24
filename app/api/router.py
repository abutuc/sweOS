from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.exercises import router as exercises_router
from app.api.goals import router as goals_router
from app.api.preferences import router as preferences_router
from app.api.profile import router as profile_router
from app.api.skills import router as skills_router


router = APIRouter()
router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(exercises_router)
router.include_router(goals_router)
router.include_router(preferences_router)
router.include_router(profile_router)
router.include_router(skills_router)


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
