"use client";

type SkillsSectionProps = {
  className?: string;
};

export function SkillsSection({ className }: SkillsSectionProps) {
  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Skills</p>
        <h2>Track strengths and weak spots with explicit levels.</h2>
      </div>

      <div className="skill-stack">
        <div className="skill-pane">
          <h3>Catalog</h3>
          <p>Browse structured skills by category.</p>
        </div>
        <div className="skill-pane">
          <h3>My levels</h3>
          <p>Set self-assessed levels and keep the model current.</p>
        </div>
      </div>

      <div className="section-actions">
        <button className="primary-button" type="button">
          Save skill levels
        </button>
      </div>
    </section>
  );
}
