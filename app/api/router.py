from fastapi import APIRouter

from app.api.goals import router as goals_router
from app.api.profile import router as profile_router
from app.api.skills import router as skills_router


router = APIRouter()
router.include_router(goals_router)
router.include_router(profile_router)
router.include_router(skills_router)


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
