"use client";

import { PreferencesSection } from "@/components/preferences-section";
import { useOnboardingStatus } from "@/components/use-onboarding-status";

export function SettingsPage() {
  useOnboardingStatus();

  return (
    <>
      <section className="hero-panel hero-panel-app">
        <p className="eyebrow">Settings</p>
        <h1>Adjust how sweOS assists, sources, and filters your daily workflow.</h1>
        <p className="hero-copy">
          Preferences are part of the control plane, not the main dashboard. Keep them here so the day-to-day experience stays focused.
        </p>
      </section>

      <section className="workspace-grid">
        <PreferencesSection className="workspace-card workspace-card-wide" />
      </section>
    </>
  );
}
