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
  const [notice, setNotice] = useState<string | null>(null);
  const [editingGoalId, setEditingGoalId] = useState<string | null>(null);
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
          setNotice(null);
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
    setNotice(null);

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
      setNotice("Goal added.");
    } catch {
      setError("Goal could not be created.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdateGoal = async (goalId: string) => {
    const goal = goals.find((item) => item.id === goalId);
    if (!goal) {
      return;
    }

    setIsSaving(true);
    setError(null);
    setNotice(null);

    try {
      const response = await api.updateGoal(goalId, {
        title: goal.title,
        description: goal.description,
        targetDate: goal.targetDate,
        priority: goal.priority,
        status: goal.status,
      });
      setGoals((current) => current.map((item) => (item.id === goalId ? response.data : item)));
      setEditingGoalId(null);
      setNotice("Goal updated.");
    } catch {
      setError("Goal could not be updated.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteGoal = async (goalId: string) => {
    setIsSaving(true);
    setError(null);
    setNotice(null);

    try {
      await api.deleteGoal(goalId);
      setGoals((current) => current.filter((goal) => goal.id !== goalId));
      setEditingGoalId((current) => (current === goalId ? null : current));
      setNotice("Goal removed.");
    } catch {
      setError("Goal could not be deleted.");
    } finally {
      setIsSaving(false);
    }
  };

  const updateGoalField = <K extends keyof Goal>(goalId: string, key: K, value: Goal[K]) => {
    setGoals((current) =>
      current.map((goal) => (goal.id === goalId ? { ...goal, [key]: value } : goal)),
    );
  };

  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Goals</p>
        <h2>Convert intention into concrete milestones.</h2>
      </div>

      <p className="section-status">
        {isLoading
          ? "Loading goals..."
          : error ?? notice ?? `${goals.length} goal${goals.length === 1 ? "" : "s"} loaded`}
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
              <span>
                {goal.status} · Priority {goal.priority}
              </span>
            </div>
            {editingGoalId === goal.id ? (
              <div className="goal-editor">
                <label className="field">
                  <span>Title</span>
                  <input
                    value={goal.title}
                    onChange={(event) => updateGoalField(goal.id, "title", event.target.value)}
                  />
                </label>
                <label className="field">
                  <span>Target date</span>
                  <input
                    value={goal.targetDate ?? ""}
                    onChange={(event) => updateGoalField(goal.id, "targetDate", event.target.value || null)}
                  />
                </label>
                <label className="field">
                  <span>Priority</span>
                  <select
                    value={String(goal.priority)}
                    onChange={(event) =>
                      updateGoalField(goal.id, "priority", Number(event.target.value))
                    }
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
                    value={goal.status}
                    onChange={(event) => updateGoalField(goal.id, "status", event.target.value)}
                  >
                    <option value="active">Active</option>
                    <option value="paused">Paused</option>
                    <option value="done">Done</option>
                  </select>
                </label>
                <label className="field field-wide">
                  <span>Description</span>
                  <textarea
                    rows={3}
                    value={goal.description ?? ""}
                    onChange={(event) =>
                      updateGoalField(goal.id, "description", event.target.value || null)
                    }
                  />
                </label>
                <div className="goal-card-actions">
                  <button
                    className="ghost-button"
                    type="button"
                    onClick={() => setEditingGoalId(null)}
                    disabled={isSaving}
                  >
                    Cancel
                  </button>
                  <button
                    className="ghost-button ghost-button-danger"
                    type="button"
                    onClick={() => handleDeleteGoal(goal.id)}
                    disabled={isSaving}
                  >
                    Delete
                  </button>
                  <button
                    className="primary-button"
                    type="button"
                    onClick={() => handleUpdateGoal(goal.id)}
                    disabled={isSaving || goal.title.trim().length === 0}
                  >
                    Save changes
                  </button>
                </div>
              </div>
            ) : (
              <>
                <p>{goal.description ?? "No description yet."}</p>
                <div className="goal-card-actions">
                  <button
                    className="ghost-button"
                    type="button"
                    onClick={() => setEditingGoalId(goal.id)}
                  >
                    Edit goal
                  </button>
                </div>
              </>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
