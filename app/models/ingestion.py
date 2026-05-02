import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IngestionSourceType(str, enum.Enum):
    rss_feed = "rss_feed"
    manual_url = "manual_url"
    manual_text = "manual_text"
    github_repository = "github_repository"
    github_search = "github_search"
    job_board = "job_board"
    company_careers_page = "company_careers_page"
    mock_exchange = "mock_exchange"


class IngestionRunStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    completed_with_errors = "completed_with_errors"
    failed = "failed"
    cancelled = "cancelled"


class IngestionTriggerType(str, enum.Enum):
    manual = "manual"
    scheduled = "scheduled"
    api = "api"
    system = "system"


class IngestionItemType(str, enum.Enum):
    job_post = "job_post"
    article = "article"
    github_repository = "github_repository"
    github_issue = "github_issue"
    mock_transaction = "mock_transaction"
    mock_balance_snapshot = "mock_balance_snapshot"
    manual_text = "manual_text"
    unknown = "unknown"


class IngestionItemStatus(str, enum.Enum):
    fetched = "fetched"
    duplicate = "duplicate"
    queued_for_parsing = "queued_for_parsing"
    parsed = "parsed"
    failed = "failed"
    archived = "archived"


class ParsedItemParserType(str, enum.Enum):
    rule_based = "rule_based"
    ai = "ai"
    mock_exchange = "mock_exchange"
    manual = "manual"


class WorkerJobType(str, enum.Enum):
    fetch_source = "fetch_source"
    deduplicate_item = "deduplicate_item"
    parse_item = "parse_item"
    classify_item = "classify_item"
    run_ai_parse = "run_ai_parse"
    run_reconciliation = "run_reconciliation"
    sync_mock_exchange = "sync_mock_exchange"


class WorkerJobStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    retrying = "retrying"
    dead_lettered = "dead_lettered"
    cancelled = "cancelled"


class AuditActorType(str, enum.Enum):
    user = "user"
    worker = "worker"
    system = "system"
    api = "api"


class ReconciliationType(str, enum.Enum):
    ingestion_completeness = "ingestion_completeness"
    parsing_completeness = "parsing_completeness"
    duplicate_detection = "duplicate_detection"
    mock_exchange_balances = "mock_exchange_balances"
    mock_exchange_transfers = "mock_exchange_transfers"


class ReconciliationStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ReconciliationItemStatus(str, enum.Enum):
    matched = "matched"
    mismatched = "mismatched"
    missing = "missing"
    unexpected = "unexpected"


class ReconciliationDiscrepancySeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ReconciliationDiscrepancyType(str, enum.Enum):
    missing_raw_item = "missing_raw_item"
    duplicate_external_id = "duplicate_external_id"
    parse_failed = "parse_failed"
    stale_item = "stale_item"
    checksum_mismatch = "checksum_mismatch"
    unexpected_status_transition = "unexpected_status_transition"
    amount_mismatch = "amount_mismatch"
    balance_mismatch = "balance_mismatch"
    missing_transfer = "missing_transfer"
    unexpected_transfer = "unexpected_transfer"


class ExternalTransactionStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class IngestionSource(Base):
    __tablename__ = "ingestion_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[IngestionSourceType] = mapped_column(String, nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    config_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    runs = relationship("IngestionRun", back_populates="source", cascade="all, delete-orphan")


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingestion_sources.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[IngestionRunStatus] = mapped_column(String, nullable=False, default=IngestionRunStatus.queued)
    trigger_type: Mapped[IngestionTriggerType] = mapped_column(String, nullable=False, default=IngestionTriggerType.manual)
    expected_item_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fetched_item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parsed_item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    source = relationship("IngestionSource", back_populates="runs")
    items = relationship("IngestionItem", back_populates="run", cascade="all, delete-orphan")
    worker_jobs = relationship("WorkerJob", back_populates="run", cascade="all, delete-orphan")
    reconciliation_runs = relationship("ReconciliationRun", back_populates="run", cascade="all, delete-orphan")


class IngestionItem(Base):
    __tablename__ = "ingestion_items"
    __table_args__ = (
        CheckConstraint("raw_content <> ''", name="ck_ingestion_items_raw_content_not_empty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ingestion_runs.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingestion_sources.id", ondelete="SET NULL"),
        nullable=True,
    )
    external_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[IngestionItemType] = mapped_column(String, nullable=False, default=IngestionItemType.unknown)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[IngestionItemStatus] = mapped_column(String, nullable=False, default=IngestionItemStatus.fetched)
    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingestion_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    run = relationship("IngestionRun", back_populates="items")
    source = relationship("IngestionSource")
    duplicate_of = relationship("IngestionItem", remote_side="IngestionItem.id")
    parsed_items = relationship("ParsedIngestionItem", back_populates="item", cascade="all, delete-orphan")
    worker_jobs = relationship("WorkerJob", back_populates="item", cascade="all, delete-orphan")
    reconciliation_items = relationship("ReconciliationItem", back_populates="item", cascade="all, delete-orphan")


class ParsedIngestionItem(Base):
    __tablename__ = "parsed_ingestion_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ingestion_items.id", ondelete="CASCADE"), nullable=False)
    parser_type: Mapped[ParsedItemParserType] = mapped_column(String, nullable=False)
    parsed_type: Mapped[str] = mapped_column(String, nullable=False)
    parsed_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    summary_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    item = relationship("IngestionItem", back_populates="parsed_items")


class WorkerJob(Base):
    __tablename__ = "worker_jobs"
    __table_args__ = (
        CheckConstraint("priority >= 0", name="ck_worker_jobs_priority_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type: Mapped[WorkerJobType] = mapped_column(String, nullable=False)
    status: Mapped[WorkerJobStatus] = mapped_column(String, nullable=False, default=WorkerJobStatus.queued)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("ingestion_runs.id", ondelete="CASCADE"), nullable=True)
    item_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("ingestion_items.id", ondelete="CASCADE"), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    locked_by: Mapped[str | None] = mapped_column(String, nullable=True)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    run = relationship("IngestionRun", back_populates="worker_jobs")
    item = relationship("IngestionItem", back_populates="worker_jobs")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    actor_type: Mapped[AuditActorType] = mapped_column(String, nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String, nullable=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("ingestion_runs.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[ReconciliationType] = mapped_column(String, nullable=False)
    status: Mapped[ReconciliationStatus] = mapped_column(String, nullable=False, default=ReconciliationStatus.queued)
    expected_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    actual_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    discrepancy_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    summary_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    run = relationship("IngestionRun", back_populates="reconciliation_runs")
    items = relationship("ReconciliationItem", back_populates="reconciliation_run", cascade="all, delete-orphan")
    discrepancies = relationship("ReconciliationDiscrepancy", back_populates="reconciliation_run", cascade="all, delete-orphan")


class ReconciliationItem(Base):
    __tablename__ = "reconciliation_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reconciliation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reconciliation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    external_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    expected_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    actual_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[ReconciliationItemStatus] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    reconciliation_run = relationship("ReconciliationRun", back_populates="items")
    item = relationship("IngestionItem", back_populates="reconciliation_items")


class ReconciliationDiscrepancy(Base):
    __tablename__ = "reconciliation_discrepancies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reconciliation_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reconciliation_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    reconciliation_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reconciliation_items.id", ondelete="CASCADE"),
        nullable=True,
    )
    severity: Mapped[ReconciliationDiscrepancySeverity] = mapped_column(String, nullable=False)
    type: Mapped[ReconciliationDiscrepancyType] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expected_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    actual_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    reconciliation_run = relationship("ReconciliationRun", back_populates="discrepancies")
    reconciliation_item = relationship("ReconciliationItem")


class ExternalAccount(Base):
    __tablename__ = "external_accounts"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_external_accounts_balance_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    account_ref: Mapped[str] = mapped_column(String, nullable=False)
    asset_symbol: Mapped[str] = mapped_column(String, nullable=False)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ExternalTransaction(Base):
    __tablename__ = "external_transactions"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_external_transactions_amount_non_negative"),
        CheckConstraint("fee >= 0", name="ck_external_transactions_fee_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    external_tx_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    from_account_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    to_account_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    asset_symbol: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(24, 8), nullable=False)
    fee: Mapped[float] = mapped_column(Numeric(24, 8), nullable=False, default=0)
    status: Mapped[ExternalTransactionStatus] = mapped_column(String, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
