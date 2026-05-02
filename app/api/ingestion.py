from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_current_user
from app.models.ingestion import (
    IngestionSourceType,
    ReconciliationDiscrepancy,
    ReconciliationType,
)
from app.schemas.ingestion import (
    AuditEventListEnvelope,
    AuditEventRead,
    EngineOverviewEnvelope,
    EngineOverviewRead,
    ExternalAccountRead,
    ExternalTransactionRead,
    IngestionActionEnvelope,
    IngestionItemListEnvelope,
    IngestionItemRead,
    IngestionRunListEnvelope,
    IngestionRunRead,
    IngestionRunStartRequest,
    IngestionSourceCreateRequest,
    IngestionSourceEnvelope,
    IngestionSourceListEnvelope,
    IngestionSourceRead,
    IngestionSourceUpdateRequest,
    ReconciliationDiscrepancyListEnvelope,
    ReconciliationDiscrepancyRead,
    ReconciliationRunListEnvelope,
    ReconciliationRunRead,
    WorkerJobListEnvelope,
    WorkerJobRead,
)
from app.services.ingestion_engine import (
    archive_item,
    cancel_run,
    cancel_worker_job,
    create_source,
    get_item,
    get_overview,
    get_reconciliation_run,
    get_run,
    get_source,
    get_worker_job,
    list_audit_events,
    list_discrepancies,
    list_external_accounts,
    list_external_transactions,
    list_items,
    list_reconciliation_runs,
    list_runs,
    list_sources,
    list_worker_jobs,
    queue_item_parse,
    retry_worker_job,
    resolve_discrepancy,
    set_source_enabled,
    start_reconciliation,
    start_run,
    sync_mock_exchange,
    update_source,
)


router = APIRouter(prefix="/ingestion", tags=["ingestion"])


def _source_or_404(db: Session, user, source_id: str):
    source = get_source(db, user, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


def _run_or_404(db: Session, user, run_id: str):
    run = get_run(db, user, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


def _item_or_404(db: Session, user, item_id: str):
    item = get_item(db, user, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


def _worker_job_or_404(db: Session, user, job_id: str):
    job = get_worker_job(db, user, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Worker job not found")
    return job


def _reconciliation_or_404(db: Session, user, reconciliation_run_id: str):
    reconciliation_run = get_reconciliation_run(db, user, reconciliation_run_id)
    if reconciliation_run is None:
        raise HTTPException(status_code=404, detail="Reconciliation run not found")
    return reconciliation_run


@router.get("/overview", response_model=EngineOverviewEnvelope)
def read_overview(
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    overview = get_overview(db, user)
    return EngineOverviewEnvelope(
        data=EngineOverviewRead.model_validate(overview),
    )


@router.post("/sources", response_model=IngestionSourceEnvelope)
def create_ingestion_source(
    payload: IngestionSourceCreateRequest,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    source = create_source(db, user, payload.model_dump(by_alias=False))
    return IngestionSourceEnvelope(data=IngestionSourceRead.model_validate(source))


@router.get("/sources", response_model=IngestionSourceListEnvelope)
def read_ingestion_sources(
    type: IngestionSourceType | None = Query(default=None),
    enabled: bool | None = Query(default=None),
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    sources = list_sources(db, user, source_type=type.value if type else None, enabled=enabled)
    return IngestionSourceListEnvelope(data=[IngestionSourceRead.model_validate(item) for item in sources])


@router.get("/sources/{source_id}", response_model=IngestionSourceEnvelope)
def read_ingestion_source(
    source_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    source = _source_or_404(db, user, source_id)
    return IngestionSourceEnvelope(data=IngestionSourceRead.model_validate(source))


@router.put("/sources/{source_id}", response_model=IngestionSourceEnvelope)
def update_ingestion_source(
    source_id: str,
    payload: IngestionSourceUpdateRequest,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    source = _source_or_404(db, user, source_id)
    updated = update_source(db, user, source, payload.model_dump(by_alias=False, exclude_none=True))
    return IngestionSourceEnvelope(data=IngestionSourceRead.model_validate(updated))


@router.post("/sources/{source_id}/enable", response_model=IngestionSourceEnvelope)
def enable_ingestion_source(
    source_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    source = _source_or_404(db, user, source_id)
    updated = set_source_enabled(db, user, source, True)
    return IngestionSourceEnvelope(data=IngestionSourceRead.model_validate(updated))


@router.post("/sources/{source_id}/disable", response_model=IngestionSourceEnvelope)
def disable_ingestion_source(
    source_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    source = _source_or_404(db, user, source_id)
    updated = set_source_enabled(db, user, source, False)
    return IngestionSourceEnvelope(data=IngestionSourceRead.model_validate(updated))


@router.post("/runs", response_model=IngestionRunRead)
def start_ingestion_run_endpoint(
    payload: IngestionRunStartRequest,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    source = _source_or_404(db, user, str(payload.source_id))
    run = start_run(db, user, source, payload.trigger_type, payload.options)
    return IngestionRunRead.model_validate(run)


@router.get("/runs", response_model=IngestionRunListEnvelope)
def read_ingestion_runs(
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    runs = list_runs(db, user, status=status, limit=limit, offset=offset)
    return IngestionRunListEnvelope(data=[IngestionRunRead.model_validate(item) for item in runs], meta={"limit": limit, "offset": offset, "count": len(runs)})


@router.get("/runs/{run_id}", response_model=IngestionRunRead)
def read_ingestion_run(
    run_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    run = _run_or_404(db, user, run_id)
    return IngestionRunRead.model_validate(run)


@router.post("/runs/{run_id}/cancel", response_model=IngestionRunRead)
def cancel_ingestion_run_endpoint(
    run_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    run = _run_or_404(db, user, run_id)
    return IngestionRunRead.model_validate(cancel_run(db, user, run))


@router.get("/items", response_model=IngestionItemListEnvelope)
def read_ingestion_items(
    run_id: str | None = Query(default=None),
    type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    items = list_items(db, user, run_id=run_id, item_type=type, status=status)
    return IngestionItemListEnvelope(data=[IngestionItemRead.model_validate(item) for item in items])


@router.get("/items/{item_id}", response_model=IngestionItemRead)
def read_ingestion_item(
    item_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    item = _item_or_404(db, user, item_id)
    return IngestionItemRead.model_validate(item)


@router.post("/items/{item_id}/parse", response_model=IngestionActionEnvelope)
def queue_item_parse_endpoint(
    item_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    item = _item_or_404(db, user, item_id)
    job = queue_item_parse(db, user, item)
    status = getattr(job.status, "value", job.status)
    return IngestionActionEnvelope(data={"jobId": str(job.id), "status": status})


@router.post("/items/{item_id}/archive", response_model=IngestionItemRead)
def archive_ingestion_item_endpoint(
    item_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    item = _item_or_404(db, user, item_id)
    return IngestionItemRead.model_validate(archive_item(db, user, item))


@router.get("/worker-jobs", response_model=WorkerJobListEnvelope)
def read_worker_jobs(
    status: str | None = Query(default=None),
    job_type: str | None = Query(default=None),
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    jobs = list_worker_jobs(db, user, status=status, job_type=job_type)
    return WorkerJobListEnvelope(data=[WorkerJobRead.model_validate(job) for job in jobs])


@router.get("/worker-jobs/{job_id}", response_model=WorkerJobRead)
def read_worker_job(
    job_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    job = _worker_job_or_404(db, user, job_id)
    return WorkerJobRead.model_validate(job)


@router.post("/worker-jobs/{job_id}/retry", response_model=WorkerJobRead)
def retry_worker_job_endpoint(
    job_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    job = _worker_job_or_404(db, user, job_id)
    return WorkerJobRead.model_validate(retry_worker_job(db, user, job))


@router.post("/worker-jobs/{job_id}/cancel", response_model=WorkerJobRead)
def cancel_worker_job_endpoint(
    job_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    job = _worker_job_or_404(db, user, job_id)
    return WorkerJobRead.model_validate(cancel_worker_job(db, user, job))


@router.post("/reconciliation-runs", response_model=ReconciliationRunRead)
def create_reconciliation_run(
    payload: dict[str, Any],
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    run = _run_or_404(db, user, str(payload["runId"]))
    reconciliation_type = ReconciliationType(payload["type"])
    reconciliation_run = start_reconciliation(db, user, run, reconciliation_type)
    return ReconciliationRunRead.model_validate(reconciliation_run)


@router.get("/reconciliation-runs", response_model=ReconciliationRunListEnvelope)
def read_reconciliation_runs(
    type: str | None = Query(default=None),
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    runs = list_reconciliation_runs(db, user, reconciliation_type=type)
    return ReconciliationRunListEnvelope(data=[ReconciliationRunRead.model_validate(item) for item in runs])


@router.get("/reconciliation-runs/{reconciliation_run_id}", response_model=ReconciliationRunRead)
def read_reconciliation_run(
    reconciliation_run_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    reconciliation_run = _reconciliation_or_404(db, user, reconciliation_run_id)
    return ReconciliationRunRead.model_validate(reconciliation_run)


@router.get("/reconciliation-runs/{reconciliation_run_id}/discrepancies", response_model=ReconciliationDiscrepancyListEnvelope)
def read_reconciliation_discrepancies(
    reconciliation_run_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    reconciliation_run = _reconciliation_or_404(db, user, reconciliation_run_id)
    discrepancies = list_discrepancies(db, user, reconciliation_run)
    return ReconciliationDiscrepancyListEnvelope(data=[ReconciliationDiscrepancyRead.model_validate(item) for item in discrepancies])


@router.post("/discrepancies/{discrepancy_id}/resolve", response_model=IngestionActionEnvelope)
def resolve_discrepancy_endpoint(
    discrepancy_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    discrepancy = db.get(ReconciliationDiscrepancy, discrepancy_id)
    if discrepancy is None:
        raise HTTPException(status_code=404, detail="Discrepancy not found")
    resolved = resolve_discrepancy(db, user, discrepancy)
    return IngestionActionEnvelope(data={"resolved": resolved.resolved})


@router.get("/audit-events", response_model=AuditEventListEnvelope)
def read_audit_events(
    entity_type: str | None = Query(default=None, alias="entityType"),
    entity_id: str | None = Query(default=None, alias="entityId"),
    event_type: str | None = Query(default=None, alias="eventType"),
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    events = list_audit_events(db, user, entity_type=entity_type, entity_id=entity_id, event_type=event_type)
    return AuditEventListEnvelope(data=[AuditEventRead.model_validate(item) for item in events])


@router.post("/mock-exchange/sync", response_model=IngestionRunRead)
def sync_mock_exchange_endpoint(
    source_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    source = _source_or_404(db, user, source_id)
    if source.type != IngestionSourceType.mock_exchange:
        raise HTTPException(status_code=400, detail="Source is not a mock exchange")
    run = sync_mock_exchange(db, user, source)
    return IngestionRunRead.model_validate(run)


@router.get("/mock-exchange/accounts", response_model=dict[str, list[ExternalAccountRead]])
def read_mock_exchange_accounts(
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    return {"data": [ExternalAccountRead.model_validate(item) for item in list_external_accounts(db)]}


@router.get("/mock-exchange/transactions", response_model=dict[str, list[ExternalTransactionRead]])
def read_mock_exchange_transactions(
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    return {"data": [ExternalTransactionRead.model_validate(item) for item in list_external_transactions(db)]}


@router.post("/mock-exchange/reconcile-transfers", response_model=IngestionActionEnvelope)
def reconcile_mock_exchange_transfers(
    source_id: str,
    db: Session = Depends(get_db_session),
    user=Depends(require_current_user),
):
    source = _source_or_404(db, user, source_id)
    if source.type != IngestionSourceType.mock_exchange:
        raise HTTPException(status_code=400, detail="Source is not a mock exchange")
    run = sync_mock_exchange(db, user, source)
    return IngestionActionEnvelope(data={"runId": str(run.id), "status": run.status.value})
