import { Download, FileText } from "lucide-react";
import PageHeading from "../components/PageHeading";
import Panel from "../components/Panel";
import usePredictXData from "../hooks/usePredictXData";
import {
  formatDateTime,
  getFailureRisk,
  getFault,
  getHealthScore,
  getRecommendationObject,
  getStatus
} from "../utils/dataHelpers";
import "../styles/pages.css";

export default function Reports() {
  const { latest, trends, alerts, loading, error } = usePredictXData({ autoRefresh: false });
  if (loading && !latest) return <div className="loading-screen">Preparing report...</div>;

  function downloadReport() {
    const report = {
      generated_at: new Date().toISOString(),
      machine_id: latest?.machine_id,
      latest_timestamp: latest?.timestamp || latest?.created_at,
      status: getStatus(latest),
      health_score: getHealthScore(latest),
      failure_risk: getFailureRisk(latest),
      detected_fault: getFault(latest),
      recommendation: getRecommendationObject(latest),
      sensor_values: {
        temperature: latest?.temperature,
        vibration: latest?.vibration,
        current: latest?.current,
        sound: latest?.sound
      },
      trends,
      alerts
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `PredictX-${latest?.machine_id || "machine"}-report.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="content-page">
      <PageHeading title="Reports" description="Generate a machine-health report from live backend data." />
      {error && <div className="error-message">{error}</div>}

      <Panel title="Machine Health Report">
        <div className="report-preview">
          <FileText size={45}/>
          <h2>PredictX AI Maintenance Report</h2>
          <p>Machine: {latest?.machine_id || "—"}</p>
          <p>Latest reading: {formatDateTime(latest?.timestamp || latest?.created_at)}</p>
          <div className="report-stat-grid">
            <div><span>Status</span><strong>{getStatus(latest)}</strong></div>
            <div><span>Health</span><strong>{Math.round(getHealthScore(latest))}%</strong></div>
            <div><span>Failure Risk</span><strong>{Math.round(getFailureRisk(latest))}%</strong></div>
            <div><span>Fault</span><strong>{getFault(latest)}</strong></div>
          </div>
          <button className="primary-action" onClick={downloadReport}><Download size={17}/> Download JSON Report</button>
        </div>
      </Panel>
    </div>
  );
}
