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
        <article className="workspace-card">Profile panel</article>
        <article className="workspace-card">Skills panel</article>
        <article className="workspace-card workspace-card-wide">Goals panel</article>
      </section>
    </main>
  );
}
