import {
  Activity,
  AudioLines,
  Thermometer,
  TrendingDown,
  TrendingUp,
  Minus,
  Zap
} from "lucide-react";

const icons = {
  temperature: Thermometer,
  vibration: Activity,
  current: Zap,
  sound: AudioLines
};

export default function SensorMetric({ type, label, value, unit, delta = 0, status = "Live" }) {
  const Icon = icons[type] || Activity;
  const numericDelta = Number(delta) || 0;
  const DeltaIcon = numericDelta > 0 ? TrendingUp : numericDelta < 0 ? TrendingDown : Minus;
  const deltaClass = numericDelta > 0 ? "metric-up" : numericDelta < 0 ? "metric-down" : "metric-flat";

  return (
    <div className="sensor-metric">
      <div>
        <span>{label}</span>
        <Icon size={18} />
      </div>
      <strong>
        {value}
        <small>{unit}</small>
      </strong>
      <div className="metric-meta-row">
        <span className={deltaClass}><DeltaIcon size={12} /> {Math.abs(numericDelta).toFixed(2)} since last</span>
        <span className="metric-live-dot"><i /> {status}</span>
      </div>
      <div className="mini-wave" aria-hidden="true">
        <i /><i /><i /><i /><i /><i /><i />
      </div>
    </div>
  );
}
