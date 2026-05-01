"use client";

import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useState,
} from "react";

import { api, type Profile } from "@/lib/api";

type ProfileSectionProps = {
  className?: string;
  onDirtyChange?: (dirty: boolean) => void;
  showSaveButton?: boolean;
};

export type ProfileSectionHandle = {
  save: () => Promise<boolean>;
};

export const ProfileSection = forwardRef<ProfileSectionHandle, ProfileSectionProps>(
  function ProfileSection(
    { className, onDirtyChange, showSaveButton = true },
    ref,
  ) {
    const [profile, setProfile] = useState<Profile | null>(null);
    const [isDirty, setIsDirty] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isSaving, setIsSaving] = useState(false);
    const [notice, setNotice] = useState<string | null>(null);
    const [validationError, setValidationError] = useState<string | null>(null);
    const [targetRolesText, setTargetRolesText] = useState(
      (profile?.targetRoles ?? []).join(", "),
    );

    useEffect(() => {
      setTargetRolesText((profile?.targetRoles ?? []).join(", "));
    }, [profile?.targetRoles]);

    const [learningGoalsText, setLearningGoalsText] = useState(
      (profile?.learningGoals ?? []).join(", "),
    );

    useEffect(() => {
      setLearningGoalsText((profile?.learningGoals ?? []).join(", "));
    }, [profile?.learningGoals]);

    useEffect(() => {
      onDirtyChange?.(isDirty);
    }, [isDirty, onDirtyChange]);

    useEffect(() => {
      let active = true;

      void api
        .getProfile()
        .then((response) => {
          if (active) {
            setProfile(response.data);
            setError(null);
            setNotice(null);
            setIsDirty(false);
          }
        })
        .catch(() => {
          if (active) {
            setError("Profile could not be loaded.");
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

    const updateProfileField = <K extends keyof Profile>(
      key: K,
      value: Profile[K],
    ) => {
      setProfile((current) => (current ? { ...current, [key]: value } : current));
      setIsDirty(true);
    };

    const parseTags = (value: string) =>
      value
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);

    const handleSave = async () => {
      if (!profile) {
        return false;
      }

      const normalizedProfile = {
        ...profile,
        targetRoles: parseTags(targetRolesText),
        learningGoals: parseTags(learningGoalsText),
      };

      const minSalary = profile.salaryExpectationMin;
      const maxSalary = profile.salaryExpectationMax;

      if (
        minSalary !== null &&
        maxSalary !== null &&
        Number(minSalary) > Number(maxSalary)
      ) {
        setValidationError(
          "Minimum salary must be less than or equal to maximum salary.",
        );
        return false;
      }

      if (profile.yearsExperience && Number(profile.yearsExperience) < 0) {
        setValidationError("Years of experience must be zero or higher.");
        return false;
      }

      setIsSaving(true);
      setError(null);
      setNotice(null);
      setValidationError(null);

      try {
        await api.saveProfile({
          ...normalizedProfile,
          headline: normalizedProfile.headline || null,
          bio: normalizedProfile.bio || null,
          yearsExperience: normalizedProfile.yearsExperience || null,
          currentRole: normalizedProfile.currentRole || null,
          targetRole: normalizedProfile.targetRole || null,
          targetSeniority: normalizedProfile.targetSeniority || null,
          summary: normalizedProfile.summary || null,
        });
        setProfile(normalizedProfile);
        setTargetRolesText(normalizedProfile.targetRoles.join(", "));
        setLearningGoalsText(normalizedProfile.learningGoals.join(", "));
        setNotice("Profile saved.");
        setIsDirty(false);
        return true;
      } catch {
        setError("Profile could not be saved.");
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
          <p className="section-kicker">Profile</p>
          <h2>Shape the engineer you want the system to optimize for.</h2>
        </div>

        <p className="section-status">
          {isLoading
            ? "Loading profile..."
            : (validationError ?? error ?? notice ?? "Profile synced with API")}
        </p>

        <div className="field-grid">
          <label className="field">
            <span>Headline</span>
            <input
              value={profile?.headline ?? ""}
              onChange={(event) =>
                updateProfileField("headline", event.target.value)
              }
              placeholder="Backend engineer with AI curiosity"
            />
          </label>
          <label className="field field-wide">
            <span>Bio</span>
            <textarea
              rows={3}
              value={profile?.bio ?? ""}
              onChange={(event) => updateProfileField("bio", event.target.value)}
              placeholder="Short background and context the system should remember."
            />
          </label>
          <label className="field">
            <span>Years of experience</span>
            <input
              value={profile?.yearsExperience ?? ""}
              onChange={(event) =>
                updateProfileField("yearsExperience", event.target.value)
              }
              placeholder="2.0"
            />
          </label>
          <label className="field field-wide">
            <span>Stack tags</span>
            <input
              value={(profile?.stack ?? []).join(", ")}
              onChange={(event) =>
                updateProfileField("stack", parseTags(event.target.value))
              }
              placeholder="Python, PostgreSQL, FastAPI"
            />
          </label>
          <label className="field">
            <span>Current role</span>
            <input
              value={profile?.currentRole ?? ""}
              onChange={(event) =>
                updateProfileField("currentRole", event.target.value)
              }
              placeholder="Software Engineer"
            />
          </label>
          <label className="field">
            <span>Primary target role</span>
            <input
              value={profile?.targetRole ?? ""}
              onChange={(event) =>
                updateProfileField("targetRole", event.target.value)
              }
              placeholder="Backend Engineer"
            />
          </label>
          <label className="field field-wide">
            <span>Target roles</span>
            <input
              value={targetRolesText}
              onChange={(event) => {
                setTargetRolesText(event.target.value);
                setIsDirty(true);
              }}
              onBlur={() =>
                updateProfileField("targetRoles", parseTags(targetRolesText))
              }
              placeholder="Backend Engineer, AI Engineer"
            />
          </label>
          <label className="field">
            <span>Target seniority</span>
            <input
              value={profile?.targetSeniority ?? ""}
              onChange={(event) =>
                updateProfileField("targetSeniority", event.target.value)
              }
              placeholder="mid"
            />
          </label>
          <label className="field field-wide">
            <span>Preferred industries</span>
            <input
              value={(profile?.preferredIndustries ?? []).join(", ")}
              onChange={(event) =>
                updateProfileField(
                  "preferredIndustries",
                  parseTags(event.target.value),
                )
              }
              placeholder="AI, Developer tools, Fintech"
            />
          </label>
          <label className="field field-wide">
            <span>Preferred locations</span>
            <input
              value={(profile?.preferredLocations ?? []).join(", ")}
              onChange={(event) =>
                updateProfileField(
                  "preferredLocations",
                  parseTags(event.target.value),
                )
              }
              placeholder="Portugal, Remote EU"
            />
          </label>
          <label className="field field-wide">
            <span>Preferred work modes</span>
            <input
              value={(profile?.preferredWorkModes ?? []).join(", ")}
              onChange={(event) =>
                updateProfileField(
                  "preferredWorkModes",
                  parseTags(event.target.value),
                )
              }
              placeholder="remote, hybrid"
            />
          </label>
          <label className="field field-wide">
            <span>Learning goals</span>
            <input
              value={learningGoalsText}
              onChange={(event) => {
                setLearningGoalsText(event.target.value);
                setIsDirty(true);
              }}
              onBlur={() =>
                updateProfileField("learningGoals", parseTags(learningGoalsText))
              }
              placeholder="System design depth, AI engineering portfolio"
            />
          </label>
          <label className="field field-wide">
            <span>Summary</span>
            <textarea
              rows={5}
              value={profile?.summary ?? ""}
              onChange={(event) =>
                updateProfileField("summary", event.target.value)
              }
              placeholder="What should sweOS know about your direction?"
            />
          </label>
          <label className="field">
            <span>Salary expectation min</span>
            <input
              value={profile?.salaryExpectationMin ?? ""}
              onChange={(event) =>
                updateProfileField(
                  "salaryExpectationMin",
                  event.target.value ? Number(event.target.value) : null,
                )
              }
              placeholder="40000"
              type="number"
            />
          </label>
          <label className="field">
            <span>Salary expectation max</span>
            <input
              value={profile?.salaryExpectationMax ?? ""}
              onChange={(event) =>
                updateProfileField(
                  "salaryExpectationMax",
                  event.target.value ? Number(event.target.value) : null,
                )
              }
              placeholder="55000"
              type="number"
            />
          </label>
        </div>

        {showSaveButton ? (
          <div className="section-actions">
            <button
              className="primary-button"
              type="button"
              onClick={handleSave}
              disabled={isSaving || !profile}
            >
              {isSaving ? "Saving..." : "Save profile"}
            </button>
          </div>
        ) : null}
      </section>
    );
  },
);
