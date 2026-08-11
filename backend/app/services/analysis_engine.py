from typing import Any, Dict

from app.services.diagnosis.engine import diagnose_machine
from app.services.health_engine import calculate_health


# ============================================================
# CONSTANTS
# ============================================================

STATUS_PRIORITY = {
    "Healthy": 1,
    "Warning": 2,
    "Critical": 3,
    "Emergency": 4,
}


# ============================================================
# BASIC UTILITIES
# ============================================================

def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Keeps a numeric value inside the provided range.
    """

    return max(minimum, min(float(value), maximum))


def round_value(value: float) -> float:
    """
    Rounds numeric values consistently for API responses.
    """

    return round(float(value), 2)


# ============================================================
# STATUS NORMALISATION
# ============================================================

def normalise_status(status: str) -> str:
    """
    Converts different status names into PredictX AI's
    standard machine statuses.
    """

    value = str(status).strip().lower()

    status_map = {
        "healthy": "Healthy",
        "normal": "Healthy",
        "safe": "Healthy",
        "low": "Healthy",

        "warning": "Warning",
        "minor": "Warning",
        "moderate": "Warning",
        "medium": "Warning",
        "attention": "Warning",

        "critical": "Critical",
        "high": "Critical",
        "danger": "Critical",

        "emergency": "Emergency",
        "severe": "Emergency",
    }

    return status_map.get(value, "Warning")


def get_fault_status(
    fault_severity: str,
    fault_code: str | None = None,
) -> str:
    """
    Converts fault severity into an overall machine status.

    HLT001 is always treated as a healthy diagnosis.
    """

    if fault_code == "HLT001":
        return "Healthy"

    severity = str(fault_severity).strip().lower()

    severity_status_map = {
        "healthy": "Healthy",
        "normal": "Healthy",
        "safe": "Healthy",
        "low": "Healthy",

        "minor": "Warning",
        "moderate": "Warning",
        "medium": "Warning",
        "warning": "Warning",

        "high": "Critical",
        "critical": "Critical",
        "danger": "Critical",

        "emergency": "Emergency",
        "severe": "Emergency",
    }

    return severity_status_map.get(
        severity,
        "Warning",
    )


def choose_higher_status(
    health_status: str,
    diagnosis_status: str,
) -> str:
    """
    Returns the more serious status between health engine
    status and diagnosis engine status.
    """

    normal_health_status = normalise_status(
        health_status
    )

    normal_diagnosis_status = normalise_status(
        diagnosis_status
    )

    health_priority = STATUS_PRIORITY.get(
        normal_health_status,
        1,
    )

    diagnosis_priority = STATUS_PRIORITY.get(
        normal_diagnosis_status,
        1,
    )

    if diagnosis_priority > health_priority:
        return normal_diagnosis_status

    return normal_health_status


# ============================================================
# SCORE AND RISK LIMITS
# ============================================================

def get_minimum_failure_risk(
    status: str,
) -> float:
    """
    Minimum expected failure risk for each machine status.
    """

    risk_map = {
        "Healthy": 0.0,
        "Warning": 25.0,
        "Critical": 60.0,
        "Emergency": 85.0,
    }

    return risk_map.get(status, 0.0)


def get_maximum_health_score(
    status: str,
) -> float:
    """
    Prevents contradictory output such as Emergency status
    with a very high health score.
    """

    score_map = {
        "Healthy": 100.0,
        "Warning": 79.0,
        "Critical": 54.0,
        "Emergency": 25.0,
    }

    return score_map.get(status, 100.0)


def synchronise_health_score(
    original_health_score: float,
    status: str,
) -> float:
    """
    Restricts health score according to final machine status.
    """

    maximum_allowed_score = get_maximum_health_score(
        status
    )

    adjusted_score = min(
        float(original_health_score),
        maximum_allowed_score,
    )

    return round_value(
        clamp(
            adjusted_score,
            0.0,
            100.0,
        )
    )


# ============================================================
# DIAGNOSIS RISK
# ============================================================

def calculate_diagnosis_risk(
    confidence: float,
    severity: str,
    fault_code: str | None = None,
) -> float:
    """
    Calculates diagnosis-based failure risk using fault
    confidence and fault severity.
    """

    if fault_code == "HLT001":
        return 0.0

    severity_factor_map = {
        "healthy": 0.0,
        "normal": 0.0,
        "safe": 0.0,
        "low": 0.10,

        "minor": 0.25,
        "moderate": 0.45,
        "medium": 0.45,
        "warning": 0.45,

        "high": 0.70,
        "critical": 0.85,
        "emergency": 1.00,
        "severe": 1.00,
    }

    normalised_severity = str(
        severity
    ).strip().lower()

    severity_factor = severity_factor_map.get(
        normalised_severity,
        0.40,
    )

    safe_confidence = clamp(
        confidence,
        0.0,
        100.0,
    )

    diagnosis_risk = (
        safe_confidence * severity_factor
    )

    return round_value(diagnosis_risk)


def calculate_combined_failure_risk(
    health_risk: float,
    diagnosis_risk: float,
    status: str,
) -> float:
    """
    Combines health engine risk and diagnosis engine risk.

    Health engine receives greater weight because it is based
    directly on current sensor values.
    """

    combined_risk = (
        float(health_risk) * 0.65
        + float(diagnosis_risk) * 0.35
    )

    minimum_risk = get_minimum_failure_risk(
        status
    )

    combined_risk = max(
        combined_risk,
        minimum_risk,
    )

    return round_value(
        clamp(
            combined_risk,
            0.0,
            100.0,
        )
    )




# ============================================================
# ABNORMAL PARAMETER DETAILS
# ============================================================

def get_abnormal_parameters(
    sensor_analysis: Dict[str, Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Converts sensor-level health results into frontend-friendly
    abnormal parameter messages.
    """

    parameter_labels = {
        "temperature": ("Temperature", "°C"),
        "vibration": ("Vibration", "level"),
        "current": ("Current", "A"),
        "sound": ("Sound", "dB"),
    }

    abnormal_parameters: list[Dict[str, Any]] = []

    for parameter, data in sensor_analysis.items():
        condition = str(data.get("condition", "normal"))

        if condition == "normal":
            continue

        label, unit = parameter_labels.get(
            parameter,
            (parameter.replace("_", " " ).title(), ""),
        )

        message_map = {
            "below_normal": f"{label} is below the expected operating range.",
            "warning": f"{label} is slightly outside the normal operating range.",
            "critical": f"{label} is in the critical operating range.",
            "emergency": f"{label} has crossed the configured safety limit.",
        }

        abnormal_parameters.append({
            "parameter": parameter,
            "display_name": label,
            "value": round_value(data.get("value", 0.0)),
            "unit": unit,
            "condition": condition,
            "message": message_map.get(
                condition,
                str(data.get("message", "Abnormal sensor behaviour detected.")),
            ),
        })

    return abnormal_parameters


# ============================================================
# SUMMARY GENERATION
# ============================================================

def generate_unified_summary(
    status: str,
    health_score: float,
    failure_risk: float,
    fault_name: str,
    confidence: float,
    emergency_shutdown: bool,
) -> str:
    """
    Creates a dashboard-friendly machine summary.
    """

    if emergency_shutdown:
        return (
            f"PredictX AI detected {fault_name} with "
            f"{round_value(confidence)}% confidence. "
            f"The machine health score is "
            f"{round_value(health_score)} and failure risk is "
            f"{round_value(failure_risk)}%. Immediate shutdown "
            f"and maintenance inspection are recommended."
        )

    if status == "Healthy":
        return (
            f"The machine is operating normally with a health "
            f"score of {round_value(health_score)}. "
            f"No serious fault signature has been detected."
        )

    if status == "Warning":
        return (
            f"Early signs of {fault_name} have been detected "
            f"with {round_value(confidence)}% confidence. "
            f"Machine health is {round_value(health_score)} "
            f"and the estimated failure risk is "
            f"{round_value(failure_risk)}%. Continue monitoring "
            f"and schedule preventive inspection."
        )

    if status == "Critical":
        return (
            f"The machine shows critical symptoms of "
            f"{fault_name}. Diagnosis confidence is "
            f"{round_value(confidence)}%, health score is "
            f"{round_value(health_score)}, and failure risk is "
            f"{round_value(failure_risk)}%. Maintenance should "
            f"be performed as soon as possible."
        )

    return (
        f"Machine status is {status}. The most likely fault is "
        f"{fault_name} with {round_value(confidence)}% "
        f"confidence."
    )


# ============================================================
# MAIN UNIFIED ANALYSIS ENGINE
# ============================================================

def analyse_machine(
    temperature: float,
    vibration: float,
    current: float,
    sound: float,
) -> Dict[str, Any]:
    """
    Runs the complete PredictX AI analysis pipeline.

    Flow:
        Sensor readings
        -> Health engine
        -> Fault diagnosis engine
        -> Status synchronisation
        -> Health score synchronisation
        -> Failure risk calculation
        -> Emergency decision
        -> Unified response
    """

    # --------------------------------------------------------
    # HEALTH ENGINE
    # --------------------------------------------------------

    health_result = calculate_health(
        temperature=temperature,
        vibration=vibration,
        current=current,
        sound=sound,
    )

    # --------------------------------------------------------
    # DIAGNOSIS ENGINE
    # --------------------------------------------------------

    diagnosis_result = diagnose_machine(
        temperature=temperature,
        vibration=vibration,
        current=current,
        sound=sound,
    )

    primary_fault = diagnosis_result.primary_fault
    fault_rule = primary_fault.rule

    fault_name = fault_rule.name
    fault_code = fault_rule.code
    fault_severity = fault_rule.severity

    confidence = round_value(
        primary_fault.confidence
    )

    sensor_analysis = health_result["sensor_analysis"]
    abnormal_parameters = get_abnormal_parameters(
        sensor_analysis
    )

    # --------------------------------------------------------
    # STATUS SYNCHRONISATION
    # --------------------------------------------------------

    health_status = health_result["status"]

    diagnosis_status = get_fault_status(
        fault_severity=fault_severity,
        fault_code=fault_code,
    )

    final_status = choose_higher_status(
        health_status=health_status,
        diagnosis_status=diagnosis_status,
    )

    is_healthy_diagnosis = (
        fault_code == "HLT001"
        and confidence >= 70.0
        and health_result["status"] == "Healthy"
        and not health_result["emergency_shutdown"]
    )

    if is_healthy_diagnosis:
        final_status = "Healthy"

    # --------------------------------------------------------
    # EMERGENCY LOGIC
    # --------------------------------------------------------

    emergency_shutdown = bool(
        health_result["emergency_shutdown"]
        or final_status == "Emergency"
    )

    if emergency_shutdown:
        final_status = "Emergency"

    # --------------------------------------------------------
    # HEALTH SCORE SYNCHRONISATION
    # --------------------------------------------------------

    health_score = synchronise_health_score(
        original_health_score=health_result[
            "health_score"
        ],
        status=final_status,
    )

    # --------------------------------------------------------
    # RISK SYNCHRONISATION
    # --------------------------------------------------------

    diagnosis_risk = calculate_diagnosis_risk(
        confidence=confidence,
        severity=fault_severity,
        fault_code=fault_code,
    )

    failure_risk = calculate_combined_failure_risk(
        health_risk=health_result["failure_risk"],
        diagnosis_risk=diagnosis_risk,
        status=final_status,
    )

    # Healthy diagnosis should keep original healthy values.
    if is_healthy_diagnosis:
        final_status = "Healthy"

        health_score = round_value(
            health_result["health_score"]
        )

        failure_risk = round_value(
            min(
                health_result["failure_risk"],
                10.0,
            )
        )

        emergency_shutdown = False

    # Emergency status always requires high failure risk.
    if emergency_shutdown:
        failure_risk = max(
            failure_risk,
            90.0,
        )

    failure_risk = round_value(
        clamp(
            failure_risk,
            0.0,
            100.0,
        )
    )

    # --------------------------------------------------------
    # USER-FRIENDLY DIAGNOSIS LABEL
    # --------------------------------------------------------

    # HLT001 means the fault-rule engine did not identify a named
    # component fault. The machine status from the health/safety engine
    # must still override the healthy fallback diagnosis.
    display_confidence = confidence

    if fault_code == "HLT001" and final_status == "Emergency":
        emergency_count = sum(
            1 for item in abnormal_parameters
            if item.get("condition") == "emergency"
        )
        detected_condition = "Multiple safety limits exceeded"
        display_fault_code = "SAF001"
        display_confidence = min(100.0, 80.0 + emergency_count * 5.0)
        display_root_cause = (
            "The current readings exceed one or more configured safety "
            "limits. A specific failed component cannot be confirmed from "
            "this single reading, but the operating condition is unsafe."
        )
        display_possible_causes = [
            item["message"] for item in abnormal_parameters
        ] or ["One or more configured safety limits were exceeded."]
        display_recommendation = (
            "Stop the machine immediately. Isolate the power supply and "
            "inspect the motor, load, mounting, wiring and sensors before restart."
        )
        display_priority = "Immediate"
        display_downtime = "Inspection required before restart"
        display_severity = "Emergency"

    elif fault_code == "HLT001" and final_status == "Critical":
        detected_condition = "Severe abnormal operating condition"
        display_fault_code = "MON002"
        display_confidence = max(70.0, min(90.0, 55.0 + len(abnormal_parameters) * 8.0))
        display_root_cause = (
            "Several readings are in a critical range, but the current "
            "pattern does not yet identify one specific component fault."
        )
        display_possible_causes = [
            item["message"] for item in abnormal_parameters
        ] or ["A severe operating abnormality is present."]
        display_recommendation = (
            "Stop or reduce operation and arrange an inspection before the "
            "next production cycle. Check load, bearings, alignment, wiring "
            "and sensor installation."
        )
        display_priority = "Urgent"
        display_downtime = "Inspection required before continued operation"
        display_severity = "Critical"

    elif fault_code == "HLT001" and final_status == "Warning":
        detected_condition = "Abnormal operating condition"
        display_fault_code = "MON001"
        display_confidence = max(35.0, min(65.0, 30.0 + len(abnormal_parameters) * 8.0))
        display_root_cause = (
            "One or more sensor values are outside the normal operating "
            "range, but the current pattern does not match a confirmed fault signature."
        )
        display_possible_causes = [
            item["message"] for item in abnormal_parameters
        ] or ["A temporary operating fluctuation may be present."]
        display_recommendation = (
            "Continue monitoring the next readings. If the condition persists, "
            "inspect mounting, alignment, lubrication and sensor condition."
        )
        display_priority = "Monitor"
        display_downtime = "No immediate downtime required"
        display_severity = "Moderate"

    else:
        detected_condition = fault_name
        display_fault_code = fault_code
        display_root_cause = fault_rule.root_cause
        display_possible_causes = fault_rule.possible_causes
        display_recommendation = fault_rule.recommendation
        display_priority = fault_rule.maintenance_priority
        display_downtime = fault_rule.estimated_downtime
        display_severity = fault_severity
        display_confidence = confidence

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = generate_unified_summary(
        status=final_status,
        health_score=health_score,
        failure_risk=failure_risk,
        fault_name=detected_condition,
        confidence=display_confidence,
        emergency_shutdown=emergency_shutdown,
    )

    # --------------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------------

    return {
        "health_score": health_score,
        "status": final_status,
        "failure_risk": failure_risk,

        "severity": display_severity,
        "emergency_shutdown": emergency_shutdown,

        "detected_fault": detected_condition,
        "fault_code": display_fault_code,
        "confidence": round_value(display_confidence),

        "root_cause": display_root_cause,
        "possible_causes": display_possible_causes,
        "recommendation": display_recommendation,

        "maintenance_priority": display_priority,
        "estimated_downtime": display_downtime,

        "sensor_analysis": sensor_analysis,
        "abnormal_parameters": abnormal_parameters,

        "summary": summary,

        # Used by serializer in main.py.
        "diagnosis_result": diagnosis_result,
    }