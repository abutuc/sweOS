"use client";

type ProfileSectionProps = {
  className?: string;
};

export function ProfileSection({ className }: ProfileSectionProps) {
  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Profile</p>
        <h2>Shape the engineer you want the system to optimize for.</h2>
      </div>

      <div className="field-grid">
        <label className="field">
          <span>Headline</span>
          <input placeholder="Backend engineer with AI curiosity" />
        </label>
        <label className="field">
          <span>Years of experience</span>
          <input placeholder="2.0" />
        </label>
        <label className="field field-wide">
          <span>Stack tags</span>
          <input placeholder="Python, PostgreSQL, FastAPI" />
        </label>
        <label className="field">
          <span>Current role</span>
          <input placeholder="Software Engineer" />
        </label>
        <label className="field">
          <span>Primary target role</span>
          <input placeholder="Backend Engineer" />
        </label>
        <label className="field field-wide">
          <span>Target roles</span>
          <input placeholder="Backend Engineer, AI Engineer" />
        </label>
        <label className="field field-wide">
          <span>Summary</span>
          <textarea rows={5} placeholder="What should sweOS know about your direction?" />
        </label>
      </div>

      <div className="section-actions">
        <button className="primary-button" type="button">
          Save profile
        </button>
      </div>
    </section>
  );
}
