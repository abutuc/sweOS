"use client";

import { useEffect, useState } from "react";

import { api, type Profile } from "@/lib/api";

type ProfileSectionProps = {
  className?: string;
};

export function ProfileSection({ className }: ProfileSectionProps) {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let active = true;

    void api
      .getProfile()
      .then((response) => {
        if (active) {
          setProfile(response.data);
          setError(null);
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

  const updateProfileField = <K extends keyof Profile>(key: K, value: Profile[K]) => {
    setProfile((current) => (current ? { ...current, [key]: value } : current));
  };

  const handleSave = async () => {
    if (!profile) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await api.saveProfile({
        ...profile,
        headline: profile.headline || null,
        bio: profile.bio || null,
        yearsExperience: profile.yearsExperience || null,
        currentRole: profile.currentRole || null,
        targetRole: profile.targetRole || null,
        targetSeniority: profile.targetSeniority || null,
        summary: profile.summary || null,
      });
    } catch {
      setError("Profile could not be saved.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Profile</p>
        <h2>Shape the engineer you want the system to optimize for.</h2>
      </div>

      <p className="section-status">
        {isLoading ? "Loading profile..." : error ?? "Profile synced with API"}
      </p>

      <div className="field-grid">
        <label className="field">
          <span>Headline</span>
          <input
            value={profile?.headline ?? ""}
            onChange={(event) => updateProfileField("headline", event.target.value)}
            placeholder="Backend engineer with AI curiosity"
          />
        </label>
        <label className="field">
          <span>Years of experience</span>
          <input
            value={profile?.yearsExperience ?? ""}
            onChange={(event) => updateProfileField("yearsExperience", event.target.value)}
            placeholder="2.0"
          />
        </label>
        <label className="field field-wide">
          <span>Stack tags</span>
          <input
            value={profile?.stack.join(", ") ?? ""}
            onChange={(event) =>
              updateProfileField(
                "stack",
                event.target.value
                  .split(",")
                  .map((item) => item.trim())
                  .filter(Boolean),
              )
            }
            placeholder="Python, PostgreSQL, FastAPI"
          />
        </label>
        <label className="field">
          <span>Current role</span>
          <input
            value={profile?.currentRole ?? ""}
            onChange={(event) => updateProfileField("currentRole", event.target.value)}
            placeholder="Software Engineer"
          />
        </label>
        <label className="field">
          <span>Primary target role</span>
          <input
            value={profile?.targetRole ?? ""}
            onChange={(event) => updateProfileField("targetRole", event.target.value)}
            placeholder="Backend Engineer"
          />
        </label>
        <label className="field field-wide">
          <span>Target roles</span>
          <input
            value={profile?.targetRoles.join(", ") ?? ""}
            onChange={(event) =>
              updateProfileField(
                "targetRoles",
                event.target.value
                  .split(",")
                  .map((item) => item.trim())
                  .filter(Boolean),
              )
            }
            placeholder="Backend Engineer, AI Engineer"
          />
        </label>
        <label className="field field-wide">
          <span>Summary</span>
          <textarea
            rows={5}
            value={profile?.summary ?? ""}
            onChange={(event) => updateProfileField("summary", event.target.value)}
            placeholder="What should sweOS know about your direction?"
          />
        </label>
      </div>

      <div className="section-actions">
        <button className="primary-button" type="button" onClick={handleSave} disabled={isSaving || !profile}>
          {isSaving ? "Saving..." : "Save profile"}
        </button>
      </div>
    </section>
  );
}
