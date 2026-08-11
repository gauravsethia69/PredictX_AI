import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  BellRing,
  CheckCircle2,
  Clock3,
  Radio,
  ShieldAlert
} from "lucide-react";
import PageHeading from "../components/PageHeading";
import Panel from "../components/Panel";
import usePredictXData from "../hooks/usePredictXData";
import { extractAlerts, formatDateTime } from "../utils/dataHelpers";
import "../styles/pages.css";

function severityTone(value = "") {
  const severity = String(value).toLowerCase();
  if (severity.includes("critical") || severity.includes("emergency")) return "danger";
  if (severity.includes("high") || severity.includes("warning")) return "warning";
  return "neutral";
}

export default function Alerts() {
  const navigate = useNavigate();
  const { alerts, loading, error } = usePredictXData();
  const items = extractAlerts(alerts);
  if (loading && !alerts) return <div className="loading-screen">Loading alerts...</div>;

  const criticalCount = items.filter((item) => severityTone(item.severity) === "danger").length;
  const warningCount = items.filter((item) => severityTone(item.severity) === "warning").length;

  return (
    <div className="content-page alerts-page">
      <PageHeading
        eyebrow="PredictX Safety Centre"
        title="Alerts"
        description="Live safety events, preventive warnings and machine attention requests."
        right={<div className={`page-status-badge ${items.length ? "page-status-danger" : "page-status-success"}`}><i /> {items.length ? `${items.length} active` : "All clear"}</div>}
      />
      {error && <div className="error-message">{error}</div>}

      <section className="alert-summary-grid">
        <article className="alert-summary-card alert-summary-primary">
          <div><BellRing size={22} /></div><span>Active alerts</span><strong>{items.length}</strong><small>Current machine events</small>
        </article>
        <article className="alert-summary-card alert-summary-danger">
          <div><ShieldAlert size={22} /></div><span>Critical</span><strong>{criticalCount}</strong><small>Immediate attention</small>
        </article>
        <article className="alert-summary-card alert-summary-warning">
          <div><AlertTriangle size={22} /></div><span>Warnings</span><strong>{warningCount}</strong><small>Preventive action</small>
        </article>
        <article className="alert-summary-card alert-summary-success">
          <div><Radio size={22} /></div><span>Alert engine</span><strong>Live</strong><small>Continuous evaluation</small>
        </article>
      </section>

      <Panel title="Active Safety Events" action={`${items.length} event${items.length === 1 ? "" : "s"}`} className="alerts-command-panel">
        <div className="premium-alert-list">
          {items.length ? items.map((alert, index) => {
            const tone = severityTone(alert.severity);
            return (
              <article key={alert.id} className={`premium-alert-item alert-item-${tone}`}>
                <div className="alert-index">{String(index + 1).padStart(2, "0")}</div>
                <div className="alert-symbol"><AlertTriangle size={22} /></div>
                <div className="alert-copy">
                  <div className="alert-title-row">
                    <h3>{alert.title}</h3>
                    <span className={`severity-chip severity-${tone}`}>{alert.severity}</span>
                  </div>
                  <p>{alert.message}</p>
                  <div className="alert-meta"><Clock3 size={13} /> {formatDateTime(alert.timestamp)}</div>
                </div>
                <button type="button" className="alert-review-button" onClick={() => navigate("/ai-prediction", { state: { fromAlert: true, alert } })}>Review report <span>→</span></button>
              </article>
            );
          }) : (
            <div className="premium-empty-state">
              <div className="empty-state-ring"><CheckCircle2 size={40} /></div>
              <span>Safety centre</span>
              <h2>No active alerts</h2>
              <p>The latest machine condition does not require an active warning. PredictX will continue monitoring every incoming reading.</p>
            </div>
          )}
        </div>
      </Panel>

      <details className="technical-disclosure">
        <summary>View alert engine payload</summary>
        <pre className="json-view">{JSON.stringify(alerts || {}, null, 2)}</pre>
      </details>
    </div>
  );
}
