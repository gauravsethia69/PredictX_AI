import { Activity, CircleDot, Cog, Fan } from "lucide-react";

export default function MachineVisual({ status = "Healthy" }) {
  const dangerous = /emergency|critical/i.test(status);

  return (
    <div className={`machine-visual ${dangerous ? "machine-danger" : ""}`}>
      <div className="machine-floor" />
      <div className="motor-body">
        <div className="motor-lines" />
        <Fan size={45} />
      </div>
      <div className="shaft" />
      <div className="bearing">
        <Cog size={48} />
      </div>
      <div className="machine-label">
        <Activity size={15} />
        <span>{status}</span>
      </div>
      <div className="machine-points">
        <span><CircleDot size={12} /> Motor</span>
        <span><CircleDot size={12} /> Bearing</span>
      </div>
    </div>
  );
}
