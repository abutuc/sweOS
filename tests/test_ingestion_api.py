import uuid
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import ingestion as ingestion_api
from app.api.dependencies import get_db_session, require_current_user
from app.main import app


class _FakeSession:
    def close(self):
        return None

    def execute(self, *_args, **_kwargs):
        return SimpleNamespace(scalar_one=lambda: 1)


def _override_current_user(user_id: uuid.UUID):
    def _override():
        return SimpleNamespace(id=user_id)

    return _override


def test_create_source_and_read_overview(monkeypatch):
    user_id = uuid.uuid4()
    fake_session = _FakeSession()
    source_id = uuid.uuid4()

    monkeypatch.setattr(ingestion_api, "create_source", lambda _db, _user, payload: SimpleNamespace(id=source_id, user_id=user_id, created_at="2026-05-02T00:00:00Z", updated_at="2026-05-02T00:00:00Z", **payload))
    monkeypatch.setattr(ingestion_api, "get_source", lambda *_args, **_kwargs: SimpleNamespace(id=source_id, user_id=user_id, name="Go Blog RSS", type="rss_feed", url="https://go.dev/blog/feed.atom", config_json={}, enabled=True, created_at="2026-05-02T00:00:00Z", updated_at="2026-05-02T00:00:00Z"))
    monkeypatch.setattr(ingestion_api, "get_overview", lambda _db, _user: SimpleNamespace(total_sources=1, active_runs=0, queued_jobs=0, failed_jobs=0, parsed_items=0, open_discrepancies=0, dead_lettered_jobs=0, recent_run_ids=[], recent_failed_job_ids=[], recent_discrepancy_ids=[]))

    def override_get_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        source_response = client.post(
            "/api/v1/ingestion/sources",
            json={
                "name": "Go Blog RSS",
                "type": "rss_feed",
                "url": "https://go.dev/blog/feed.atom",
                "config": {"tags": ["go"]},
            },
        )
        overview_response = client.get("/api/v1/ingestion/overview")

    app.dependency_overrides.clear()

    assert source_response.status_code == 200
    assert source_response.json()["data"]["name"] == "Go Blog RSS"
    assert overview_response.status_code == 200
    assert overview_response.json()["data"]["totalSources"] == 1


def test_run_item_job_and_audit_endpoints(monkeypatch):
    user_id = uuid.uuid4()
    fake_session = _FakeSession()
    run_id = uuid.uuid4()
    item_id = uuid.uuid4()
    job_id = uuid.uuid4()
    event_id = uuid.uuid4()

    monkeypatch.setattr(ingestion_api, "start_run", lambda *_args, **_kwargs: SimpleNamespace(id=run_id, source_id=uuid.uuid4(), status="queued", trigger_type="manual", expected_item_count=None, fetched_item_count=0, parsed_item_count=0, failed_item_count=0, started_at=None, completed_at=None, error_message=None, metadata_json={}, created_at="2026-05-02T00:00:00Z", updated_at="2026-05-02T00:00:00Z"))
    monkeypatch.setattr(ingestion_api, "get_run", lambda *_args, **_kwargs: SimpleNamespace(id=run_id, source_id=uuid.uuid4(), status="completed", trigger_type="manual", expected_item_count=1, fetched_item_count=1, parsed_item_count=1, failed_item_count=0, started_at="2026-05-02T00:00:00Z", completed_at="2026-05-02T00:01:00Z", error_message=None, metadata_json={}, created_at="2026-05-02T00:00:00Z", updated_at="2026-05-02T00:01:00Z"))
    monkeypatch.setattr(ingestion_api, "get_source", lambda *_args, **_kwargs: SimpleNamespace(id=uuid.uuid4(), user_id=user_id, name="Mock Source", type="rss_feed", url=None, config_json={}, enabled=True, created_at="2026-05-02T00:00:00Z", updated_at="2026-05-02T00:00:00Z"))
    monkeypatch.setattr(ingestion_api, "get_item", lambda *_args, **_kwargs: SimpleNamespace(id=item_id, run_id=run_id, source_id=None, external_id="ext-1", canonical_url=None, type="article", title="Example", raw_content="body", raw_json={}, content_hash="abc", status="fetched", duplicate_of_id=None, fetched_at="2026-05-02T00:00:00Z", created_at="2026-05-02T00:00:00Z", updated_at="2026-05-02T00:00:00Z"))
    monkeypatch.setattr(ingestion_api, "list_runs", lambda *_args, **_kwargs: [SimpleNamespace(id=run_id, source_id=uuid.uuid4(), status="completed", trigger_type="manual", expected_item_count=1, fetched_item_count=1, parsed_item_count=1, failed_item_count=0, started_at="2026-05-02T00:00:00Z", completed_at="2026-05-02T00:01:00Z", error_message=None, metadata_json={}, created_at="2026-05-02T00:00:00Z", updated_at="2026-05-02T00:01:00Z")])
    monkeypatch.setattr(ingestion_api, "list_items", lambda *_args, **_kwargs: [SimpleNamespace(id=item_id, run_id=run_id, source_id=None, external_id="ext-1", canonical_url=None, type="article", title="Example", raw_content="body", raw_json={}, content_hash="abc", status="fetched", duplicate_of_id=None, fetched_at="2026-05-02T00:00:00Z", created_at="2026-05-02T00:00:00Z", updated_at="2026-05-02T00:00:00Z")])
    monkeypatch.setattr(ingestion_api, "queue_item_parse", lambda *_args, **_kwargs: SimpleNamespace(id=job_id, status="completed"))
    monkeypatch.setattr(ingestion_api, "list_worker_jobs", lambda *_args, **_kwargs: [SimpleNamespace(id=job_id, job_type="parse_item", status="completed", priority=5, run_id=run_id, item_id=item_id, idempotency_key="parse_item:item", payload_json={}, attempts=1, max_attempts=3, locked_by=None, locked_until=None, available_at="2026-05-02T00:00:00Z", started_at=None, completed_at=None, last_error=None, created_at="2026-05-02T00:00:00Z", updated_at="2026-05-02T00:00:00Z")])
    monkeypatch.setattr(ingestion_api, "list_audit_events", lambda *_args, **_kwargs: [SimpleNamespace(id=event_id, entity_type="ingestion_run", entity_id=run_id, event_type="run_started", actor_type="api", actor_id=str(user_id), payload_json={}, created_at="2026-05-02T00:00:00Z")])
    monkeypatch.setattr(ingestion_api, "list_reconciliation_runs", lambda *_args, **_kwargs: [SimpleNamespace(id=uuid.uuid4(), run_id=run_id, type="parsing_completeness", status="completed", expected_count=1, actual_count=1, discrepancy_count=0, started_at="2026-05-02T00:00:00Z", completed_at="2026-05-02T00:01:00Z", summary_markdown="ok", metadata_json={}, created_at="2026-05-02T00:00:00Z")])
    monkeypatch.setattr(ingestion_api, "start_reconciliation", lambda *_args, **_kwargs: SimpleNamespace(id=uuid.uuid4(), run_id=run_id, type="parsing_completeness", status="completed", expected_count=1, actual_count=1, discrepancy_count=0, started_at="2026-05-02T00:00:00Z", completed_at="2026-05-02T00:01:00Z", summary_markdown="ok", metadata_json={}, created_at="2026-05-02T00:00:00Z"))
    monkeypatch.setattr(ingestion_api, "resolve_discrepancy", lambda *_args, **_kwargs: SimpleNamespace(resolved=True))
    monkeypatch.setattr(ingestion_api, "list_discrepancies", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(ingestion_api, "get_reconciliation_run", lambda *_args, **_kwargs: SimpleNamespace(id=uuid.uuid4(), run_id=run_id, type="parsing_completeness", status="completed", expected_count=1, actual_count=1, discrepancy_count=0, started_at="2026-05-02T00:00:00Z", completed_at="2026-05-02T00:01:00Z", summary_markdown="ok", metadata_json={}, created_at="2026-05-02T00:00:00Z"))

    def override_get_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[require_current_user] = _override_current_user(user_id)

    with TestClient(app) as client:
        run_response = client.post(
            "/api/v1/ingestion/runs",
            json={"sourceId": str(uuid.uuid4()), "triggerType": "manual", "options": {}},
        )
        items_response = client.get("/api/v1/ingestion/items")
        job_response = client.post(f"/api/v1/ingestion/items/{item_id}/parse")
        events_response = client.get("/api/v1/ingestion/audit-events")
        reconciliation_response = client.post("/api/v1/ingestion/reconciliation-runs", json={"runId": str(run_id), "type": "parsing_completeness"})

    app.dependency_overrides.clear()

    assert run_response.status_code == 200
    assert items_response.status_code == 200
    assert job_response.status_code == 200
    assert events_response.status_code == 200
    assert reconciliation_response.status_code == 200
