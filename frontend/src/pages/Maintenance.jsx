import { useLocation, useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  ArrowLeft,
  CalendarClock,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Cpu,
  Gauge,
  ShieldCheck,
  Sparkles,
  Wrench
} from "lucide-react";
import PageHeading from "../components/PageHeading";
import Panel from "../components/Panel";
import usePredictXData from "../hooks/usePredictXData";
import {
  getAnalysis,
  getConfidence,
  getEstimatedDowntime,
  getFault,
  getFaultCode,
  getMaintenancePriority,
  getPrimaryFault,
  getRecommendationObject,
  getShutdownRecommended,
  getStatus,
  statusTone
} from "../utils/dataHelpers";
import "../styles/pages.css";

function MaintenanceStat({ icon: Icon, label, value, tone = "orange" }) {
  return (
    <article className={`maintenance-stat maintenance-stat-${tone}`}>
      <div><Icon size={20} /></div>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

export default function Maintenance() {
  const navigate = useNavigate();
  const location = useLocation();
  const { latest, alerts, loading, error } = usePredictXData();
  if (loading && !latest) return <div className="loading-screen">Loading backend maintenance data...</div>;

  const analysis = getAnalysis(latest);
  const primaryFault = getPrimaryFault(latest);
  const recommendation = getRecommendationObject(latest);
  const shutdown = getShutdownRecommended(latest);
  const status = getStatus(latest);
  const tone = statusTone(status);
  const confidenceValue = getConfidence(latest);
  const confidence = confidenceValue == null ? null : Math.round(Math.min(100, Math.max(0, confidenceValue)));
  const fault = getFault(latest);
  const faultCode = getFaultCode(latest);
  const fromPrediction = Boolean(location.state?.fromPrediction);
  const canContinue = recommendation.machine_can_continue;
  const priority = getMaintenancePriority(latest);
  const estimatedDowntime = getEstimatedDowntime(latest);
  const steps = Array.isArray(primaryFault.maintenance_steps) ? primaryFault.maintenance_steps : [];
  const precautions = Array.isArray(primaryFault.safety_precautions) ? primaryFault.safety_precautions : [];
  const tools = Array.isArray(primaryFault.tools) ? primaryFault.tools : [];

  return (
    <div className="content-page maintenance-page">
      <PageHeading
        eyebrow="PredictX Backend Maintenance Intelligence"
        title="Maintenance Command Centre"
        description="This page uses the recommended action, priority, downtime, steps, tools and safety precautions returned by FastAPI."
        right={
          fromPrediction ? (
            <button className="maintenance-back-button" onClick={() => navigate("/ai-prediction")}>
              <ArrowLeft size={16} /> Back to prediction
            </button>
          ) : (
            <div className={`page-status-badge page-status-${tone}`}><i /> {status}</div>
          )
        }
      />
      {error && <div className="error-message">{error}</div>}

      <section className="maintenance-hero-grid">
        <Panel className={`maintenance-hero maintenance-hero-${shutdown ? "danger" : tone}`}>
          <div className="maintenance-hero-copy">
            <span><Sparkles size={15} /> Backend recommended decision</span>
            <h2>{recommendation.action}</h2>
            <p>{recommendation.estimate_note}</p>
            <div className="maintenance-hero-tags">
              <b>{fault}</b>
              <small>Fault code {faultCode}</small>
            </div>
          </div>
          <div className={`maintenance-hero-orb ${shutdown ? "danger" : "success"}`}>
            {shutdown ? <AlertTriangle size={42} /> : <ShieldCheck size={42} />}
            <strong>{shutdown ? "STOP" : "NO STOP"}</strong>
            <span>{latest?.failure_stage || "—"}</span>
          </div>
        </Panel>

        <Panel className="maintenance-priority-card">
          <div className={`maintenance-priority-badge ${shutdown ? "danger" : "success"}`}>
            {shutdown ? <AlertTriangle size={30} /> : <CheckCircle2 size={30} />}
          </div>
          <span>Maintenance priority</span>
          <h2>{priority}</h2>
          <p>{recommendation.timeframe}</p>
          <div className="maintenance-confidence-row">
            <span>Failure probability</span><strong>{Math.round(latest?.failure_probability ?? 0)}%</strong>
          </div>
          <div className="maintenance-confidence-track"><i style={{ width: `${Math.min(100, Math.max(0, latest?.failure_probability ?? 0))}%` }} /></div>
        </Panel>
      </section>

      <section className="maintenance-stat-grid">
        <MaintenanceStat icon={Clock3} label="Response timeframe" value={recommendation.timeframe} />
        <MaintenanceStat icon={Gauge} label="Can machine continue?" value={canContinue === null ? "—" : canContinue ? "Yes" : "No"} tone={canContinue === false ? "danger" : "success"} />
        <MaintenanceStat icon={CalendarClock} label="Service estimate" value={recommendation.service_time_estimate} tone="purple" />
        <MaintenanceStat icon={Cpu} label="Estimated downtime" value={estimatedDowntime} tone={tone === "danger" ? "danger" : tone === "warning" ? "warning" : "success"} />
      </section>

      <Panel title="Backend Maintenance Steps" action={`${steps.length} step${steps.length === 1 ? "" : "s"}`} className="maintenance-workflow-panel">
        <div className="maintenance-workflow">
          {steps.length ? steps.map((step, index) => (
            <article key={`${step}-${index}`}>
              <div>{String(index + 1).padStart(2, "0")}</div>
              <span>Maintenance step</span>
              <h3>{step}</h3>
              <p>{primaryFault.recommendation || recommendation.action}</p>
            </article>
          )) : <p className="empty-state-text">No maintenance steps were returned by the backend.</p>}
        </div>
      </Panel>

      <section className="maintenance-bottom-grid">
        <Panel title="Required Tools" action={`${tools.length} item${tools.length === 1 ? "" : "s"}`}>
          <div className="technician-checklist">
            {tools.length ? tools.map((item, index) => (
              <label key={`${item}-${index}`}><Wrench size={16} /> <span>{String(index + 1).padStart(2, "0")}</span> {item}</label>
            )) : <p className="empty-state-text">No tools were returned by the backend.</p>}
          </div>
        </Panel>

        <Panel title="Safety Precautions" action={`${precautions.length} item${precautions.length === 1 ? "" : "s"}`}>
          <div className="technician-checklist">
            {precautions.length ? precautions.map((item, index) => (
              <label key={`${item}-${index}`}><AlertTriangle size={16} /> <span>{String(index + 1).padStart(2, "0")}</span> {item}</label>
            )) : <p className="empty-state-text">No safety precautions were returned by the backend.</p>}
          </div>
        </Panel>
      </section>

      <Panel title="ESP32 Decision Summary" action={latest?.source || "esp32"}>
        <div className="maintenance-decision-summary">
          <ClipboardCheck size={34} />
          <h3>{recommendation.action}</h3>
          <p>{latest?.prediction_explanation || recommendation.estimate_note}</p>
          <button type="button" onClick={() => navigate("/reports")}>Open reports</button>
        </div>
      </Panel>

      <details className="technical-disclosure maintenance-technical">
        <summary>View backend alerts and maintenance payload</summary>
        <pre className="json-view">{JSON.stringify(alerts || {}, null, 2)}</pre>
      </details>
    </div>
  );
}
