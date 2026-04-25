"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { api, type AnalyticsDashboard, type DashboardSummary } from "@/lib/api";
import { isProfileOnboardingComplete } from "@/lib/onboarding";

export function DashboardPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    void Promise.all([api.getDashboardSummary(), api.getAnalyticsDashboard()])
      .then(([summaryResponse, analyticsResponse]) => {
        if (!active) {
          return;
        }

        if (!isProfileOnboardingComplete(summaryResponse.data.profile)) {
          router.replace("/onboarding");
          return;
        }

        setSummary(summaryResponse.data);
        setAnalytics(analyticsResponse.data);
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

  if (isLoading || !summary || !analytics) {
    return (
      <section className="loading-panel loading-panel-skeleton">
        <p className="eyebrow">Dashboard</p>
        <h1>Loading daily cockpit.</h1>
        <div className="skeleton-grid" aria-hidden="true">
          <span className="skeleton-line skeleton-line-wide" />
          <span className="skeleton-line" />
          <span className="skeleton-card" />
          <span className="skeleton-card" />
        </div>
      </section>
    );
  }

  const { profile, goals, exercises } = summary;
  const averageScore = analytics.summary.averageScore;

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
            <span>Completed exercises</span>
            <strong>{analytics.summary.totalExercisesCompleted}</strong>
          </article>
          <article className="metric-card">
            <span>Average score</span>
            <strong>{averageScore === null ? "n/a" : `${averageScore.toFixed(1)}/10`}</strong>
          </article>
          <article className="metric-card">
            <span>Practice streak</span>
            <strong>
              {analytics.summary.streakDays} day{analytics.summary.streakDays === 1 ? "" : "s"}
            </strong>
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
            <p className="section-kicker">Weak Areas</p>
            <h2>What to reinforce next</h2>
          </div>
          <div className="mastery-list">
            {analytics.weakTopics.slice(0, 3).map((item) => (
              <article className="mastery-card" key={item.topic}>
                <div className="goal-card-topline">
                  <strong>{item.topic}</strong>
                  <span>{item.masteryScore.toFixed(1)}/10</span>
                </div>
                <p>
                  {item.attemptsCount} attempt{item.attemptsCount === 1 ? "" : "s"} ·{" "}
                  {item.weakestDimension ?? "no weak dimension yet"}
                </p>
              </article>
            ))}
            {analytics.weakTopics.length === 0 ? <p className="empty-state">No mastery signals yet. Complete an exercise to seed your analytics.</p> : null}
          </div>
        </section>

        <section className="workspace-card">
          <div className="section-heading">
            <p className="section-kicker">Strong Topics</p>
            <h2>Where quality is trending well</h2>
          </div>
          <div className="mastery-list">
            {analytics.strongTopics.slice(0, 3).map((item) => (
              <article className="mastery-card" key={item.topic}>
                <div className="goal-card-topline">
                  <strong>{item.topic}</strong>
                  <span>{item.masteryScore.toFixed(1)}/10</span>
                </div>
                <p>
                  {item.attemptsCount} attempt{item.attemptsCount === 1 ? "" : "s"} recorded
                </p>
              </article>
            ))}
            {analytics.strongTopics.length === 0 ? <p className="empty-state">Strong topics appear after evaluated exercises.</p> : null}
          </div>
        </section>

        <section className="workspace-card">
          <div className="section-heading">
            <p className="section-kicker">Timeline</p>
            <h2>Recent evaluated activity</h2>
          </div>
          <div className="exercise-history">
            {analytics.recentActivity.slice(0, 4).map((item) => (
              <article className="exercise-history-item" key={item.entityId}>
                <strong>{item.title}</strong>
                <span>{new Date(item.createdAt).toLocaleDateString()}</span>
              </article>
            ))}
            {analytics.recentActivity.length === 0 ? <p className="empty-state">Evaluated submissions will appear here.</p> : null}
          </div>
        </section>

        <section className="workspace-card workspace-card-wide">
          <div className="section-heading">
            <p className="section-kicker">Goals & Backlog</p>
            <h2>Keep direction and exercise volume visible</h2>
          </div>
          <div className="mastery-list">
            <article className="mastery-card">
              <div className="goal-card-topline">
                <strong>Tracked goals</strong>
                <span>{goals.length}</span>
              </div>
              <p>{goals[0]?.title ?? "Add goals during onboarding or from your profile workflow."}</p>
            </article>
            <article className="mastery-card">
              <div className="goal-card-topline">
                <strong>Generated exercise backlog</strong>
                <span>{exercises.length}</span>
              </div>
              <p>{exercises[0]?.title ?? "Generate your first exercise from Practice."}</p>
            </article>
          </div>
        </section>
      </section>
    </>
  );
}
