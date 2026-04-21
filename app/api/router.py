from fastapi import APIRouter

from app.api.profile import router as profile_router


router = APIRouter()
router.include_router(profile_router)


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
