"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { AccountSection } from "@/components/account-section";
import { useAuthContext } from "@/components/auth-context";
import { PreferencesSection } from "@/components/preferences-section";
import { ProfileSection } from "@/components/profile-section";
import { SkillsSection } from "@/components/skills-section";
import { useOnboardingStatus } from "@/components/use-onboarding-status";

export function OnboardingPage() {
  const router = useRouter();
  const { user, setUser } = useAuthContext();
  const { isLoading, isComplete } = useOnboardingStatus();
  const [error, setError] = useState<string | null>(null);

  const handleContinue = () => {
    if (!isComplete) {
      setError("Add your profile direction, stack, and target role before continuing.");
      return;
    }

    router.replace("/");
  };

  return (
    <>
      <section className="hero-panel hero-panel-app">
        <p className="eyebrow">Onboarding</p>
        <h1>Set the profile shape once, then use the app from a calmer daily dashboard.</h1>
        <p className="hero-copy">
          First-time flow: identity, profile, skills, and preferences. Daily flow: dashboard and practice.
        </p>
      </section>

      <section className="workspace-grid">
        <section className="workspace-card workspace-card-wide">
          <div className="section-heading">
            <p className="section-kicker">Setup Flow</p>
            <h2>Complete the engineer context that powers recommendations.</h2>
          </div>
          <p className="section-status">
            {isLoading
              ? "Checking onboarding progress..."
              : error ??
                (isComplete
                  ? "Profile direction is complete. You can continue to the dashboard."
                  : "Complete the core profile fields before moving into the daily flow.")}
          </p>
          <div className="section-actions section-actions-left">
            <button className="primary-button" type="button" onClick={handleContinue} disabled={isLoading}>
              Continue to dashboard
            </button>
          </div>
        </section>

        <AccountSection className="workspace-card" user={user} onUserUpdated={setUser} />
        <ProfileSection className="workspace-card" />
        <SkillsSection className="workspace-card workspace-card-wide" />
        <PreferencesSection className="workspace-card workspace-card-wide" />
      </section>
    </>
  );
}
