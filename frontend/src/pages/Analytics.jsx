import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import PageHeading from "../components/PageHeading";
import Panel from "../components/Panel";
import SensorChart from "../components/SensorChart";
import usePredictXData from "../hooks/usePredictXData";
import { normalizeReadings } from "../utils/dataHelpers";
import "../styles/pages.css";

function trendValue(trends, key) {
  const value =
    trends?.sensor_trends?.[key] ||
    trends?.trends?.[key] ||
    trends?.[`${key}_trend`] ||
    trends?.[key] ||
    {};
  return typeof value === "string" ? { direction: value } : value || {};
}

function TrendCard({ label, value }) {
  const direction = String(value?.direction || value?.trend || "—");
  const lower = direction.toLowerCase();
  const Icon = lower.includes("rising") || lower.includes("increase") ? ArrowUpRight : lower.includes("fall") || lower.includes("decrease") ? ArrowDownRight : Minus;
  return (
    <div className="trend-card">
      <span>{label}</span>
      <Icon size={22} />
      <strong>{direction}</strong>
      <small>{value?.percentage_change ?? value?.change_percent ?? "—"}% change</small>
    </div>
  );
}

export default function Analytics() {
  const { readings, trends, loading, error } = usePredictXData({ limit: 80 });
  if (loading && !readings.length) return <div className="loading-screen">Loading analytics...</div>;

  return (
    <div className="content-page">
      <PageHeading title="Analytics" description="Historical trends and machine deterioration analysis." />
      {error && <div className="error-message">{error}</div>}

      <div className="trend-grid">
        <TrendCard label="Temperature Trend" value={trendValue(trends, "temperature")} />
        <TrendCard label="Vibration Trend" value={trendValue(trends, "vibration")} />
        <TrendCard label="Current Trend" value={trendValue(trends, "current")} />
        <TrendCard label="Sound Trend" value={trendValue(trends, "sound")} />
      </div>

      <Panel title="Historical Sensor Analytics" action={trends?.machine_trend || trends?.overall_trend || "—"}>
        <div className="large-chart"><SensorChart data={normalizeReadings(readings)} /></div>
      </Panel>

      <Panel title="Trend Engine Response">
        <pre className="json-view">{JSON.stringify(trends || {}, null, 2)}</pre>
      </Panel>
    </div>
  );
}
