from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.dependencies import get_db_session
from app.api.cvs import router as cvs_router
from app.api.dashboard import router as dashboard_router
from app.api.ingestion import router as ingestion_router
from app.api.exercises import router as exercises_router
from app.api.goals import router as goals_router
from app.api.jobs import router as jobs_router
from app.api.learning import router as learning_router
from app.api.preferences import router as preferences_router
from app.api.profile import router as profile_router
from app.api.skills import router as skills_router


router = APIRouter()
router.include_router(analytics_router)
router.include_router(auth_router)
router.include_router(cvs_router)
router.include_router(dashboard_router)
router.include_router(ingestion_router)
router.include_router(exercises_router)
router.include_router(goals_router)
router.include_router(jobs_router)
router.include_router(learning_router)
router.include_router(preferences_router)
router.include_router(profile_router)
router.include_router(skills_router)


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
def readyz(db: Session = Depends(get_db_session)) -> dict[str, str]:
    db.execute(text("select 1"))
    return {"status": "ok"}


@router.get("/metrics")
def metrics(db: Session = Depends(get_db_session)) -> Response:
    total_sources = db.execute(text("select count(*) from ingestion_sources")).scalar_one()
    active_runs = db.execute(text("select count(*) from ingestion_runs where status in ('queued', 'running')")).scalar_one()
    failed_jobs = db.execute(text("select count(*) from worker_jobs where status in ('failed', 'dead_lettered')")).scalar_one()
    body = "\n".join(
        [
            "# HELP ingestion_sources_total Total ingestion sources",
            "# TYPE ingestion_sources_total gauge",
            f"ingestion_sources_total {total_sources}",
            "# HELP ingestion_active_runs Current active ingestion runs",
            "# TYPE ingestion_active_runs gauge",
            f"ingestion_active_runs {active_runs}",
            "# HELP ingestion_failed_jobs Current failed or dead-lettered jobs",
            "# TYPE ingestion_failed_jobs gauge",
            f"ingestion_failed_jobs {failed_jobs}",
        ]
    )
    return Response(content=body, media_type="text/plain; version=0.0.4")
