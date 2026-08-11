import { useCallback, useEffect, useState } from "react";
import {
  getAlerts,
  getBackendHealth,
  getLatestReading,
  getReadings,
  getReadableError,
  getTrends,
  REFRESH_INTERVAL
} from "../api/predictxApi";
import { useMachine } from "../context/MachineContext";

export default function usePredictXData({
  autoRefresh = true,
  limit = 30
} = {}) {
  const { selectedMachineId } = useMachine();

  const [latest, setLatest] = useState(null);
  const [readings, setReadings] = useState([]);
  const [trends, setTrends] = useState(null);
  const [alerts, setAlerts] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    if (!selectedMachineId) {
      setLatest(null);
      setReadings([]);
      setTrends(null);
      setAlerts(null);
      setLoading(false);
      setError("No machine data is available in the backend yet.");
      return;
    }

    const results = await Promise.allSettled([
      getBackendHealth(),
      getLatestReading(selectedMachineId),
      getReadings(selectedMachineId, limit),
      getTrends(selectedMachineId, limit),
      getAlerts(selectedMachineId, limit)
    ]);

    setBackendOnline(results[0].status === "fulfilled");

    if (results[1].status === "fulfilled") {
      setLatest(results[1].value);
      setError("");
    } else {
      setError(getReadableError(results[1].reason));
    }

    if (results[2].status === "fulfilled") {
      setReadings(results[2].value);
    } else {
      setReadings([]);
    }

    if (results[3].status === "fulfilled") {
      setTrends(results[3].value);
    } else {
      setTrends(null);
    }

    if (results[4].status === "fulfilled") {
      setAlerts(results[4].value);
    } else {
      setAlerts(null);
    }

    setLoading(false);
  }, [limit, selectedMachineId]);

  useEffect(() => {
    setLoading(true);
    refresh();

    if (!autoRefresh) return;

    const timer = window.setInterval(refresh, REFRESH_INTERVAL);
    return () => window.clearInterval(timer);
  }, [autoRefresh, refresh]);

  return {
    machineId: selectedMachineId,
    latest,
    readings,
    trends,
    alerts,
    backendOnline,
    loading,
    error,
    refresh
  };
}
