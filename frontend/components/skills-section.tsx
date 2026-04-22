"use client";

import { useEffect, useState } from "react";

import { api, type SkillCatalogItem, type UserSkill } from "@/lib/api";

type SkillsSectionProps = {
  className?: string;
};

export function SkillsSection({ className }: SkillsSectionProps) {
  const [catalog, setCatalog] = useState<SkillCatalogItem[]>([]);
  const [userSkills, setUserSkills] = useState<UserSkill[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    void Promise.all([api.getSkillCatalog(), api.getUserSkills()])
      .then(([catalogResponse, userSkillsResponse]) => {
        if (active) {
          setCatalog(catalogResponse.data);
          setUserSkills(userSkillsResponse.data);
          setError(null);
        }
      })
      .catch(() => {
        if (active) {
          setError("Skills could not be loaded.");
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

  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Skills</p>
        <h2>Track strengths and weak spots with explicit levels.</h2>
      </div>

      <p className="section-status">
        {isLoading
          ? "Loading skills..."
          : error ?? `${catalog.length} skills in catalog, ${userSkills.length} tracked`}
      </p>

      <div className="skill-stack">
        <div className="skill-pane">
          <h3>Catalog</h3>
          <div className="skill-chip-grid">
            {catalog.slice(0, 8).map((skill) => (
              <span className="skill-chip" key={skill.id}>
                {skill.name}
              </span>
            ))}
          </div>
        </div>
        <div className="skill-pane">
          <h3>My levels</h3>
          <div className="skill-level-list">
            {userSkills.map((skill) => (
              <label className="skill-level-row" key={skill.skillId}>
                <span>{skill.skillName}</span>
                <select value={skill.selfAssessedLevel} onChange={() => undefined}>
                  <option value="beginner">Beginner</option>
                  <option value="elementary">Elementary</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                  <option value="expert">Expert</option>
                </select>
              </label>
            ))}
          </div>
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
