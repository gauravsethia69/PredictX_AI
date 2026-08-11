import { Database, Server, Timer, Wrench } from "lucide-react";
import PageHeading from "../components/PageHeading";
import Panel from "../components/Panel";
import {
  API_BASE_URL,
  REFRESH_INTERVAL
} from "../api/predictxApi";
import { useMachine } from "../context/MachineContext";
import "../styles/pages.css";

export default function Settings() {
  const {
    machines,
    selectedMachineId,
    setSelectedMachineId
  } = useMachine();

  return (
    <div className="content-page">
      <PageHeading
        title="Settings"
        description="Runtime configuration discovered from the backend."
      />

      <div className="settings-grid">
        <Panel title="Backend Connection">
          <div className="setting-row">
            <Server size={20} />
            <div>
              <span>API Base URL</span>
              <strong>{API_BASE_URL}</strong>
            </div>
          </div>
        </Panel>

        <Panel title="Current Machine">
          <div className="setting-row">
            <Wrench size={20} />
            <div>
              <span>Selected dynamically</span>
              <strong>{selectedMachineId || "None"}</strong>
            </div>
          </div>
        </Panel>

        <Panel title="Discovered Assets">
          <div className="setting-row">
            <Database size={20} />
            <div>
              <span>Machines found</span>
              <strong>{machines.length}</strong>
            </div>
          </div>
        </Panel>

        <Panel title="Live Refresh">
          <div className="setting-row">
            <Timer size={20} />
            <div>
              <span>Polling interval</span>
              <strong>{REFRESH_INTERVAL / 1000} seconds</strong>
            </div>
          </div>
        </Panel>
      </div>

      <Panel title="Machine Selection">
        <div className="dynamic-machine-list">
          {machines.length ? (
            machines.map((machine) => (
              <button
                key={machine.machine_id}
                className={
                  machine.machine_id === selectedMachineId
                    ? "selected"
                    : ""
                }
                onClick={() =>
                  setSelectedMachineId(machine.machine_id)
                }
              >
                <strong>{machine.machine_id}</strong>
                <span>{machine.source}</span>
                <small>{machine.status}</small>
              </button>
            ))
          ) : (
            <p>No machine records exist yet.</p>
          )}
        </div>
      </Panel>

      <Panel title="Environment Configuration">
        <div className="config-help">
          Only the backend URL and refresh interval remain in
          <code>.env</code>. Machine IDs are loaded dynamically.
          <pre>{`VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_REFRESH_INTERVAL=3000`}</pre>
        </div>
      </Panel>
    </div>
  );
}
