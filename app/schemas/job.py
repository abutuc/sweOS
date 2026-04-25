import uuid
from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field

from app.models.job import JobStatus
from app.schemas.base import ApiSchema


class JobCreateRequest(ApiSchema):
    title: str
    company_name: str | None = None
    source_url: str | None = None
    raw_description: str
    location: str | None = None
    work_mode: str | None = None


class JobRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company_name: str | None = None
    source_url: str | None = None
    location: str | None = None
    work_mode: str | None = None
    raw_description: str | None = None


class JobCreateData(ApiSchema):
    job: JobRead


class JobCreateEnvelope(ApiSchema):
    data: JobCreateData


class JobParseRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parsed_title: str | None = None
    parsed_company_name: str | None = None
    responsibilities_json: list[str] = Field(alias="responsibilities")
    required_skills_json: list[str] = Field(alias="requiredSkills")
    preferred_skills_json: list[str] = Field(alias="preferredSkills")
    keywords_json: list[str] = Field(alias="keywords")
    seniority_assessment: str | None = None
    summary_markdown: str | None = None


class JobParseData(ApiSchema):
    parse: JobParseRead


class JobParseEnvelope(ApiSchema):
    data: JobParseData


class JobListItem(ApiSchema):
    id: uuid.UUID
    title: str
    company_name: str | None = None
    location: str | None = None
    status: JobStatus | None = None
    match_score: float | None = None
    user_job_id: uuid.UUID | None = None


class JobListEnvelope(ApiSchema):
    data: list[JobListItem]
    meta: dict[str, int]


class UserJobSaveRequest(ApiSchema):
    status: JobStatus = JobStatus.saved
    notes: str | None = None


class UserJobSaveData(ApiSchema):
    user_job_id: uuid.UUID
    status: JobStatus


class UserJobSaveEnvelope(ApiSchema):
    data: UserJobSaveData


class JobGapAnalysisRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fit_summary_markdown: str
    matched_skills_json: list[dict[str, Any]] = Field(alias="matchedSkills")
    missing_skills_json: list[dict[str, Any]] = Field(alias="missingSkills")
    weak_evidence_json: list[dict[str, Any]] = Field(alias="weakEvidence")
    recommendation_json: dict[str, Any] = Field(alias="recommendation")
    created_at: datetime | None = None


class JobGapAnalysisData(ApiSchema):
    analysis: JobGapAnalysisRead


class JobGapAnalysisEnvelope(ApiSchema):
    data: JobGapAnalysisData
