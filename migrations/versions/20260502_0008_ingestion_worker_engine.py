"""add ingestion worker engine schema

Revision ID: 20260502_0008
Revises: 20260423_0007
Create Date: 2026-05-02 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260502_0008"
down_revision: Union[str, None] = "20260423_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _check(name: str, column: str, values: list[str]) -> sa.CheckConstraint:
    quoted = ", ".join(repr(value) for value in values)
    return sa.CheckConstraint(f"{column} in ({quoted})", name=name)


def upgrade() -> None:
    op.create_table(
        "ingestion_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        _check("ck_ingestion_sources_type", "type", [
            "rss_feed",
            "manual_url",
            "manual_text",
            "github_repository",
            "github_search",
            "job_board",
            "company_careers_page",
            "mock_exchange",
        ]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ingestion_sources_type", "ingestion_sources", ["type"])
    op.create_index("idx_ingestion_sources_enabled", "ingestion_sources", ["enabled"])

    op.create_table(
        "ingestion_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="queued"),
        sa.Column("trigger_type", sa.String(), nullable=False, server_default="manual"),
        sa.Column("expected_item_count", sa.Integer(), nullable=True),
        sa.Column("fetched_item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("parsed_item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["source_id"], ["ingestion_sources.id"], ondelete="SET NULL"),
        _check("ck_ingestion_runs_status", "status", ["queued", "running", "completed", "completed_with_errors", "failed", "cancelled"]),
        _check("ck_ingestion_runs_trigger_type", "trigger_type", ["manual", "scheduled", "api", "system"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ingestion_runs_status", "ingestion_runs", ["status"])
    op.create_index("idx_ingestion_runs_created_at", "ingestion_runs", ["created_at"])

    op.create_table(
        "ingestion_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_id", sa.Text(), nullable=True),
        sa.Column("canonical_url", sa.Text(), nullable=True),
        sa.Column("type", sa.String(), nullable=False, server_default="unknown"),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("raw_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("content_hash", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="fetched"),
        sa.Column("duplicate_of_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["run_id"], ["ingestion_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["ingestion_sources.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["duplicate_of_id"], ["ingestion_items.id"], ondelete="SET NULL"),
        _check("ck_ingestion_items_type", "type", [
            "job_post",
            "article",
            "github_repository",
            "github_issue",
            "mock_transaction",
            "mock_balance_snapshot",
            "manual_text",
            "unknown",
        ]),
        _check("ck_ingestion_items_status", "status", ["fetched", "duplicate", "queued_for_parsing", "parsed", "failed", "archived"]),
        sa.CheckConstraint("raw_content <> ''", name="ck_ingestion_items_raw_content_not_empty"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "external_id"),
        sa.UniqueConstraint("content_hash"),
    )
    op.create_index("idx_ingestion_items_run_id", "ingestion_items", ["run_id"])
    op.create_index("idx_ingestion_items_status", "ingestion_items", ["status"])
    op.create_index("idx_ingestion_items_type", "ingestion_items", ["type"])
    op.create_index("idx_ingestion_items_content_hash", "ingestion_items", ["content_hash"])

    op.create_table(
        "parsed_ingestion_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parser_type", sa.String(), nullable=False),
        sa.Column("parsed_type", sa.String(), nullable=False),
        sa.Column("parsed_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("summary_markdown", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("prompt_version", sa.String(), nullable=True),
        sa.Column("model_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["item_id"], ["ingestion_items.id"], ondelete="CASCADE"),
        _check("ck_parsed_ingestion_items_parser_type", "parser_type", ["rule_based", "ai", "mock_exchange", "manual"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_parsed_items_item_id", "parsed_ingestion_items", ["item_id"])
    op.create_index("idx_parsed_items_parsed_type", "parsed_ingestion_items", ["parsed_type"])

    op.create_table(
        "worker_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="queued"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("idempotency_key", sa.String(), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("locked_by", sa.String(), nullable=True),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["run_id"], ["ingestion_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["ingestion_items.id"], ondelete="CASCADE"),
        _check("ck_worker_jobs_job_type", "job_type", [
            "fetch_source",
            "deduplicate_item",
            "parse_item",
            "classify_item",
            "run_ai_parse",
            "run_reconciliation",
            "sync_mock_exchange",
        ]),
        _check("ck_worker_jobs_status", "status", ["queued", "processing", "completed", "failed", "retrying", "dead_lettered", "cancelled"]),
        sa.CheckConstraint("priority >= 0", name="ck_worker_jobs_priority_non_negative"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("idx_worker_jobs_status_available", "worker_jobs", ["status", "available_at"])
    op.create_index("idx_worker_jobs_type", "worker_jobs", ["job_type"])
    op.create_index("idx_worker_jobs_run_id", "worker_jobs", ["run_id"])

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("actor_type", sa.String(), nullable=False),
        sa.Column("actor_id", sa.String(), nullable=True),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        _check("ck_audit_events_actor_type", "actor_type", ["user", "worker", "system", "api"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_events_entity", "audit_events", ["entity_type", "entity_id"])
    op.create_index("idx_audit_events_event_type", "audit_events", ["event_type"])
    op.create_index("idx_audit_events_created_at", "audit_events", ["created_at"])

    op.create_table(
        "reconciliation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="queued"),
        sa.Column("expected_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("actual_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("discrepancy_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary_markdown", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["run_id"], ["ingestion_runs.id"], ondelete="SET NULL"),
        _check("ck_reconciliation_runs_type", "type", [
            "ingestion_completeness",
            "parsing_completeness",
            "duplicate_detection",
            "mock_exchange_balances",
            "mock_exchange_transfers",
        ]),
        _check("ck_reconciliation_runs_status", "status", ["queued", "running", "completed", "failed"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_reconciliation_runs_type", "reconciliation_runs", ["type"])
    op.create_index("idx_reconciliation_runs_status", "reconciliation_runs", ["status"])
    op.create_index("idx_reconciliation_runs_created_at", "reconciliation_runs", ["created_at"])

    op.create_table(
        "reconciliation_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reconciliation_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_reference", sa.String(), nullable=True),
        sa.Column("expected_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("actual_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["reconciliation_run_id"], ["reconciliation_runs.id"], ondelete="CASCADE"),
        _check("ck_reconciliation_items_status", "status", ["matched", "mismatched", "missing", "unexpected"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_reconciliation_items_run", "reconciliation_items", ["reconciliation_run_id"])
    op.create_index("idx_reconciliation_items_status", "reconciliation_items", ["status"])

    op.create_table(
        "reconciliation_discrepancies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reconciliation_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reconciliation_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("expected_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("actual_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["reconciliation_run_id"], ["reconciliation_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reconciliation_item_id"], ["reconciliation_items.id"], ondelete="CASCADE"),
        _check("ck_reconciliation_discrepancies_severity", "severity", ["low", "medium", "high", "critical"]),
        _check("ck_reconciliation_discrepancies_type", "type", [
            "missing_raw_item",
            "duplicate_external_id",
            "parse_failed",
            "stale_item",
            "checksum_mismatch",
            "unexpected_status_transition",
            "amount_mismatch",
            "balance_mismatch",
            "missing_transfer",
            "unexpected_transfer",
        ]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_reconciliation_discrepancies_run", "reconciliation_discrepancies", ["reconciliation_run_id"])
    op.create_index("idx_reconciliation_discrepancies_type", "reconciliation_discrepancies", ["type"])
    op.create_index("idx_reconciliation_discrepancies_severity", "reconciliation_discrepancies", ["severity"])

    op.create_table(
        "external_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("account_ref", sa.String(), nullable=False),
        sa.Column("asset_symbol", sa.String(), nullable=False),
        sa.Column("balance", sa.Numeric(24, 8), nullable=False, server_default="0"),
        sa.Column("raw_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "account_ref", "asset_symbol"),
    )

    op.create_table(
        "external_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("external_tx_id", sa.String(), nullable=False),
        sa.Column("from_account_ref", sa.String(), nullable=True),
        sa.Column("to_account_ref", sa.String(), nullable=True),
        sa.Column("asset_symbol", sa.String(), nullable=False),
        sa.Column("amount", sa.Numeric(24, 8), nullable=False),
        sa.Column("fee", sa.Numeric(24, 8), nullable=False, server_default="0"),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        _check("ck_external_transactions_status", "status", ["pending", "completed", "failed", "cancelled"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "external_tx_id"),
    )


def downgrade() -> None:
    op.drop_table("external_transactions")
    op.drop_table("external_accounts")
    op.drop_index("idx_reconciliation_discrepancies_severity", table_name="reconciliation_discrepancies")
    op.drop_index("idx_reconciliation_discrepancies_type", table_name="reconciliation_discrepancies")
    op.drop_index("idx_reconciliation_discrepancies_run", table_name="reconciliation_discrepancies")
    op.drop_table("reconciliation_discrepancies")
    op.drop_index("idx_reconciliation_items_status", table_name="reconciliation_items")
    op.drop_index("idx_reconciliation_items_run", table_name="reconciliation_items")
    op.drop_table("reconciliation_items")
    op.drop_index("idx_reconciliation_runs_created_at", table_name="reconciliation_runs")
    op.drop_index("idx_reconciliation_runs_status", table_name="reconciliation_runs")
    op.drop_index("idx_reconciliation_runs_type", table_name="reconciliation_runs")
    op.drop_table("reconciliation_runs")
    op.drop_index("idx_audit_events_created_at", table_name="audit_events")
    op.drop_index("idx_audit_events_event_type", table_name="audit_events")
    op.drop_index("idx_audit_events_entity", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("idx_worker_jobs_run_id", table_name="worker_jobs")
    op.drop_index("idx_worker_jobs_type", table_name="worker_jobs")
    op.drop_index("idx_worker_jobs_status_available", table_name="worker_jobs")
    op.drop_table("worker_jobs")
    op.drop_index("idx_parsed_items_parsed_type", table_name="parsed_ingestion_items")
    op.drop_index("idx_parsed_items_item_id", table_name="parsed_ingestion_items")
    op.drop_table("parsed_ingestion_items")
    op.drop_index("idx_ingestion_items_content_hash", table_name="ingestion_items")
    op.drop_index("idx_ingestion_items_type", table_name="ingestion_items")
    op.drop_index("idx_ingestion_items_status", table_name="ingestion_items")
    op.drop_index("idx_ingestion_items_run_id", table_name="ingestion_items")
    op.drop_table("ingestion_items")
    op.drop_index("idx_ingestion_runs_created_at", table_name="ingestion_runs")
    op.drop_index("idx_ingestion_runs_status", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
    op.drop_index("idx_ingestion_sources_enabled", table_name="ingestion_sources")
    op.drop_index("idx_ingestion_sources_type", table_name="ingestion_sources")
    op.drop_table("ingestion_sources")
