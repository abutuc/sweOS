"use client";

import {
  forwardRef,
  useDeferredValue,
  useEffect,
  useImperativeHandle,
  useState,
} from "react";

import { api, type SkillCatalogItem, type UserSkill } from "@/lib/api";

type SkillsSectionProps = {
  className?: string;
  onDirtyChange?: (dirty: boolean) => void;
  showSaveButton?: boolean;
};
const MAX_VISIBLE_CATALOG_SKILLS = 80;

export type SkillsSectionHandle = {
  save: () => Promise<boolean>;
};

export const SkillsSection = forwardRef<SkillsSectionHandle, SkillsSectionProps>(
  function SkillsSection(
    { className, onDirtyChange, showSaveButton = true },
    ref,
  ) {
  const [catalog, setCatalog] = useState<SkillCatalogItem[]>([]);
  const [userSkills, setUserSkills] = useState<UserSkill[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const deferredSearch = useDeferredValue(search);
  const deferredCategory = useDeferredValue(category);

  const skillLevelOptions = [
    { value: "beginner", label: "Beginner", shortLabel: "B" },
    { value: "elementary", label: "Elementary", shortLabel: "E" },
    { value: "intermediate", label: "Intermediate", shortLabel: "I" },
    { value: "advanced", label: "Advanced", shortLabel: "A" },
    { value: "expert", label: "Expert", shortLabel: "X" },
  ] as const;

  useEffect(() => {
    let active = true;

    void Promise.all([api.getSkillCatalog(), api.getUserSkills()])
      .then(([catalogResponse, userSkillsResponse]) => {
        if (active) {
          setCatalog(catalogResponse.data);
          setUserSkills(userSkillsResponse.data);
          setError(null);
          setNotice(null);
          setIsDirty(false);
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

  useEffect(() => {
    onDirtyChange?.(isDirty);
  }, [isDirty, onDirtyChange]);

  const trackedSkillIds = new Set(userSkills.map((skill) => skill.skillId));
  const categories = [
    "all",
    ...new Set(catalog.map((skill) => skill.category)),
  ];
  const matchingCatalog = catalog.filter((skill) => {
    const normalizedSearch = deferredSearch.trim().toLowerCase();
    const matchesCategory =
      deferredCategory === "all" || skill.category === deferredCategory;
    const matchesSearch =
      normalizedSearch.length === 0 ||
      skill.name.toLowerCase().includes(normalizedSearch) ||
      skill.slug.toLowerCase().includes(normalizedSearch);

    return matchesCategory && matchesSearch;
  });
  const visibleCatalog = matchingCatalog.slice(0, MAX_VISIBLE_CATALOG_SKILLS);

  const updateSkillLevel = (skillId: string, level: string) => {
    setUserSkills((current) =>
      current.map((skill) =>
        skill.skillId === skillId
          ? { ...skill, selfAssessedLevel: level }
          : skill,
      ),
    );
    setIsDirty(true);
  };

  const addSkillToTrackedList = (skill: SkillCatalogItem) => {
    if (trackedSkillIds.has(skill.id)) {
      return;
    }

    setUserSkills((current) => [
      ...current,
      {
        skillId: skill.id,
        skillSlug: skill.slug,
        skillName: skill.name,
        category: skill.category,
        selfAssessedLevel: "beginner",
        measuredLevel: null,
        confidenceScore: null,
        evidenceCount: 0,
        lastEvaluatedAt: null,
      },
    ]);
    setIsDirty(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setNotice(null);

    try {
      await api.saveUserSkills({
        skills: userSkills.map((skill) => ({
          skillId: skill.skillId,
          selfAssessedLevel: skill.selfAssessedLevel,
        })),
      });
      setNotice("Skill levels saved.");
      setIsDirty(false);
      return true;
    } catch {
      setError("Skill levels could not be saved.");
      return false;
    } finally {
      setIsSaving(false);
    }
  };

  useImperativeHandle(ref, () => ({
    save: handleSave,
  }));

  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Skills</p>
        <h2>Track strengths and weak spots with explicit levels.</h2>
      </div>

      <p className="section-status">
        {isLoading
          ? "Loading skills..."
          : (error ??
            notice ??
            `${catalog.length} skills in catalog, ${userSkills.length} tracked`)}
      </p>

      <div className="skill-stack">
        <div className="skill-pane">
          <h3>Catalog</h3>
          <div className="skill-filter-row">
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search skills"
            />
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
            >
              {categories.map((item) => (
                <option key={item} value={item}>
                  {item === "all" ? "All categories" : item}
                </option>
              ))}
            </select>
          </div>
          <div className="skill-chip-grid">
            {visibleCatalog.map((skill) => (
              <button
                className={`skill-chip ${trackedSkillIds.has(skill.id) ? "skill-chip-active" : ""}`}
                key={skill.id}
                type="button"
                onClick={() => addSkillToTrackedList(skill)}
                disabled={trackedSkillIds.has(skill.id)}
              >
                {skill.name}
              </button>
            ))}
          </div>
          {visibleCatalog.length === 0 ? (
            <p className="empty-state">No catalog skills match this filter.</p>
          ) : null}
          {matchingCatalog.length > visibleCatalog.length ? (
            <p className="empty-state">
              Showing first {visibleCatalog.length} matches. Refine the search
              to narrow the catalog.
            </p>
          ) : null}
        </div>
        <div className="skill-pane">
          <h3>My levels</h3>
          <div className="skill-level-list">
            {userSkills.map((skill) => (
              <label className="skill-level-row" key={skill.skillId}>
                <span>{skill.skillName}</span>
                <div
                  className="skill-level-picker"
                  role="radiogroup"
                  aria-label={`Skill level for ${skill.skillName}`}
                >
                  {skillLevelOptions.map((option) => {
                    const isSelected = skill.selfAssessedLevel === option.value;

                    return (
                      <button
                        key={option.value}
                        type="button"
                        className={`skill-level-option ${isSelected ? "selected" : ""}`}
                        role="radio"
                        aria-checked={isSelected}
                        title={option.label}
                        onClick={() =>
                          updateSkillLevel(skill.skillId, option.value)
                        }
                      >
                        <span className="skill-level-short">
                          {option.shortLabel}
                        </span>
                        <span className="skill-level-full">{option.label}</span>
                      </button>
                    );
                  })}
                </div>
              </label>
            ))}
          </div>
          {userSkills.length === 0 ? (
            <p className="empty-state">
              Add skills from the catalog to start tracking your level.
            </p>
          ) : null}
        </div>
      </div>

      {showSaveButton ? (
        <div className="section-actions">
          <button
            className="primary-button"
            type="button"
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving ? "Saving..." : "Save skill levels"}
          </button>
        </div>
      ) : null}
    </section>
  );
});
