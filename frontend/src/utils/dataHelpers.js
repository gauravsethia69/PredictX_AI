export function safeNumber(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function getAnalysis(reading) {
  return reading?.analysis || {};
}

export function getDiagnosis(reading) {
  return reading?.diagnosis || {};
}

export function getPrimaryFault(reading) {
  return getDiagnosis(reading)?.primary_fault || {};
}

// V2/V3 contract: prediction fields come directly from the ESP32 payload.
export function getHealthScore(reading) {
  return safeNumber(reading?.health ?? getAnalysis(reading).health_score, 0);
}

export function getFailureRisk(reading) {
  return safeNumber(reading?.failure_probability ?? getAnalysis(reading).failure_risk, 0);
}

export function getStatus(reading) {
  return reading?.machine_status || getAnalysis(reading).status || "—";
}

export function getSeverity(reading) {
  return reading?.failure_stage || getAnalysis(reading).severity || getPrimaryFault(reading).severity || "—";
}

export function getFault(reading) {
  return reading?.diagnosis || getAnalysis(reading).detected_fault || getPrimaryFault(reading).name || "—";
}

export function getFaultCode(reading) {
  return getAnalysis(reading).fault_code || getPrimaryFault(reading).code || "—";
}

export function getConfidence(reading) {
  const value = reading?.prediction_confidence ?? getAnalysis(reading).confidence ?? getPrimaryFault(reading).confidence;
  return value == null ? null : safeNumber(value, 0);
}

export function getRecommendationObject(reading) {
  const backendRecommendation = reading?.recommendation;
  const value = getAnalysis(reading).recommended_action;

  if (typeof backendRecommendation === "string" && backendRecommendation.trim()) {
    return {
      action: backendRecommendation,
      timeframe: reading?.failure_stage || "—",
      machine_can_continue: reading?.motor_running ?? null,
      service_time_estimate: reading?.remaining_life_hours != null ? `${safeNumber(reading.remaining_life_hours)} hrs remaining life` : "—",
      estimate_note: reading?.prediction_explanation || "—"
    };
  }

  if (!value || typeof value !== "object") {
    return { action: "—", timeframe: "—", machine_can_continue: null, service_time_estimate: "—", estimate_note: "—" };
  }

  return {
    action: value.action || "—",
    timeframe: value.timeframe || "—",
    machine_can_continue: typeof value.machine_can_continue === "boolean" ? value.machine_can_continue : null,
    service_time_estimate: value.service_time_estimate || "—",
    estimate_note: value.estimate_note || "—"
  };
}

export function getRecommendation(reading) {
  return reading?.recommendation || getAnalysis(reading).recommendation || getRecommendationObject(reading).action;
}

export function getShutdownRecommended(reading) {
  return String(reading?.machine_status || "").toUpperCase() === "STOP" || Boolean(getAnalysis(reading).shutdown_recommended);
}

export function getMaintenancePriority(reading) {
  if (String(reading?.failure_stage || "").toLowerCase().includes("emergency")) return "HIGH";
  return getAnalysis(reading).maintenance_priority || getPrimaryFault(reading).maintenance_priority || "—";
}

export function getEstimatedDowntime(reading) {
  if (reading?.remaining_life_hours != null) return `${safeNumber(reading.remaining_life_hours)} hrs`;
  return getAnalysis(reading).estimated_downtime || getPrimaryFault(reading).estimated_downtime || "—";
}

export function getDataSource(reading) {
  return {
    type: reading?.source || reading?.data_source?.type || "—",
    message: reading?.prediction_explanation || reading?.data_source?.message || "Live ESP32 telemetry"
  };
}

export function getTestContext(reading) {
  return reading?.test_context || {};
}

export function extractAlerts(payload) {
  const possible = payload?.alerts || [];
  if (!Array.isArray(possible)) return [];

  return possible.map((alert, index) => ({
    id: alert?.id ?? alert?.code ?? index,
    title: alert?.title || alert?.code || "Machine Alert",
    message: alert?.message || "—",
    severity: alert?.severity || "—",
    timestamp: alert?.timestamp || alert?.created_at || "",
    category: alert?.category || "—",
    action_required: alert?.action_required || "—",
    immediate_action: Boolean(alert?.immediate_action)
  }));
}

export function normalizeReadings(readings = []) {
  return [...readings]
    .reverse()
    .map((item, index) => ({
      raw: item,
      index: index + 1,
      timestamp: item.timestamp || "",
      time: formatTime(item.timestamp),
      temperature: safeNumber(item.temperature),
      vibration: safeNumber(item.vibration),
      current: safeNumber(item.current),
      sound: safeNumber(item.sound),
      health: getHealthScore(item),
      risk: getFailureRisk(item),
      status: getStatus(item)
    }));
}

export function formatTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function formatDateTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

export function statusTone(status = "") {
  const value = String(status).toLowerCase();
  if (value.includes("stop") || value.includes("emergency") || value.includes("critical")) return "danger";
  if (value.includes("warning") || value.includes("attention")) return "warning";
  if (value.includes("healthy") || value.includes("normal") || value.includes("good")) return "success";
  return "neutral";
}
