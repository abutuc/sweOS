import uuid
from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field

from app.models.ingestion import (
    AuditActorType,
    ExternalTransactionStatus,
    IngestionItemStatus,
    IngestionItemType,
    IngestionRunStatus,
    IngestionSourceType,
    IngestionTriggerType,
    ParsedItemParserType,
    ReconciliationDiscrepancySeverity,
    ReconciliationDiscrepancyType,
    ReconciliationItemStatus,
    ReconciliationStatus,
    ReconciliationType,
    WorkerJobStatus,
    WorkerJobType,
)
from app.schemas.base import ApiSchema


class IngestionSourceCreateRequest(ApiSchema):
    name: str
    type: IngestionSourceType
    url: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class IngestionSourceUpdateRequest(ApiSchema):
    name: str | None = None
    type: IngestionSourceType | None = None
    url: str | None = None
    config: dict[str, Any] | None = None
    enabled: bool | None = None


class IngestionSourceRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None = None
    name: str
    type: IngestionSourceType
    url: str | None = None
    config_json: dict[str, Any] = Field(alias="config")
    enabled: bool
    created_at: datetime
    updated_at: datetime


class IngestionSourceEnvelope(ApiSchema):
    data: IngestionSourceRead


class IngestionSourceListEnvelope(ApiSchema):
    data: list[IngestionSourceRead]


class IngestionRunStartRequest(ApiSchema):
    source_id: uuid.UUID = Field(alias="sourceId")
    trigger_type: IngestionTriggerType = Field(default=IngestionTriggerType.manual, alias="triggerType")
    options: dict[str, Any] = Field(default_factory=dict)


class IngestionRunCancelEnvelope(ApiSchema):
    data: dict[str, bool]


class IngestionRunRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_id: uuid.UUID | None = Field(alias="sourceId")
    status: IngestionRunStatus
    trigger_type: IngestionTriggerType = Field(alias="triggerType")
    expected_item_count: int | None = Field(alias="expectedItemCount")
    fetched_item_count: int = Field(alias="fetchedItemCount")
    parsed_item_count: int = Field(alias="parsedItemCount")
    failed_item_count: int = Field(alias="failedItemCount")
    started_at: datetime | None = Field(alias="startedAt")
    completed_at: datetime | None = Field(alias="completedAt")
    error_message: str | None = Field(alias="errorMessage")
    metadata_json: dict[str, Any] = Field(alias="metadata")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class IngestionRunListEnvelope(ApiSchema):
    data: list[IngestionRunRead]
    meta: dict[str, int]


class IngestionItemRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID = Field(alias="runId")
    source_id: uuid.UUID | None = Field(alias="sourceId")
    external_id: str | None = Field(alias="externalId")
    canonical_url: str | None = Field(alias="canonicalUrl")
    type: IngestionItemType
    title: str | None = None
    raw_content: str = Field(alias="rawContent")
    raw_json: dict[str, Any] = Field(alias="rawJson")
    content_hash: str = Field(alias="contentHash")
    status: IngestionItemStatus
    duplicate_of_id: uuid.UUID | None = Field(alias="duplicateOfId")
    fetched_at: datetime = Field(alias="fetchedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class IngestionItemListEnvelope(ApiSchema):
    data: list[IngestionItemRead]


class ParsedItemRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    item_id: uuid.UUID = Field(alias="itemId")
    parser_type: ParsedItemParserType = Field(alias="parserType")
    parsed_type: str = Field(alias="parsedType")
    parsed_json: dict[str, Any] = Field(alias="parsedJson")
    summary_markdown: str | None = Field(alias="summaryMarkdown")
    confidence_score: float | None = Field(alias="confidenceScore")
    prompt_version: str | None = Field(alias="promptVersion")
    model_name: str | None = Field(alias="modelName")
    created_at: datetime = Field(alias="createdAt")


class WorkerJobRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_type: WorkerJobType = Field(alias="jobType")
    status: WorkerJobStatus
    priority: int
    run_id: uuid.UUID | None = Field(alias="runId")
    item_id: uuid.UUID | None = Field(alias="itemId")
    idempotency_key: str = Field(alias="idempotencyKey")
    payload_json: dict[str, Any] = Field(alias="payload")
    attempts: int
    max_attempts: int = Field(alias="maxAttempts")
    locked_by: str | None = Field(alias="lockedBy")
    locked_until: datetime | None = Field(alias="lockedUntil")
    available_at: datetime = Field(alias="availableAt")
    started_at: datetime | None = Field(alias="startedAt")
    completed_at: datetime | None = Field(alias="completedAt")
    last_error: str | None = Field(alias="lastError")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class WorkerJobListEnvelope(ApiSchema):
    data: list[WorkerJobRead]


class ReconciliationRunRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID | None = Field(alias="runId")
    type: ReconciliationType
    status: ReconciliationStatus
    expected_count: int = Field(alias="expectedCount")
    actual_count: int = Field(alias="actualCount")
    discrepancy_count: int = Field(alias="discrepancyCount")
    started_at: datetime | None = Field(alias="startedAt")
    completed_at: datetime | None = Field(alias="completedAt")
    summary_markdown: str | None = Field(alias="summaryMarkdown")
    metadata_json: dict[str, Any] = Field(alias="metadata")
    created_at: datetime = Field(alias="createdAt")


class ReconciliationRunListEnvelope(ApiSchema):
    data: list[ReconciliationRunRead]


class ReconciliationDiscrepancyRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reconciliation_run_id: uuid.UUID = Field(alias="reconciliationRunId")
    reconciliation_item_id: uuid.UUID | None = Field(alias="reconciliationItemId")
    severity: ReconciliationDiscrepancySeverity
    type: ReconciliationDiscrepancyType
    description: str
    expected_json: dict[str, Any] = Field(alias="expected")
    actual_json: dict[str, Any] = Field(alias="actual")
    resolved: bool
    resolved_at: datetime | None = Field(alias="resolvedAt")
    created_at: datetime = Field(alias="createdAt")


class ReconciliationDiscrepancyListEnvelope(ApiSchema):
    data: list[ReconciliationDiscrepancyRead]


class AuditEventRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entity_type: str = Field(alias="entityType")
    entity_id: uuid.UUID = Field(alias="entityId")
    event_type: str = Field(alias="eventType")
    actor_type: AuditActorType = Field(alias="actorType")
    actor_id: str | None = Field(alias="actorId")
    payload_json: dict[str, Any] = Field(alias="payload")
    created_at: datetime = Field(alias="createdAt")


class AuditEventListEnvelope(ApiSchema):
    data: list[AuditEventRead]


class ExternalAccountRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider: str
    account_ref: str = Field(alias="accountRef")
    asset_symbol: str = Field(alias="assetSymbol")
    balance: float
    raw_json: dict[str, Any] = Field(alias="raw")
    last_synced_at: datetime | None = Field(alias="lastSyncedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class ExternalTransactionRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider: str
    external_tx_id: str = Field(alias="externalTxId")
    from_account_ref: str | None = Field(alias="fromAccountRef")
    to_account_ref: str | None = Field(alias="toAccountRef")
    asset_symbol: str = Field(alias="assetSymbol")
    amount: float
    fee: float
    status: ExternalTransactionStatus
    occurred_at: datetime = Field(alias="occurredAt")
    raw_json: dict[str, Any] = Field(alias="raw")
    created_at: datetime = Field(alias="createdAt")


class EngineOverviewRead(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    total_sources: int = Field(alias="totalSources")
    active_runs: int = Field(alias="activeRuns")
    queued_jobs: int = Field(alias="queuedJobs")
    failed_jobs: int = Field(alias="failedJobs")
    parsed_items: int = Field(alias="parsedItems")
    open_discrepancies: int = Field(alias="openDiscrepancies")
    dead_lettered_jobs: int = Field(alias="deadLetteredJobs")
    recent_run_ids: list[str] = Field(alias="recentRunIds")
    recent_failed_job_ids: list[str] = Field(alias="recentFailedJobIds")
    recent_discrepancy_ids: list[str] = Field(alias="recentDiscrepancyIds")


class EngineOverviewEnvelope(ApiSchema):
    data: EngineOverviewRead


class IngestionActionEnvelope(ApiSchema):
    data: dict[str, Any]
