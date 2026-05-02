# sweOS Ingestion / Worker Engine — Full Implementation Specification

**Target implementer:** Codex / AI coding agent  
**Target application:** sweOS  
**Target section:** `Applications`  
**Primary language for new service:** Go  
**Primary goal:** Build a recruiter-attractive, production-style Go backend module that demonstrates asynchronous workflows, external API integrations, reconciliation, auditability, observability, security basics, and clean system design.

---

## 1. Executive Summary

Implement a new sweOS application called **Ingestion & Worker Engine**.

This application should ingest external career/learning/engineering signals, process them asynchronously, persist structured artifacts, and expose operational visibility through the sweOS UI.

The project should be designed as a realistic backend/platform engineering showcase, especially for roles involving:

- Go backend development
- REST and/or gRPC APIs
- external API integrations
- asynchronous workers
- financial-operations-style reconciliation
- auditability
- observability
- PostgreSQL-backed workflows
- Docker-based development
- security and reliability basics

The feature should be visible inside the existing sweOS frontend under an **Applications** section, as a new app card/page named:

```text
Ingestion Engine
```

or:

```text
Worker Platform
```

---

## 2. Product Purpose

The Ingestion / Worker Engine exists to power background intelligence inside sweOS.

It should collect and process data from sources such as:

- job descriptions
- company career pages
- RSS feeds
- GitHub repositories
- technical articles
- mock financial/exchange APIs
- manually submitted URLs or text

It should then:

1. store the raw input,
2. normalize it,
3. deduplicate it,
4. classify it,
5. optionally send it to an AI workflow,
6. persist structured artifacts,
7. reconcile expected vs actual processing results,
8. expose health, metrics, and audit trails.

This is not just a CRUD module. It should behave like a real backend worker platform.

---

## 3. Recruiter-Facing Project Pitch

Use this description in the README and portfolio:

> **sweOS Ingestion & Worker Engine** is a Go-based backend platform for reliable asynchronous ingestion, external API integration, structured AI artifact processing, reconciliation, auditability, and observability. It includes REST/gRPC APIs, PostgreSQL-backed workers, idempotent job processing, retry/dead-letter behavior, Prometheus metrics, structured logs, and a simulated financial reconciliation module.

---

## 4. High-Level Architecture

```text
sweOS Frontend
  └── Applications / Ingestion Engine
        ├── Sources UI
        ├── Ingestion Runs UI
        ├── Worker Jobs UI
        ├── Raw / Parsed Items UI
        ├── Reconciliation UI
        ├── Audit Events UI
        └── Metrics / Health UI

sweOS Backend / API Gateway
  └── proxies or integrates with Go service

Go Ingestion Engine Service
  ├── REST API
  ├── optional gRPC API
  ├── Worker Orchestrator
  ├── Source Integrations
  ├── Deduplication Service
  ├── Parser / Classifier Service
  ├── AI Artifact Adapter
  ├── Reconciliation Engine
  ├── Audit Event Ledger
  ├── Metrics Exporter
  └── PostgreSQL Repository Layer

PostgreSQL
  ├── ingestion_sources
  ├── ingestion_runs
  ├── ingestion_items
  ├── parsed_ingestion_items
  ├── worker_jobs
  ├── audit_events
  ├── reconciliation_runs
  ├── reconciliation_items
  ├── reconciliation_discrepancies
  └── external_accounts / external_transactions for mock FinOps module
```

---

## 5. Recommended Repository Structure

If sweOS is currently a monorepo, add the Go service as a separate service package:

```text
sweos/
  apps/
    web/
      src/
        app/
        components/
        features/
          applications/
            ingestion-engine/
  services/
    ingestion-engine/
      cmd/
        api/
          main.go
        worker/
          main.go
        cli/
          main.go
      internal/
        api/
          rest/
          grpc/
        app/
        config/
        database/
        domain/
          audit/
          ingestion/
          jobs/
          reconciliation/
          integrations/
          metrics/
        integrations/
          rss/
          github/
          jobboard/
          llm/
          mockexchange/
        repositories/
        workers/
        telemetry/
        security/
      migrations/
      proto/
      tests/
      Dockerfile
      docker-compose.yml
      Makefile
      README.md
```

If sweOS currently has only one backend, still keep this service modular so it can be run independently.

---

## 6. Technology Requirements

### Backend service

Use:

```text
Go 1.22+
PostgreSQL
Docker
Docker Compose
```

Recommended Go packages:

```text
HTTP router: chi or net/http
Database: pgx
Migrations: goose or golang-migrate
SQL generation: sqlc optional
Logging: slog or zerolog
Metrics: Prometheus client_golang
CLI: cobra optional
gRPC: google.golang.org/grpc optional but recommended
Config: envconfig, cleanenv, or viper
Testing: Go testing package + testcontainers optional
```

### Frontend

Use the existing sweOS frontend stack. Based on previous project context, implement this as a new **Applications** feature/page rather than a disconnected standalone UI.

---

## 7. Core Domain Concepts

## 7.1 Ingestion Source

A source defines where data comes from.

Examples:

```text
rss_feed
manual_url
manual_text
github_repository
github_search
job_board
company_careers_page
mock_exchange
```

A source can be enabled or disabled.

## 7.2 Ingestion Run

An ingestion run is a single execution attempt for one or more sources.

Examples:

```text
Run RSS ingestion for selected sources
Run GitHub repository scan
Run manual job description import
Run mock exchange reconciliation import
```

## 7.3 Ingestion Item

An ingestion item is one raw piece of fetched/imported content.

Examples:

```text
job post
article
repository metadata
mock transaction
mock balance snapshot
manual pasted text
```

## 7.4 Parsed Item

A parsed item is a structured version of an ingestion item.

Examples:

```json
{
  "type": "job_post",
  "title": "Software Engineer - Go",
  "company": "Example Company",
  "requiredSkills": ["Go", "PostgreSQL", "Docker"],
  "responsibilities": ["Build internal services", "Integrate external APIs"]
}
```

## 7.5 Worker Job

A worker job is an asynchronous task.

Examples:

```text
fetch_source
parse_item
deduplicate_item
classify_item
run_ai_parse
run_reconciliation
sync_mock_exchange
```

## 7.6 Audit Event

An audit event is an append-only record of a meaningful state transition.

Examples:

```text
source_created
run_started
item_fetched
item_deduplicated
item_parse_failed
worker_job_retried
reconciliation_completed
discrepancy_detected
```

## 7.7 Reconciliation Run

A reconciliation run compares expected records against actual processed records.

This module is intentionally inspired by financial operations workflows.

Examples:

```text
Expected 50 fetched items, actual 50 stored items
Expected 50 stored items, actual 48 parsed items
Expected mock transfer amount 100.00 USDC, actual 99.98 USDC
```

---

## 8. Data Model

Create migrations for the following tables.

Use:

```sql
uuid primary keys
timestamptz timestamps
jsonb for flexible payloads
text enums via CHECK constraints or PostgreSQL enum types
```

---

## 8.1 `ingestion_sources`

```sql
create table ingestion_sources (
  id uuid primary key default gen_random_uuid(),
  user_id uuid null,
  name text not null,
  type text not null check (type in (
    'rss_feed',
    'manual_url',
    'manual_text',
    'github_repository',
    'github_search',
    'job_board',
    'company_careers_page',
    'mock_exchange'
  )),
  url text null,
  config_json jsonb not null default '{}'::jsonb,
  enabled boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_ingestion_sources_type on ingestion_sources(type);
create index idx_ingestion_sources_enabled on ingestion_sources(enabled);
```

---

## 8.2 `ingestion_runs`

```sql
create table ingestion_runs (
  id uuid primary key default gen_random_uuid(),
  source_id uuid null references ingestion_sources(id) on delete set null,
  status text not null check (status in (
    'queued',
    'running',
    'completed',
    'completed_with_errors',
    'failed',
    'cancelled'
  )) default 'queued',
  trigger_type text not null check (trigger_type in (
    'manual',
    'scheduled',
    'api',
    'system'
  )) default 'manual',
  expected_item_count integer null,
  fetched_item_count integer not null default 0,
  parsed_item_count integer not null default 0,
  failed_item_count integer not null default 0,
  started_at timestamptz null,
  completed_at timestamptz null,
  error_message text null,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_ingestion_runs_status on ingestion_runs(status);
create index idx_ingestion_runs_created_at on ingestion_runs(created_at desc);
```

---

## 8.3 `ingestion_items`

```sql
create table ingestion_items (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references ingestion_runs(id) on delete cascade,
  source_id uuid null references ingestion_sources(id) on delete set null,
  external_id text null,
  canonical_url text null,
  type text not null check (type in (
    'job_post',
    'article',
    'github_repository',
    'github_issue',
    'mock_transaction',
    'mock_balance_snapshot',
    'manual_text',
    'unknown'
  )) default 'unknown',
  title text null,
  raw_content text not null,
  raw_json jsonb not null default '{}'::jsonb,
  content_hash text not null,
  status text not null check (status in (
    'fetched',
    'duplicate',
    'queued_for_parsing',
    'parsed',
    'failed',
    'archived'
  )) default 'fetched',
  duplicate_of_id uuid null references ingestion_items(id) on delete set null,
  fetched_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(source_id, external_id),
  unique(content_hash)
);

create index idx_ingestion_items_run_id on ingestion_items(run_id);
create index idx_ingestion_items_status on ingestion_items(status);
create index idx_ingestion_items_type on ingestion_items(type);
create index idx_ingestion_items_content_hash on ingestion_items(content_hash);
```

---

## 8.4 `parsed_ingestion_items`

```sql
create table parsed_ingestion_items (
  id uuid primary key default gen_random_uuid(),
  item_id uuid not null references ingestion_items(id) on delete cascade,
  parser_type text not null check (parser_type in (
    'rule_based',
    'ai',
    'mock_exchange',
    'manual'
  )),
  parsed_type text not null,
  parsed_json jsonb not null,
  summary_markdown text null,
  confidence_score numeric(5,2) null,
  prompt_version text null,
  model_name text null,
  created_at timestamptz not null default now()
);

create index idx_parsed_items_item_id on parsed_ingestion_items(item_id);
create index idx_parsed_items_parsed_type on parsed_ingestion_items(parsed_type);
```

---

## 8.5 `worker_jobs`

```sql
create table worker_jobs (
  id uuid primary key default gen_random_uuid(),
  job_type text not null check (job_type in (
    'fetch_source',
    'deduplicate_item',
    'parse_item',
    'classify_item',
    'run_ai_parse',
    'run_reconciliation',
    'sync_mock_exchange'
  )),
  status text not null check (status in (
    'queued',
    'processing',
    'completed',
    'failed',
    'retrying',
    'dead_lettered',
    'cancelled'
  )) default 'queued',
  priority integer not null default 5,
  run_id uuid null references ingestion_runs(id) on delete cascade,
  item_id uuid null references ingestion_items(id) on delete cascade,
  idempotency_key text not null,
  payload_json jsonb not null default '{}'::jsonb,
  attempts integer not null default 0,
  max_attempts integer not null default 3,
  locked_by text null,
  locked_until timestamptz null,
  available_at timestamptz not null default now(),
  started_at timestamptz null,
  completed_at timestamptz null,
  last_error text null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(idempotency_key)
);

create index idx_worker_jobs_status_available on worker_jobs(status, available_at);
create index idx_worker_jobs_type on worker_jobs(job_type);
create index idx_worker_jobs_run_id on worker_jobs(run_id);
```

---

## 8.6 `audit_events`

```sql
create table audit_events (
  id uuid primary key default gen_random_uuid(),
  entity_type text not null,
  entity_id uuid not null,
  event_type text not null,
  actor_type text not null check (actor_type in (
    'user',
    'worker',
    'system',
    'api'
  )),
  actor_id text null,
  payload_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_audit_events_entity on audit_events(entity_type, entity_id);
create index idx_audit_events_event_type on audit_events(event_type);
create index idx_audit_events_created_at on audit_events(created_at desc);
```

Audit events must be append-only. Do not update or delete them through normal application flows.

---

## 8.7 `reconciliation_runs`

```sql
create table reconciliation_runs (
  id uuid primary key default gen_random_uuid(),
  run_id uuid null references ingestion_runs(id) on delete set null,
  type text not null check (type in (
    'ingestion_completeness',
    'parsing_completeness',
    'duplicate_detection',
    'mock_exchange_balances',
    'mock_exchange_transfers'
  )),
  status text not null check (status in (
    'queued',
    'running',
    'completed',
    'failed'
  )) default 'queued',
  expected_count integer not null default 0,
  actual_count integer not null default 0,
  discrepancy_count integer not null default 0,
  started_at timestamptz null,
  completed_at timestamptz null,
  summary_markdown text null,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_reconciliation_runs_type on reconciliation_runs(type);
create index idx_reconciliation_runs_status on reconciliation_runs(status);
create index idx_reconciliation_runs_created_at on reconciliation_runs(created_at desc);
```

---

## 8.8 `reconciliation_items`

```sql
create table reconciliation_items (
  id uuid primary key default gen_random_uuid(),
  reconciliation_run_id uuid not null references reconciliation_runs(id) on delete cascade,
  entity_type text not null,
  entity_id uuid null,
  external_reference text null,
  expected_json jsonb not null default '{}'::jsonb,
  actual_json jsonb not null default '{}'::jsonb,
  status text not null check (status in (
    'matched',
    'mismatched',
    'missing',
    'unexpected'
  )),
  created_at timestamptz not null default now()
);

create index idx_reconciliation_items_run on reconciliation_items(reconciliation_run_id);
create index idx_reconciliation_items_status on reconciliation_items(status);
```

---

## 8.9 `reconciliation_discrepancies`

```sql
create table reconciliation_discrepancies (
  id uuid primary key default gen_random_uuid(),
  reconciliation_run_id uuid not null references reconciliation_runs(id) on delete cascade,
  reconciliation_item_id uuid null references reconciliation_items(id) on delete cascade,
  severity text not null check (severity in ('low', 'medium', 'high', 'critical')),
  type text not null check (type in (
    'missing_raw_item',
    'duplicate_external_id',
    'parse_failed',
    'stale_item',
    'checksum_mismatch',
    'unexpected_status_transition',
    'amount_mismatch',
    'balance_mismatch',
    'missing_transfer',
    'unexpected_transfer'
  )),
  description text not null,
  expected_json jsonb not null default '{}'::jsonb,
  actual_json jsonb not null default '{}'::jsonb,
  resolved boolean not null default false,
  resolved_at timestamptz null,
  created_at timestamptz not null default now()
);

create index idx_reconciliation_discrepancies_run on reconciliation_discrepancies(reconciliation_run_id);
create index idx_reconciliation_discrepancies_type on reconciliation_discrepancies(type);
create index idx_reconciliation_discrepancies_severity on reconciliation_discrepancies(severity);
```

---

## 8.10 Mock FinOps Tables

These tables simulate external exchange/custodian operations without using real funds.

### `external_accounts`

```sql
create table external_accounts (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  account_ref text not null,
  asset_symbol text not null,
  balance numeric(24,8) not null default 0,
  raw_json jsonb not null default '{}'::jsonb,
  last_synced_at timestamptz null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(provider, account_ref, asset_symbol)
);
```

### `external_transactions`

```sql
create table external_transactions (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  external_tx_id text not null,
  from_account_ref text null,
  to_account_ref text null,
  asset_symbol text not null,
  amount numeric(24,8) not null,
  fee numeric(24,8) not null default 0,
  status text not null check (status in (
    'pending',
    'completed',
    'failed',
    'cancelled'
  )),
  occurred_at timestamptz not null,
  raw_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique(provider, external_tx_id)
);
```

---

## 9. REST API Specification

All endpoints should be under:

```text
/api/v1/ingestion
```

Use a consistent response envelope:

```json
{
  "data": {},
  "meta": {}
}
```

Errors:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request body",
    "details": []
  }
}
```

---

## 9.1 Sources

### Create source

```http
POST /api/v1/ingestion/sources
```

Request:

```json
{
  "name": "Go Blog RSS",
  "type": "rss_feed",
  "url": "https://go.dev/blog/feed.atom",
  "config": {
    "tags": ["go", "backend"],
    "defaultItemType": "article"
  }
}
```

Response:

```json
{
  "data": {
    "id": "uuid",
    "name": "Go Blog RSS",
    "type": "rss_feed",
    "enabled": true
  }
}
```

### List sources

```http
GET /api/v1/ingestion/sources?type=rss_feed&enabled=true
```

### Get source

```http
GET /api/v1/ingestion/sources/{sourceId}
```

### Update source

```http
PUT /api/v1/ingestion/sources/{sourceId}
```

### Disable source

```http
POST /api/v1/ingestion/sources/{sourceId}/disable
```

### Enable source

```http
POST /api/v1/ingestion/sources/{sourceId}/enable
```

---

## 9.2 Ingestion Runs

### Start ingestion run

```http
POST /api/v1/ingestion/runs
```

Request:

```json
{
  "sourceId": "uuid",
  "triggerType": "manual",
  "options": {
    "parseImmediately": true,
    "runReconciliation": true
  }
}
```

Response:

```json
{
  "data": {
    "runId": "uuid",
    "status": "queued"
  }
}
```

### List runs

```http
GET /api/v1/ingestion/runs?status=running&limit=20&offset=0
```

### Get run

```http
GET /api/v1/ingestion/runs/{runId}
```

Response:

```json
{
  "data": {
    "id": "uuid",
    "status": "completed_with_errors",
    "sourceId": "uuid",
    "expectedItemCount": 50,
    "fetchedItemCount": 50,
    "parsedItemCount": 48,
    "failedItemCount": 2,
    "startedAt": "2026-05-02T10:00:00Z",
    "completedAt": "2026-05-02T10:02:00Z"
  }
}
```

### Cancel run

```http
POST /api/v1/ingestion/runs/{runId}/cancel
```

---

## 9.3 Items

### List items

```http
GET /api/v1/ingestion/items?runId=uuid&type=job_post&status=parsed
```

### Get item

```http
GET /api/v1/ingestion/items/{itemId}
```

### Queue item parse

```http
POST /api/v1/ingestion/items/{itemId}/parse
```

### Archive item

```http
POST /api/v1/ingestion/items/{itemId}/archive
```

---

## 9.4 Worker Jobs

### List worker jobs

```http
GET /api/v1/ingestion/worker-jobs?status=failed&jobType=parse_item
```

### Get worker job

```http
GET /api/v1/ingestion/worker-jobs/{jobId}
```

### Retry worker job

```http
POST /api/v1/ingestion/worker-jobs/{jobId}/retry
```

### Cancel worker job

```http
POST /api/v1/ingestion/worker-jobs/{jobId}/cancel
```

---

## 9.5 Reconciliation

### Start reconciliation

```http
POST /api/v1/ingestion/reconciliation-runs
```

Request:

```json
{
  "runId": "uuid",
  "type": "parsing_completeness"
}
```

Response:

```json
{
  "data": {
    "reconciliationRunId": "uuid",
    "status": "queued"
  }
}
```

### List reconciliation runs

```http
GET /api/v1/ingestion/reconciliation-runs?type=parsing_completeness
```

### Get reconciliation run

```http
GET /api/v1/ingestion/reconciliation-runs/{reconciliationRunId}
```

Response:

```json
{
  "data": {
    "id": "uuid",
    "type": "parsing_completeness",
    "status": "completed",
    "expectedCount": 50,
    "actualCount": 48,
    "discrepancyCount": 2,
    "summaryMarkdown": "48 of 50 items were parsed successfully. 2 items failed parsing."
  }
}
```

### List discrepancies

```http
GET /api/v1/ingestion/reconciliation-runs/{reconciliationRunId}/discrepancies
```

### Resolve discrepancy

```http
POST /api/v1/ingestion/discrepancies/{discrepancyId}/resolve
```

---

## 9.6 Audit Events

### List audit events

```http
GET /api/v1/ingestion/audit-events?entityType=ingestion_run&entityId=uuid
```

Response:

```json
{
  "data": [
    {
      "id": "uuid",
      "entityType": "ingestion_run",
      "entityId": "uuid",
      "eventType": "run_started",
      "actorType": "worker",
      "createdAt": "2026-05-02T10:00:00Z",
      "payload": {}
    }
  ]
}
```

---

## 9.7 Mock FinOps API

### Sync mock exchange data

```http
POST /api/v1/ingestion/mock-exchange/sync
```

### List external accounts

```http
GET /api/v1/ingestion/mock-exchange/accounts
```

### List external transactions

```http
GET /api/v1/ingestion/mock-exchange/transactions
```

### Run mock transfer reconciliation

```http
POST /api/v1/ingestion/mock-exchange/reconcile-transfers
```

---

## 9.8 Health and Metrics

### Health

```http
GET /healthz
```

Response:

```json
{
  "status": "ok"
}
```

### Readiness

```http
GET /readyz
```

Should verify database connectivity.

### Metrics

```http
GET /metrics
```

Expose Prometheus metrics.

---

## 10. Optional gRPC API

Add gRPC if feasible. This is highly recommended for portfolio value.

Create:

```text
proto/ingestion/v1/ingestion.proto
proto/reconciliation/v1/reconciliation.proto
```

Suggested services:

```proto
service IngestionService {
  rpc StartRun(StartRunRequest) returns (StartRunResponse);
  rpc GetRun(GetRunRequest) returns (GetRunResponse);
  rpc CancelRun(CancelRunRequest) returns (CancelRunResponse);
}

service WorkerService {
  rpc ReportHeartbeat(WorkerHeartbeatRequest) returns (WorkerHeartbeatResponse);
}

service ReconciliationService {
  rpc StartReconciliation(StartReconciliationRequest) returns (StartReconciliationResponse);
  rpc GetReconciliation(GetReconciliationRequest) returns (GetReconciliationResponse);
}
```

The REST API remains the main API used by the UI.

gRPC demonstrates internal service communication maturity.

---

## 11. Worker Behavior

## 11.1 Job acquisition

Workers should claim jobs using a PostgreSQL transaction.

Pseudo-flow:

```text
1. Select queued job where available_at <= now()
2. Lock row with FOR UPDATE SKIP LOCKED
3. Set status = processing
4. Increment attempts
5. Set locked_by and locked_until
6. Commit
7. Execute job
8. Mark completed or failed/retrying/dead_lettered
```

## 11.2 Retry policy

Use exponential backoff:

```text
attempt 1: retry after 30 seconds
attempt 2: retry after 2 minutes
attempt 3: retry after 10 minutes
```

After `max_attempts`, mark as:

```text
dead_lettered
```

## 11.3 Idempotency

Every worker job must have an `idempotency_key`.

Examples:

```text
fetch_source:{sourceId}:{dateHour}
parse_item:{itemId}
reconcile_run:{runId}:parsing_completeness
mock_exchange_sync:{provider}:{dateHour}
```

Before creating a worker job, try inserting with the unique `idempotency_key`. If it already exists, return the existing job.

## 11.4 Graceful shutdown

Workers must handle OS signals:

```text
SIGINT
SIGTERM
```

On shutdown:

1. stop claiming new jobs,
2. allow in-progress job to finish if possible,
3. release expired locks naturally through `locked_until`,
4. close database connections.

---

## 12. Processing Pipelines

## 12.1 RSS / Article pipeline

```text
source_created
run_started
fetch_source job queued
RSS feed fetched
items extracted
content hashes computed
duplicates marked
parse_item jobs queued
items parsed as articles
optional summaries created
reconciliation queued
run completed
```

## 12.2 Job post pipeline

```text
manual URL/text submitted OR job board fetched
raw job post stored
job post parsed into structured required/preferred skills
parsed output stored
optional sweOS job entity created
optional gap-analysis workflow triggered
```

Parsed job shape:

```json
{
  "title": "Senior Software Engineer (Golang)",
  "company": "Example Company",
  "location": "Remote / Portugal",
  "responsibilities": [],
  "requiredSkills": [],
  "preferredSkills": [],
  "keywords": [],
  "seniorityAssessment": "senior",
  "summaryMarkdown": ""
}
```

## 12.3 GitHub repository pipeline

```text
GitHub repo URL submitted
repository metadata fetched
README fetched if available
languages fetched
topics fetched
repository classified
learning/project insight generated
```

Parsed repository shape:

```json
{
  "name": "repo-name",
  "owner": "owner",
  "description": "",
  "languages": ["Go", "TypeScript"],
  "topics": ["backend", "workers"],
  "stars": 123,
  "forks": 10,
  "readmeSummary": "",
  "learningValue": "high"
}
```

## 12.4 Mock exchange pipeline

```text
sync_mock_exchange job queued
mock balances fetched
mock transactions fetched
external_accounts updated
external_transactions inserted
mock transfer reconciliation queued
discrepancies detected
```

This module must not connect to real exchanges or move real funds. It is a safe simulation.

---

## 13. Reconciliation Rules

## 13.1 Ingestion completeness

Check:

```text
expected fetched count vs actual stored item count
```

Discrepancies:

```text
missing_raw_item
checksum_mismatch
duplicate_external_id
```

## 13.2 Parsing completeness

Check:

```text
fetched non-duplicate items vs parsed items
```

Discrepancies:

```text
parse_failed
missing_raw_item
unexpected_status_transition
```

## 13.3 Duplicate detection

Check:

```text
same content_hash
same source_id + external_id
similar canonical_url
```

Discrepancies:

```text
duplicate_external_id
checksum_mismatch
```

## 13.4 Mock exchange transfer reconciliation

Check:

```text
expected transfer amount vs actual transaction amount
expected asset vs actual asset
expected account refs vs actual account refs
expected status vs actual status
```

Discrepancies:

```text
amount_mismatch
missing_transfer
unexpected_transfer
balance_mismatch
```

Example discrepancy:

```json
{
  "severity": "medium",
  "type": "amount_mismatch",
  "description": "Expected transfer of 100.00 USDC but actual amount was 99.98 USDC after fee.",
  "expected": {
    "asset": "USDC",
    "amount": "100.00"
  },
  "actual": {
    "asset": "USDC",
    "amount": "99.98",
    "fee": "0.02"
  }
}
```

---

## 14. AI Integration

The service should support AI parsing but must not depend on it for all behavior.

Implement the AI layer behind an interface:

```go
type Parser interface {
    Parse(ctx context.Context, item IngestionItem) (ParsedItem, error)
}
```

Implement at least:

```text
RuleBasedParser
MockAIParser
OptionalLLMParser
```

The AI output must be structured JSON, not free-form text.

For every AI parse, store:

```text
parsed_json
summary_markdown
prompt_version
model_name
confidence_score
```

Prompt versioning should be compatible with existing sweOS AI workflow principles.

---

## 15. Observability Requirements

## 15.1 Structured logging

Every log should include useful fields:

```text
request_id
run_id
job_id
item_id
source_id
worker_id
job_type
status
error
```

Use `slog` or `zerolog`.

## 15.2 Metrics

Expose Prometheus metrics:

```text
ingestion_runs_total
 ingestion_runs_completed_total
 ingestion_runs_failed_total
 ingestion_items_fetched_total
 ingestion_items_parsed_total
 ingestion_items_failed_total
 worker_jobs_total
 worker_jobs_completed_total
 worker_jobs_failed_total
 worker_jobs_dead_lettered_total
 worker_job_duration_seconds
 worker_queue_depth
 external_api_requests_total
 external_api_errors_total
 reconciliation_runs_total
 reconciliation_discrepancies_total
 ai_parse_requests_total
 ai_parse_failures_total
```

Use labels carefully:

```text
source_type
job_type
status
discrepancy_type
severity
```

Do not create high-cardinality labels from UUIDs.

## 15.3 Health checks

Implement:

```text
/healthz
/readyz
/metrics
```

Readiness should fail if PostgreSQL is unavailable.

---

## 16. Security Requirements

Implement basic production-minded security.

Required:

```text
JWT or existing sweOS auth integration for REST endpoints
internal API key for worker/admin operations if needed
input validation on all requests
safe URL validation for external fetches
HTTP client timeouts
no secrets in logs
configuration via environment variables
least-privilege database user in Docker Compose
CORS aligned with existing sweOS frontend
```

URL fetching must guard against obvious SSRF risks:

```text
block localhost/private IP ranges by default
allowlist optional development mode
limit response body size
set request timeout
```

---

## 17. Frontend Integration: Applications Section

Add the feature to the sweOS Applications section.

## 17.1 Application card

Add a card:

```text
Title: Ingestion Engine
Description: Reliable background ingestion, worker jobs, reconciliation, and auditability for sweOS intelligence workflows.
Status: Active / Experimental
Primary action: Open
```

Optional card metrics:

```text
Active runs
Queued jobs
Failed jobs
Discrepancies
```

## 17.2 Main page route

Recommended route:

```text
/applications/ingestion-engine
```

or if current routing style differs, follow existing application route conventions.

## 17.3 Page tabs

The page should include tabs:

```text
Overview
Sources
Runs
Items
Worker Jobs
Reconciliation
Audit Log
Mock FinOps
Settings
```

---

## 18. Frontend Page Requirements

## 18.1 Overview tab

Show cards:

```text
Total Sources
Active Runs
Queued Jobs
Failed Jobs
Parsed Items
Open Discrepancies
Dead-lettered Jobs
```

Show recent activity:

```text
latest ingestion runs
latest failed jobs
latest reconciliation discrepancies
```

## 18.2 Sources tab

Features:

```text
list sources
create source
enable/disable source
trigger ingestion run from source
```

Form fields:

```text
name
type
url
config JSON / advanced options
enabled
```

## 18.3 Runs tab

Features:

```text
list ingestion runs
filter by status
open run details
cancel running/queued run
trigger reconciliation for run
```

Run detail should show:

```text
status
source
counts
started/completed timestamps
error message
related items
related worker jobs
audit events
```

## 18.4 Items tab

Features:

```text
list ingestion items
filter by type/status/source/run
open raw content
open parsed JSON
queue parse
archive item
```

## 18.5 Worker Jobs tab

Features:

```text
list worker jobs
filter by status/job type
retry failed/dead-lettered job
cancel queued job
show attempts and last error
```

Use clear visual status labels.

## 18.6 Reconciliation tab

Features:

```text
list reconciliation runs
open reconciliation details
list discrepancies
resolve discrepancy
```

Reconciliation detail should show:

```text
expected count
actual count
discrepancy count
summary
severity breakdown
```

## 18.7 Audit Log tab

Features:

```text
list audit events
filter by entity type
filter by event type
filter by date
open payload JSON
```

## 18.8 Mock FinOps tab

Features:

```text
sync mock exchange
list mock accounts
list mock transactions
run mock transfer reconciliation
show amount/balance discrepancies
```

Make it clear this is a simulation.

## 18.9 Settings tab

Features:

```text
configure polling interval
configure max retry attempts
configure default run options
configure source fetch timeout
configure body size limit
```

---

## 19. UI Style Requirements

Follow existing sweOS design language.

Use:

```text
cards for metrics
status pills for state
tables for runs/jobs/items
side panels or detail pages for raw JSON
clear empty states
clear error states
```

Important states:

```text
queued
running
completed
failed
retrying
dead_lettered
completed_with_errors
```

Do not hide errors. This application is meant to showcase operational visibility.

---

## 20. CLI Requirements

Add a CLI binary if feasible:

```text
sweos-ingestion
```

Commands:

```text
sweos-ingestion sources list
sweos-ingestion runs start --source <id>
sweos-ingestion runs get <id>
sweos-ingestion jobs list --status failed
sweos-ingestion jobs retry <id>
sweos-ingestion reconcile --run <id> --type parsing_completeness
sweos-ingestion mock-exchange sync
```

This is optional for product functionality but valuable for portfolio demonstration.

---

## 21. Configuration

Environment variables:

```text
APP_ENV=development
HTTP_ADDR=:8081
GRPC_ADDR=:9091
DATABASE_URL=postgres://...
JWT_SECRET=...
INTERNAL_API_KEY=...
WORKER_ID=worker-local-1
WORKER_CONCURRENCY=5
WORKER_POLL_INTERVAL_SECONDS=5
WORKER_LOCK_TIMEOUT_SECONDS=300
FETCH_TIMEOUT_SECONDS=15
FETCH_MAX_BODY_BYTES=5242880
ENABLE_PRIVATE_URL_FETCH=false
PROMETHEUS_ENABLED=true
LLM_PROVIDER=mock
LLM_API_KEY=
```

---

## 22. Docker Compose

Provide a local development setup:

```text
postgres
ingestion-api
ingestion-worker
prometheus optional
grafana optional
```

Minimum:

```yaml
services:
  postgres:
    image: postgres:16
  ingestion-api:
    build: .
    command: ./api
  ingestion-worker:
    build: .
    command: ./worker
```

---

## 23. Makefile Commands

Implement:

```text
make run-api
make run-worker
make run-cli
make test
make lint
make migrate-up
make migrate-down
make docker-up
make docker-down
make generate
```

---

## 24. Testing Requirements

## 24.1 Unit tests

Cover:

```text
idempotency key generation
content hashing
deduplication logic
retry backoff calculation
reconciliation comparison logic
URL validation
parser behavior
```

## 24.2 Integration tests

Cover:

```text
create source -> start run -> worker fetches -> item stored
item parse job -> parsed item stored
failed job -> retry -> dead-letter after max attempts
reconciliation detects missing parsed items
mock exchange reconciliation detects amount mismatch
```

## 24.3 API tests

Cover:

```text
source CRUD
run creation
item listing
job retry
reconciliation creation
audit event listing
```

---

## 25. Acceptance Criteria

The implementation is complete when all criteria below are satisfied.

## 25.1 Backend

- [ ] Go service compiles and runs locally.
- [ ] PostgreSQL migrations create all required tables.
- [ ] REST API exposes source, run, item, job, reconciliation, audit, and mock FinOps endpoints.
- [ ] Worker process claims jobs using safe locking.
- [ ] Worker jobs support retries and dead-lettering.
- [ ] Worker jobs are idempotent.
- [ ] Ingestion items are deduplicated by content hash and external ID.
- [ ] Parsed items are stored as structured JSON.
- [ ] Audit events are written for important state transitions.
- [ ] Reconciliation detects missing/failed/duplicate items.
- [ ] Mock exchange sync and reconciliation work with simulated data.
- [ ] `/healthz`, `/readyz`, and `/metrics` exist.
- [ ] Structured logs include useful correlation fields.
- [ ] Tests cover core behavior.

## 25.2 Frontend

- [ ] Applications section includes an Ingestion Engine card.
- [ ] Ingestion Engine page exists.
- [ ] Overview tab shows operational metrics.
- [ ] Sources tab supports listing and creating sources.
- [ ] Runs tab supports listing and opening run details.
- [ ] Items tab supports viewing raw and parsed item data.
- [ ] Worker Jobs tab supports retrying failed jobs.
- [ ] Reconciliation tab shows runs and discrepancies.
- [ ] Audit Log tab shows event timeline.
- [ ] Mock FinOps tab shows simulated accounts/transactions/reconciliation.
- [ ] UI handles loading, empty, and error states.

## 25.3 Portfolio Quality

- [ ] README explains architecture and trade-offs.
- [ ] README includes local setup instructions.
- [ ] README includes screenshots or placeholders.
- [ ] README includes API examples.
- [ ] README explains idempotency, retries, auditability, and reconciliation.
- [ ] Optional architecture diagram is included.

---

## 26. Suggested Implementation Order

Implement in this order.

## Phase 1 — Foundation

```text
Go service skeleton
config loading
database connection
migrations
health/readiness endpoints
basic REST router
Docker Compose
```

## Phase 2 — Sources and Runs

```text
source CRUD
start ingestion run
create worker job
run listing/detail
basic audit events
```

## Phase 3 — Worker Engine

```text
worker job table
job claiming with SKIP LOCKED
retry/backoff
dead-letter behavior
idempotency keys
structured logs
```

## Phase 4 — Ingestion Items

```text
RSS integration
manual text/url ingestion
content hashing
deduplication
item listing/detail
```

## Phase 5 — Parsing

```text
rule-based parser
mock AI parser
parsed item persistence
job post parser shape
article parser shape
```

## Phase 6 — Reconciliation

```text
ingestion completeness reconciliation
parsing completeness reconciliation
discrepancy records
resolve discrepancy endpoint
```

## Phase 7 — Mock FinOps

```text
mock exchange client
mock accounts
mock transactions
sync job
transfer reconciliation
amount mismatch examples
```

## Phase 8 — Observability and Security

```text
Prometheus metrics
request logging
JWT/auth integration
URL safety validation
timeouts/body limits
```

## Phase 9 — Frontend Applications Integration

```text
application card
main page
tabs
tables
detail views
actions
empty/error/loading states
```

## Phase 10 — Polish

```text
tests
README
architecture diagram
example data
screenshots/demo script
```

---

## 27. Example Demo Scenario

Use this as the final demonstration path.

```text
1. Open sweOS Applications.
2. Click Ingestion Engine.
3. Create RSS source: Go Blog.
4. Trigger ingestion run.
5. Watch worker jobs process items.
6. Open parsed article item.
7. Trigger parsing completeness reconciliation.
8. Show zero or some discrepancies.
9. Open Audit Log and show event timeline.
10. Open Mock FinOps tab.
11. Sync mock exchange data.
12. Run transfer reconciliation.
13. Show amount mismatch discrepancy.
14. Retry a failed/dead-lettered job.
15. Show Prometheus metrics endpoint.
```

---

## 28. Non-Goals

Do not implement these in the first version:

```text
real exchange integrations
real asset transfers
real trading logic
complex Kubernetes deployment
multi-tenant billing
advanced scheduling UI
full AI agent orchestration
```

The project should simulate financial operations safely while demonstrating backend engineering maturity.

---

## 29. Engineering Principles

Follow these principles throughout the implementation:

```text
Prefer simple, explicit code.
Keep domain logic outside HTTP handlers.
Use interfaces for external integrations.
Make workers idempotent.
Persist structured outputs.
Never rely on free-form AI text as the system of record.
Log state transitions.
Expose operational visibility.
Fail safely.
Design for retries.
Make errors inspectable from the UI.
```

---

## 30. Final Expected Outcome

After implementation, sweOS should contain a new application that demonstrates a production-style Go backend system.

The strongest visible capabilities should be:

```text
Go backend service
PostgreSQL persistence
REST API
optional gRPC API
background worker system
external integrations
idempotent processing
retry/dead-letter behavior
structured AI artifact support
reconciliation engine
audit ledger
Prometheus metrics
secure URL fetching
Dockerized development
Applications UI integration
```

This should be strong enough to discuss in interviews as a serious backend/platform engineering project rather than a simple personal app feature.
