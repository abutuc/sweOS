import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db_session, require_current_user
from app.models.cv import CvDocument, CvVersion
from app.models.job import Job, JobStatus, UserJob
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.user_skill import UserSkill
from app.schemas.job import (
    JobCreateData,
    JobCreateEnvelope,
    JobCreateRequest,
    JobGapAnalysisData,
    JobGapAnalysisEnvelope,
    JobGapAnalysisRead,
    JobListEnvelope,
    JobListItem,
    JobParseData,
    JobParseEnvelope,
    JobParseRead,
    JobRead,
    UserJobSaveEnvelope,
    UserJobSaveRequest,
)
from app.services.application_studio import analyze_job_gap, parse_job_description


router = APIRouter(tags=["jobs"])


@router.post("/jobs", response_model=JobCreateEnvelope)
def create_job(
    payload: JobCreateRequest,
    db: Session = Depends(get_db_session),
    _user: User = Depends(require_current_user),
) -> JobCreateEnvelope:
    job = Job(
        title=payload.title,
        company_name=payload.company_name,
        source_url=payload.source_url,
        raw_description=payload.raw_description,
        location=payload.location,
        work_mode=payload.work_mode,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return JobCreateEnvelope(data=JobCreateData(job=JobRead.model_validate(job)))


@router.post("/jobs/{job_id}/parse", response_model=JobParseEnvelope)
def parse_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    _user: User = Depends(require_current_user),
) -> JobParseEnvelope:
    job = db.query(Job).filter(Job.id == job_id).one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job_parse = parse_job_description(job)
    db.add(job_parse)
    db.commit()
    db.refresh(job_parse)
    return JobParseEnvelope(data=JobParseData(parse=JobParseRead.model_validate(job_parse)))


@router.get("/jobs", response_model=JobListEnvelope)
def list_jobs(
    status: JobStatus | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> JobListEnvelope:
    query = db.query(UserJob).options(joinedload(UserJob.job)).filter(UserJob.user_id == user.id)
    if status:
        query = query.filter(UserJob.status == status)
    if search:
        pattern = f"%{search}%"
        query = query.join(Job).filter(Job.title.ilike(pattern) | Job.company_name.ilike(pattern))

    total = query.count()
    user_jobs = query.order_by(UserJob.created_at.desc()).offset(offset).limit(limit).all()
    return JobListEnvelope(
        data=[
            JobListItem(
                id=user_job.job.id,
                user_job_id=user_job.id,
                title=user_job.job.title,
                company_name=user_job.job.company_name,
                location=user_job.job.location,
                status=user_job.status,
                match_score=user_job.match_score,
            )
            for user_job in user_jobs
        ],
        meta={"limit": limit, "offset": offset, "total": total},
    )


@router.post("/jobs/{job_id}/save", response_model=UserJobSaveEnvelope)
def save_job(
    job_id: uuid.UUID,
    payload: UserJobSaveRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> UserJobSaveEnvelope:
    job = db.query(Job).filter(Job.id == job_id).one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    user_job = (
        db.query(UserJob)
        .filter(UserJob.user_id == user.id, UserJob.job_id == job_id)
        .one_or_none()
    )
    if user_job is None:
        user_job = UserJob(user_id=user.id, job_id=job_id, status=payload.status, notes=payload.notes)
        db.add(user_job)
    else:
        user_job.status = payload.status
        user_job.notes = payload.notes

    db.commit()
    db.refresh(user_job)
    return UserJobSaveEnvelope(data={"userJobId": user_job.id, "status": user_job.status})


@router.post("/user-jobs/{user_job_id}/gap-analysis", response_model=JobGapAnalysisEnvelope)
def create_gap_analysis(
    user_job_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> JobGapAnalysisEnvelope:
    user_job = (
        db.query(UserJob)
        .options(joinedload(UserJob.job).joinedload(Job.parses))
        .filter(UserJob.id == user_job_id, UserJob.user_id == user.id)
        .one_or_none()
    )
    if user_job is None:
        raise HTTPException(status_code=404, detail="Saved job not found")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).one_or_none()
    user_skills = db.query(UserSkill).options(joinedload(UserSkill.skill)).filter(UserSkill.user_id == user.id).all()
    cv_versions = (
        db.query(CvVersion)
        .join(CvDocument)
        .filter(CvDocument.user_id == user.id)
        .order_by(CvVersion.created_at.desc())
        .limit(5)
        .all()
    )
    analysis = analyze_job_gap(user_job, profile, user_skills, cv_versions)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    db.refresh(user_job)

    return JobGapAnalysisEnvelope(
        data=JobGapAnalysisData(analysis=JobGapAnalysisRead.model_validate(analysis))
    )
