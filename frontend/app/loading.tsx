export default function Loading() {
  return (
    <section className="loading-panel loading-panel-skeleton" aria-label="Loading workspace">
      <p className="eyebrow">sweOS</p>
      <h1>Preparing workspace.</h1>
      <div className="skeleton-grid" aria-hidden="true">
        <span className="skeleton-line skeleton-line-wide" />
        <span className="skeleton-line" />
        <span className="skeleton-card" />
        <span className="skeleton-card" />
      </div>
    </section>
  );
}
