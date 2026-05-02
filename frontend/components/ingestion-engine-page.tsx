"use client";

import { useEffect, useMemo, useState } from "react";

import {
  api,
  type AuditEvent,
  type ExternalAccount,
  type ExternalTransaction,
  type IngestionItem,
  type IngestionOverview,
  type IngestionRun,
  type IngestionSource,
  type ReconciliationDiscrepancy,
  type ReconciliationRun,
  type WorkerJob,
} from "@/lib/api";

type TabKey = "overview" | "sources" | "runs" | "items" | "workerJobs" | "reconciliation" | "auditLog" | "mockFinops" | "settings";

type SourceDraft = {
  name: string;
  type: string;
  url: string;
  configJson: string;
  enabled: boolean;
};

const TABS: Array<{ key: TabKey; label: string }> = [
  { key: "overview", label: "Overview" },
  { key: "sources", label: "Sources" },
  { key: "runs", label: "Runs" },
  { key: "items", label: "Items" },
  { key: "workerJobs", label: "Worker Jobs" },
  { key: "reconciliation", label: "Reconciliation" },
  { key: "auditLog", label: "Audit Log" },
  { key: "mockFinops", label: "Mock FinOps" },
  { key: "settings", label: "Settings" },
];

const DEFAULT_SOURCE_DRAFT: SourceDraft = {
  name: "Go Blog RSS",
  type: "rss_feed",
  url: "https://go.dev/blog/feed.atom",
  configJson: JSON.stringify({ tags: ["go", "backend"], defaultItemType: "article" }, null, 2),
  enabled: true,
};

function formatDateTime(value: string | null) {
  if (!value) {
    return "n/a";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusLabel(value: string) {
  return value.replaceAll("_", " ");
}

function prettyJson(value: Record<string, unknown> | unknown) {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function IngestionEnginePage() {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [overview, setOverview] = useState<IngestionOverview | null>(null);
  const [sources, setSources] = useState<IngestionSource[]>([]);
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [items, setItems] = useState<IngestionItem[]>([]);
  const [jobs, setJobs] = useState<WorkerJob[]>([]);
  const [reconciliationRuns, setReconciliationRuns] = useState<ReconciliationRun[]>([]);
  const [discrepancies, setDiscrepancies] = useState<ReconciliationDiscrepancy[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [accounts, setAccounts] = useState<ExternalAccount[]>([]);
  const [transactions, setTransactions] = useState<ExternalTransaction[]>([]);
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [selectedReconciliationId, setSelectedReconciliationId] = useState<string | null>(null);
  const [sourceDraft, setSourceDraft] = useState<SourceDraft>(DEFAULT_SOURCE_DRAFT);
  const [settingsDraft, setSettingsDraft] = useState({
    pollingIntervalSeconds: "5",
    maxRetryAttempts: "3",
    fetchTimeoutSeconds: "15",
    bodyLimitBytes: "5242880",
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isWorking, setIsWorking] = useState(false);
  const [status, setStatus] = useState("Ingestion engine ready.");
  const [error, setError] = useState<string | null>(null);

  const selectedSource = useMemo(
    () => sources.find((item) => item.id === selectedSourceId) ?? sources[0] ?? null,
    [selectedSourceId, sources],
  );
  const selectedRun = useMemo(
    () => runs.find((item) => item.id === selectedRunId) ?? runs[0] ?? null,
    [selectedRunId, runs],
  );
  const selectedItem = useMemo(
    () => items.find((item) => item.id === selectedItemId) ?? items[0] ?? null,
    [selectedItemId, items],
  );
  const selectedJob = useMemo(
    () => jobs.find((item) => item.id === selectedJobId) ?? jobs[0] ?? null,
    [selectedJobId, jobs],
  );
  const selectedReconciliation = useMemo(
    () => reconciliationRuns.find((item) => item.id === selectedReconciliationId) ?? reconciliationRuns[0] ?? null,
    [selectedReconciliationId, reconciliationRuns],
  );
  const selectedDiscrepancies = useMemo(
    () => discrepancies.filter((item) => item.reconciliationRunId === selectedReconciliation?.id),
    [discrepancies, selectedReconciliation],
  );

  const refreshAll = async () => {
    const [
      overviewResponse,
      sourcesResponse,
      runsResponse,
      itemsResponse,
      jobsResponse,
      reconciliationResponse,
      auditResponse,
      accountsResponse,
      transactionsResponse,
    ] = await Promise.all([
      api.getIngestionOverview(),
      api.listIngestionSources(),
      api.listIngestionRuns({ limit: 50 }),
      api.listIngestionItems(),
      api.listIngestionWorkerJobs(),
      api.listIngestionReconciliationRuns(),
      api.listIngestionAuditEvents(),
      api.listIngestionMockExchangeAccounts(),
      api.listIngestionMockExchangeTransactions(),
    ]);

    setOverview(overviewResponse.data);
    setSources(sourcesResponse.data);
    setRuns(runsResponse.data);
    setItems(itemsResponse.data);
    setJobs(jobsResponse.data);
    setReconciliationRuns(reconciliationResponse.data);
    setAuditEvents(auditResponse.data);
    setAccounts(accountsResponse.data);
    setTransactions(transactionsResponse.data);
    setSelectedSourceId((current) => current ?? sourcesResponse.data[0]?.id ?? null);
    setSelectedRunId((current) => current ?? runsResponse.data[0]?.id ?? null);
    setSelectedItemId((current) => current ?? itemsResponse.data[0]?.id ?? null);
    setSelectedJobId((current) => current ?? jobsResponse.data[0]?.id ?? null);
    setSelectedReconciliationId((current) => current ?? reconciliationResponse.data[0]?.id ?? null);
    setError(null);
  };

  useEffect(() => {
    let active = true;

    void refreshAll()
      .catch(() => {
        if (active) {
          setError("Ingestion engine could not be loaded.");
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (selectedReconciliation?.id) {
      void api
        .listIngestionDiscrepancies(selectedReconciliation.id)
        .then((response) => setDiscrepancies(response.data))
        .catch(() => setDiscrepancies([]));
    }
  }, [selectedReconciliation?.id]);

  const saveSource = async () => {
    setIsWorking(true);
    setError(null);
    try {
      const config = sourceDraft.configJson.trim() ? JSON.parse(sourceDraft.configJson) : {};
      await api.createIngestionSource({
        name: sourceDraft.name,
        type: sourceDraft.type,
        url: sourceDraft.url || null,
        config,
        enabled: sourceDraft.enabled,
      });
      setStatus("Source created.");
      await refreshAll();
    } catch {
      setError("Source could not be saved.");
    } finally {
      setIsWorking(false);
    }
  };

  const toggleSource = async (source: IngestionSource) => {
    setIsWorking(true);
    setError(null);
    try {
      if (source.enabled) {
        await api.disableIngestionSource(source.id);
      } else {
        await api.enableIngestionSource(source.id);
      }
      setStatus(`${source.name} updated.`);
      await refreshAll();
    } catch {
      setError("Source could not be updated.");
    } finally {
      setIsWorking(false);
    }
  };

  const startRun = async (source: IngestionSource) => {
    setIsWorking(true);
    setError(null);
    try {
      await api.startIngestionRun({ sourceId: source.id, triggerType: "manual", options: { parseImmediately: true } });
      setStatus(`Run queued for ${source.name}.`);
      await refreshAll();
    } catch {
      setError("Run could not be started.");
    } finally {
      setIsWorking(false);
    }
  };

  const cancelRun = async (run: IngestionRun) => {
    setIsWorking(true);
    setError(null);
    try {
      await api.cancelIngestionRun(run.id);
      setStatus("Run cancelled.");
      await refreshAll();
    } catch {
      setError("Run could not be cancelled.");
    } finally {
      setIsWorking(false);
    }
  };

  const parseSelectedItem = async (item: IngestionItem) => {
    setIsWorking(true);
    setError(null);
    try {
      await api.queueIngestionItemParse(item.id);
      setStatus("Item parse queued.");
      await refreshAll();
    } catch {
      setError("Item could not be queued for parsing.");
    } finally {
      setIsWorking(false);
    }
  };

  const archiveSelectedItem = async (item: IngestionItem) => {
    setIsWorking(true);
    setError(null);
    try {
      await api.archiveIngestionItem(item.id);
      setStatus("Item archived.");
      await refreshAll();
    } catch {
      setError("Item could not be archived.");
    } finally {
      setIsWorking(false);
    }
  };

  const retryJob = async (job: WorkerJob) => {
    setIsWorking(true);
    setError(null);
    try {
      await api.retryIngestionWorkerJob(job.id);
      setStatus("Worker job retried.");
      await refreshAll();
    } catch {
      setError("Worker job could not be retried.");
    } finally {
      setIsWorking(false);
    }
  };

  const cancelJob = async (job: WorkerJob) => {
    setIsWorking(true);
    setError(null);
    try {
      await api.cancelIngestionWorkerJob(job.id);
      setStatus("Worker job cancelled.");
      await refreshAll();
    } catch {
      setError("Worker job could not be cancelled.");
    } finally {
      setIsWorking(false);
    }
  };

  const reconcileSelectedRun = async (run: IngestionRun, type: string) => {
    setIsWorking(true);
    setError(null);
    try {
      await api.startIngestionReconciliation({ runId: run.id, type });
      setStatus("Reconciliation started.");
      await refreshAll();
    } catch {
      setError("Reconciliation could not be started.");
    } finally {
      setIsWorking(false);
    }
  };

  const resolveSelectedDiscrepancy = async (discrepancyId: string) => {
    setIsWorking(true);
    setError(null);
    try {
      await api.resolveIngestionDiscrepancy(discrepancyId);
      setStatus("Discrepancy resolved.");
      await refreshAll();
    } catch {
      setError("Discrepancy could not be resolved.");
    } finally {
      setIsWorking(false);
    }
  };

  const syncMockExchange = async () => {
    if (!selectedSource || selectedSource.type !== "mock_exchange") {
      setError("Select a mock exchange source first.");
      return;
    }

    setIsWorking(true);
    setError(null);
    try {
      await api.syncIngestionMockExchange(selectedSource.id);
      setStatus("Mock exchange synced.");
      await refreshAll();
    } catch {
      setError("Mock exchange could not be synced.");
    } finally {
      setIsWorking(false);
    }
  };

  const runMockExchangeReconciliation = async () => {
    if (!selectedSource || selectedSource.type !== "mock_exchange") {
      setError("Select a mock exchange source first.");
      return;
    }

    setIsWorking(true);
    setError(null);
    try {
      await api.reconcileIngestionMockExchangeTransfers(selectedSource.id);
      setStatus("Mock transfer reconciliation started.");
      await refreshAll();
    } catch {
      setError("Mock transfer reconciliation could not be started.");
    } finally {
      setIsWorking(false);
    }
  };

  const saveSettings = () => {
    setStatus(
      `Settings updated locally: polling every ${settingsDraft.pollingIntervalSeconds}s with ${settingsDraft.maxRetryAttempts} retries.`,
    );
  };

  if (isLoading) {
    return (
      <section className="loading-panel loading-panel-skeleton">
        <p className="eyebrow">Ingestion Engine</p>
        <h1>Loading operational panels.</h1>
        <div className="skeleton-grid" aria-hidden="true">
          <span className="skeleton-line skeleton-line-wide" />
          <span className="skeleton-line" />
          <span className="skeleton-card" />
          <span className="skeleton-card" />
        </div>
      </section>
    );
  }

  return (
    <>
      <section className="hero-panel hero-panel-app hero-panel-ingestion">
        <div className="hero-panel-topline">
          <div>
            <p className="eyebrow">Applications</p>
            <h1>Ingestion Engine</h1>
            <p className="hero-copy">
              Reliable background ingestion, worker jobs, reconciliation, and auditability for sweOS intelligence workflows.
            </p>
          </div>
          <div className="hero-actions">
            <button className="primary-button" type="button" onClick={() => void refreshAll()} disabled={isWorking}>
              Refresh
            </button>
            <span className="ghost-pill">Active</span>
          </div>
        </div>

        <div className="hero-stats">
          <article className="metric-card">
            <span>Total sources</span>
            <strong>{overview?.totalSources ?? 0}</strong>
          </article>
          <article className="metric-card">
            <span>Active runs</span>
            <strong>{overview?.activeRuns ?? 0}</strong>
          </article>
          <article className="metric-card">
            <span>Queued jobs</span>
            <strong>{overview?.queuedJobs ?? 0}</strong>
          </article>
          <article className="metric-card">
            <span>Open discrepancies</span>
            <strong>{overview?.openDiscrepancies ?? 0}</strong>
          </article>
        </div>
      </section>

      <p className="section-status">{isWorking ? "Working..." : error ?? status}</p>

      <section className="workspace-card workspace-card-wide ingestion-shell">
        <div className="ingestion-tabs" role="tablist" aria-label="Ingestion engine tabs">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              className={activeTab === tab.key ? "ingestion-tab ingestion-tab-active" : "ingestion-tab"}
              type="button"
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "overview" ? (
          <div className="ingestion-tab-panel">
            <div className="ingestion-grid">
              <article className="mastery-card">
                <strong>Parsed items</strong>
                <p>{overview?.parsedItems ?? 0}</p>
              </article>
              <article className="mastery-card">
                <strong>Failed jobs</strong>
                <p>{overview?.failedJobs ?? 0}</p>
              </article>
              <article className="mastery-card">
                <strong>Dead-lettered jobs</strong>
                <p>{overview?.deadLetteredJobs ?? 0}</p>
              </article>
              <article className="mastery-card">
                <strong>Queued jobs</strong>
                <p>{overview?.queuedJobs ?? 0}</p>
              </article>
            </div>

            <div className="ingestion-columns">
              <section className="ingestion-panel">
                <h3>Recent runs</h3>
                <div className="exercise-history">
                  {runs.slice(0, 4).map((run) => (
                    <button className="exercise-history-item" key={run.id} type="button" onClick={() => setSelectedRunId(run.id)}>
                      <strong>{statusLabel(run.status)}</strong>
                      <span>{formatDateTime(run.createdAt)}</span>
                    </button>
                  ))}
                  {runs.length === 0 ? <p className="empty-state">Runs will appear here.</p> : null}
                </div>
              </section>
              <section className="ingestion-panel">
                <h3>Recent discrepancies</h3>
                <div className="exercise-history">
                  {selectedDiscrepancies.slice(0, 4).map((item) => (
                    <article className="exercise-history-item" key={item.id}>
                      <strong>{item.type}</strong>
                      <span>{item.description}</span>
                    </article>
                  ))}
                  {selectedDiscrepancies.length === 0 ? <p className="empty-state">No active discrepancies.</p> : null}
                </div>
              </section>
            </div>
          </div>
        ) : null}

        {activeTab === "sources" ? (
          <div className="ingestion-tab-panel ingestion-grid-two">
            <section className="ingestion-panel">
              <h3>Create source</h3>
              <div className="field-grid">
                <label className="field">
                  <span>Name</span>
                  <input value={sourceDraft.name} onChange={(event) => setSourceDraft((current) => ({ ...current, name: event.target.value }))} />
                </label>
                <label className="field">
                  <span>Type</span>
                  <input value={sourceDraft.type} onChange={(event) => setSourceDraft((current) => ({ ...current, type: event.target.value }))} />
                </label>
                <label className="field field-wide">
                  <span>URL</span>
                  <input value={sourceDraft.url} onChange={(event) => setSourceDraft((current) => ({ ...current, url: event.target.value }))} />
                </label>
                <label className="field field-wide">
                  <span>Config JSON</span>
                  <textarea rows={10} value={sourceDraft.configJson} onChange={(event) => setSourceDraft((current) => ({ ...current, configJson: event.target.value }))} />
                </label>
                <label className="field">
                  <span>Enabled</span>
                  <input
                    checked={sourceDraft.enabled}
                    type="checkbox"
                    onChange={(event) => setSourceDraft((current) => ({ ...current, enabled: event.target.checked }))}
                  />
                </label>
              </div>
              <div className="section-actions">
                <button className="primary-button" type="button" onClick={() => void saveSource()} disabled={isWorking}>
                  Save source
                </button>
              </div>
            </section>

            <section className="ingestion-panel">
              <h3>Sources</h3>
              <div className="exercise-history">
                {sources.map((source) => (
                  <button
                    className={selectedSource?.id === source.id ? "exercise-history-item ingestion-history-active" : "exercise-history-item"}
                    key={source.id}
                    type="button"
                    onClick={() => setSelectedSourceId(source.id)}
                  >
                    <strong>{source.name}</strong>
                    <span>
                      {source.type} · {source.enabled ? "enabled" : "disabled"}
                    </span>
                  </button>
                ))}
                {sources.length === 0 ? <p className="empty-state">Create a source to begin ingesting data.</p> : null}
              </div>

              {selectedSource ? (
                <div className="detail-stack">
                  <article className="mastery-card">
                    <strong>Selected source</strong>
                    <p>
                      {selectedSource.type} · {selectedSource.url ?? "No URL"}
                    </p>
                    <pre className="markdown-preview">{prettyJson(selectedSource.config)}</pre>
                  </article>
                  <div className="section-actions">
                    <button className="ghost-button" type="button" onClick={() => void toggleSource(selectedSource)} disabled={isWorking}>
                      {selectedSource.enabled ? "Disable" : "Enable"}
                    </button>
                    <button className="ghost-button" type="button" onClick={() => void startRun(selectedSource)} disabled={isWorking}>
                      Trigger run
                    </button>
                  </div>
                </div>
              ) : null}
            </section>
          </div>
        ) : null}

        {activeTab === "runs" ? (
          <div className="ingestion-tab-panel ingestion-grid-two">
            <section className="ingestion-panel">
              <h3>Runs</h3>
              <div className="exercise-history">
                {runs.map((run) => (
                  <button
                    className={selectedRun?.id === run.id ? "exercise-history-item ingestion-history-active" : "exercise-history-item"}
                    key={run.id}
                    type="button"
                    onClick={() => setSelectedRunId(run.id)}
                  >
                    <strong>{statusLabel(run.status)}</strong>
                    <span>
                      {run.fetchedItemCount} fetched · {run.parsedItemCount} parsed · {run.failedItemCount} failed
                    </span>
                  </button>
                ))}
                {runs.length === 0 ? <p className="empty-state">Triggered runs appear here.</p> : null}
              </div>
            </section>

            <section className="ingestion-panel">
              <h3>Run detail</h3>
              {selectedRun ? (
                <article className="mastery-card">
                  <strong>{selectedRun.status}</strong>
                  <p>
                    started {formatDateTime(selectedRun.startedAt)} · completed {formatDateTime(selectedRun.completedAt)}
                  </p>
                  <p>{selectedRun.errorMessage ?? "No error message."}</p>
                  <div className="section-actions">
                    <button className="ghost-button" type="button" onClick={() => void cancelRun(selectedRun)} disabled={isWorking}>
                      Cancel
                    </button>
                    <button className="ghost-button" type="button" onClick={() => void reconcileSelectedRun(selectedRun, "parsing_completeness")} disabled={isWorking}>
                      Reconcile parsing
                    </button>
                  </div>
                </article>
              ) : (
                <p className="empty-state">Select a run to inspect counts and actions.</p>
              )}
            </section>
          </div>
        ) : null}

        {activeTab === "items" ? (
          <div className="ingestion-tab-panel ingestion-grid-two">
            <section className="ingestion-panel">
              <h3>Items</h3>
              <div className="exercise-history">
                {items.map((item) => (
                  <button
                    className={selectedItem?.id === item.id ? "exercise-history-item ingestion-history-active" : "exercise-history-item"}
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedItemId(item.id)}
                  >
                    <strong>{item.title ?? item.type}</strong>
                    <span>
                      {item.type} · {statusLabel(item.status)}
                    </span>
                  </button>
                ))}
                {items.length === 0 ? <p className="empty-state">Fetched items appear here.</p> : null}
              </div>
            </section>

            <section className="ingestion-panel">
              <h3>Item detail</h3>
              {selectedItem ? (
                <article className="mastery-card">
                  <strong>{selectedItem.title ?? "Untitled item"}</strong>
                  <p>
                    {selectedItem.type} · {selectedItem.status} · {selectedItem.canonicalUrl ?? "No URL"}
                  </p>
                  <pre className="markdown-preview">{selectedItem.rawContent}</pre>
                  <pre className="markdown-preview">{prettyJson(selectedItem.rawJson)}</pre>
                  <div className="section-actions">
                    <button className="ghost-button" type="button" onClick={() => void parseSelectedItem(selectedItem)} disabled={isWorking}>
                      Parse
                    </button>
                    <button className="ghost-button" type="button" onClick={() => void archiveSelectedItem(selectedItem)} disabled={isWorking}>
                      Archive
                    </button>
                  </div>
                </article>
              ) : (
                <p className="empty-state">Select an item to inspect the raw payload.</p>
              )}
            </section>
          </div>
        ) : null}

        {activeTab === "workerJobs" ? (
          <div className="ingestion-tab-panel ingestion-grid-two">
            <section className="ingestion-panel">
              <h3>Worker jobs</h3>
              <div className="exercise-history">
                {jobs.map((job) => (
                  <button
                    className={selectedJob?.id === job.id ? "exercise-history-item ingestion-history-active" : "exercise-history-item"}
                    key={job.id}
                    type="button"
                    onClick={() => setSelectedJobId(job.id)}
                  >
                    <strong>{job.jobType}</strong>
                    <span>
                      {job.status} · attempts {job.attempts}/{job.maxAttempts}
                    </span>
                  </button>
                ))}
                {jobs.length === 0 ? <p className="empty-state">Queued jobs appear here.</p> : null}
              </div>
            </section>

            <section className="ingestion-panel">
              <h3>Job detail</h3>
              {selectedJob ? (
                <article className="mastery-card">
                  <strong>{selectedJob.jobType}</strong>
                  <p>{selectedJob.lastError ?? "No last error."}</p>
                  <pre className="markdown-preview">{prettyJson(selectedJob.payload)}</pre>
                  <div className="section-actions">
                    <button className="ghost-button" type="button" onClick={() => void retryJob(selectedJob)} disabled={isWorking}>
                      Retry
                    </button>
                    <button className="ghost-button" type="button" onClick={() => void cancelJob(selectedJob)} disabled={isWorking}>
                      Cancel
                    </button>
                  </div>
                </article>
              ) : (
                <p className="empty-state">Select a job to inspect attempts and payload.</p>
              )}
            </section>
          </div>
        ) : null}

        {activeTab === "reconciliation" ? (
          <div className="ingestion-tab-panel ingestion-grid-two">
            <section className="ingestion-panel">
              <h3>Reconciliation runs</h3>
              <div className="exercise-history">
                {reconciliationRuns.map((run) => (
                  <button
                    className={selectedReconciliation?.id === run.id ? "exercise-history-item ingestion-history-active" : "exercise-history-item"}
                    key={run.id}
                    type="button"
                    onClick={() => setSelectedReconciliationId(run.id)}
                  >
                    <strong>{run.type}</strong>
                    <span>
                      {run.status} · {run.discrepancyCount} discrepancies
                    </span>
                  </button>
                ))}
                {reconciliationRuns.length === 0 ? <p className="empty-state">Reconciliation runs appear here.</p> : null}
              </div>
            </section>

            <section className="ingestion-panel">
              <h3>Discrepancies</h3>
              {selectedReconciliation ? (
                <>
                  <article className="mastery-card">
                    <strong>{selectedReconciliation.type}</strong>
                    <p>{selectedReconciliation.summaryMarkdown ?? "No summary yet."}</p>
                  </article>
                  <div className="exercise-history">
                    {selectedDiscrepancies.map((item) => (
                      <article className="exercise-history-item" key={item.id}>
                        <strong>{item.type}</strong>
                        <span>
                          {item.severity} · {item.resolved ? "resolved" : "open"}
                        </span>
                        <p>{item.description}</p>
                        {!item.resolved ? (
                          <button className="ghost-button" type="button" onClick={() => void resolveSelectedDiscrepancy(item.id)} disabled={isWorking}>
                            Resolve
                          </button>
                        ) : null}
                      </article>
                    ))}
                    {selectedDiscrepancies.length === 0 ? <p className="empty-state">No discrepancies for this run.</p> : null}
                  </div>
                </>
              ) : (
                <p className="empty-state">Select a reconciliation run to inspect discrepancies.</p>
              )}
            </section>
          </div>
        ) : null}

        {activeTab === "auditLog" ? (
          <div className="ingestion-tab-panel">
            <div className="exercise-history">
              {auditEvents.map((event) => (
                <article className="exercise-history-item" key={event.id}>
                  <strong>
                    {event.eventType} · {event.entityType}
                  </strong>
                  <span>{formatDateTime(event.createdAt)}</span>
                  <p>{event.actorType}</p>
                  <pre className="markdown-preview">{prettyJson(event.payload)}</pre>
                </article>
              ))}
              {auditEvents.length === 0 ? <p className="empty-state">Audit events will appear here.</p> : null}
            </div>
          </div>
        ) : null}

        {activeTab === "mockFinops" ? (
          <div className="ingestion-tab-panel ingestion-grid-two">
            <section className="ingestion-panel">
              <h3>Mock exchange</h3>
              <p className="empty-state">This tab is a simulation of external account reconciliation.</p>
              <div className="section-actions">
                <button className="primary-button" type="button" onClick={() => void syncMockExchange()} disabled={isWorking}>
                  Sync mock exchange
                </button>
                <button className="ghost-button" type="button" onClick={() => void runMockExchangeReconciliation()} disabled={isWorking}>
                  Reconcile transfers
                </button>
              </div>
            </section>

            <section className="ingestion-panel">
              <h3>Accounts and transactions</h3>
              <div className="ingestion-columns">
                <article className="mastery-card">
                  <strong>Accounts</strong>
                  <p>{accounts.length}</p>
                </article>
                <article className="mastery-card">
                  <strong>Transactions</strong>
                  <p>{transactions.length}</p>
                </article>
              </div>
              <pre className="markdown-preview">{prettyJson(accounts[0] ?? {})}</pre>
              <pre className="markdown-preview">{prettyJson(transactions[0] ?? {})}</pre>
            </section>
          </div>
        ) : null}

        {activeTab === "settings" ? (
          <div className="ingestion-tab-panel ingestion-grid-two">
            <section className="ingestion-panel">
              <h3>Operational settings</h3>
              <div className="field-grid">
                <label className="field">
                  <span>Polling interval (seconds)</span>
                  <input
                    value={settingsDraft.pollingIntervalSeconds}
                    onChange={(event) => setSettingsDraft((current) => ({ ...current, pollingIntervalSeconds: event.target.value }))}
                  />
                </label>
                <label className="field">
                  <span>Max retry attempts</span>
                  <input
                    value={settingsDraft.maxRetryAttempts}
                    onChange={(event) => setSettingsDraft((current) => ({ ...current, maxRetryAttempts: event.target.value }))}
                  />
                </label>
                <label className="field">
                  <span>Source fetch timeout</span>
                  <input
                    value={settingsDraft.fetchTimeoutSeconds}
                    onChange={(event) => setSettingsDraft((current) => ({ ...current, fetchTimeoutSeconds: event.target.value }))}
                  />
                </label>
                <label className="field">
                  <span>Body size limit</span>
                  <input
                    value={settingsDraft.bodyLimitBytes}
                    onChange={(event) => setSettingsDraft((current) => ({ ...current, bodyLimitBytes: event.target.value }))}
                  />
                </label>
              </div>
              <div className="section-actions">
                <button className="primary-button" type="button" onClick={saveSettings}>
                  Save settings
                </button>
              </div>
            </section>

            <section className="ingestion-panel">
              <h3>Current snapshot</h3>
              <pre className="markdown-preview">
                {prettyJson({
                  sources: sources.length,
                  runs: runs.length,
                  items: items.length,
                  workerJobs: jobs.length,
                  discrepancies: discrepancies.length,
                })}
              </pre>
            </section>
          </div>
        ) : null}
      </section>
    </>
  );
}
