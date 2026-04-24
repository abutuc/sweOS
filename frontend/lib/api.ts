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

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

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

export const api = {
  register: async (payload: { email: string; password: string; fullName?: string }) => {
    const response = await request<{ data: AuthPayload }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setStoredToken(response.data.token);
    setStoredUser(response.data.user);
    return response;
  },
  login: async (payload: { email: string; password: string }) => {
    const response = await request<{ data: AuthPayload }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setStoredToken(response.data.token);
    setStoredUser(response.data.user);
    return response;
  },
  getMe: () => request<{ data: AuthUser }>("/auth/me"),
  updateMe: (payload: { fullName: string | null }) =>
    request<{ data: AuthUser }>("/auth/me", {
      method: "PUT",
      body: JSON.stringify(payload),
    }).then((response) => {
      setStoredUser(response.data);
      return response;
    }),
  getProfile: () => request<{ data: Profile }>("/profile"),
  saveProfile: (payload: Partial<Profile>) =>
    request<{ data: { updated: boolean } }>("/profile", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  getSkillCatalog: () => request<{ data: SkillCatalogItem[] }>("/skills/catalog"),
  getUserSkills: () => request<{ data: UserSkill[] }>("/skills/me"),
  saveUserSkills: (payload: { skills: Array<{ skillId: string; selfAssessedLevel: string }> }) =>
    request<{ data: { updatedCount: number } }>("/skills/me", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  getGoals: () => request<{ data: Goal[] }>("/goals"),
  createGoal: (payload: Omit<Goal, "id" | "userId">) =>
    request<{ data: Goal }>("/goals", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateGoal: (goalId: string, payload: Omit<Goal, "id" | "userId">) =>
    request<{ data: Goal }>(`/goals/${goalId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  deleteGoal: (goalId: string) =>
    request<{ data: { deleted: boolean } }>(`/goals/${goalId}`, {
      method: "DELETE",
    }),
  getPreferences: () => request<{ data: Preferences }>("/preferences"),
  savePreferences: (payload: Partial<Preferences>) =>
    request<{ data: { updated: boolean } }>("/preferences", {
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
    request<{ data: { exercise: Exercise } }>("/exercises/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listExercises: () => request<{ data: ExerciseSummary[]; meta: Record<string, number> }>("/exercises"),
  getExercise: (exerciseId: string) => request<{ data: Exercise }>(`/exercises/${exerciseId}`),
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
    request<{ data: { attempt: ExerciseAttempt } }>(`/exercises/${exerciseId}/attempts`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  evaluateAttempt: (attemptId: string) =>
    request<{ data: ExerciseEvaluation }>(`/exercise-attempts/${attemptId}/evaluate`, {
      method: "POST",
    }),
  getTopicMastery: () => request<{ data: TopicMastery[] }>("/topic-mastery"),
};
