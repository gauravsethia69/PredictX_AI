const RENDER_API_BASE_URL = "https://predictx-ai-ef8m.onrender.com";

export const REFRESH_INTERVAL =
  Number(import.meta.env.VITE_REFRESH_INTERVAL) || 3000;

const DIRECT_TIMEOUT_MS = 90000;
const PROXY_TIMEOUT_MS = 20000;

async function fetchJson(url, options = {}, timeoutMs = DIRECT_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      cache: "no-store",
    });

    const contentType = response.headers.get("content-type") || "";
    let body = null;

    if (contentType.includes("application/json")) {
      body = await response.json();
    } else {
      const raw = await response.text();
      body = raw ? { detail: raw } : null;
    }

    if (!response.ok) {
      const error = new Error(
        body?.detail || body?.message || `Request failed with status ${response.status}.`
      );
      error.status = response.status;
      error.responseData = body;
      throw error;
    }

    return body;
  } finally {
    window.clearTimeout(timer);
  }
}

async function apiRequest(path, options = {}) {
  const directUrl = `${RENDER_API_BASE_URL}${path}`;

  // 1) Direct Render request. GET requests intentionally have NO Content-Type
  // header so the browser can make a simple CORS request without preflight.
  try {
    return await fetchJson(directUrl, options, DIRECT_TIMEOUT_MS);
  } catch (directError) {
    console.warn("Direct Render request failed; trying Vercel proxy:", directError);
  }

  // 2) Fallback through Vercel rewrite (/api/* -> Render /api/*).
  return fetchJson(path, options, PROXY_TIMEOUT_MS);
}

// --------------------------------------------------
// BACKEND HEALTH
// --------------------------------------------------
export function getBackendHealth() {
  return apiRequest("/api/health");
}

// --------------------------------------------------
// MACHINES
// --------------------------------------------------
export async function getMachines() {
  const data = await apiRequest("/api/machines");

  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.machines)) return data.machines;
  return [];
}

// --------------------------------------------------
// MACHINE DISCOVERY
// --------------------------------------------------
export async function discoverMachines(limit = 100) {
  try {
    const machines = await getMachines();
    if (machines.length > 0) return machines;
  } catch (error) {
    console.warn("GET /api/machines failed. Trying readings discovery.", error);
  }

  try {
    const readings = await getReadings(undefined, limit);
    const machineMap = new Map();

    readings.forEach((reading) => {
      const machineId = reading?.machine_id;
      if (!machineId) return;

      const timestamp = reading?.timestamp || reading?.created_at || "";
      const previous = machineMap.get(machineId);

      if (!previous || new Date(timestamp) > new Date(previous.timestamp || 0)) {
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
    console.error("Machine discovery failed completely:", error);
    throw error;
  }
}

// --------------------------------------------------
// READINGS
// --------------------------------------------------
export async function getReadings(machineId, limit = 30) {
  const query = new URLSearchParams({ limit: String(limit) });
  if (machineId) query.set("machine_id", machineId);

  const data = await apiRequest(`/api/readings?${query.toString()}`);
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.readings)) return data.readings;
  return [];
}

// --------------------------------------------------
// LATEST READING
// --------------------------------------------------
export async function getLatestReading(machineId) {
  if (!machineId) throw new Error("A machine must be selected.");

  const data = await apiRequest(
    `/api/readings/latest/${encodeURIComponent(machineId)}`
  );

  return data?.reading || data;
}

// --------------------------------------------------
// TRENDS
// --------------------------------------------------
export function getTrends(machineId, limit = 30) {
  if (!machineId) throw new Error("A machine must be selected.");
  const query = new URLSearchParams({ limit: String(limit) });
  return apiRequest(`/api/trends/${encodeURIComponent(machineId)}?${query.toString()}`);
}

// --------------------------------------------------
// ALERTS
// --------------------------------------------------
export function getAlerts(machineId, limit = 30) {
  if (!machineId) throw new Error("A machine must be selected.");
  const query = new URLSearchParams({ limit: String(limit) });
  return apiRequest(`/api/alerts/${encodeURIComponent(machineId)}?${query.toString()}`);
}

// --------------------------------------------------
// SEND SENSOR DATA
// --------------------------------------------------
export function sendSensorData(payload) {
  return apiRequest("/api/sensor-data", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

// --------------------------------------------------
// ERROR HANDLING
// --------------------------------------------------
export function getReadableError(error) {
  if (error?.name === "AbortError") {
    return "Backend request timed out while Render was waking up.";
  }

  if (error?.responseData?.detail) {
    return String(error.responseData.detail);
  }

  if (error?.message) {
    return error.message;
  }

  return `Cannot connect to PredictX backend at ${RENDER_API_BASE_URL}.`;
}
