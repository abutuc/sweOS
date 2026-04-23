"use client";

import { LearningGymSection } from "@/components/learning-gym-section";
import { useOnboardingStatus } from "@/components/use-onboarding-status";

export function PracticePage() {
  useOnboardingStatus({ redirectIfIncomplete: true });

  return (
    <>
      <section className="hero-panel hero-panel-app">
        <p className="eyebrow">Practice</p>
        <h1>Run focused learning sessions without the profile setup noise.</h1>
        <p className="hero-copy">
          Generate exercises, submit solutions, and review feedback in a dedicated practice surface.
        </p>
      </section>

      <section className="workspace-grid">
        <LearningGymSection className="workspace-card workspace-card-wide" />
      </section>
    </>
  );
}
