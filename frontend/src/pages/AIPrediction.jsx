import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  ArrowRight,
  Bot,
  CheckCircle2,
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
  getFailureRisk,
  getDiagnosis,
  getFault,
  getFaultCode,
  getRecommendationObject,
  getShutdownRecommended,
  getStatus,
  statusTone
} from "../utils/dataHelpers";
import "../styles/pages.css";

function DecisionTile({ icon: Icon, label, value, tone = "neutral" }) {
  return (
    <article className={`decision-tile decision-${tone}`}>
      <div className="decision-icon"><Icon size={19} /></div>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

export default function AIPrediction() {
  const navigate = useNavigate();
  const { latest, loading, error } = usePredictXData();
  if (loading && !latest) return <div className="loading-screen">Loading backend diagnosis...</div>;

  const analysis = getAnalysis(latest);
  const diagnosis = getDiagnosis(latest);
  const failureRisk = getFailureRisk(latest);
  const explanation = latest?.prediction_explanation || "—";
  const recommendation = getRecommendationObject(latest);
  const status = getStatus(latest);
  const tone = statusTone(status);
  const shutdown = getShutdownRecommended(latest);
  const confidenceValue = getConfidence(latest);
  const confidence = confidenceValue == null ? null : Math.min(100, Math.max(0, confidenceValue));
  const machineCanContinue = recommendation.machine_can_continue;
  const maintenanceLabel = recommendation.action === "—" ? "Open maintenance" : recommendation.action;

  return (
    <div className="content-page prediction-page">
      <PageHeading
        eyebrow="PredictX Backend Intelligence"
        title="AI Prediction"
        description="All diagnosis and maintenance fields shown here are returned by the latest sensor-reading API response."
        right={<div className={`page-status-badge page-status-${tone}`}><i /> {status}</div>}
      />
      {error && <div className="error-message">{error}</div>}

      <section className="prediction-command-grid">
        <Panel className={`diagnosis-command-card diagnosis-command-${tone}`}>
          <div className="diagnosis-command-top">
            <span><Sparkles size={15} /> Backend diagnosis</span>
            <b>Fault code {getFaultCode(latest)}</b>
          </div>

          <div className="diagnosis-command-body">
            <div className={`diagnosis-orb diagnosis-orb-${tone}`}>
              {tone === "danger" ? <AlertTriangle size={42} /> : <Bot size={42} />}
            </div>
            <div>
              <small>{latest?.machine_status || status}</small>
              <h2>{getFault(latest)}</h2>
              <p>{explanation}</p>
            </div>
          </div>

          <div className="confidence-block">
            <div><span>Failure probability</span><strong>{Math.round(failureRisk)}%</strong></div>
            <div className="confidence-track"><i style={{ width: `${failureRisk}%` }} /></div>
          </div>
        </Panel>

        <Panel className={`safety-command-card safety-command-${shutdown ? "danger" : "success"}`}>
          <div className="safety-command-icon">
            {shutdown ? <AlertTriangle size={34} /> : <ShieldCheck size={34} />}
          </div>
          <span>Backend safety decision</span>
          <h2>{shutdown ? "Shutdown recommended" : "Shutdown not recommended"}</h2>
          <p>{explanation}</p>
          <div className="safety-seal">
            {shutdown ? <AlertTriangle size={16} /> : <CheckCircle2 size={16} />}
            {latest?.failure_stage || "—"}
          </div>
        </Panel>
      </section>

      <section className="decision-summary-grid">
        <DecisionTile icon={Wrench} label="Recommended action" value={recommendation.action} tone={shutdown ? "danger" : "orange"} />
        <DecisionTile icon={Clock3} label="Response timeframe" value={recommendation.timeframe} tone="orange" />
        <DecisionTile icon={Gauge} label="Can machine continue?" value={machineCanContinue === null ? "—" : machineCanContinue ? "Yes" : "No"} tone={machineCanContinue === false ? "danger" : "success"} />
        <DecisionTile icon={Cpu} label="Service estimate" value={recommendation.service_time_estimate} tone="purple" />
      </section>

      <Panel title="ESP32 Recommendation" action={latest?.source || "esp32"} className="action-plan-panel">
        <div className="action-plan-layout">
          <div className="action-plan-main">
            <div className="action-step-number">01</div>
            <div>
              <span>Recommended action</span>
              <h3>{recommendation.action}</h3>
              <p>{recommendation.estimate_note}</p>
            </div>
          </div>
          <button className="action-plan-button" type="button" onClick={() => navigate("/maintenance", { state: { fromPrediction: true } })}>
            {maintenanceLabel} <ArrowRight size={17} />
          </button>
        </div>
      </Panel>

      <details className="technical-disclosure">
        <summary>View complete backend diagnosis payload</summary>
        <pre className="json-view">{JSON.stringify(diagnosis, null, 2)}</pre>
      </details>
    </div>
  );
}
