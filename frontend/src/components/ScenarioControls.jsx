import { useEffect, useRef, useState } from "react";
import { Play, RotateCcw, Square, Sparkles } from "lucide-react";
import {
  getReadableError,
  sendSensorData
} from "../api/predictxApi";
import { useMachine } from "../context/MachineContext";

const scenarios = {
  Healthy: {
    temperature: 43.2,
    vibration: 0.7,
    current: 1.8,
    sound: 52.4
  },
  Warning: {
    temperature: 63.5,
    vibration: 2.1,
    current: 3.4,
    sound: 71.6
  },
  Critical: {
    temperature: 84.7,
    vibration: 5.3,
    current: 5.8,
    sound: 89.5
  },
  Emergency: {
    temperature: 109.4,
    vibration: 8.6,
    current: 8.2,
    sound: 108.3
  }
};

const autoSequence = [
  "Healthy",
  "Healthy",
  "Warning",
  "Warning",
  "Critical",
  "Emergency"
];

export default function ScenarioControls({ onSent }) {
  const { selectedMachineId, refreshMachines } = useMachine();
  const [sending, setSending] = useState("");
  const [newMachineId, setNewMachineId] = useState("");
  const [message, setMessage] = useState("");
  const [autoRunning, setAutoRunning] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const autoIndex = useRef(0);
  const timerRef = useRef(null);

  async function runScenario(name, silent = false) {
    const machineId = newMachineId.trim() || selectedMachineId || "MACHINE-001";

    try {
      setSending(name);
      setMessage("");

      setActiveStep(Math.max(0, autoSequence.indexOf(name)));

      await sendSensorData({
        machine_id: machineId,
        ...scenarios[name],
        motor_running: true,
        source: "simulator"
      });

      setNewMachineId("");
      await refreshMachines();
      await onSent?.();

      if (!silent) {
        setMessage(`${name} reading sent to ${machineId}.`);
      }
    } catch (error) {
      setMessage(getReadableError(error));
      stopAutoDemo();
    } finally {
      setSending("");
    }
  }

  function startAutoDemo() {
    if (autoRunning) return;

    autoIndex.current = 0;
    setAutoRunning(true);
    setMessage("Auto demo started: Healthy → Warning → Critical → Emergency");

    runScenario(autoSequence[0], true);
    autoIndex.current = 1;

    timerRef.current = window.setInterval(() => {
      const scenario = autoSequence[autoIndex.current % autoSequence.length];
      runScenario(scenario, true);
      autoIndex.current += 1;
    }, 4000);
  }

  function stopAutoDemo() {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setAutoRunning(false);
    setActiveStep(0);
  }

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
      }
    };
  }, []);

  return (
    <section className="demo-console">
      <div className="demo-console-heading">
        <div>
          <span className="eyebrow"><Sparkles size={13} /> Simulation studio</span>
          <strong>Test the complete PredictX pipeline without hardware</strong>
        </div>
        <span className="simulation-badge">SIMULATION MODE</span>
      </div>

      <div className="scenario-controls">
        <input
          value={newMachineId}
          onChange={(event) => setNewMachineId(event.target.value)}
          placeholder={selectedMachineId || "MACHINE-001"}
          aria-label="Machine ID for demo data"
        />

        {Object.keys(scenarios).map((name) => (
          <button
            key={name}
            className={`scenario-${name.toLowerCase()}`}
            onClick={() => runScenario(name)}
            disabled={Boolean(sending) || autoRunning}
          >
            {sending === name ? "Sending..." : name}
          </button>
        ))}

        {!autoRunning ? (
          <button className="auto-demo-button" onClick={startAutoDemo} disabled={Boolean(sending)}>
            <Play size={14} /> Auto demo
          </button>
        ) : (
          <button className="stop-demo-button" onClick={stopAutoDemo}>
            <Square size={13} /> Stop demo
          </button>
        )}
      </div>

      <div className="demo-sequence-track" aria-label="Automatic demo sequence">
        {autoSequence.map((step, index) => (
          <div
            key={`${step}-${index}`}
            className={`demo-sequence-step ${autoRunning && index === activeStep ? "active" : ""} ${index < activeStep ? "complete" : ""}`}
          >
            <i />
            <span>{step}</span>
          </div>
        ))}
        <button type="button" className="reset-demo-button" onClick={() => { stopAutoDemo(); setMessage(""); }} title="Reset demo state">
          <RotateCcw size={13} /> Reset
        </button>
      </div>

      {message && <p className="demo-message">{message}</p>}
    </section>
  );
}
