from __future__ import annotations

from typing import Any, Dict, List


# ============================================================
# ALERT PRIORITY
# ============================================================

ALERT_PRIORITY = {
    "Info": 1,
    "Low": 2,
    "Medium": 3,
    "High": 4,
    "Critical": 5,
}


# ============================================================
# BASIC UTILITIES
# ============================================================

def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:

    return max(
        minimum,
        min(float(value), maximum),
    )


def round_value(
    value: float,
    digits: int = 2,
) -> float:

    return round(
        float(value),
        digits,
    )


# ============================================================
# STATUS NORMALIZATION
# ============================================================

def normalise_status(
    status: str,
) -> str:
    """
    Converts Arduino status into backend
    standard status.

    Arduino is the source of truth.

    STOP means relay/machine stopped.
    It does NOT automatically mean Emergency.
    """

    value = str(
        status
    ).strip().lower()

    status_map = {

        # ----------------------------------------------------
        # Healthy
        # ----------------------------------------------------

        "healthy": "Healthy",
        "normal": "Healthy",
        "safe": "Healthy",
        "good": "Healthy",

        # Arduino may report STOP when relay is stopped.
        # Do NOT treat it as an emergency.
        "stop": "Healthy",

        # ----------------------------------------------------
        # Warning
        # ----------------------------------------------------

        "warning": "Warning",
        "minor": "Warning",
        "moderate": "Warning",
        "degrading": "Warning",
        "attention": "Warning",

        # ----------------------------------------------------
        # Critical
        # ----------------------------------------------------

        "critical": "Critical",
        "high": "Critical",
        "danger": "Critical",

        # ----------------------------------------------------
        # Emergency
        # ----------------------------------------------------

        "emergency": "Emergency",
        "severe": "Emergency",
    }

    return status_map.get(
        value,
        "Warning",
    )


# ============================================================
# ALERT CREATOR
# ============================================================

def create_alert(
    code: str,
    title: str,
    message: str,
    severity: str,
    category: str,
    action_required: str,
    immediate_action: bool = False,
    sensor: str | None = None,
) -> Dict[str, Any]:

    return {

        "code": code,

        "title": title,

        "message": message,

        "severity": severity,

        "priority": ALERT_PRIORITY.get(
            severity,
            1,
        ),

        "category": category,

        "sensor": sensor,

        "action_required": action_required,

        "immediate_action": immediate_action,
    }


# ============================================================
# MACHINE STATUS ALERTS
# ============================================================

def generate_status_alerts(
    analysis_result: Dict[str, Any],
) -> List[Dict[str, Any]]:

    alerts: List[
        Dict[str, Any]
    ] = []

    status = normalise_status(
        analysis_result.get(
            "status",
            "Warning",
        )
    )

    health_score = round_value(
        analysis_result.get(
            "health_score",
            0.0,
        )
    )

    failure_risk = round_value(
        analysis_result.get(
            "failure_risk",
            0.0,
        )
    )

    fault_name = analysis_result.get(
        "detected_fault",
        "Unknown condition",
    )

    recommendation = analysis_result.get(
        "recommendation",
        "Inspect the machine.",
    )

    emergency_shutdown = bool(
        analysis_result.get(
            "emergency_shutdown",
            False,
        )
    )

    # ========================================================
    # EMERGENCY
    # ========================================================

    if (
        emergency_shutdown
        or status == "Emergency"
    ):

        alerts.append(
            create_alert(

                code="ALT-EMERGENCY-001",

                title=(
                    "Immediate Safety Attention Required"
                ),

                message=(
                    f"The Arduino detected a serious "
                    f"machine condition associated with "
                    f"{fault_name}. "
                    f"Machine health is "
                    f"{health_score} and failure risk "
                    f"is {failure_risk}%."
                ),

                severity="Critical",

                category="Emergency",

                action_required=(
                    "Stopping the machine is recommended. "
                    "Perform a physical inspection before "
                    "restarting it."
                ),

                immediate_action=True,
            )
        )

        return alerts

    # ========================================================
    # CRITICAL
    # ========================================================

    if status == "Critical":

        alerts.append(
            create_alert(

                code="ALT-CRITICAL-001",

                title=(
                    "Critical Machine Condition"
                ),

                message=(
                    f"The Arduino reports a critical "
                    f"machine condition associated with "
                    f"{fault_name}. "
                    f"Machine health is "
                    f"{health_score} and failure risk "
                    f"is {failure_risk}%."
                ),

                severity="High",

                category="Machine health",

                action_required=(
                    recommendation
                ),

                immediate_action=True,
            )
        )

    # ========================================================
    # WARNING
    # ========================================================

    elif status == "Warning":

        alerts.append(
            create_alert(

                code="ALT-WARNING-001",

                title=(
                    "Preventive Inspection Recommended"
                ),

                message=(
                    f"The Arduino reports a warning "
                    f"condition associated with "
                    f"{fault_name}. "
                    f"Current failure risk is "
                    f"{failure_risk}%."
                ),

                severity="Medium",

                category="Preventive maintenance",

                action_required=(
                    recommendation
                ),

                immediate_action=False,
            )
        )

    # ========================================================
    # HEALTHY
    # ========================================================

    elif status == "Healthy":

        alerts.append(
            create_alert(

                code="ALT-HEALTHY-001",

                title=(
                    "Machine Operating Normally"
                ),

                message=(
                    f"The Arduino reports normal "
                    f"machine operation. "
                    f"Health score is "
                    f"{health_score} and estimated "
                    f"failure risk is "
                    f"{failure_risk}%."
                ),

                severity="Info",

                category="Machine health",

                action_required=(
                    "Continue routine condition monitoring."
                ),

                immediate_action=False,
            )
        )

    return alerts


# ============================================================
# TREND ALERTS
# ============================================================

def generate_machine_trend_alerts(
    trend_result: Dict[str, Any],
) -> List[Dict[str, Any]]:

    alerts: List[
        Dict[str, Any]
    ] = []

    machine_trend = trend_result.get(
        "machine_trend",
        "Insufficient data",
    )

    trend_risk_score = round_value(
        trend_result.get(
            "trend_risk_score",
            0.0,
        )
    )

    if machine_trend == "Degrading":

        alerts.append(
            create_alert(

                code="ALT-TREND-001",

                title=(
                    "Machine Condition Degrading"
                ),

                message=(
                    "Historical sensor readings indicate "
                    "that machine condition is gradually "
                    "degrading. "
                    f"Trend risk score is "
                    f"{trend_risk_score}%."
                ),

                severity="High",

                category="Historical trend",

                action_required=(
                    "Schedule preventive maintenance "
                    "and inspect the fastest-rising "
                    "sensor values."
                ),

                immediate_action=False,
            )
        )

    elif machine_trend == "Improving":

        alerts.append(
            create_alert(

                code="ALT-TREND-002",

                title=(
                    "Machine Condition Improving"
                ),

                message=(
                    "Historical readings show an "
                    "improvement in machine condition."
                ),

                severity="Info",

                category="Historical trend",

                action_required=(
                    "Continue monitoring to confirm "
                    "that the improvement remains stable."
                ),

                immediate_action=False,
            )
        )

    return alerts


# ============================================================
# SENSOR TREND ALERTS
# ============================================================

def generate_sensor_trend_alerts(
    trend_result: Dict[str, Any],
) -> List[Dict[str, Any]]:

    alerts: List[
        Dict[str, Any]
    ] = []

    sensor_trends = trend_result.get(
        "sensor_trends",
        {},
    )

    for (
        sensor_name,
        sensor_data,
    ) in sensor_trends.items():

        trend = sensor_data.get(
            "trend",
            "Stable",
        )

        percentage_change = round_value(
            sensor_data.get(
                "percentage_change",
                0.0,
            )
        )

        if trend != "Increasing":
            continue

        readable_sensor = (
            sensor_name
            .replace("_", " ")
            .title()
        )

        alerts.append(
            create_alert(

                code=(
                    "ALT-SENSOR-TREND-"
                    f"{sensor_name.upper()}"
                ),

                title=(
                    f"{readable_sensor} Increasing"
                ),

                message=(
                    f"{readable_sensor} increased by "
                    f"{percentage_change}% across "
                    f"the analysed readings."
                ),

                severity="Medium",

                category="Sensor trend",

                sensor=sensor_name,

                action_required=(
                    f"Inspect the machine components "
                    f"associated with "
                    f"{readable_sensor.lower()}."
                ),

                immediate_action=False,
            )
        )

    return alerts


# ============================================================
# ANOMALY ALERTS
# ============================================================

def generate_anomaly_alerts(
    trend_result: Dict[str, Any],
) -> List[Dict[str, Any]]:

    alerts: List[
        Dict[str, Any]
    ] = []

    anomalies = trend_result.get(
        "latest_anomalies",
        [],
    )

    severity_map = {
        "Low": "Low",
        "Moderate": "Medium",
        "High": "High",
    }

    for anomaly in anomalies:

        if not anomaly.get(
            "is_anomaly",
            False,
        ):
            continue

        sensor_name = anomaly.get(
            "sensor",
            "unknown_sensor",
        )

        readable_sensor = (
            sensor_name
            .replace("_", " ")
            .title()
        )

        anomaly_severity = anomaly.get(
            "severity",
            "Low",
        )

        alert_severity = severity_map.get(
            anomaly_severity,
            "Medium",
        )

        direction = anomaly.get(
            "direction",
            "Sudden change",
        )

        percentage_change = abs(
            round_value(
                anomaly.get(
                    "percentage_change",
                    0.0,
                )
            )
        )

        alerts.append(
            create_alert(

                code=(
                    "ALT-ANOMALY-"
                    f"{sensor_name.upper()}"
                ),

                title=(
                    f"{readable_sensor} "
                    f"Anomaly Detected"
                ),

                message=(
                    f"{direction} detected in "
                    f"{readable_sensor.lower()}. "
                    f"The latest value changed by "
                    f"{percentage_change}%."
                ),

                severity=alert_severity,

                category="Sensor anomaly",

                sensor=sensor_name,

                action_required=(
                    f"Verify the "
                    f"{readable_sensor.lower()} "
                    f"sensor and inspect related "
                    f"machine parts."
                ),

                immediate_action=(
                    alert_severity == "High"
                ),
            )
        )

    return alerts


# ============================================================
# ALERT SORTING
# ============================================================

def sort_alerts(
    alerts: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    return sorted(
        alerts,
        key=lambda alert: alert.get(
            "priority",
            0,
        ),
        reverse=True,
    )


def get_highest_alert_severity(
    alerts: List[Dict[str, Any]],
) -> str:

    if not alerts:
        return "None"

    highest_alert = max(
        alerts,
        key=lambda alert: alert.get(
            "priority",
            0,
        ),
    )

    return highest_alert.get(
        "severity",
        "None",
    )


# ============================================================
# MAINTENANCE DECISION
# ============================================================

def determine_maintenance_action(
    analysis_result: Dict[str, Any],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    status = normalise_status(
        analysis_result.get(
            "status",
            "Warning",
        )
    )

    machine_trend = trend_result.get(
        "machine_trend",
        "Stable",
    )

    emergency_shutdown = bool(
        analysis_result.get(
            "emergency_shutdown",
            False,
        )
    )

    # ========================================================
    # EMERGENCY
    # ========================================================

    if (
        emergency_shutdown
        or status == "Emergency"
    ):

        return {
            "required": True,

            "urgency": "Immediate",

            "timeframe": "Immediately",

            "action": (
                "Stop the machine and begin "
                "emergency maintenance inspection."
            ),
        }

    # ========================================================
    # CRITICAL
    # ========================================================

    if status == "Critical":

        return {
            "required": True,

            "urgency": "Urgent",

            "timeframe": "Within 24 hours",

            "action": analysis_result.get(
                "recommendation",
                "Perform urgent maintenance.",
            ),
        }

    # ========================================================
    # WARNING / DEGRADING
    # ========================================================

    if (
        status == "Warning"
        or machine_trend == "Degrading"
    ):

        return {
            "required": True,

            "urgency": "Scheduled",

            "timeframe": "Within 3 to 7 days",

            "action": analysis_result.get(
                "recommendation",
                "Schedule preventive inspection.",
            ),
        }

    # ========================================================
    # HEALTHY
    # ========================================================

    return {
        "required": False,

        "urgency": "Routine",

        "timeframe": (
            "According to regular schedule"
        ),

        "action": (
            "Continue routine machine monitoring "
            "and maintenance."
        ),
    }


# ============================================================
# MAIN ALERT ENGINE
# ============================================================

def generate_machine_alerts(
    analysis_result: Dict[str, Any],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    alerts: List[
        Dict[str, Any]
    ] = []

    # --------------------------------------------------------
    # Current Arduino status
    # --------------------------------------------------------

    alerts.extend(
        generate_status_alerts(
            analysis_result=analysis_result,
        )
    )

    # --------------------------------------------------------
    # Historical machine trend
    # --------------------------------------------------------

    alerts.extend(
        generate_machine_trend_alerts(
            trend_result=trend_result,
        )
    )

    # --------------------------------------------------------
    # Sensor trends
    # --------------------------------------------------------

    alerts.extend(
        generate_sensor_trend_alerts(
            trend_result=trend_result,
        )
    )

    # --------------------------------------------------------
    # Latest anomalies
    # --------------------------------------------------------

    alerts.extend(
        generate_anomaly_alerts(
            trend_result=trend_result,
        )
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    sorted_alerts = sort_alerts(
        alerts
    )

    # --------------------------------------------------------
    # Counts
    # --------------------------------------------------------

    actionable_alert_count = sum(
        1
        for alert in sorted_alerts
        if alert["severity"] != "Info"
    )

    immediate_alert_count = sum(
        1
        for alert in sorted_alerts
        if alert["immediate_action"]
    )

    highest_severity = (
        get_highest_alert_severity(
            alerts=sorted_alerts,
        )
    )

    # --------------------------------------------------------
    # Maintenance
    # --------------------------------------------------------

    maintenance = (
        determine_maintenance_action(
            analysis_result=analysis_result,
            trend_result=trend_result,
        )
    )

    return {

        "alert_count": len(
            sorted_alerts
        ),

        "actionable_alert_count": (
            actionable_alert_count
        ),

        "immediate_alert_count": (
            immediate_alert_count
        ),

        "highest_severity": (
            highest_severity
        ),

        "maintenance": maintenance,

        "alerts": sorted_alerts,
    }