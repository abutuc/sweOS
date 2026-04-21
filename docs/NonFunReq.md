# Non-Functional Requirements

## NFR-1 Performance

- Search results should return within acceptable interactive latency.
- Common dashboard and retrieval operations should feel near real-time.
- AI workflows should support streaming when possible.

## NFR-2 Reliability

- The system shall preserve user data and workflow state across failures.
- Long-running workflows shall be resumable.
- Background ingestion jobs shall be retryable and idempotent.

This is exactly where workflow runtimes like LangGraph and Temporal become valuable: persistence, durable execution, and recovery from interruptions.

## NFR-3 Security

- The system shall encrypt secrets and sensitive data at rest and in transit.
- The system shall isolate model/API credentials from client code.
- The system shall log privileged operations.
- The system shall support secure document handling.

## NFR-4 Privacy

- The system shall allow local-only or self-hosted operation where feasible.
- The system shall clearly separate personal profile data, documents, and generated outputs.
- The system shall let the user delete stored artifacts and history.

## NFR-5 Explainability

- AI-generated recommendations shall be accompanied by rationale.
- External-data-based claims shall include source references.
- Automated scoring shall expose the rubric used.

## NFR-6 Auditability

- The system shall retain traceability for major AI actions:
  - prompt/workflow used
  - retrieved context
  - output version
  - approval state

## NFR-7 Modularity

- The architecture shall support independent modules for learning, market radar, and CV studio.
- New exercise types, news sources, and job adapters shall be pluggable.

## NFR-8 Maintainability

- The codebase shall enforce clear domain boundaries.
- AI prompts, evaluation rubrics, and source connectors shall be versioned.
- Business rules shall be testable independently of model calls.

## NFR-9 Scalability

- The system shall support increasing volumes of documents, exercises, opportunities, and history without major redesign.
- Retrieval and ingestion pipelines shall scale independently.

## NFR-10 Usability

- The user shall be able to complete the main workflows with minimal friction.
- Generated output shall always be editable.
- Important actions shall be reversible when possible.

## NFR-11 Availability

- Core local features shall remain available even when external AI providers or ingestion sources are unavailable.
- The system shall degrade gracefully when external APIs fail.

## NFR-12 Interoperability

- The system shall expose/import data via standard formats where useful:
  - Markdown
  - PDF/docx exports
  - JSON
  - CSV
  - RSS/API adapters

## NFR-13 Observability

- The system shall log workflow failures, ingestion errors, latency, and model/tool failures.
- The system shall provide operator-facing diagnostics for agentic flows.

## NFR-14 Cost Control

- The system shall support model/provider selection by workflow type.
- Expensive AI operations shall be rate-limited, cached, or deferred where appropriate.
- The system shall distinguish between cheap deterministic operations and expensive model-driven ones.

## NFR-15 Quality Assurance

- The system shall include automated tests for domain logic.
- AI-assisted evaluation flows shall be benchmarked against curated examples.
- Prompt and rubric changes shall be regression-tested.
