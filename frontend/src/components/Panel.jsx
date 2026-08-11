export default function Panel({ title, action, className = "", children }) {
  return (
    <section className={`panel ${className}`}>
      {(title || action) && (
        <header className="panel-header">
          <h3>{title}</h3>
          {action && <span>{action}</span>}
        </header>
      )}
      {children}
    </section>
  );
}
