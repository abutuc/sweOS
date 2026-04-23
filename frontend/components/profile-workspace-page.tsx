"use client";

import { AccountSection } from "@/components/account-section";
import { ProfileSection } from "@/components/profile-section";
import { SkillsSection } from "@/components/skills-section";
import { useAuthContext } from "@/components/auth-context";
import { useOnboardingStatus } from "@/components/use-onboarding-status";

export function ProfileWorkspacePage() {
  const { user, setUser } = useAuthContext();

  useOnboardingStatus();

  return (
    <>
      <section className="hero-panel hero-panel-app">
        <p className="eyebrow">Profile Workspace</p>
        <h1>Manage your identity, profile shape, and skill graph away from the daily cockpit.</h1>
        <p className="hero-copy">
          This is the slower-moving setup layer. Use it to keep the system’s understanding of you accurate.
        </p>
      </section>

      <section className="workspace-grid">
        <AccountSection className="workspace-card" user={user} onUserUpdated={setUser} />
        <ProfileSection className="workspace-card" />
        <SkillsSection className="workspace-card workspace-card-wide" />
      </section>
    </>
  );
}
