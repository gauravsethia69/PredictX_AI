import { Activity, Cpu, Radio } from "lucide-react";
import PageHeading from "../components/PageHeading";
import Panel from "../components/Panel";
import { useMachine } from "../context/MachineContext";
import { formatDateTime, statusTone } from "../utils/dataHelpers";
import "../styles/pages.css";

export default function Machines() {
  const {
    machines,
    selectedMachineId,
    setSelectedMachineId,
    loadingMachines,
    machineError
  } = useMachine();

  if (loadingMachines) {
    return <div className="loading-screen">Discovering machines...</div>;
  }

  return (
    <div className="content-page">
      <PageHeading
        title="Machines"
        description="Assets discovered automatically from backend readings."
      />

      {machineError && (
        <div className="error-message">{machineError}</div>
      )}

      <div className="machine-discovery-grid">
        {machines.length ? (
          machines.map((machine) => {
            const tone = statusTone(machine.status);
            const selected =
              machine.machine_id === selectedMachineId;

            return (
              <Panel
                key={machine.machine_id}
                className={`machine-card ${selected ? "selected-machine-card" : ""}`}
              >
                <div className="machine-card-head">
                  <div className="asset-icon">
                    <Cpu size={28} />
                  </div>

                  <div>
                    <span>Machine ID</span>
                    <h2>{machine.machine_id}</h2>
                    <p>{formatDateTime(machine.timestamp)}</p>
                  </div>

                  <span className={`status-chip ${tone}`}>
                    {machine.status}
                  </span>
                </div>

                <div className="machine-stat-row">
                  <div>
                    <Radio size={18} />
                    <span>Source</span>
                    <strong>{machine.source}</strong>
                  </div>

                  <div>
                    <Activity size={18} />
                    <span>Motor</span>
                    <strong>
                      {machine.motor_running === false
                        ? "Stopped"
                        : "Running"}
                    </strong>
                  </div>
                </div>

                <button
                  className="primary-action"
                  onClick={() =>
                    setSelectedMachineId(machine.machine_id)
                  }
                >
                  {selected ? "Currently monitoring" : "Monitor machine"}
                </button>
              </Panel>
            );
          })
        ) : (
          <Panel>
            <div className="empty-state">
              <Cpu size={44} />
              <h3>No machines found</h3>
              <p>
                Send sensor data from Swagger, ESP32, or the demo
                controls to create the first machine.
              </p>
            </div>
          </Panel>
        )}
      </div>
    </div>
  );
}
