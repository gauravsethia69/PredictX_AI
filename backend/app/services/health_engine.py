from typing import Dict, Any


# ============================================================
# NORMAL SENSOR OPERATING RANGES
# ============================================================

NORMAL_RANGES = {
    "temperature": {
        "minimum": 20.0,
        "maximum": 55.0,
        "warning_maximum": 70.0,
        "critical_maximum": 85.0,
        "weight": 30.0,
    },

    "vibration": {
        "minimum": 0.0,
        "maximum": 0.7,
        "warning_maximum": 1.3,
        "critical_maximum": 2.0,
        "weight": 30.0,
    },

    "current": {
        "minimum": 0.5,
        "maximum": 2.2,
        "warning_maximum": 3.0,
        "critical_maximum": 4.0,
        "weight": 25.0,
    },

    "sound": {
        "minimum": 25.0,
        "maximum": 60.0,
        "warning_maximum": 75.0,
        "critical_maximum": 90.0,
        "weight": 15.0,
    },
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Keeps a numeric value inside a defined range.
    """

    return max(minimum, min(value, maximum))


def round_value(value: float) -> float:
    """
    Rounds values consistently for API responses.
    """

    return round(float(value), 2)


# ============================================================
# SENSOR PENALTY CALCULATION
# ============================================================

def calculate_sensor_penalty(
    value: float,
    minimum: float,
    maximum: float,
    warning_maximum: float,
    critical_maximum: float,
    weight: float,
) -> Dict[str, Any]:
    """
    Calculates health penalty for an individual sensor.

    Penalty behaviour:

    Normal range:
        0 penalty

    Warning range:
        up to 45% of sensor weight

    Critical range:
        45% to 85% of sensor weight

    Emergency range:
        up to 100% of sensor weight
    """

    value = float(value)

    # --------------------------------------------------------
    # BELOW MINIMUM RANGE
    # --------------------------------------------------------

    if value < minimum:
        lower_distance = minimum - value
        reference_range = max(maximum - minimum, 1.0)

        ratio = lower_distance / reference_range
        ratio = clamp(ratio, 0.0, 1.0)

        penalty = weight * ratio * 0.5

        return {
            "value": round_value(value),
            "condition": "below_normal",
            "penalty": round_value(penalty),
            "health_contribution": round_value(weight - penalty),
            "message": (
                "Sensor value is below the expected operating range."
            ),
        }

    # --------------------------------------------------------
    # NORMAL RANGE
    # --------------------------------------------------------

    if minimum <= value <= maximum:
        return {
            "value": round_value(value),
            "condition": "normal",
            "penalty": 0.0,
            "health_contribution": round_value(weight),
            "message": "Sensor value is within the normal range.",
        }

    # --------------------------------------------------------
    # WARNING RANGE
    # --------------------------------------------------------

    if maximum < value <= warning_maximum:
        warning_span = max(
            warning_maximum - maximum,
            0.001,
        )

        ratio = (
            value - maximum
        ) / warning_span

        ratio = clamp(ratio, 0.0, 1.0)

        penalty = weight * (
            0.10 + ratio * 0.35
        )

        return {
            "value": round_value(value),
            "condition": "warning",
            "penalty": round_value(penalty),
            "health_contribution": round_value(weight - penalty),
            "message": (
                "Sensor value is above normal and needs monitoring."
            ),
        }

    # --------------------------------------------------------
    # CRITICAL RANGE
    # --------------------------------------------------------

    if warning_maximum < value <= critical_maximum:
        critical_span = max(
            critical_maximum - warning_maximum,
            0.001,
        )

        ratio = (
            value - warning_maximum
        ) / critical_span

        ratio = clamp(ratio, 0.0, 1.0)

        penalty = weight * (
            0.45 + ratio * 0.40
        )

        return {
            "value": round_value(value),
            "condition": "critical",
            "penalty": round_value(penalty),
            "health_contribution": round_value(weight - penalty),
            "message": (
                "Sensor value is in the critical operating range."
            ),
        }

    # --------------------------------------------------------
    # EMERGENCY RANGE
    # --------------------------------------------------------

    emergency_span = max(
        critical_maximum * 0.5,
        1.0,
    )

    ratio = (
        value - critical_maximum
    ) / emergency_span

    ratio = clamp(ratio, 0.0, 1.0)

    penalty = weight * (
        0.85 + ratio * 0.15
    )

    penalty = clamp(
        penalty,
        0.0,
        weight,
    )

    return {
        "value": round_value(value),
        "condition": "emergency",
        "penalty": round_value(penalty),
        "health_contribution": round_value(weight - penalty),
        "message": (
            "Sensor value has crossed the safe operating limit."
        ),
    }


# ============================================================
# STATUS CLASSIFICATION
# ============================================================

def get_machine_status(
    health_score: float,
    sensor_analysis: Dict[str, Dict[str, Any]],
) -> str:
    """
    Determines overall machine status using both health score
    and sensor-level conditions.
    """

    conditions = [
        data["condition"]
        for data in sensor_analysis.values()
    ]

    if "emergency" in conditions:
        return "Emergency"

    if health_score < 30:
        return "Critical"

    if "critical" in conditions:
        return "Critical"

    if health_score < 55:
        return "Critical"

    if "warning" in conditions:
        return "Warning"

    if health_score < 80:
        return "Warning"

    return "Healthy"


def get_severity(
    status: str,
) -> str:
    """
    Converts machine status into severity level.
    """

    severity_map = {
        "Healthy": "Low",
        "Warning": "Moderate",
        "Critical": "High",
        "Emergency": "Emergency",
    }

    return severity_map.get(
        status,
        "Unknown",
    )


# ============================================================
# FAILURE RISK
# ============================================================

def calculate_failure_risk(
    health_score: float,
    sensor_analysis: Dict[str, Dict[str, Any]],
) -> float:
    """
    Calculates failure risk using inverse health score and
    additional penalties for critical sensor behaviour.
    """

    base_risk = 100.0 - health_score

    warning_count = sum(
        1
        for data in sensor_analysis.values()
        if data["condition"] == "warning"
    )

    critical_count = sum(
        1
        for data in sensor_analysis.values()
        if data["condition"] == "critical"
    )

    emergency_count = sum(
        1
        for data in sensor_analysis.values()
        if data["condition"] == "emergency"
    )

    extra_risk = (
        warning_count * 2.5
        + critical_count * 6.0
        + emergency_count * 12.0
    )

    failure_risk = base_risk + extra_risk

    return round_value(
        clamp(
            failure_risk,
            0.0,
            100.0,
        )
    )


# ============================================================
# EMERGENCY SHUTDOWN LOGIC
# ============================================================

def should_emergency_shutdown(
    temperature: float,
    vibration: float,
    current: float,
    sound: float,
    health_score: float,
) -> bool:
    """
    Determines whether the machine should be stopped
    immediately.

    Shutdown is triggered for dangerous sensor combinations
    or extremely low machine health.
    """

    extreme_temperature = temperature >= 90.0
    extreme_vibration = vibration >= 2.5
    extreme_current = current >= 4.5
    extreme_sound = sound >= 95.0

    severe_combination = (
        temperature >= 82.0
        and vibration >= 1.8
    )

    overload_combination = (
        current >= 3.8
        and temperature >= 78.0
    )

    bearing_failure_combination = (
        vibration >= 2.0
        and sound >= 80.0
    )

    return bool(
        extreme_temperature
        or extreme_vibration
        or extreme_current
        or extreme_sound
        or severe_combination
        or overload_combination
        or bearing_failure_combination
        or health_score <= 20.0
    )


# ============================================================
# SUMMARY GENERATOR
# ============================================================

def generate_health_summary(
    status: str,
    health_score: float,
    sensor_analysis: Dict[str, Dict[str, Any]],
    emergency_shutdown: bool,
) -> str:
    """
    Generates a short human-readable machine health summary.
    """

    abnormal_sensors = [
        sensor_name
        for sensor_name, data
        in sensor_analysis.items()
        if data["condition"] != "normal"
    ]

    if emergency_shutdown:
        return (
            "Dangerous machine behaviour detected. "
            "Immediate shutdown and inspection are recommended."
        )

    if status == "Healthy":
        return (
            "The machine is operating within the expected "
            "sensor limits and no immediate maintenance action "
            "is required."
        )

    if status == "Warning":
        names = ", ".join(abnormal_sensors)

        return (
            f"The machine is showing early abnormal behaviour "
            f"in {names}. Continue monitoring and schedule an "
            f"inspection."
        )

    if status == "Critical":
        names = ", ".join(abnormal_sensors)

        return (
            f"Critical machine behaviour is present in {names}. "
            f"Maintenance should be performed as soon as possible."
        )

    return (
        f"Machine health score is {health_score}. "
        "Review sensor readings and perform inspection."
    )


# ============================================================
# MAIN HEALTH ENGINE
# ============================================================

def calculate_health(
    temperature: float,
    vibration: float,
    current: float,
    sound: float,
) -> Dict[str, Any]:
    """
    Main PredictX AI health analysis function.

    Returns:
        health_score
        status
        failure_risk
        severity
        emergency_shutdown
        detected_fault
        recommendation
        sensor_analysis
        summary
    """

    sensor_values = {
        "temperature": float(temperature),
        "vibration": float(vibration),
        "current": float(current),
        "sound": float(sound),
    }

    sensor_analysis: Dict[str, Dict[str, Any]] = {}

    total_penalty = 0.0

    for sensor_name, value in sensor_values.items():
        configuration = NORMAL_RANGES[sensor_name]

        analysis = calculate_sensor_penalty(
            value=value,
            minimum=configuration["minimum"],
            maximum=configuration["maximum"],
            warning_maximum=configuration["warning_maximum"],
            critical_maximum=configuration["critical_maximum"],
            weight=configuration["weight"],
        )

        sensor_analysis[sensor_name] = analysis

        total_penalty += analysis["penalty"]

    health_score = clamp(
        100.0 - total_penalty,
        0.0,
        100.0,
    )

    health_score = round_value(health_score)

    status = get_machine_status(
        health_score=health_score,
        sensor_analysis=sensor_analysis,
    )

    severity = get_severity(status)

    failure_risk = calculate_failure_risk(
        health_score=health_score,
        sensor_analysis=sensor_analysis,
    )

    emergency_shutdown = should_emergency_shutdown(
        temperature=temperature,
        vibration=vibration,
        current=current,
        sound=sound,
        health_score=health_score,
    )

    if emergency_shutdown:
        status = "Emergency"
        severity = "Emergency"

    summary = generate_health_summary(
        status=status,
        health_score=health_score,
        sensor_analysis=sensor_analysis,
        emergency_shutdown=emergency_shutdown,
    )

    return {
        "health_score": health_score,
        "status": status,
        "failure_risk": failure_risk,
        "severity": severity,
        "emergency_shutdown": emergency_shutdown,

        # Diagnosis engine will replace these fields in main.py.
        "detected_fault": "Pending diagnosis",
        "recommendation": (
            "Run the diagnosis engine for detailed maintenance advice."
        ),

        "sensor_analysis": sensor_analysis,
        "summary": summary,
    }


# ============================================================
# OPTIONAL BACKWARD-COMPATIBLE FUNCTION
# ============================================================

def analyze_machine_health(
    temperature: float,
    vibration: float,
    current: float,
    sound: float,
) -> Dict[str, Any]:
    """
    Alias for older code that may still call
    analyze_machine_health().
    """

    return calculate_health(
        temperature=temperature,
        vibration=vibration,
        current=current,
        sound=sound,
    )