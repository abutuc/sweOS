import uuid
from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field

from app.models.cv import CvVersionStatus
from app.schemas.base import ApiSchema


class CvDocumentCreateRequest(ApiSchema):
    name: str
    description: str | None = None


class CvDocumentCreateData(ApiSchema):
    cv_document_id: uuid.UUID


class CvDocumentCreateEnvelope(ApiSchema):
    data: CvDocumentCreateData


class CvVersionCreateRequest(ApiSchema):
    status: CvVersionStatus = CvVersionStatus.base
    title: str
    structured_content: dict[str, Any]


class CvVersionCreateData(ApiSchema):
    cv_version_id: uuid.UUID


class CvVersionCreateEnvelope(ApiSchema):
    data: CvVersionCreateData


class CvVersionSummary(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: CvVersionStatus
    title: str
    job_id: uuid.UUID | None = None
    created_by_ai: bool
    created_at: datetime


class CvVersionListEnvelope(ApiSchema):
    data: list[CvVersionSummary]


class CvTailorRequest(ApiSchema):
    base_version_id: uuid.UUID
    job_id: uuid.UUID
    preferences: dict[str, Any] = Field(default_factory=dict)


class CvVersionRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: CvVersionStatus
    title: str
    structured_content_json: dict[str, Any] = Field(alias="structuredContent")
    rendered_markdown: str | None = None


class CvTailorData(ApiSchema):
    cv_version: CvVersionRead


class CvTailorEnvelope(ApiSchema):
    data: CvTailorData


class CvFeedbackRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    score: float | None = None
    strengths_json: list[str] = Field(alias="strengths")
    weaknesses_json: list[str] = Field(alias="weaknesses")
    suggestions_json: list[str] = Field(alias="suggestions")


class CvFeedbackData(ApiSchema):
    feedback: CvFeedbackRead


class CvFeedbackEnvelope(ApiSchema):
    data: CvFeedbackData
