from app.services.ingestion_engine import build_idempotency_key, content_hash, is_safe_fetch_url, retry_backoff_seconds


def test_content_hash_changes_for_different_payloads():
    first = content_hash("hello world", canonical_url="https://example.com/a", external_id="1")
    second = content_hash("hello world", canonical_url="https://example.com/a", external_id="2")

    assert first != second


def test_build_idempotency_key_joins_non_empty_parts():
    assert build_idempotency_key("fetch_source", "source-1", "", "2026050201") == "fetch_source:source-1:2026050201"


def test_retry_backoff_seconds_steps_up():
    assert retry_backoff_seconds(1) == 30
    assert retry_backoff_seconds(2) == 120
    assert retry_backoff_seconds(3) == 600
    assert retry_backoff_seconds(5) == 600


def test_is_safe_fetch_url_blocks_private_and_local_urls():
    assert is_safe_fetch_url("https://go.dev/blog") is True
    assert is_safe_fetch_url("http://localhost:8080") is False
    assert is_safe_fetch_url("http://127.0.0.1:9000") is False
