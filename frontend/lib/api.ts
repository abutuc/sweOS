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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export const api = {
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
};
