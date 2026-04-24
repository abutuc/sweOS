"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { LearningGymSection } from "@/components/learning-gym-section";
import { api, type LearningSummary } from "@/lib/api";
import { isProfileOnboardingComplete } from "@/lib/onboarding";

export function PracticePage() {
  const router = useRouter();
  const [summary, setSummary] = useState<LearningSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    void api
      .getLearningSummary()
      .then((response) => {
        if (!active) {
          return;
        }

        if (!isProfileOnboardingComplete(response.data.profile)) {
          router.replace("/onboarding");
          return;
        }

        setSummary(response.data);
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [router]);

  if (isLoading || !summary) {
    return (
      <section className="loading-panel loading-panel-skeleton">
        <p className="eyebrow">Practice</p>
        <h1>Loading learning gym.</h1>
        <div className="skeleton-grid" aria-hidden="true">
          <span className="skeleton-line skeleton-line-wide" />
          <span className="skeleton-line" />
          <span className="skeleton-card" />
          <span className="skeleton-card" />
        </div>
      </section>
    );
  }

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
        <LearningGymSection
          className="workspace-card workspace-card-wide"
          initialExercises={summary.exercises}
          initialTopicMastery={summary.topicMastery}
          skipInitialLoad
        />
      </section>
    </>
  );
}
