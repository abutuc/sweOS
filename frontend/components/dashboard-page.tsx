"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { api, type DashboardSummary } from "@/lib/api";
import { isProfileOnboardingComplete } from "@/lib/onboarding";

export function DashboardPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    void api
      .getDashboardSummary()
      .then((response) => {
        if (!active) {
          return;
        }

        if (!isProfileOnboardingComplete(response.data.profile)) {
          router.replace("/onboarding");
          return;
        }

        setSummary(response.data);
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [router]);

  if (isLoading || !summary) {
    return (
      <section className="loading-panel">
        <p className="eyebrow">Dashboard</p>
        <h1>Loading daily cockpit.</h1>
      </section>
    );
  }

  const { profile, goals, exercises, topicMastery } = summary;

  return (
    <>
      <section className="hero-panel hero-panel-app">
        <div className="hero-panel-topline">
          <div>
            <p className="eyebrow">Daily Flow</p>
            <h1>Operate from a focused dashboard, not a crowded workspace.</h1>
            <p className="hero-copy">
              Resume the next exercise, watch your weakest topics, and keep your goals moving without opening every control at once.
            </p>
          </div>
          <div className="hero-actions">
            <Link className="primary-button" href="/practice">
              Start practice
            </Link>
            <Link className="ghost-button" href="/profile">
              Review profile
            </Link>
          </div>
        </div>

        <div className="hero-stats">
          <article className="metric-card">
            <span>Primary target</span>
            <strong>{profile?.targetRole ?? "Set target role"}</strong>
          </article>
          <article className="metric-card">
            <span>Tracked goals</span>
            <strong>{goals.length}</strong>
          </article>
          <article className="metric-card">
            <span>Generated exercises</span>
            <strong>{exercises.length}</strong>
          </article>
        </div>
      </section>

      <section className="workspace-grid">
        <section className="workspace-card">
          <div className="section-heading">
            <p className="section-kicker">Focus</p>
            <h2>Current direction</h2>
          </div>
          <div className="dashboard-copy">
            <p>{profile?.summary ?? "Add a profile summary so the system can personalize your daily recommendations."}</p>
            <div className="exercise-badges">
              {(profile?.stack ?? []).slice(0, 6).map((item) => (
                <span className="exercise-badge" key={item}>
                  {item}
                </span>
              ))}
            </div>
          </div>
        </section>

        <section className="workspace-card">
          <div className="section-heading">
            <p className="section-kicker">Weak Topics</p>
            <h2>What to reinforce next</h2>
          </div>
          <div className="mastery-list">
            {topicMastery.slice(0, 3).map((item) => (
              <article className="mastery-card" key={item.topic}>
                <div className="goal-card-topline">
                  <strong>{item.topic}</strong>
                  <span>{item.averageScore.toFixed(1)}/10</span>
                </div>
                <p>{item.weakestDimension ?? "No weak dimension yet"}</p>
              </article>
            ))}
            {topicMastery.length === 0 ? <p className="empty-state">No mastery signals yet. Complete an exercise to seed your daily flow.</p> : null}
          </div>
        </section>

        <section className="workspace-card">
          <div className="section-heading">
            <p className="section-kicker">Goals</p>
            <h2>Keep momentum visible</h2>
          </div>
          <div className="mastery-list">
            {goals.slice(0, 3).map((goal) => (
              <article className="mastery-card" key={goal.id}>
                <div className="goal-card-topline">
                  <strong>{goal.title}</strong>
                  <span>{goal.horizon}</span>
                </div>
                <p>{goal.description ?? "No description yet."}</p>
              </article>
            ))}
            {goals.length === 0 ? <p className="empty-state">Add goals during onboarding or from your profile workflow.</p> : null}
          </div>
        </section>

        <section className="workspace-card">
          <div className="section-heading">
            <p className="section-kicker">Recent Practice</p>
            <h2>Generated exercise backlog</h2>
          </div>
          <div className="exercise-history">
            {exercises.slice(0, 4).map((exercise) => (
              <article className="exercise-history-item" key={exercise.id}>
                <strong>{exercise.title}</strong>
                <span>
                  {exercise.type} · {exercise.topic} · {exercise.difficulty}
                </span>
              </article>
            ))}
            {exercises.length === 0 ? <p className="empty-state">Generate your first exercise from Practice.</p> : null}
          </div>
        </section>
      </section>
    </>
  );
}
