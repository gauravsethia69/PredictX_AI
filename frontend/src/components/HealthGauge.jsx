export default function HealthGauge({
  value = 0,
  label,
  status = "Healthy",
  tone = "success"
}) {
  const clamped = Math.max(0, Math.min(100, Number(value) || 0));
  const degree = clamped * 3.6;

  return (
    <div className={`health-gauge tone-${tone}`}>
      <div
        className="gauge-ring"
        style={{
          background: `conic-gradient(var(--gauge-color) ${degree}deg, #232830 ${degree}deg)`
        }}
      >
        <div className="gauge-inner">
          <strong>{Math.round(clamped)}%</strong>
        </div>
      </div>
      <span>{label}</span>
      <small>{status}</small>
    </div>
  );
}
