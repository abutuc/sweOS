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
          <input defaultValue={profile?.headline ?? ""} placeholder="Backend engineer with AI curiosity" />
        </label>
        <label className="field">
          <span>Years of experience</span>
          <input defaultValue={profile?.yearsExperience ?? ""} placeholder="2.0" />
        </label>
        <label className="field field-wide">
          <span>Stack tags</span>
          <input
            defaultValue={profile?.stack.join(", ") ?? ""}
            placeholder="Python, PostgreSQL, FastAPI"
          />
        </label>
        <label className="field">
          <span>Current role</span>
          <input defaultValue={profile?.currentRole ?? ""} placeholder="Software Engineer" />
        </label>
        <label className="field">
          <span>Primary target role</span>
          <input defaultValue={profile?.targetRole ?? ""} placeholder="Backend Engineer" />
        </label>
        <label className="field field-wide">
          <span>Target roles</span>
          <input
            defaultValue={profile?.targetRoles.join(", ") ?? ""}
            placeholder="Backend Engineer, AI Engineer"
          />
        </label>
        <label className="field field-wide">
          <span>Summary</span>
          <textarea
            rows={5}
            defaultValue={profile?.summary ?? ""}
            placeholder="What should sweOS know about your direction?"
          />
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
