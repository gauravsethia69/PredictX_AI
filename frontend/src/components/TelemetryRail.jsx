import { Activity, Cpu, Gauge, RadioTower, Waves } from "lucide-react";

export default function TelemetryRail({ machineId, sampleCount, source, backendOnline, status, refreshInterval = 3000 }) {
  const items = [
    { icon: Cpu, label: "Asset", value: machineId || "Awaiting machine" },
    { icon: Waves, label: "Samples", value: `${sampleCount || 0} buffered` },
    { icon: RadioTower, label: "Source", value: source || "simulator" },
    { icon: Gauge, label: "Polling", value: `${refreshInterval / 1000}s refresh` },
    { icon: Activity, label: "System", value: backendOnline ? status || "Online" : "Disconnected" }
  ];

  return (
    <section className="telemetry-rail" aria-label="Live telemetry summary">
      <div className="telemetry-marquee">
        {[...items, ...items].map(({ icon: Icon, label, value }, index) => (
          <div className="telemetry-item" key={`${label}-${index}`}>
            <Icon size={14} />
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
