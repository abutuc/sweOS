import { GoalsSection } from "@/components/goals-section";
import { ProfileSection } from "@/components/profile-section";
import { SkillsSection } from "@/components/skills-section";

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero-panel">
        <p className="eyebrow">Epic 1</p>
        <h1>Engineer identity, skill map, and role direction.</h1>
        <p className="hero-copy">
          Build a usable profile foundation with stack tags, structured skills, and concrete goals.
        </p>
      </section>

      <section className="workspace-grid">
        <ProfileSection className="workspace-card" />
        <SkillsSection className="workspace-card" />
        <GoalsSection className="workspace-card workspace-card-wide" />
      </section>
    </main>
  );
}
