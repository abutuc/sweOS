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

export type TopicMastery = {
  topic: string;
  attemptsCount: number;
  averageScore: number;
  weakestDimension: string | null;
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
  listExercises: () => cachedGet<{ data: ExerciseSummary[]; meta: Record<string, number> }>("/exercises"),
  getExercise: (exerciseId: string) => cachedGet<{ data: Exercise }>(`/exercises/${exerciseId}`),
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
};
