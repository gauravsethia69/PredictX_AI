import axios from "axios";
const API_BASE_URL = "";

export const REFRESH_INTERVAL =
  Number(import.meta.env.VITE_REFRESH_INTERVAL) || 3000;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// --------------------------------------------------
// BACKEND HEALTH
// --------------------------------------------------

export async function getBackendHealth() {
  const { data } = await api.get("/api/health");
  return data;
}

// --------------------------------------------------
// MACHINES
// --------------------------------------------------

export async function getMachines() {
  const { data } = await api.get("/api/machines");

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.machines)) {
    return data.machines;
  }

  return [];
}

// --------------------------------------------------
// MACHINE DISCOVERY
// --------------------------------------------------

export async function discoverMachines(limit = 100) {
  // First try the dedicated machine endpoint.
  try {
    const machines = await getMachines();

    if (machines.length > 0) {
      return machines;
    }
  } catch (error) {
    console.warn(
      "GET /api/machines failed. Trying readings discovery.",
      error
    );
  }

  // Fall back to discovering machines from readings.
  try {
    const readings = await getReadings(undefined, limit);

    const machineMap = new Map();

    readings.forEach((reading) => {
      const machineId = reading?.machine_id;

      if (!machineId) {
        return;
      }

      const timestamp =
        reading?.timestamp ||
        reading?.created_at ||
        "";

      const previous = machineMap.get(machineId);

      if (
        !previous ||
        new Date(timestamp) >
          new Date(previous.timestamp || 0)
      ) {
        machineMap.set(machineId, {
          machine_id: machineId,
          timestamp,
          source: reading?.source || "unknown",
          motor_running: reading?.motor_running,
          status:
            reading?.analysis?.status ||
            reading?.status ||
            reading?.machine_status ||
            "Unknown",
        });
      }
    });

    return Array.from(machineMap.values()).sort((a, b) =>
      a.machine_id.localeCompare(b.machine_id)
    );
  } catch (error) {
    console.warn(
      "Machine discovery from readings failed.",
      error
    );

    return [];
  }
}

// --------------------------------------------------
// READINGS
// --------------------------------------------------

export async function getReadings(machineId, limit = 30) {
  const params = {
    limit,
  };

  if (machineId) {
    params.machine_id = machineId;
  }

  const { data } = await api.get("/api/readings", {
    params,
  });

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.readings)) {
    return data.readings;
  }

  return [];
}

// --------------------------------------------------
// LATEST READING
// --------------------------------------------------

export async function getLatestReading(machineId) {
  if (!machineId) {
    throw new Error("A machine must be selected.");
  }

  const { data } = await api.get(
    `/api/readings/latest/${encodeURIComponent(machineId)}`
  );

  return data?.reading || data;
}

// --------------------------------------------------
// TRENDS
// --------------------------------------------------

export async function getTrends(machineId, limit = 30) {
  if (!machineId) {
    throw new Error("A machine must be selected.");
  }

  const { data } = await api.get(
    `/api/trends/${encodeURIComponent(machineId)}`,
    {
      params: {
        limit,
      },
    }
  );

  return data;
}

// --------------------------------------------------
// ALERTS
// --------------------------------------------------

export async function getAlerts(machineId, limit = 30) {
  if (!machineId) {
    throw new Error("A machine must be selected.");
  }

  const { data } = await api.get(
    `/api/alerts/${encodeURIComponent(machineId)}`,
    {
      params: {
        limit,
      },
    }
  );

  return data;
}

// --------------------------------------------------
// SEND SENSOR DATA
// --------------------------------------------------

export async function sendSensorData(payload) {
  const { data } = await api.post(
    "/api/sensor-data",
    payload
  );

  return data;
}

// --------------------------------------------------
// ERROR HANDLING
// --------------------------------------------------

function normaliseErrorDetail(detail) {
  if (!detail) {
    return "";
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (item && typeof item === "object") {
          const location = Array.isArray(item.loc)
            ? item.loc.join(" → ")
            : "";

          const message =
            item.msg ||
            item.message ||
            item.type ||
            "Validation error";

          return location
            ? `${location}: ${message}`
            : message;
        }

        return String(item);
      })
      .join(" | ");
  }

  if (typeof detail === "object") {
    return (
      detail.message ||
      detail.msg ||
      detail.error ||
      JSON.stringify(detail)
    );
  }

  return String(detail);
}

export function getReadableError(error) {
  if (error?.code === "ECONNABORTED") {
    return "Backend request timed out.";
  }

  if (!error?.response) {
    return (
      error?.message ||
      `Cannot connect to backend at ${API_BASE_URL}. Start FastAPI and verify CORS.`
    );
  }

  const responseData = error.response?.data || {};

  const detail = normaliseErrorDetail(
    responseData.detail
  );

  const message = normaliseErrorDetail(
    responseData.message
  );

  return (
    detail ||
    message ||
    `Request failed with status ${error.response.status}.`
  );
}