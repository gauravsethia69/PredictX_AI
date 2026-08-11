import {
  Bell,
  CircleUserRound,
  RefreshCw,
  Wifi,
} from "lucide-react";
import { useMachine } from "../context/MachineContext";
import "../styles/topbar.css";

export default function Topbar() {
  const {
    machines,
    selectedMachine,
    selectedMachineId,
    setSelectedMachineId,
    refreshMachines,
    loadingMachines,
  } = useMachine();

  return (
    <header className="topbar">
      <div className="topbar-machine">
        <div className="machine-selector-group">
          <span className="machine-label">Current machine</span>

          <select
            id="machine-selector"
            value={selectedMachineId || ""}
            onChange={(event) =>
              setSelectedMachineId(event.target.value)
            }
            disabled={
              loadingMachines || machines.length === 0
            }
          >
            {machines.length === 0 ? (
              <option value="no-machines">
                No machines found
              </option>
            ) : (
              machines.map((machine, index) => {
                const machineId =
                  machine.machine_id || `machine-${index}`;

                return (
                  <option
                    key={`${machineId}-${index}`}
                    value={machineId}
                  >
                    {machineId}
                  </option>
                );
              })
            )}
          </select>
        </div>

        <strong className="data-source">
        {selectedMachine
          ? "Live machine data"
       : "Waiting for machine data"}
       </strong>
      </div>

      <div className="topbar-actions">
        <span className="live-badge">
          <Wifi size={15} />
          Live
        </span>

        <button
          type="button"
          aria-label="Refresh machines"
          onClick={refreshMachines}
          title="Refresh machine list"
          disabled={loadingMachines}
        >
          <RefreshCw
            size={17}
            className={loadingMachines ? "spin" : ""}
          />
        </button>

        <button
          type="button"
          aria-label="Notifications"
        >
          <Bell size={18} />
        </button>

        <button
          type="button"
          aria-label="User account"
        >
          <CircleUserRound size={20} />
        </button>
      </div>
    </header>
  );
}