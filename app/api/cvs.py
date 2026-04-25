import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db_session, require_current_user
from app.models.cv import CvDocument, CvFeedback, CvVersion
from app.models.job import Job
from app.models.user import User
from app.schemas.cv import (
    CvDocumentCreateEnvelope,
    CvDocumentCreateRequest,
    CvFeedbackData,
    CvFeedbackEnvelope,
    CvFeedbackRead,
    CvTailorData,
    CvTailorEnvelope,
    CvTailorRequest,
    CvVersionCreateEnvelope,
    CvVersionCreateRequest,
    CvVersionListEnvelope,
    CvVersionRead,
    CvVersionSummary,
)
from app.services.application_studio import generate_cv_feedback, latest_parse_for, render_cv_markdown, tailor_cv


router = APIRouter(tags=["cvs"])


@router.post("/cvs", response_model=CvDocumentCreateEnvelope)
def create_cv_document(
    payload: CvDocumentCreateRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> CvDocumentCreateEnvelope:
    document = CvDocument(user_id=user.id, name=payload.name, description=payload.description)
    db.add(document)
    db.commit()
    db.refresh(document)
    return CvDocumentCreateEnvelope(data={"cvDocumentId": document.id})


def _get_user_document(db: Session, user: User, cv_document_id: uuid.UUID) -> CvDocument:
    document = (
        db.query(CvDocument)
        .filter(CvDocument.id == cv_document_id, CvDocument.user_id == user.id)
        .one_or_none()
    )
    if document is None:
        raise HTTPException(status_code=404, detail="CV document not found")
    return document


@router.post("/cvs/{cv_document_id}/versions", response_model=CvVersionCreateEnvelope)
def create_cv_version(
    cv_document_id: uuid.UUID,
    payload: CvVersionCreateRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> CvVersionCreateEnvelope:
    _get_user_document(db, user, cv_document_id)
    rendered_markdown = render_cv_markdown(payload.structured_content)
    version = CvVersion(
        cv_document_id=cv_document_id,
        status=payload.status,
        title=payload.title,
        summary=payload.structured_content.get("summary"),
        structured_content_json=payload.structured_content,
        rendered_markdown=rendered_markdown,
        ats_plain_text=rendered_markdown,
        created_by_ai=False,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return CvVersionCreateEnvelope(data={"cvVersionId": version.id})


@router.get("/cvs/{cv_document_id}/versions", response_model=CvVersionListEnvelope)
def list_cv_versions(
    cv_document_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> CvVersionListEnvelope:
    _get_user_document(db, user, cv_document_id)
    versions = (
        db.query(CvVersion)
        .filter(CvVersion.cv_document_id == cv_document_id)
        .order_by(CvVersion.created_at.desc())
        .all()
    )
    return CvVersionListEnvelope(data=[CvVersionSummary.model_validate(version) for version in versions])


@router.post("/cvs/{cv_document_id}/tailor", response_model=CvTailorEnvelope)
def tailor_cv_for_job(
    cv_document_id: uuid.UUID,
    payload: CvTailorRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> CvTailorEnvelope:
    _get_user_document(db, user, cv_document_id)
    base_version = (
        db.query(CvVersion)
        .filter(CvVersion.id == payload.base_version_id, CvVersion.cv_document_id == cv_document_id)
        .one_or_none()
    )
    if base_version is None:
        raise HTTPException(status_code=404, detail="Base CV version not found")

    job = db.query(Job).options(joinedload(Job.parses)).filter(Job.id == payload.job_id).one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    tailored = tailor_cv(base_version, job, latest_parse_for(job), payload.preferences)
    db.add(tailored)
    db.commit()
    db.refresh(tailored)
    return CvTailorEnvelope(data=CvTailorData(cv_version=CvVersionRead.model_validate(tailored)))


@router.post("/cv-versions/{cv_version_id}/feedback", response_model=CvFeedbackEnvelope)
def create_cv_feedback(
    cv_version_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> CvFeedbackEnvelope:
    version = (
        db.query(CvVersion)
        .join(CvDocument)
        .filter(CvVersion.id == cv_version_id, CvDocument.user_id == user.id)
        .one_or_none()
    )
    if version is None:
        raise HTTPException(status_code=404, detail="CV version not found")

    feedback = generate_cv_feedback(version)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return CvFeedbackEnvelope(data=CvFeedbackData(feedback=CvFeedbackRead.model_validate(feedback)))
