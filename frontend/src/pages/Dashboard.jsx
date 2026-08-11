import {
  Activity,
  AlertTriangle,
  Bell,
  Bot,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Database,
  Gauge,
  Radio,
  ShieldAlert,
  Sparkles,
  Star,
  Wrench
} from "lucide-react";
import { useMemo } from "react";
import usePredictXData from "../hooks/usePredictXData";
import HealthGauge from "../components/HealthGauge";
import MachineVisual from "../components/MachineVisual";
import Panel from "../components/Panel";
import ScenarioControls from "../components/ScenarioControls";
import SensorChart from "../components/SensorChart";
import SensorMetric from "../components/SensorMetric";
import {
  extractAlerts,
  getConfidence,
  getDataSource,
  getEstimatedDowntime,
  getFailureRisk,
  getFault,
  getHealthScore,
  getMaintenancePriority,
  getRecommendation,
  getRecommendationObject,
  getSeverity,
  getShutdownRecommended,
  getStatus,
  normalizeReadings,
  safeNumber,
  statusTone
} from "../utils/dataHelpers";
import "../styles/dashboard.css";

function formatTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleTimeString();
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 12) return "Good Morning";
  if (hour >= 12 && hour < 17) return "Good Afternoon";
  return "Good Evening";
}

function MetricCard({ icon: Icon, label, value, caption, tone = "orange" }) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <div className="metric-card-head">
        <div className="metric-icon"><Icon size={22} /></div>
        <div>
          <span>{label}</span>
          <strong>{value}</strong>
          <small>{caption}</small>
        </div>
      </div>
    </article>
  );
}

export default function Dashboard() {
  const {
    machineId,
    latest,
    readings,
    alerts,
    backendOnline,
    loading: initialLoading,
    error,
    refresh: loadDashboard
  } = usePredictXData({ limit: 30 });

  const chartData = useMemo(() => normalizeReadings(readings), [readings]);

  if (initialLoading && !latest) {
    return <div className="loading-screen">Connecting to PredictX backend...</div>;
  }

  const analysis = latest?.analysis || {};
  const predictionExplanation = latest?.prediction_explanation || "—";
  const healthScore = getHealthScore(latest);
  const failureRisk = getFailureRisk(latest);
  const status = getStatus(latest);
  const severity = getSeverity(latest);
  const fault = getFault(latest);
  const confidence = getConfidence(latest);
  const recommendation = getRecommendation(latest);
  const recommendationDetails = getRecommendationObject(latest);
  const maintenancePriority = getMaintenancePriority(latest);
  const estimatedDowntime = getEstimatedDowntime(latest);
  const shutdown = getShutdownRecommended(latest);
  const tone = statusTone(status);
  const activeAlerts = extractAlerts(alerts);
  const timestamp = latest?.timestamp;
  const sourceInfo = getDataSource(latest);

  return (
    <div className="dashboard-page premium-dashboard">
      <section className="premium-heading-row">
        <div>
          <span className="premium-kicker"><Sparkles size={14} /> Backend-powered predictive maintenance</span>
          <h1><span>{getGreeting()},</span> Operator! 👋</h1>
          <p>Every value below comes directly from the PredictX FastAPI backend.</p>
        </div>

        <div className="premium-status-cluster">
          <div className={`backend-pill ${backendOnline ? "online" : "offline"}`}>
            <i /> {backendOnline ? "Backend connected" : "Backend offline"}
          </div>
          <div className="notification-pill"><Bell size={17} /><b>{activeAlerts.length}</b></div>
        </div>
      </section>

      {error && <div className="error-message">{error}</div>}

      <section className={`overview-card overview-${tone}`}>
        <div className="overview-copy">
          <span className="section-eyebrow"><Activity size={15} /> Machine Overview</span>
          <div className="machine-overview-grid">
            <div><span>Machine ID</span><strong>{machineId || "—"}</strong></div>
            <div><span>Status</span><strong className={`status-text status-${tone}`}>{status}</strong></div>
            <div><span>Source</span><strong>{latest?.source || "—"}</strong></div>
            <div><span>Last Updated</span><strong>{formatTime(timestamp)}</strong></div>
          </div>
        </div>

        <div className="overview-centre">
          <span>Overall Health</span>
          <strong>{Math.round(healthScore)}%</strong>
          <b className={`health-label health-${tone}`}>{status}</b>
        </div>

        <div className="overview-gauge">
          <HealthGauge value={healthScore} label="Health Score" status={status} tone={tone} />
        </div>
      </section>

      <section className="metric-grid">
        <MetricCard icon={Gauge} label="Health Score" value={`${Math.round(healthScore)}%`} caption={status} tone="red" />
        <MetricCard icon={ShieldAlert} label="Failure Risk" value={`${Math.round(failureRisk)}%`} caption={`Severity: ${severity}`} tone="orange" />
        <MetricCard icon={Star} label="Remaining Life" value={`${Math.round(safeNumber(latest?.remaining_life_hours))} hrs`} caption={latest?.failure_stage || "—"} tone="yellow" />
        <MetricCard icon={Wrench} label="Maintenance Priority" value={maintenancePriority} caption={`Downtime: ${estimatedDowntime}`} tone="purple" />
      </section>

      <ScenarioControls onSent={loadDashboard} />

      <section className="premium-middle-grid">
        <Panel title="Parameter Trends" action={`${chartData.length} backend readings`} className="premium-chart-panel">
          <SensorChart data={chartData} />
        </Panel>

        <Panel title="Machine Visual Twin" action={sourceInfo.type || latest?.source || "—"} className="premium-machine-panel">
          <MachineVisual status={status} />
          <div className="machine-sensor-list">
            <SensorMetric type="temperature" label="Temperature" value={safeNumber(latest?.temperature).toFixed(1)} unit="°C" compact />
            <SensorMetric type="vibration" label="Vibration" value={safeNumber(latest?.vibration).toFixed(2)} unit="prototype unit" compact />
            <SensorMetric type="current" label="Current" value={safeNumber(latest?.current).toFixed(2)} unit="A" compact />
            <SensorMetric type="sound" label="Sound" value={safeNumber(latest?.sound).toFixed(0)} unit="dB" compact />
          </div>
        </Panel>

        <Panel title="Latest Diagnosis" action={latest?.machine_status || "—"} className="diagnosis-panel">
          <div className={`diagnosis-badge diagnosis-${tone}`}><Bot size={24} /></div>
          <h3>{fault}</h3>
          <p>{predictionExplanation}</p>
          <div className="diagnosis-facts">
            <span><b>{Math.round(failureRisk)}%</b> Failure Risk</span>
            <span><b>{latest?.motor_running ? "RUNNING" : "STOPPED"}</b> Motor</span>
          </div>
        </Panel>
      </section>

      <section className="premium-bottom-grid">
        <Panel title="Backend Recommendation" className="bottom-card">
          <div className="recommendation-content">
            <Bot size={23} />
            <div>
              <strong>{recommendationDetails.action}</strong>
              <p>{recommendationDetails.estimate_note}</p>
            </div>
          </div>
        </Panel>

        <Panel title="Active Alerts" action={activeAlerts.length} className="bottom-card">
          {activeAlerts.length > 0 ? (
            <div className="alert-stack">
              {activeAlerts.slice(0, 2).map((alert) => (
                <div key={alert.id}><AlertTriangle size={15} /><span>{alert.message}</span></div>
              ))}
            </div>
          ) : (
            <div className="empty-alert"><CheckCircle2 size={24} /><span>No active alerts returned</span></div>
          )}
        </Panel>

        <Panel title="Maintenance Decision" className="bottom-card">
          <div className="maintenance-summary">
            <CalendarDays size={29} />
            <span>Response timeframe</span>
            <strong>{recommendationDetails.timeframe}</strong>
            <small>Service estimate: {recommendationDetails.service_time_estimate}</small>
          </div>
        </Panel>

        <Panel title="Backend Data Source" className="bottom-card">
          <div className="quality-summary">
            <Database size={32} />
            <div>
              <strong>{sourceInfo.type || latest?.source || "—"}</strong>
              <p>{sourceInfo.message || "—"}</p>
            </div>
          </div>
        </Panel>
      </section>

      <footer className="dashboard-footnote"><Radio size={14} /> Data source and analysis fields are returned by the backend API.</footer>
    </div>
  );
}
