"use client";

import { useState } from "react";

import { api, type AuthUser } from "@/lib/api";

type AccountSectionProps = {
  className?: string;
  user: AuthUser;
  onUserUpdated: (user: AuthUser) => void;
};

export function AccountSection({ className, user, onUserUpdated }: AccountSectionProps) {
  const [fullName, setFullName] = useState(user.fullName ?? "");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setNotice(null);

    try {
      const response = await api.updateMe({
        fullName: fullName.trim().length > 0 ? fullName.trim() : null,
      });
      onUserUpdated(response.data);
      setFullName(response.data.fullName ?? "");
      setNotice("Identity updated.");
    } catch {
      setError("Identity could not be updated.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Identity</p>
        <h2>Keep your account details aligned with your engineering profile.</h2>
      </div>

      <p className="section-status">{error ?? notice ?? "Identity synced with API"}</p>

      <div className="field-grid">
        <label className="field">
          <span>Email</span>
          <input value={user.email} readOnly />
        </label>
        <label className="field">
          <span>Full name</span>
          <input
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            placeholder="Andre Butuc"
          />
        </label>
      </div>

      <div className="section-actions">
        <button className="primary-button" type="button" onClick={handleSave} disabled={isSaving}>
          {isSaving ? "Saving..." : "Save identity"}
        </button>
      </div>
    </section>
  );
}
