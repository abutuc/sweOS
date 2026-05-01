"use client";

import { useState } from "react";

import { AccountSection } from "@/components/account-section";
import { ProfileSection } from "@/components/profile-section";
import { SkillsSection } from "@/components/skills-section";
import { useAuthContext } from "@/components/auth-context";
import { useOnboardingStatus } from "@/components/use-onboarding-status";

const PROFILE_STEPS = [
  {
    id: "identity",
    label: "Identity",
    kicker: "Account",
    description: "Keep your account details aligned with the engineer profile.",
  },
  {
    id: "profile",
    label: "Profile",
    kicker: "Direction",
    description: "Describe the work, seniority, and goals you want the system to optimize for.",
  },
  {
    id: "skills",
    label: "Skills",
    kicker: "Signals",
    description: "Track the skill graph that powers recommendations and practice.",
  },
] as const;

export function ProfileWorkspacePage() {
  const { user, setUser } = useAuthContext();
  const [activeStep, setActiveStep] = useState(0);

  useOnboardingStatus();

  const currentStep = PROFILE_STEPS[activeStep];

  return (
    <>
      <section className="hero-panel hero-panel-app">
        <p className="eyebrow">Profile Workspace</p>
        <h1>Manage your identity, profile shape, and skill graph away from the daily cockpit.</h1>
        <p className="hero-copy">
          This is the slower-moving setup layer. Use it to keep the system’s understanding of you accurate.
        </p>
      </section>

      <section className="workspace-card workspace-card-wide profile-wizard-card">
        <div className="section-heading">
          <p className="section-kicker">Profile Wizard</p>
          <h2>Move through identity, direction, and skills one step at a time.</h2>
        </div>

        <p className="section-status">
          Step {activeStep + 1} of {PROFILE_STEPS.length}: {currentStep.description}
        </p>

        <div className="wizard-stepper" role="tablist" aria-label="Profile sections">
          {PROFILE_STEPS.map((step, index) => {
            const isActive = index === activeStep;

            return (
              <button
                key={step.id}
                type="button"
                id={`profile-step-tab-${step.id}`}
                className={`wizard-step ${isActive ? "wizard-step-active" : ""}`}
                role="tab"
                aria-selected={isActive}
                aria-current={isActive ? "step" : undefined}
                onClick={() => setActiveStep(index)}
              >
                <span className="wizard-step-index">{index + 1}</span>
                <span className="wizard-step-copy">
                  <span className="wizard-step-label">{step.label}</span>
                  <span className="wizard-step-kicker">{step.kicker}</span>
                </span>
              </button>
            );
          })}
        </div>

        <div className="wizard-panel-stack">
          <div
            id="profile-step-identity"
            className="wizard-panel"
            role="tabpanel"
            aria-labelledby="profile-step-tab-identity"
            hidden={activeStep !== 0}
          >
            <AccountSection className="wizard-panel-inner" user={user} onUserUpdated={setUser} />
          </div>

          <div
            id="profile-step-profile"
            className="wizard-panel"
            role="tabpanel"
            aria-labelledby="profile-step-tab-profile"
            hidden={activeStep !== 1}
          >
            <ProfileSection className="wizard-panel-inner" />
          </div>

          <div
            id="profile-step-skills"
            className="wizard-panel"
            role="tabpanel"
            aria-labelledby="profile-step-tab-skills"
            hidden={activeStep !== 2}
          >
            <SkillsSection className="wizard-panel-inner" />
          </div>
        </div>

        <div className="section-actions section-actions-split">
          <button
            className="ghost-button"
            type="button"
            onClick={() => setActiveStep((current) => Math.max(0, current - 1))}
            disabled={activeStep === 0}
          >
            Previous
          </button>
          <button
            className="primary-button"
            type="button"
            onClick={() =>
              setActiveStep((current) => Math.min(PROFILE_STEPS.length - 1, current + 1))
            }
            disabled={activeStep === PROFILE_STEPS.length - 1}
          >
            Next
          </button>
        </div>
      </section>
    </>
  );
}
