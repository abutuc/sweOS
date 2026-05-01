"use client";

import { forwardRef, useEffect, useImperativeHandle, useState } from "react";

import { api, type AuthUser } from "@/lib/api";

type AccountSectionProps = {
  className?: string;
  user: AuthUser;
  onUserUpdated: (user: AuthUser) => void;
  onDirtyChange?: (dirty: boolean) => void;
  showSaveButton?: boolean;
};

export type AccountSectionHandle = {
  save: () => Promise<boolean>;
};

export const AccountSection = forwardRef<AccountSectionHandle, AccountSectionProps>(
  function AccountSection(
    { className, user, onUserUpdated, onDirtyChange, showSaveButton = true },
    ref,
  ) {
    const [fullName, setFullName] = useState(user.fullName ?? "");
    const [isDirty, setIsDirty] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [notice, setNotice] = useState<string | null>(null);

    useEffect(() => {
      setFullName(user.fullName ?? "");
      setIsDirty(false);
    }, [user.fullName]);

    useEffect(() => {
      onDirtyChange?.(isDirty);
    }, [isDirty, onDirtyChange]);

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
        setIsDirty(false);
        return true;
      } catch {
        setError("Identity could not be updated.");
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
              onChange={(event) => {
                setFullName(event.target.value);
                setIsDirty(true);
              }}
              placeholder="Andre Butuc"
            />
          </label>
        </div>

        {showSaveButton ? (
          <div className="section-actions">
            <button className="primary-button" type="button" onClick={handleSave} disabled={isSaving}>
              {isSaving ? "Saving..." : "Save identity"}
            </button>
          </div>
        ) : null}
      </section>
    );
  },
);
