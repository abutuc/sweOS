"use client";

type GoalsSectionProps = {
  className?: string;
};

export function GoalsSection({ className }: GoalsSectionProps) {
  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Goals</p>
        <h2>Convert intention into concrete milestones.</h2>
      </div>

      <div className="field-grid">
        <label className="field">
          <span>Goal title</span>
          <input placeholder="Land backend engineer role" />
        </label>
        <label className="field">
          <span>Target date</span>
          <input placeholder="2026-08-01" />
        </label>
        <label className="field">
          <span>Priority</span>
          <select defaultValue="2">
            <option value="1">1 - Critical</option>
            <option value="2">2 - High</option>
            <option value="3">3 - Medium</option>
            <option value="4">4 - Low</option>
            <option value="5">5 - Parking lot</option>
          </select>
        </label>
        <label className="field">
          <span>Status</span>
          <select defaultValue="active">
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="done">Done</option>
          </select>
        </label>
        <label className="field field-wide">
          <span>Description</span>
          <textarea rows={4} placeholder="Why this goal matters right now." />
        </label>
      </div>

      <div className="section-actions">
        <button className="primary-button" type="button">
          Add goal
        </button>
      </div>
    </section>
  );
}
