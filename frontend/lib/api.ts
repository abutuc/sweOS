import { getStoredToken, setStoredToken, setStoredUser } from "@/lib/session";

export type AuthUser = {
  id: string;
  email: string;
  fullName: string | null;
};

export type AuthPayload = {
  user: AuthUser;
  token: string;
};

export type Profile = {
  userId: string;
  headline: string | null;
  bio: string | null;
  yearsExperience: string | null;
  currentRole: string | null;
  stack: string[];
  targetRole: string | null;
  targetRoles: string[];
  targetSeniority: string | null;
  preferredIndustries: string[];
  preferredLocations: string[];
  preferredWorkModes: string[];
  salaryExpectationMin: number | null;
  salaryExpectationMax: number | null;
  learningGoals: string[];
  summary: string | null;
};

export type SkillCatalogItem = {
  id: string;
  slug: string;
  name: string;
  category: string;
  description: string | null;
};

export type UserSkill = {
  skillId: string;
  skillSlug: string;
  skillName: string;
  category: string;
  selfAssessedLevel: string;
  measuredLevel: string | null;
  confidenceScore: string | null;
  evidenceCount: number;
  lastEvaluatedAt: string | null;
};

export type Goal = {
  id: string;
  userId: string;
  title: string;
  description: string | null;
  targetDate: string | null;
  horizon: string;
  priority: number;
  status: string;
};

export type Preferences = {
  userId: string;
  contentSources: string[];
  notificationCadence: string;
  aiAssistanceLevel: string;
  privacySettings: Record<string, unknown>;
  targetOpportunityFilters: Record<string, unknown>;
};

export type ExerciseSummary = {
  id: string;
  type: string;
  topic: string;
  difficulty: string;
  title: string;
  createdAt: string;
};

export type Exercise = {
  id: string;
  type: string;
  topic: string;
  subtopic: string | null;
  difficulty: string;
  title: string;
  promptMarkdown: string;
  constraints: Record<string, unknown>;
  expectedOutcomes: string[];
  hints: string[];
  tags: string[];
  createdAt: string | null;
};

export type ExerciseAttempt = {
  id: string;
  exerciseId: string;
  status: string;
  answerMarkdown: string | null;
  answerCode: string | null;
  answerSql: string | null;
  answerJson: Record<string, unknown>;
  submittedAt: string | null;
  evaluatedAt: string | null;
};

export type ExerciseEvaluation = {
  overallScore: number;
  rubricScores: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  feedbackMarkdown: string;
  recommendedNextTopics: string[];
  improvementActions: Array<{ action: string; why: string }>;
};

export type ExerciseRunCase = {
  index: number;
  passed: boolean;
  input: unknown[];
  expected: unknown;
  actual: unknown | null;
  error: string | null;
};

export type ExerciseRunResult = {
  passed: boolean;
  totalCases: number;
  passedCases: number;
  stdout: string;
  stderr: string;
  runtimeMs: number | null;
  caseResults: ExerciseRunCase[];
  message: string;
};

export type TopicMastery = {
  topic: string;
  attemptsCount: number;
  averageScore: number;
  weakestDimension: string | null;
  lastPracticedAt: string | null;
};

export type DashboardSummary = {
  profile: Profile;
  goals: Goal[];
  exercises: ExerciseSummary[];
  topicMastery: TopicMastery[];
};

export type LearningSummary = {
  profile: Profile;
  exercises: ExerciseSummary[];
  topicMastery: TopicMastery[];
};

export type AnalyticsSummary = {
  totalExercisesCompleted: number;
  averageScore: number | null;
  streakDays: number;
};

export type AnalyticsTopic = {
  topic: string;
  weakestDimension: string | null;
  masteryScore: number;
  attemptsCount: number;
};

export type AnalyticsActivity = {
  type: string;
  entityId: string;
  title: string;
  createdAt: string;
};

export type AnalyticsDashboard = {
  summary: AnalyticsSummary;
  weakTopics: AnalyticsTopic[];
  strongTopics: AnalyticsTopic[];
  recentActivity: AnalyticsActivity[];
};

export type Job = {
  id: string;
  title: string;
  companyName: string | null;
  sourceUrl: string | null;
  location: string | null;
  workMode: string | null;
  rawDescription?: string | null;
};

export type JobListItem = {
  id: string;
  userJobId: string | null;
  title: string;
  companyName: string | null;
  location: string | null;
  status: string | null;
  matchScore: number | null;
};

export type JobParse = {
  id: string;
  parsedTitle: string | null;
  parsedCompanyName: string | null;
  responsibilities: string[];
  requiredSkills: string[];
  preferredSkills: string[];
  keywords: string[];
  seniorityAssessment: string | null;
  summaryMarkdown: string | null;
};

export type JobGapAnalysis = {
  id: string;
  fitSummaryMarkdown: string;
  matchedSkills: Array<{ skill: string; strength: string }>;
  missingSkills: Array<{ skill: string; severity: string }>;
  weakEvidence: Array<{ skill: string; issue: string }>;
  recommendation: { applyNow?: boolean; priority?: string; nextActions?: string[] };
};

export type CvVersion = {
  id: string;
  status: string;
  title: string;
  jobId: string | null;
  createdByAi: boolean;
  createdAt: string;
};

export type CvTailoredVersion = {
  id: string;
  status: string;
  title: string;
  structuredContent: Record<string, unknown>;
  renderedMarkdown: string | null;
};

export type CvFeedback = {
  score: number | null;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
};

export type IngestionSource = {
  id: string;
  userId: string | null;
  name: string;
  type: string;
  url: string | null;
  config: Record<string, unknown>;
  enabled: boolean;
  createdAt: string;
  updatedAt: string;
};

export type IngestionRun = {
  id: string;
  sourceId: string | null;
  status: string;
  triggerType: string;
  expectedItemCount: number | null;
  fetchedItemCount: number;
  parsedItemCount: number;
  failedItemCount: number;
  startedAt: string | null;
  completedAt: string | null;
  errorMessage: string | null;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
};

export type IngestionItem = {
  id: string;
  runId: string;
  sourceId: string | null;
  externalId: string | null;
  canonicalUrl: string | null;
  type: string;
  title: string | null;
  rawContent: string;
  rawJson: Record<string, unknown>;
  contentHash: string;
  status: string;
  duplicateOfId: string | null;
  fetchedAt: string;
  createdAt: string;
  updatedAt: string;
};

export type WorkerJob = {
  id: string;
  jobType: string;
  status: string;
  priority: number;
  runId: string | null;
  itemId: string | null;
  idempotencyKey: string;
  payload: Record<string, unknown>;
  attempts: number;
  maxAttempts: number;
  lockedBy: string | null;
  lockedUntil: string | null;
  availableAt: string;
  startedAt: string | null;
  completedAt: string | null;
  lastError: string | null;
  createdAt: string;
  updatedAt: string;
};

export type ReconciliationRun = {
  id: string;
  runId: string | null;
  type: string;
  status: string;
  expectedCount: number;
  actualCount: number;
  discrepancyCount: number;
  startedAt: string | null;
  completedAt: string | null;
  summaryMarkdown: string | null;
  metadata: Record<string, unknown>;
  createdAt: string;
};

export type ReconciliationDiscrepancy = {
  id: string;
  reconciliationRunId: string;
  reconciliationItemId: string | null;
  severity: string;
  type: string;
  description: string;
  expected: Record<string, unknown>;
  actual: Record<string, unknown>;
  resolved: boolean;
  resolvedAt: string | null;
  createdAt: string;
};

export type AuditEvent = {
  id: string;
  entityType: string;
  entityId: string;
  eventType: string;
  actorType: string;
  actorId: string | null;
  payload: Record<string, unknown>;
  createdAt: string;
};

export type ExternalAccount = {
  id: string;
  provider: string;
  accountRef: string;
  assetSymbol: string;
  balance: number;
  raw: Record<string, unknown>;
  lastSyncedAt: string | null;
  createdAt: string;
  updatedAt: string;
};

export type ExternalTransaction = {
  id: string;
  provider: string;
  externalTxId: string;
  fromAccountRef: string | null;
  toAccountRef: string | null;
  assetSymbol: string;
  amount: number;
  fee: number;
  status: string;
  occurredAt: string;
  raw: Record<string, unknown>;
  createdAt: string;
};

export type IngestionOverview = {
  totalSources: number;
  activeRuns: number;
  queuedJobs: number;
  failedJobs: number;
  parsedItems: number;
  openDiscrepancies: number;
  deadLetteredJobs: number;
  recentRunIds: string[];
  recentFailedJobIds: string[];
  recentDiscrepancyIds: string[];
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const READ_CACHE_TTL_MS = 4_000;

type ReadCacheEntry = {
  expiresAt: number;
  promise: Promise<unknown>;
};

const readCache = new Map<string, ReadCacheEntry>();

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getStoredToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const errorBody = (await response.json()) as { detail?: string };
      if (errorBody.detail) {
        message = errorBody.detail;
      }
    } catch {}

    throw new ApiError(message, response.status);
  }

  return (await response.json()) as T;
}

function clearReadCache() {
  readCache.clear();
}

function cachedGet<T>(path: string): Promise<T> {
  const token = getStoredToken() ?? "anonymous";
  const cacheKey = `${token}:${path}`;
  const cached = readCache.get(cacheKey);

  if (cached && cached.expiresAt > Date.now()) {
    return cached.promise as Promise<T>;
  }

  const promise = request<T>(path).catch((error) => {
    readCache.delete(cacheKey);
    throw error;
  });
  readCache.set(cacheKey, {
    expiresAt: Date.now() + READ_CACHE_TTL_MS,
    promise,
  });
  return promise;
}

function buildQueryPath(path: string, params?: Record<string, string | number | boolean | undefined>) {
  if (!params) {
    return path;
  }

  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined) {
      continue;
    }
    query.set(key, String(value));
  }

  const queryString = query.toString();
  return queryString.length > 0 ? `${path}?${queryString}` : path;
}

async function mutatingRequest<T>(path: string, init: RequestInit): Promise<T> {
  const response = await request<T>(path, init);
  clearReadCache();
  return response;
}

export const api = {
  register: async (payload: { email: string; password: string; fullName?: string }) => {
    const response = await request<{ data: AuthPayload }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setStoredToken(response.data.token);
    setStoredUser(response.data.user);
    clearReadCache();
    return response;
  },
  login: async (payload: { email: string; password: string }) => {
    const response = await request<{ data: AuthPayload }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setStoredToken(response.data.token);
    setStoredUser(response.data.user);
    clearReadCache();
    return response;
  },
  getMe: () => cachedGet<{ data: AuthUser }>("/auth/me"),
  updateMe: (payload: { fullName: string | null }) =>
    mutatingRequest<{ data: AuthUser }>("/auth/me", {
      method: "PUT",
      body: JSON.stringify(payload),
    }).then((response) => {
      setStoredUser(response.data);
      return response;
    }),
  getDashboardSummary: () => cachedGet<{ data: DashboardSummary }>("/dashboard/summary"),
  getAnalyticsDashboard: () => cachedGet<{ data: AnalyticsDashboard }>("/analytics/dashboard"),
  getLearningSummary: () => cachedGet<{ data: LearningSummary }>("/learning/summary"),
  getProfile: () => cachedGet<{ data: Profile }>("/profile"),
  saveProfile: (payload: Partial<Profile>) =>
    mutatingRequest<{ data: { updated: boolean } }>("/profile", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  getSkillCatalog: () => cachedGet<{ data: SkillCatalogItem[] }>("/skills/catalog"),
  getUserSkills: () => cachedGet<{ data: UserSkill[] }>("/skills/me"),
  saveUserSkills: (payload: { skills: Array<{ skillId: string; selfAssessedLevel: string }> }) =>
    mutatingRequest<{ data: { updatedCount: number } }>("/skills/me", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  getGoals: () => cachedGet<{ data: Goal[] }>("/goals"),
  createGoal: (payload: Omit<Goal, "id" | "userId">) =>
    mutatingRequest<{ data: Goal }>("/goals", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateGoal: (goalId: string, payload: Omit<Goal, "id" | "userId">) =>
    mutatingRequest<{ data: Goal }>(`/goals/${goalId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteGoal: (goalId: string) =>
    mutatingRequest<{ data: { deleted: boolean } }>(`/goals/${goalId}`, {
      method: "DELETE",
    }),
  getPreferences: () => cachedGet<{ data: Preferences }>("/preferences"),
  savePreferences: (payload: Partial<Preferences>) =>
    mutatingRequest<{ data: { updated: boolean } }>("/preferences", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  generateExercise: (payload: {
    type: string;
    topic: string;
    subtopic?: string;
    difficulty: string;
    timeLimitMinutes: number;
    includeHints: boolean;
    context: {
      targetRole?: string | null;
      weakTopics: string[];
    };
  }) =>
    mutatingRequest<{ data: { exercise: Exercise } }>("/exercises/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listExercises: (params?: {
    type?: string;
    topic?: string;
    difficulty?: string;
    tag?: string;
    limit?: number;
    offset?: number;
  }) =>
    cachedGet<{ data: ExerciseSummary[]; meta: Record<string, number> }>(
      buildQueryPath("/exercises", params),
    ),
  getExercise: (exerciseId: string) => cachedGet<{ data: Exercise }>(`/exercises/${exerciseId}`),
  runExerciseCode: (exerciseId: string, payload: { answerCode: string }) =>
    mutatingRequest<{ data: ExerciseRunResult }>(`/exercises/${exerciseId}/run`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  createAttempt: (
    exerciseId: string,
    payload: {
      answerMarkdown?: string | null;
      answerCode?: string | null;
      answerSql?: string | null;
      answerJson?: Record<string, unknown>;
      submit: boolean;
    },
  ) =>
    mutatingRequest<{ data: { attempt: ExerciseAttempt } }>(`/exercises/${exerciseId}/attempts`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  evaluateAttempt: (attemptId: string) =>
    mutatingRequest<{ data: ExerciseEvaluation }>(`/exercise-attempts/${attemptId}/evaluate`, {
      method: "POST",
    }),
  getTopicMastery: () => cachedGet<{ data: TopicMastery[] }>("/topic-mastery"),
  createJob: (payload: {
    title: string;
    companyName?: string | null;
    sourceUrl?: string | null;
    rawDescription: string;
    location?: string | null;
    workMode?: string | null;
  }) =>
    mutatingRequest<{ data: { job: Job } }>("/jobs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  parseJob: (jobId: string) =>
    mutatingRequest<{ data: { parse: JobParse } }>(`/jobs/${jobId}/parse`, {
      method: "POST",
    }),
  listJobs: () => cachedGet<{ data: JobListItem[]; meta: Record<string, number> }>("/jobs"),
  saveJob: (jobId: string, payload: { status: string; notes?: string | null }) =>
    mutatingRequest<{ data: { userJobId: string; status: string } }>(`/jobs/${jobId}/save`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  analyzeJobGap: (userJobId: string) =>
    mutatingRequest<{ data: { analysis: JobGapAnalysis } }>(`/user-jobs/${userJobId}/gap-analysis`, {
      method: "POST",
    }),
  createCvDocument: (payload: { name: string; description?: string | null }) =>
    mutatingRequest<{ data: { cvDocumentId: string } }>("/cvs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  createCvVersion: (
    cvDocumentId: string,
    payload: { status: string; title: string; structuredContent: Record<string, unknown> },
  ) =>
    mutatingRequest<{ data: { cvVersionId: string } }>(`/cvs/${cvDocumentId}/versions`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listCvVersions: (cvDocumentId: string) =>
    cachedGet<{ data: CvVersion[] }>(`/cvs/${cvDocumentId}/versions`),
  tailorCv: (
    cvDocumentId: string,
    payload: { baseVersionId: string; jobId: string; preferences: Record<string, unknown> },
  ) =>
    mutatingRequest<{ data: { cvVersion: CvTailoredVersion } }>(`/cvs/${cvDocumentId}/tailor`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  createCvFeedback: (cvVersionId: string) =>
    mutatingRequest<{ data: { feedback: CvFeedback } }>(`/cv-versions/${cvVersionId}/feedback`, {
      method: "POST",
    }),
  getIngestionOverview: () => cachedGet<{ data: IngestionOverview }>("/ingestion/overview"),
  listIngestionSources: (params?: { type?: string; enabled?: boolean }) =>
    cachedGet<{ data: IngestionSource[] }>(buildQueryPath("/ingestion/sources", params)),
  createIngestionSource: (payload: { name: string; type: string; url?: string | null; config?: Record<string, unknown>; enabled?: boolean }) =>
    mutatingRequest<{ data: IngestionSource }>("/ingestion/sources", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateIngestionSource: (sourceId: string, payload: { name?: string | null; type?: string | null; url?: string | null; config?: Record<string, unknown> | null; enabled?: boolean | null }) =>
    mutatingRequest<{ data: IngestionSource }>(`/ingestion/sources/${sourceId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  enableIngestionSource: (sourceId: string) =>
    mutatingRequest<{ data: IngestionSource }>(`/ingestion/sources/${sourceId}/enable`, {
      method: "POST",
    }),
  disableIngestionSource: (sourceId: string) =>
    mutatingRequest<{ data: IngestionSource }>(`/ingestion/sources/${sourceId}/disable`, {
      method: "POST",
    }),
  startIngestionRun: (payload: { sourceId: string; triggerType?: string; options?: Record<string, unknown> }) =>
    mutatingRequest<{ data: IngestionRun }>("/ingestion/runs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listIngestionRuns: (params?: { status?: string; limit?: number; offset?: number }) =>
    cachedGet<{ data: IngestionRun[]; meta: Record<string, number> }>(buildQueryPath("/ingestion/runs", params)),
  getIngestionRun: (runId: string) => cachedGet<{ data: IngestionRun }>(`/ingestion/runs/${runId}`),
  cancelIngestionRun: (runId: string) =>
    mutatingRequest<{ data: IngestionRun }>(`/ingestion/runs/${runId}/cancel`, {
      method: "POST",
    }),
  listIngestionItems: (params?: { runId?: string; type?: string; status?: string }) =>
    cachedGet<{ data: IngestionItem[] }>(buildQueryPath("/ingestion/items", params)),
  getIngestionItem: (itemId: string) => cachedGet<{ data: IngestionItem }>(`/ingestion/items/${itemId}`),
  queueIngestionItemParse: (itemId: string) =>
    mutatingRequest<{ data: { jobId: string; status: string } }>(`/ingestion/items/${itemId}/parse`, {
      method: "POST",
    }),
  archiveIngestionItem: (itemId: string) =>
    mutatingRequest<{ data: IngestionItem }>(`/ingestion/items/${itemId}/archive`, {
      method: "POST",
    }),
  listIngestionWorkerJobs: (params?: { status?: string; jobType?: string }) =>
    cachedGet<{ data: WorkerJob[] }>(buildQueryPath("/ingestion/worker-jobs", params)),
  getIngestionWorkerJob: (jobId: string) => cachedGet<{ data: WorkerJob }>(`/ingestion/worker-jobs/${jobId}`),
  retryIngestionWorkerJob: (jobId: string) =>
    mutatingRequest<{ data: WorkerJob }>(`/ingestion/worker-jobs/${jobId}/retry`, {
      method: "POST",
    }),
  cancelIngestionWorkerJob: (jobId: string) =>
    mutatingRequest<{ data: WorkerJob }>(`/ingestion/worker-jobs/${jobId}/cancel`, {
      method: "POST",
    }),
  startIngestionReconciliation: (payload: { runId: string; type: string }) =>
    mutatingRequest<{ data: ReconciliationRun }>("/ingestion/reconciliation-runs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listIngestionReconciliationRuns: (params?: { type?: string }) =>
    cachedGet<{ data: ReconciliationRun[] }>(buildQueryPath("/ingestion/reconciliation-runs", params)),
  getIngestionReconciliationRun: (reconciliationRunId: string) =>
    cachedGet<{ data: ReconciliationRun }>(`/ingestion/reconciliation-runs/${reconciliationRunId}`),
  listIngestionDiscrepancies: (reconciliationRunId: string) =>
    cachedGet<{ data: ReconciliationDiscrepancy[] }>(`/ingestion/reconciliation-runs/${reconciliationRunId}/discrepancies`),
  resolveIngestionDiscrepancy: (discrepancyId: string) =>
    mutatingRequest<{ data: { resolved: boolean } }>(`/ingestion/discrepancies/${discrepancyId}/resolve`, {
      method: "POST",
    }),
  listIngestionAuditEvents: (params?: { entityType?: string; entityId?: string; eventType?: string }) =>
    cachedGet<{ data: AuditEvent[] }>(buildQueryPath("/ingestion/audit-events", params)),
  syncIngestionMockExchange: (sourceId: string) =>
    mutatingRequest<{ data: IngestionRun }>(`/ingestion/mock-exchange/sync?source_id=${encodeURIComponent(sourceId)}`, {
      method: "POST",
    }),
  listIngestionMockExchangeAccounts: () =>
    cachedGet<{ data: ExternalAccount[] }>("/ingestion/mock-exchange/accounts"),
  listIngestionMockExchangeTransactions: () =>
    cachedGet<{ data: ExternalTransaction[] }>("/ingestion/mock-exchange/transactions"),
  reconcileIngestionMockExchangeTransfers: (sourceId: string) =>
    mutatingRequest<{ data: { runId: string; status: string } }>(`/ingestion/mock-exchange/reconcile-transfers?source_id=${encodeURIComponent(sourceId)}`, {
      method: "POST",
    }),
};
