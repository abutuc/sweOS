from __future__ import annotations

import hashlib
import ipaddress
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.ingestion import (
    AuditActorType,
    AuditEvent,
    ExternalAccount,
    ExternalTransaction,
    ExternalTransactionStatus,
    IngestionItem,
    IngestionItemStatus,
    IngestionItemType,
    IngestionRun,
    IngestionRunStatus,
    IngestionSource,
    IngestionSourceType,
    IngestionTriggerType,
    ParsedIngestionItem,
    ParsedItemParserType,
    ReconciliationDiscrepancy,
    ReconciliationDiscrepancySeverity,
    ReconciliationDiscrepancyType,
    ReconciliationItem,
    ReconciliationItemStatus,
    ReconciliationRun,
    ReconciliationStatus,
    ReconciliationType,
    WorkerJob,
    WorkerJobStatus,
    WorkerJobType,
)
from app.models.user import User
from app.services.ingestion_parsers import MockAIParser, OptionalLLMParser, ParsedArtifact, Parser, RuleBasedParser, parse_source_url


RETRY_BACKOFF_SECONDS = (30, 120, 600)


@dataclass(slots=True)
class EngineOverview:
    total_sources: int
    active_runs: int
    queued_jobs: int
    failed_jobs: int
    parsed_items: int
    open_discrepancies: int
    dead_lettered_jobs: int
    recent_run_ids: list[str]
    recent_failed_job_ids: list[str]
    recent_discrepancy_ids: list[str]


def content_hash(raw_content: str, canonical_url: str | None = None, external_id: str | None = None) -> str:
    payload = {
        "canonical_url": canonical_url,
        "external_id": external_id,
        "raw_content": raw_content.strip(),
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_idempotency_key(*parts: str) -> str:
    normalized = [part.strip() for part in parts if part and part.strip()]
    return ":".join(normalized)


def retry_backoff_seconds(attempts: int) -> int:
    if attempts <= 1:
        return RETRY_BACKOFF_SECONDS[0]
    if attempts == 2:
        return RETRY_BACKOFF_SECONDS[1]
    return RETRY_BACKOFF_SECONDS[-1]


def is_safe_fetch_url(url: str, allow_private: bool = False) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False

    host = parsed.hostname.lower()
    if host in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
        return allow_private

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return True

    if allow_private:
        return True

    return not (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _event(db: Session, *, entity_type: str, entity_id: str, event_type: str, actor_type: AuditActorType, actor_id: str | None = None, payload: dict[str, Any] | None = None) -> AuditEvent:
    event = AuditEvent(
        entity_type=entity_type,
        entity_id=entity_id,
        event_type=event_type,
        actor_type=actor_type,
        actor_id=actor_id,
        payload_json=payload or {},
    )
    db.add(event)
    return event


def _choose_parser(source_type: IngestionSourceType, use_ai: bool = False) -> Parser:
    if use_ai:
        return MockAIParser()

    if source_type is IngestionSourceType.mock_exchange:
        return RuleBasedParser()

    return RuleBasedParser()


def _sample_items_for_source(source: IngestionSource) -> list[dict[str, Any]]:
    config = source.config_json or {}
    base_url = parse_source_url(source.url) or source.url

    if source.type == IngestionSourceType.rss_feed:
        feed_title = config.get("title") or source.name
        return [
            {
                "type": "article",
                "title": f"{feed_title} roundup",
                "canonical_url": f"{base_url}/item-1" if base_url else None,
                "raw_content": f"Article from {source.name}. It discusses Go, PostgreSQL, Docker, and background ingestion workflows.",
                "raw_json": {"source": source.name, "feedTitle": feed_title},
            },
            {
                "type": "article",
                "title": f"{feed_title} signals",
                "canonical_url": f"{base_url}/item-2" if base_url else None,
                "raw_content": f"{source.name} published notes on reliability, queues, and reconciliation.",
                "raw_json": {"source": source.name, "feedTitle": feed_title},
            },
        ]

    if source.type in {IngestionSourceType.manual_url, IngestionSourceType.company_careers_page}:
        return [
            {
                "type": "job_post",
                "title": config.get("title") or source.name,
                "canonical_url": base_url,
                "raw_content": config.get("text") or f"Fetched role description from {source.name}. Responsibilities include Go, APIs, workers, and PostgreSQL.",
                "raw_json": {
                    "company": config.get("company"),
                    "location": config.get("location"),
                    "seniority": config.get("seniority") or "mid",
                },
            }
        ]

    if source.type is IngestionSourceType.manual_text:
        return [
            {
                "type": str(config.get("itemType") or "manual_text"),
                "title": config.get("title") or source.name,
                "canonical_url": base_url,
                "raw_content": config.get("text") or "Manual ingestion sample text covering workers, deduplication, and audit events.",
                "raw_json": {"sourceName": source.name},
            }
        ]

    if source.type in {IngestionSourceType.github_repository, IngestionSourceType.github_search}:
        repo_name = config.get("repoName") or "sweos/ingestion-engine"
        owner, _, name = repo_name.partition("/")
        if not name:
            owner, name = "sweos", repo_name
        return [
            {
                "type": "github_repository",
                "title": name,
                "canonical_url": base_url or f"https://github.com/{owner}/{name}",
                "raw_content": config.get("readme") or "Repository metadata with Go services, workers, and observability.",
                "raw_json": {
                    "full_name": f"{owner}/{name}",
                    "owner": owner,
                    "name": name,
                    "description": config.get("description") or "Background worker platform",
                    "languages": config.get("languages") or ["Go", "TypeScript"],
                    "topics": config.get("topics") or ["backend", "workers", "platform"],
                    "stars": config.get("stars") or 128,
                    "forks": config.get("forks") or 11,
                },
            }
        ]

    if source.type is IngestionSourceType.job_board:
        return [
            {
                "type": "job_post",
                "title": config.get("title") or "Senior Go Backend Engineer",
                "canonical_url": base_url,
                "raw_content": config.get("text") or "Build ingestion services, async workers, and reconciliation pipelines using Go, PostgreSQL, and Docker.",
                "raw_json": {
                    "company": config.get("company") or source.name,
                    "location": config.get("location") or "Remote",
                    "seniority": config.get("seniority") or "senior",
                },
            }
        ]

    if source.type is IngestionSourceType.mock_exchange:
        provider = config.get("provider") or "mock-exchange"
        return [
            {
                "type": "mock_balance_snapshot",
                "title": f"{provider} balance snapshot",
                "canonical_url": None,
                "raw_content": "Balance snapshot for simulated custodial account.",
                "raw_json": {
                    "provider": provider,
                    "account_ref": config.get("accountRef") or "acct-001",
                    "asset_symbol": config.get("assetSymbol") or "USDC",
                    "balance": config.get("balance") or 1000.0,
                },
            },
            {
                "type": "mock_transaction",
                "title": f"{provider} transfer",
                "canonical_url": None,
                "raw_content": "Completed simulated transfer after reconciliation.",
                "raw_json": {
                    "provider": provider,
                    "external_tx_id": config.get("externalTxId") or "tx-001",
                    "from_account_ref": config.get("fromAccountRef") or "acct-001",
                    "to_account_ref": config.get("toAccountRef") or "acct-002",
                    "asset_symbol": config.get("assetSymbol") or "USDC",
                    "amount": config.get("amount") or 100.0,
                    "fee": config.get("fee") or 0.02,
                    "status": "completed",
                },
            },
        ]

    return [
        {
            "type": "unknown",
            "title": source.name,
            "canonical_url": base_url,
            "raw_content": config.get("text") or f"Signal captured from {source.name}.",
            "raw_json": {"sourceName": source.name},
        }
    ]


def _persist_item(db: Session, run: IngestionRun, source: IngestionSource, payload: dict[str, Any]) -> IngestionItem:
    canonical_url = payload.get("canonical_url")
    external_id = payload.get("external_id")
    raw_content = str(payload.get("raw_content") or "")
    digest = content_hash(raw_content, canonical_url=canonical_url, external_id=external_id)
    duplicate = db.query(IngestionItem).filter(IngestionItem.content_hash == digest).one_or_none()

    item = IngestionItem(
        run_id=run.id,
        source_id=source.id,
        external_id=external_id,
        canonical_url=canonical_url,
        type=payload.get("type") or IngestionItemType.unknown,
        title=payload.get("title"),
        raw_content=raw_content,
        raw_json=payload.get("raw_json") or {},
        content_hash=digest,
        status=IngestionItemStatus.duplicate if duplicate else IngestionItemStatus.fetched,
        duplicate_of_id=duplicate.id if duplicate else None,
        fetched_at=_now(),
    )
    db.add(item)
    run.fetched_item_count += 1
    if duplicate:
        _event(
            db,
            entity_type="ingestion_item",
            entity_id=str(item.id),
            event_type="item_deduplicated",
            actor_type=AuditActorType.system,
            payload={"duplicateOfId": str(duplicate.id), "contentHash": digest},
        )
    else:
        _event(
            db,
            entity_type="ingestion_item",
            entity_id=str(item.id),
            event_type="item_fetched",
            actor_type=AuditActorType.worker,
            payload={"contentHash": digest, "itemType": item.type},
        )
    return item


def _persist_parsed_item(db: Session, item: IngestionItem, parsed: ParsedArtifact) -> ParsedIngestionItem:
    parsed_item = ParsedIngestionItem(
        item_id=item.id,
        parser_type=ParsedItemParserType.ai if parsed.model_name and parsed.model_name != "rule-based-parser" else ParsedItemParserType.rule_based,
        parsed_type=parsed.parsed_type,
        parsed_json=parsed.parsed_json,
        summary_markdown=parsed.summary_markdown,
        confidence_score=parsed.confidence_score,
        prompt_version=parsed.prompt_version,
        model_name=parsed.model_name,
    )
    db.add(parsed_item)
    item.status = IngestionItemStatus.parsed
    _event(
        db,
        entity_type="ingestion_item",
        entity_id=str(item.id),
        event_type="item_parsed",
        actor_type=AuditActorType.worker,
        payload={"parsedType": parsed.parsed_type, "confidenceScore": parsed.confidence_score},
    )
    return parsed_item


def _queue_job(
    db: Session,
    *,
    job_type: WorkerJobType,
    run_id: str | None,
    item_id: str | None,
    payload_json: dict[str, Any] | None = None,
    idempotency_key: str,
    priority: int = 5,
) -> WorkerJob:
    existing = db.query(WorkerJob).filter(WorkerJob.idempotency_key == idempotency_key).one_or_none()
    if existing is not None:
        return existing

    job = WorkerJob(
        job_type=job_type,
        status=WorkerJobStatus.queued,
        priority=priority,
        run_id=run_id,
        item_id=item_id,
        idempotency_key=idempotency_key,
        payload_json=payload_json or {},
    )
    db.add(job)
    _event(
        db,
        entity_type="worker_job",
        entity_id=str(job.id),
        event_type="worker_job_queued",
        actor_type=AuditActorType.system,
        payload={"jobType": job_type, "idempotencyKey": idempotency_key},
    )
    return job


def _process_job(db: Session, job: WorkerJob, source_lookup: dict[str, IngestionSource], parser: Parser | None = None) -> None:
    job.status = WorkerJobStatus.processing
    job.started_at = _now()
    job.attempts += 1
    parser = parser or RuleBasedParser()

    try:
        if job.job_type == WorkerJobType.fetch_source and job.run_id:
            run = db.get(IngestionRun, job.run_id)
            if run is None or run.source_id is None:
                raise RuntimeError("Run or source missing")
            source = source_lookup[str(run.source_id)]
            for payload in _sample_items_for_source(source):
                item = _persist_item(db, run, source, payload)
                if item.status == IngestionItemStatus.fetched:
                    parse_job = _queue_job(
                        db,
                        job_type=WorkerJobType.parse_item,
                        run_id=str(run.id),
                        item_id=str(item.id),
                        payload_json={"itemId": str(item.id)},
                        idempotency_key=build_idempotency_key("parse_item", str(item.id)),
                    )
                    _process_job(db, parse_job, source_lookup, parser)
                else:
                    run.failed_item_count += 1
            run.status = IngestionRunStatus.completed_with_errors if run.failed_item_count else IngestionRunStatus.completed
            run.completed_at = _now()
            _event(
                db,
                entity_type="ingestion_run",
                entity_id=str(run.id),
                event_type="run_completed",
                actor_type=AuditActorType.worker,
                payload={"status": run.status, "fetchedItemCount": run.fetched_item_count, "parsedItemCount": run.parsed_item_count},
            )
        elif job.job_type == WorkerJobType.parse_item and job.item_id:
            item = db.get(IngestionItem, job.item_id)
            if item is None:
                raise RuntimeError("Item missing")
            if item.status == IngestionItemStatus.duplicate:
                job.status = WorkerJobStatus.completed
                job.completed_at = _now()
                return
            parsed = parser.parse(
                {
                    "type": item.type,
                    "title": item.title,
                    "raw_content": item.raw_content,
                    "raw_json": item.raw_json,
                    "canonical_url": item.canonical_url,
                    "external_id": item.external_id,
                }
            )
            _persist_parsed_item(db, item, parsed)
            run = db.get(IngestionRun, item.run_id)
            if run is not None:
                run.parsed_item_count += 1
        elif job.job_type == WorkerJobType.sync_mock_exchange and job.run_id:
            run = db.get(IngestionRun, job.run_id)
            if run is None or run.source_id is None:
                raise RuntimeError("Run missing")
            source = source_lookup[str(run.source_id)]
            payloads = _sample_items_for_source(source)
            for payload in payloads:
                item = _persist_item(db, run, source, payload)
                parsed = MockAIParser().parse(
                    {
                        "type": item.type,
                        "title": item.title,
                        "raw_content": item.raw_content,
                        "raw_json": item.raw_json,
                        "canonical_url": item.canonical_url,
                        "external_id": item.external_id,
                    }
                )
                _persist_parsed_item(db, item, parsed)
                run.parsed_item_count += 1
            run.status = IngestionRunStatus.completed
            run.completed_at = _now()
        elif job.job_type == WorkerJobType.run_reconciliation and job.run_id:
            run = db.get(IngestionRun, job.run_id)
            if run is None:
                raise RuntimeError("Run missing")
            reconcile_run(db, run, ReconciliationType.parsing_completeness)
        else:
            raise RuntimeError(f"Unsupported job type {job.job_type}")

        job.status = WorkerJobStatus.completed
        job.completed_at = _now()
        job.last_error = None
    except Exception as exc:  # pragma: no cover - exercised via API/unit tests
        job.last_error = str(exc)
        job.status = WorkerJobStatus.failed
        if job.attempts < job.max_attempts:
            job.status = WorkerJobStatus.retrying
            job.available_at = _now() + timedelta(seconds=retry_backoff_seconds(job.attempts))
        else:
            job.status = WorkerJobStatus.dead_lettered
        if job.run_id:
            run = db.get(IngestionRun, job.run_id)
            if run is not None:
                run.failed_item_count += 1
                if run.status != IngestionRunStatus.completed:
                    run.status = IngestionRunStatus.completed_with_errors
                run.error_message = str(exc)
        _event(
            db,
            entity_type="worker_job",
            entity_id=str(job.id),
            event_type="worker_job_failed" if job.status != WorkerJobStatus.dead_lettered else "worker_job_dead_lettered",
            actor_type=AuditActorType.worker,
            payload={"error": str(exc), "attempts": job.attempts},
        )
    finally:
        job.updated_at = _now()


def create_source(db: Session, user: User, payload: dict[str, Any]) -> IngestionSource:
    source = IngestionSource(
        user_id=user.id,
        name=payload["name"],
        type=payload["type"],
        url=payload.get("url"),
        config_json=payload.get("config") or {},
        enabled=payload.get("enabled", True),
    )
    db.add(source)
    db.flush()
    _event(db, entity_type="ingestion_source", entity_id=str(source.id), event_type="source_created", actor_type=AuditActorType.api, actor_id=str(user.id))
    db.commit()
    db.refresh(source)
    return source


def list_sources(db: Session, user: User, source_type: str | None = None, enabled: bool | None = None) -> list[IngestionSource]:
    query = db.query(IngestionSource).filter(or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None)))
    if source_type:
        query = query.filter(IngestionSource.type == source_type)
    if enabled is not None:
        query = query.filter(IngestionSource.enabled == enabled)
    return query.order_by(IngestionSource.created_at.desc()).all()


def get_source(db: Session, user: User, source_id: str) -> IngestionSource | None:
    return (
        db.query(IngestionSource)
        .filter(
            and_(
                IngestionSource.id == source_id,
                or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None)),
            )
        )
        .one_or_none()
    )


def update_source(db: Session, user: User, source: IngestionSource, payload: dict[str, Any]) -> IngestionSource:
    source.name = payload.get("name", source.name)
    source.type = payload.get("type", source.type)
    source.url = payload.get("url", source.url)
    source.config_json = payload.get("config", source.config_json)
    if "enabled" in payload:
        source.enabled = bool(payload["enabled"])
    _event(db, entity_type="ingestion_source", entity_id=str(source.id), event_type="source_updated", actor_type=AuditActorType.api, actor_id=str(user.id))
    db.commit()
    db.refresh(source)
    return source


def set_source_enabled(db: Session, user: User, source: IngestionSource, enabled: bool) -> IngestionSource:
    source.enabled = enabled
    event_type = "source_enabled" if enabled else "source_disabled"
    _event(db, entity_type="ingestion_source", entity_id=str(source.id), event_type=event_type, actor_type=AuditActorType.api, actor_id=str(user.id))
    db.commit()
    db.refresh(source)
    return source


def start_run(db: Session, user: User, source: IngestionSource, trigger_type: IngestionTriggerType, options: dict[str, Any] | None = None) -> IngestionRun:
    options = options or {}
    run = IngestionRun(
        source_id=source.id,
        status=IngestionRunStatus.queued,
        trigger_type=trigger_type,
        expected_item_count=options.get("expectedItemCount"),
        metadata_json=options,
    )
    db.add(run)
    db.flush()
    _event(db, entity_type="ingestion_run", entity_id=str(run.id), event_type="run_started", actor_type=AuditActorType.api, actor_id=str(user.id))
    job = _queue_job(
        db,
        job_type=WorkerJobType.fetch_source,
        run_id=str(run.id),
        item_id=None,
        payload_json={"sourceId": str(source.id), "triggerType": trigger_type},
        idempotency_key=build_idempotency_key("fetch_source", str(source.id), run.created_at.strftime("%Y%m%d%H")),
    )
    source_lookup = {str(source.id): source}
    _process_job(db, job, source_lookup, _choose_parser(source.type, use_ai=bool(options.get("useMockAi"))))
    db.commit()
    db.refresh(run)
    return run


def list_runs(db: Session, user: User, status: str | None = None, limit: int = 20, offset: int = 0) -> list[IngestionRun]:
    query = (
        db.query(IngestionRun)
        .join(IngestionSource, IngestionSource.id == IngestionRun.source_id)
        .filter(or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None)))
    )
    if status:
        query = query.filter(IngestionRun.status == status)
    return query.order_by(IngestionRun.created_at.desc()).offset(offset).limit(limit).all()


def get_run(db: Session, user: User, run_id: str) -> IngestionRun | None:
    return (
        db.query(IngestionRun)
        .join(IngestionSource, IngestionSource.id == IngestionRun.source_id)
        .filter(
            and_(
                IngestionRun.id == run_id,
                or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None)),
            )
        )
        .one_or_none()
    )


def cancel_run(db: Session, user: User, run: IngestionRun) -> IngestionRun:
    if run.status in {IngestionRunStatus.completed, IngestionRunStatus.failed}:
        return run
    run.status = IngestionRunStatus.cancelled
    _event(db, entity_type="ingestion_run", entity_id=str(run.id), event_type="run_cancelled", actor_type=AuditActorType.api, actor_id=str(user.id))
    db.commit()
    db.refresh(run)
    return run


def list_items(
    db: Session,
    user: User,
    run_id: str | None = None,
    item_type: str | None = None,
    status: str | None = None,
) -> list[IngestionItem]:
    query = db.query(IngestionItem).join(IngestionRun, IngestionRun.id == IngestionItem.run_id).join(IngestionSource, IngestionSource.id == IngestionRun.source_id)
    query = query.filter(or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None)))
    if run_id:
        query = query.filter(IngestionItem.run_id == run_id)
    if item_type:
        query = query.filter(IngestionItem.type == item_type)
    if status:
        query = query.filter(IngestionItem.status == status)
    return query.order_by(IngestionItem.created_at.desc()).all()


def get_item(db: Session, user: User, item_id: str) -> IngestionItem | None:
    return (
        db.query(IngestionItem)
        .join(IngestionRun, IngestionRun.id == IngestionItem.run_id)
        .join(IngestionSource, IngestionSource.id == IngestionRun.source_id)
        .filter(
            and_(
                IngestionItem.id == item_id,
                or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None)),
            )
        )
        .one_or_none()
    )


def queue_item_parse(db: Session, user: User, item: IngestionItem, use_ai: bool = False) -> WorkerJob:
    item.status = IngestionItemStatus.queued_for_parsing
    run = db.get(IngestionRun, item.run_id)
    if run is not None:
        run.metadata_json = {**(run.metadata_json or {}), "parseImmediately": True}
    source = db.get(IngestionSource, item.source_id) if item.source_id else None
    parser = _choose_parser(source.type if source else IngestionSourceType.manual_text, use_ai=use_ai)
    job = _queue_job(
        db,
        job_type=WorkerJobType.parse_item,
        run_id=str(item.run_id),
        item_id=str(item.id),
        payload_json={"itemId": str(item.id), "useAi": use_ai},
        idempotency_key=build_idempotency_key("parse_item", str(item.id)),
    )
    source_lookup = {str(source.id): source} if source is not None else {}
    _process_job(db, job, source_lookup, parser)
    db.commit()
    db.refresh(item)
    return job


def archive_item(db: Session, user: User, item: IngestionItem) -> IngestionItem:
    item.status = IngestionItemStatus.archived
    _event(db, entity_type="ingestion_item", entity_id=str(item.id), event_type="item_archived", actor_type=AuditActorType.api, actor_id=str(user.id))
    db.commit()
    db.refresh(item)
    return item


def list_worker_jobs(
    db: Session,
    user: User,
    status: str | None = None,
    job_type: str | None = None,
) -> list[WorkerJob]:
    query = db.query(WorkerJob).join(IngestionRun, IngestionRun.id == WorkerJob.run_id, isouter=True).join(IngestionSource, IngestionSource.id == IngestionRun.source_id, isouter=True)
    query = query.filter(or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None), IngestionSource.id.is_(None)))
    if status:
        query = query.filter(WorkerJob.status == status)
    if job_type:
        query = query.filter(WorkerJob.job_type == job_type)
    return query.order_by(WorkerJob.created_at.desc()).all()


def get_worker_job(db: Session, user: User, job_id: str) -> WorkerJob | None:
    return (
        db.query(WorkerJob)
        .join(IngestionRun, IngestionRun.id == WorkerJob.run_id, isouter=True)
        .join(IngestionSource, IngestionSource.id == IngestionRun.source_id, isouter=True)
        .filter(
            and_(
                WorkerJob.id == job_id,
                or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None), IngestionSource.id.is_(None)),
            )
        )
        .one_or_none()
    )


def retry_worker_job(db: Session, user: User, job: WorkerJob) -> WorkerJob:
    job.status = WorkerJobStatus.queued
    job.last_error = None
    job.available_at = _now()
    job.attempts = max(0, job.attempts - 1)
    _event(db, entity_type="worker_job", entity_id=str(job.id), event_type="worker_job_retried", actor_type=AuditActorType.api, actor_id=str(user.id))
    db.commit()
    db.refresh(job)
    return job


def cancel_worker_job(db: Session, user: User, job: WorkerJob) -> WorkerJob:
    job.status = WorkerJobStatus.cancelled
    _event(db, entity_type="worker_job", entity_id=str(job.id), event_type="worker_job_cancelled", actor_type=AuditActorType.api, actor_id=str(user.id))
    db.commit()
    db.refresh(job)
    return job


def _new_discrepancy(
    reconciliation_run: ReconciliationRun,
    *,
    severity: ReconciliationDiscrepancySeverity,
    discrepancy_type: ReconciliationDiscrepancyType,
    description: str,
    expected_json: dict[str, Any] | None = None,
    actual_json: dict[str, Any] | None = None,
    item: ReconciliationItem | None = None,
) -> ReconciliationDiscrepancy:
    return ReconciliationDiscrepancy(
        reconciliation_run_id=reconciliation_run.id,
        reconciliation_item_id=item.id if item else None,
        severity=severity,
        type=discrepancy_type,
        description=description,
        expected_json=expected_json or {},
        actual_json=actual_json or {},
    )


def reconcile_run(db: Session, run: IngestionRun, reconciliation_type: ReconciliationType) -> ReconciliationRun:
    reconciliation_run = ReconciliationRun(
        run_id=run.id,
        type=reconciliation_type,
        status=ReconciliationStatus.running,
        started_at=_now(),
    )
    db.add(reconciliation_run)
    db.flush()

    items = db.query(IngestionItem).filter(IngestionItem.run_id == run.id).all()
    parsed_items = db.query(ParsedIngestionItem).join(IngestionItem, IngestionItem.id == ParsedIngestionItem.item_id).filter(IngestionItem.run_id == run.id).all()

    if reconciliation_type is ReconciliationType.parsing_completeness:
        reconciliation_run.expected_count = len([item for item in items if item.status != IngestionItemStatus.duplicate])
        reconciliation_run.actual_count = len(parsed_items)
        for item in items:
            if item.status == IngestionItemStatus.duplicate:
                continue
            if not any(parsed.item_id == item.id for parsed in parsed_items):
                discrepancy = _new_discrepancy(
                    reconciliation_run,
                    severity=ReconciliationDiscrepancySeverity.medium,
                    discrepancy_type=ReconciliationDiscrepancyType.parse_failed,
                    description=f"Item {item.id} was fetched but not parsed.",
                    expected_json={"status": "parsed"},
                    actual_json={"status": item.status},
                )
                db.add(discrepancy)
                reconciliation_run.discrepancy_count += 1
    elif reconciliation_type is ReconciliationType.ingestion_completeness:
        reconciliation_run.expected_count = run.expected_item_count or len(items)
        reconciliation_run.actual_count = len(items)
        if reconciliation_run.actual_count != reconciliation_run.expected_count:
            discrepancy = _new_discrepancy(
                reconciliation_run,
                severity=ReconciliationDiscrepancySeverity.medium,
                discrepancy_type=ReconciliationDiscrepancyType.missing_raw_item,
                description="Fetched item count differs from expected item count.",
                expected_json={"expected": reconciliation_run.expected_count},
                actual_json={"actual": reconciliation_run.actual_count},
            )
            db.add(discrepancy)
            reconciliation_run.discrepancy_count += 1
    elif reconciliation_type is ReconciliationType.duplicate_detection:
        reconciliation_run.expected_count = len(items)
        reconciliation_run.actual_count = len(items)
        duplicates = [item for item in items if item.duplicate_of_id is not None]
        reconciliation_run.discrepancy_count = len(duplicates)
        for item in duplicates:
            db.add(
                _new_discrepancy(
                    reconciliation_run,
                    severity=ReconciliationDiscrepancySeverity.low,
                    discrepancy_type=ReconciliationDiscrepancyType.duplicate_external_id,
                    description="Duplicate item detected by content hash.",
                    expected_json={"contentHash": item.content_hash},
                    actual_json={"duplicateOfId": str(item.duplicate_of_id)},
                )
            )
    elif reconciliation_type is ReconciliationType.mock_exchange_transfers:
        transactions = db.query(ExternalTransaction).order_by(ExternalTransaction.created_at.desc()).all()
        reconciliation_run.expected_count = len(transactions)
        reconciliation_run.actual_count = len(transactions)
        for tx in transactions:
            if float(tx.amount) < 100.0:
                db.add(
                    _new_discrepancy(
                        reconciliation_run,
                        severity=ReconciliationDiscrepancySeverity.medium,
                        discrepancy_type=ReconciliationDiscrepancyType.amount_mismatch,
                        description=f"Transaction {tx.external_tx_id} settled below the expected threshold.",
                        expected_json={"amount": "100.00", "asset": tx.asset_symbol},
                        actual_json={"amount": str(tx.amount), "fee": str(tx.fee)},
                    )
                )
                reconciliation_run.discrepancy_count += 1
    else:
        reconciliation_run.expected_count = len(items)
        reconciliation_run.actual_count = len(parsed_items)

    reconciliation_run.status = ReconciliationStatus.completed
    reconciliation_run.completed_at = _now()
    reconciliation_run.summary_markdown = f"{reconciliation_run.actual_count} of {reconciliation_run.expected_count} records matched."
    _event(
        db,
        entity_type="reconciliation_run",
        entity_id=str(reconciliation_run.id),
        event_type="reconciliation_completed",
        actor_type=AuditActorType.worker,
        payload={"type": reconciliation_type, "discrepancyCount": reconciliation_run.discrepancy_count},
    )
    db.commit()
    db.refresh(reconciliation_run)
    return reconciliation_run


def start_reconciliation(db: Session, user: User, run: IngestionRun, reconciliation_type: ReconciliationType) -> ReconciliationRun:
    reconciliation_run = reconcile_run(db, run, reconciliation_type)
    return reconciliation_run


def list_reconciliation_runs(db: Session, user: User, reconciliation_type: str | None = None) -> list[ReconciliationRun]:
    query = db.query(ReconciliationRun).join(IngestionRun, IngestionRun.id == ReconciliationRun.run_id, isouter=True).join(IngestionSource, IngestionSource.id == IngestionRun.source_id, isouter=True)
    query = query.filter(or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None), IngestionSource.id.is_(None)))
    if reconciliation_type:
        query = query.filter(ReconciliationRun.type == reconciliation_type)
    return query.order_by(ReconciliationRun.created_at.desc()).all()


def get_reconciliation_run(db: Session, user: User, reconciliation_run_id: str) -> ReconciliationRun | None:
    return (
        db.query(ReconciliationRun)
        .join(IngestionRun, IngestionRun.id == ReconciliationRun.run_id, isouter=True)
        .join(IngestionSource, IngestionSource.id == IngestionRun.source_id, isouter=True)
        .filter(
            and_(
                ReconciliationRun.id == reconciliation_run_id,
                or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None), IngestionSource.id.is_(None)),
            )
        )
        .one_or_none()
    )


def list_discrepancies(db: Session, user: User, reconciliation_run: ReconciliationRun) -> list[ReconciliationDiscrepancy]:
    query = db.query(ReconciliationDiscrepancy).filter(ReconciliationDiscrepancy.reconciliation_run_id == reconciliation_run.id)
    return query.order_by(ReconciliationDiscrepancy.created_at.desc()).all()


def resolve_discrepancy(db: Session, user: User, discrepancy: ReconciliationDiscrepancy) -> ReconciliationDiscrepancy:
    discrepancy.resolved = True
    discrepancy.resolved_at = _now()
    _event(
        db,
        entity_type="reconciliation_discrepancy",
        entity_id=str(discrepancy.id),
        event_type="discrepancy_resolved",
        actor_type=AuditActorType.api,
        actor_id=str(user.id),
    )
    db.commit()
    db.refresh(discrepancy)
    return discrepancy


def list_audit_events(
    db: Session,
    user: User,
    entity_type: str | None = None,
    entity_id: str | None = None,
    event_type: str | None = None,
) -> list[AuditEvent]:
    query = db.query(AuditEvent)
    if entity_type:
        query = query.filter(AuditEvent.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditEvent.entity_id == entity_id)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type)
    return query.order_by(AuditEvent.created_at.desc()).all()


def sync_mock_exchange(db: Session, user: User, source: IngestionSource) -> IngestionRun:
    run = start_run(db, user, source, IngestionTriggerType.api, {"useMockAi": True})
    if run.source_id is None:
        raise RuntimeError("Run missing source")
    source_lookup = {str(source.id): source}
    job = _queue_job(
        db,
        job_type=WorkerJobType.sync_mock_exchange,
        run_id=str(run.id),
        item_id=None,
        payload_json={"sourceId": str(source.id)},
        idempotency_key=build_idempotency_key("mock_exchange_sync", str(source.id), run.created_at.strftime("%Y%m%d%H")),
    )
    _process_job(db, job, source_lookup, MockAIParser())
    reconciliation = start_reconciliation(db, user, run, ReconciliationType.mock_exchange_transfers)
    run.metadata_json = {**(run.metadata_json or {}), "reconciliationRunId": str(reconciliation.id)}
    db.commit()
    db.refresh(run)
    return run


def list_external_accounts(db: Session) -> list[ExternalAccount]:
    return db.query(ExternalAccount).order_by(ExternalAccount.created_at.desc()).all()


def list_external_transactions(db: Session) -> list[ExternalTransaction]:
    return db.query(ExternalTransaction).order_by(ExternalTransaction.created_at.desc()).all()


def get_overview(db: Session, user: User) -> EngineOverview:
    sources = db.query(IngestionSource).filter(or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None)))
    active_runs = db.query(IngestionRun).join(IngestionSource, IngestionSource.id == IngestionRun.source_id).filter(or_(IngestionSource.user_id == user.id, IngestionSource.user_id.is_(None)), IngestionRun.status.in_([IngestionRunStatus.queued, IngestionRunStatus.running])).count()
    queued_jobs = db.query(WorkerJob).filter(WorkerJob.status == WorkerJobStatus.queued).count()
    failed_jobs = db.query(WorkerJob).filter(WorkerJob.status == WorkerJobStatus.failed).count()
    parsed_items = db.query(ParsedIngestionItem).count()
    open_discrepancies = db.query(ReconciliationDiscrepancy).filter(ReconciliationDiscrepancy.resolved.is_(False)).count()
    dead_lettered_jobs = db.query(WorkerJob).filter(WorkerJob.status == WorkerJobStatus.dead_lettered).count()
    recent_runs = [str(item.id) for item in db.query(IngestionRun).order_by(IngestionRun.created_at.desc()).limit(3).all()]
    recent_failed_jobs = [str(item.id) for item in db.query(WorkerJob).filter(WorkerJob.status == WorkerJobStatus.failed).order_by(WorkerJob.created_at.desc()).limit(3).all()]
    recent_discrepancies = [str(item.id) for item in db.query(ReconciliationDiscrepancy).order_by(ReconciliationDiscrepancy.created_at.desc()).limit(3).all()]
    return EngineOverview(
        total_sources=sources.count(),
        active_runs=active_runs,
        queued_jobs=queued_jobs,
        failed_jobs=failed_jobs,
        parsed_items=parsed_items,
        open_discrepancies=open_discrepancies,
        dead_lettered_jobs=dead_lettered_jobs,
        recent_run_ids=recent_runs,
        recent_failed_job_ids=recent_failed_jobs,
        recent_discrepancy_ids=recent_discrepancies,
    )
