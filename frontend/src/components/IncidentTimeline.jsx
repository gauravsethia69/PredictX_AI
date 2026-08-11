import { AlertTriangle, CheckCircle2, Clock3, Database, Sparkles } from "lucide-react";
import { extractAlerts, formatDateTime } from "../utils/dataHelpers";

export default function IncidentTimeline({ latest, alerts }) {
  const alertItems = extractAlerts(alerts).slice(0, 3);
  const fallback = [
    {
      title: "Sensor packet accepted",
      message: `Latest packet stored from ${latest?.source || "simulator"}.`,
      timestamp: latest?.timestamp || latest?.created_at,
      icon: Database,
      tone: "neutral"
    },
    {
      title: "AI analysis completed",
      message: "Health score, risk and explainable diagnosis refreshed.",
      timestamp: latest?.timestamp || latest?.created_at,
      icon: Sparkles,
      tone: "success"
    }
  ];

  const items = alertItems.length
    ? alertItems.map((alert) => ({
        ...alert,
        icon: AlertTriangle,
        tone: /critical|emergency|high/i.test(alert.severity) ? "danger" : "warning"
      }))
    : fallback;

  return (
    <div className="incident-timeline">
      {items.map((item, index) => {
        const Icon = item.icon || CheckCircle2;
        return (
          <article key={item.id ?? index} className={`timeline-item timeline-${item.tone || "neutral"}`}>
            <div className="timeline-icon"><Icon size={15} /></div>
            <div>
              <strong>{item.title || "System event"}</strong>
              <p>{item.message}</p>
              <small><Clock3 size={11} /> {formatDateTime(item.timestamp)}</small>
            </div>
          </article>
        );
      })}
    </div>
  );
}
