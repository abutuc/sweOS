"use client";

import { useEffect, useState } from "react";

import { AuthPanel } from "@/components/auth-panel";
import { GoalsSection } from "@/components/goals-section";
import { ProfileSection } from "@/components/profile-section";
import { SkillsSection } from "@/components/skills-section";
import { api, ApiError, type AuthUser } from "@/lib/api";
import { clearStoredToken, getStoredToken } from "@/lib/session";

export function CompanionApp() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  useEffect(() => {
    const token = getStoredToken();

    if (!token) {
      setIsBootstrapping(false);
      return;
    }

    void api
      .getProfile()
      .then(() => {
        const payload = JSON.parse(atob(token.split(".")[1] ?? ""));
        setUser({
          id: payload.sub as string,
          email: "authenticated@sweos.local",
          fullName: null,
        });
      })
      .catch((error) => {
        if (error instanceof ApiError && error.status === 401) {
          clearStoredToken();
        }
      })
      .finally(() => {
        setIsBootstrapping(false);
      });
  }, []);

  const handleLogout = () => {
    clearStoredToken();
    setUser(null);
  };

  if (isBootstrapping) {
    return (
      <main className="page-shell">
        <section className="loading-panel">
          <p className="eyebrow">Booting</p>
          <h1>Restoring your engineering workspace.</h1>
        </section>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="page-shell">
        <AuthPanel onAuthenticated={setUser} />
      </main>
    );
  }

  return (
    <main className="page-shell page-shell-app">
      <section className="hero-panel hero-panel-app">
        <div className="hero-panel-topline">
          <div>
            <p className="eyebrow">sweOS Companion</p>
            <h1>Your engineering operating surface.</h1>
            <p className="hero-copy">
              Keep your profile direction, skill signals, and next milestones aligned.
            </p>
          </div>
          <div className="hero-actions">
            <div className="identity-chip">
              <span className="identity-chip-label">Active identity</span>
              <strong>{user.fullName ?? user.email}</strong>
            </div>
            <button className="ghost-button" type="button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>

        <div className="hero-stats">
          <article className="metric-card">
            <span>Profile memory</span>
            <strong>Persistent</strong>
          </article>
          <article className="metric-card">
            <span>Skill graph</span>
            <strong>Structured</strong>
          </article>
          <article className="metric-card">
            <span>Goal cadence</span>
            <strong>Tracked</strong>
          </article>
        </div>
      </section>

      <section className="workspace-grid">
        <ProfileSection className="workspace-card" />
        <SkillsSection className="workspace-card" />
        <GoalsSection className="workspace-card workspace-card-wide" />
      </section>
    </main>
  );
}
