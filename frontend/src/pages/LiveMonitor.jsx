import PageHeading from "../components/PageHeading";
import Panel from "../components/Panel";
import SensorChart from "../components/SensorChart";
import SensorMetric from "../components/SensorMetric";
import usePredictXData from "../hooks/usePredictXData";
import { normalizeReadings, safeNumber } from "../utils/dataHelpers";
import "../styles/pages.css";

export default function LiveMonitor() {
  const { latest, readings, loading, error, backendOnline } = usePredictXData({ limit: 50 });

  if (loading && !latest) return <div className="loading-screen">Loading live monitor...</div>;

  return (
    <div className="content-page">
      <PageHeading
        title="Live Monitor"
        description="Live sensor values automatically refresh from the FastAPI backend."
        right={<div className={`connection-pill ${backendOnline ? "online" : "offline"}`}><i />{backendOnline ? "Live" : "Offline"}</div>}
      />
      {error && <div className="error-message">{error}</div>}

      <div className="live-metric-grid">
        <SensorMetric type="temperature" label="Temperature" value={safeNumber(latest?.temperature).toFixed(1)} unit="°C" />
        <SensorMetric type="vibration" label="Vibration RMS" value={safeNumber(latest?.vibration).toFixed(2)} unit="mm/s" />
        <SensorMetric type="current" label="Current" value={safeNumber(latest?.current).toFixed(2)} unit="A" />
        <SensorMetric type="sound" label="Sound Level" value={safeNumber(latest?.sound).toFixed(0)} unit="dB" />
      </div>

      <Panel title="Live Sensor Waveforms" action="Auto refresh">
        <div className="large-chart"><SensorChart data={normalizeReadings(readings)} /></div>
      </Panel>

      <Panel title="Recent Sensor Readings">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Time</th><th>Temperature</th><th>Vibration</th><th>Current</th><th>Sound</th><th>Status</th></tr></thead>
            <tbody>
              {normalizeReadings(readings).slice().reverse().map((row) => (
                <tr key={`${row.timestamp}-${row.index}`}>
                  <td>{row.time}</td><td>{row.temperature.toFixed(1)} °C</td><td>{row.vibration.toFixed(2)}</td><td>{row.current.toFixed(2)} A</td><td>{row.sound.toFixed(0)} dB</td><td>{row.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
