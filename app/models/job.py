import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.exercise import SourceType


class JobStatus(str, enum.Enum):
    saved = "saved"
    considering = "considering"
    applied = "applied"
    interviewing = "interviewing"
    offer = "offer"
    rejected = "rejected"
    archived = "archived"


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("external_id", "source_url", name="uq_jobs_external_id_source_url"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type", values_callable=lambda enum_cls: [item.value for item in enum_cls]),
        nullable=False,
        default=SourceType.manual,
    )
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    company_name: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    work_mode: Mapped[str | None] = mapped_column(String, nullable=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str | None] = mapped_column(String, nullable=True)
    seniority: Mapped[str | None] = mapped_column(String, nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String, nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    parses = relationship("JobParse", back_populates="job", cascade="all, delete-orphan")
    user_jobs = relationship("UserJob", back_populates="job", cascade="all, delete-orphan")


class JobParse(Base):
    __tablename__ = "job_parses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    parsed_title: Mapped[str | None] = mapped_column(String, nullable=True)
    parsed_company_name: Mapped[str | None] = mapped_column(String, nullable=True)
    responsibilities_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    required_skills_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    preferred_skills_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    keywords_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    seniority_assessment: Mapped[str | None] = mapped_column(String, nullable=True)
    summary_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    job = relationship("Job", back_populates="parses")


class UserJob(Base):
    __tablename__ = "user_jobs"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_user_jobs_user_id_job_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", values_callable=lambda enum_cls: [item.value for item in enum_cls]),
        nullable=False,
        default=JobStatus.saved,
    )
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    interest_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    job = relationship("Job", back_populates="user_jobs")
    analyses = relationship("JobGapAnalysis", back_populates="user_job", cascade="all, delete-orphan")


class JobGapAnalysis(Base):
    __tablename__ = "job_gap_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    fit_summary_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    matched_skills_json: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    missing_skills_json: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    weak_evidence_json: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    recommendation_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user_job = relationship("UserJob", back_populates="analyses")
