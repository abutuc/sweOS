"use client";

import { useEffect, useState } from "react";

import { api, type Preferences } from "@/lib/api";

type PreferencesSectionProps = {
  className?: string;
};

function parseTags(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatJson(value: Record<string, unknown>) {
  return JSON.stringify(value, null, 2);
}

export function PreferencesSection({ className }: PreferencesSectionProps) {
  const [preferences, setPreferences] = useState<Preferences | null>(null);
  const [privacyJson, setPrivacyJson] = useState("{}");
  const [filtersJson, setFiltersJson] = useState("{}");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    void api
      .getPreferences()
      .then((response) => {
        if (active) {
          setPreferences(response.data);
          setPrivacyJson(formatJson(response.data.privacySettings));
          setFiltersJson(formatJson(response.data.targetOpportunityFilters));
          setError(null);
          setNotice(null);
        }
      })
      .catch(() => {
        if (active) {
          setError("Preferences could not be loaded.");
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

  const updatePreferenceField = <K extends keyof Preferences>(key: K, value: Preferences[K]) => {
    setPreferences((current) => (current ? { ...current, [key]: value } : current));
  };

  const handleSave = async () => {
    if (!preferences) {
      return;
    }

    let privacySettings: Record<string, unknown>;
    let targetOpportunityFilters: Record<string, unknown>;

    try {
      privacySettings = JSON.parse(privacyJson) as Record<string, unknown>;
      targetOpportunityFilters = JSON.parse(filtersJson) as Record<string, unknown>;
    } catch {
      setError("Privacy settings and opportunity filters must be valid JSON objects.");
      return;
    }

    setIsSaving(true);
    setError(null);
    setNotice(null);

    try {
      await api.savePreferences({
        ...preferences,
        privacySettings,
        targetOpportunityFilters,
      });
      setNotice("Preferences saved.");
    } catch {
      setError("Preferences could not be saved.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <section className={className}>
      <div className="section-heading">
        <p className="section-kicker">Preferences</p>
        <h2>Tune how sweOS sources, assists, and protects your workflow.</h2>
      </div>

      <p className="section-status">
        {isLoading ? "Loading preferences..." : error ?? notice ?? "Preferences synced with API"}
      </p>

      <div className="field-grid">
        <label className="field field-wide">
          <span>Content sources</span>
          <input
            value={(preferences?.contentSources ?? []).join(", ")}
            onChange={(event) =>
              updatePreferenceField("contentSources", parseTags(event.target.value))
            }
            placeholder="Stack Overflow, Hacker News, Company blogs"
          />
        </label>
        <label className="field">
          <span>Notification cadence</span>
          <select
            value={preferences?.notificationCadence ?? "weekly"}
            onChange={(event) =>
              updatePreferenceField("notificationCadence", event.target.value)
            }
          >
            <option value="none">None</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </select>
        </label>
        <label className="field">
          <span>AI assistance level</span>
          <select
            value={preferences?.aiAssistanceLevel ?? "balanced"}
            onChange={(event) =>
              updatePreferenceField("aiAssistanceLevel", event.target.value)
            }
          >
            <option value="minimal">Minimal</option>
            <option value="balanced">Balanced</option>
            <option value="proactive">Proactive</option>
          </select>
        </label>
        <label className="field field-wide">
          <span>Privacy settings JSON</span>
          <textarea
            rows={5}
            value={privacyJson}
            onChange={(event) => setPrivacyJson(event.target.value)}
            placeholder='{"localOnly": true}'
          />
        </label>
        <label className="field field-wide">
          <span>Target opportunity filters JSON</span>
          <textarea
            rows={5}
            value={filtersJson}
            onChange={(event) => setFiltersJson(event.target.value)}
            placeholder='{"remote": true, "locations": ["Portugal"]}'
          />
        </label>
      </div>

      <div className="section-actions">
        <button
          className="primary-button"
          type="button"
          onClick={handleSave}
          disabled={isSaving || !preferences}
        >
          {isSaving ? "Saving..." : "Save preferences"}
        </button>
      </div>
    </section>
  );
}
