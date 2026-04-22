"use client";

import { useEffect, useState } from "react";

import { api, type Goal } from "@/lib/api";

type GoalsSectionProps = {
  className?: string;
};

export function GoalsSection({ className }: GoalsSectionProps) {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [draft, setDraft] = useState({
    title: "",
    targetDate: "",
    priority: "2",
    status: "active",
    description: "",
  });

  useEffect(() => {
    let active = true;

    void api
      .getGoals()
      .then((response) => {
        if (active) {
          setGoals(response.data);
          setError(null);
        }
      })
      .catch(() => {
        if (active) {
          setError("Goals could not be loaded.");
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

  const handleCreateGoal = async () => {
    setIsSaving(true);
    setError(null);

    try {
      const response = await api.createGoal({
        title: draft.title,
        description: draft.description || null,
        targetDate: draft.targetDate || null,
        priority: Number(draft.priority),
        status: draft.status,
      });

      setGoals((current) => [response.data, ...current]);
      setDraft({
        title: "",
        targetDate: "",
        priority: "2",
        status: "active",
        description: "",
      });
    } catch {
      setError("Goal could not be created.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Goals</p>
        <h2>Convert intention into concrete milestones.</h2>
      </div>

      <p className="section-status">
        {isLoading ? "Loading goals..." : error ?? `${goals.length} goal${goals.length === 1 ? "" : "s"} loaded`}
      </p>

      <div className="field-grid">
        <label className="field">
          <span>Goal title</span>
          <input
            value={draft.title}
            onChange={(event) => setDraft((current) => ({ ...current, title: event.target.value }))}
            placeholder="Land backend engineer role"
          />
        </label>
        <label className="field">
          <span>Target date</span>
          <input
            value={draft.targetDate}
            onChange={(event) => setDraft((current) => ({ ...current, targetDate: event.target.value }))}
            placeholder="2026-08-01"
          />
        </label>
        <label className="field">
          <span>Priority</span>
          <select
            value={draft.priority}
            onChange={(event) => setDraft((current) => ({ ...current, priority: event.target.value }))}
          >
            <option value="1">1 - Critical</option>
            <option value="2">2 - High</option>
            <option value="3">3 - Medium</option>
            <option value="4">4 - Low</option>
            <option value="5">5 - Parking lot</option>
          </select>
        </label>
        <label className="field">
          <span>Status</span>
          <select
            value={draft.status}
            onChange={(event) => setDraft((current) => ({ ...current, status: event.target.value }))}
          >
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="done">Done</option>
          </select>
        </label>
        <label className="field field-wide">
          <span>Description</span>
          <textarea
            rows={4}
            value={draft.description}
            onChange={(event) => setDraft((current) => ({ ...current, description: event.target.value }))}
            placeholder="Why this goal matters right now."
          />
        </label>
      </div>

      <div className="section-actions">
        <button
          className="primary-button"
          type="button"
          onClick={handleCreateGoal}
          disabled={isSaving || draft.title.trim().length === 0}
        >
          {isSaving ? "Adding..." : "Add goal"}
        </button>
      </div>

      <div className="goal-list">
        {goals.map((goal) => (
          <article className="goal-card" key={goal.id}>
            <div className="goal-card-topline">
              <strong>{goal.title}</strong>
              <span>Priority {goal.priority}</span>
            </div>
            <p>{goal.description ?? "No description yet."}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
