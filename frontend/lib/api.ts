import { getStoredToken, setStoredToken } from "@/lib/session";

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
  preferredLocations: string[];
  preferredWorkModes: string[];
  salaryExpectationMin: number | null;
  salaryExpectationMax: number | null;
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
  priority: number;
  status: string;
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
    return response;
  },
  login: async (payload: { email: string; password: string }) => {
    const response = await request<{ data: AuthPayload }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setStoredToken(response.data.token);
    return response;
  },
  getMe: () => request<{ data: AuthUser }>("/auth/me"),
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
};
