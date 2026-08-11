
from __future__ import annotations

from typing import Any, Dict, List


# ============================================================
# PredictX AI - INDUSTRIAL FAULT DETECTION ENGINE
# ============================================================
#
# IMPORTANT ARCHITECTURE
#
# ESP32:
#   - Reads sensors
#   - Calculates health
#   - Calculates failure probability
#   - Calculates machine status
#
# BACKEND:
#   - Analyses historical sensor behaviour
#   - Detects abnormal combinations
#   - Identifies likely fault patterns
#   - Provides confidence and evidence
#
# This is a rule-based industrial diagnostic engine.
# It is designed to be explainable and suitable for
# predictive-maintenance demonstrations.
#
# Sensors:
#   temperature
#   vibration
#   current
#   sound
#
# ============================================================


# ============================================================
# SENSOR LIMITS
# ============================================================

SENSOR_LIMITS = {
    "temperature": {
        "warning": 60.0,
        "critical": 75.0,
        "emergency": 90.0,
    },

    "vibration": {
        "warning": 1.00,
        "critical": 1.80,
        "emergency": 2.50,
    },

    "current": {
        "warning": 3.00,
        "critical": 4.00,
        "emergency": 5.00,
    },

    "sound": {
        "warning": 80.0,
        "critical": 100.0,
        "emergency": 120.0,
    },
}


# ============================================================
# FAULT DEFINITIONS
# ============================================================

FAULT_DEFINITIONS = {
    "Bearing Wear": {
        "description": (
            "Increasing vibration and abnormal acoustic behaviour "
            "may indicate progressive bearing degradation."
        ),
        "components": [
            "Bearings",
            "Shaft",
            "Lubrication system",
        ],
    },

    "Bearing Overheating": {
        "description": (
            "Elevated temperature combined with vibration may "
            "indicate bearing friction or inadequate lubrication."
        ),
        "components": [
            "Bearings",
            "Lubrication system",
            "Shaft alignment",
        ],
    },

    "Motor Overload": {
        "description": (
            "Elevated electrical current with increasing "
            "temperature may indicate motor overload."
        ),
        "components": [
            "Motor",
            "Electrical supply",
            "Mechanical load",
        ],
    },

    "Electrical Overload": {
        "description": (
            "Abnormally high current may indicate excessive "
            "electrical or mechanical loading."
        ),
        "components": [
            "Motor winding",
            "Power supply",
            "Electrical connections",
        ],
    },

    "Mechanical Imbalance": {
        "description": (
            "Persistent vibration increase with relatively "
            "normal current may indicate rotating imbalance."
        ),
        "components": [
            "Rotor",
            "Fan",
            "Coupling",
            "Shaft",
        ],
    },

    "Misalignment": {
        "description": (
            "Increasing vibration together with increased "
            "temperature can be associated with shaft or "
            "coupling misalignment."
        ),
        "components": [
            "Shaft",
            "Coupling",
            "Motor mounting",
        ],
    },

    "Mechanical Friction": {
        "description": (
            "Simultaneous increases in temperature, current "
            "and vibration may indicate abnormal mechanical friction."
        ),
        "components": [
            "Bearings",
            "Shaft",
            "Coupling",
            "Lubrication system",
        ],
    },

    "Acoustic Abnormality": {
        "description": (
            "A significant increase in sound level may indicate "
            "mechanical looseness, friction or abnormal vibration."
        ),
        "components": [
            "Bearings",
            "Housing",
            "Rotor",
            "Coupling",
        ],
    },

    "Thermal Stress": {
        "description": (
            "Persistent elevated temperature may indicate "
            "insufficient cooling, excessive load or friction."
        ),
        "components": [
            "Cooling system",
            "Motor",
            "Bearings",
            "Ventilation",
        ],
    },

    "Possible Sensor Anomaly": {
        "description": (
            "The sensor pattern is inconsistent with the other "
            "machine parameters and should be verified."
        ),
        "components": [
            "Sensor wiring",
            "Sensor mounting",
            "Sensor calibration",
        ],
    },
}


# ============================================================
# UTILITIES
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
    return round(float(value), digits)


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        if value is None:
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


# ============================================================
# SENSOR SEVERITY
# ============================================================

def get_sensor_severity(
    sensor_name: str,
    value: float,
) -> str:
    """
    Determines the severity of an individual sensor value.
    """

    limits = SENSOR_LIMITS.get(
        sensor_name,
        {},
    )

    if value >= limits.get(
        "emergency",
        float("inf"),
    ):
        return "Emergency"

    if value >= limits.get(
        "critical",
        float("inf"),
    ):
        return "Critical"

    if value >= limits.get(
        "warning",
        float("inf"),
    ):
        return "Warning"

    return "Normal"


# ============================================================
# GET LATEST SENSOR VALUES
# ============================================================

def get_latest_values(
    readings: List[Any],
) -> Dict[str, float]:
    """
    Extracts the latest sensor values.
    """

    if not readings:
        return {
            "temperature": 0.0,
            "vibration": 0.0,
            "current": 0.0,
            "sound": 0.0,
        }

    latest = readings[-1]

    return {
        "temperature": safe_float(
            getattr(
                latest,
                "temperature",
                0.0,
            )
        ),

        "vibration": safe_float(
            getattr(
                latest,
                "vibration",
                0.0,
            )
        ),

        "current": safe_float(
            getattr(
                latest,
                "current",
                0.0,
            )
        ),

        "sound": safe_float(
            getattr(
                latest,
                "sound",
                0.0,
            )
        ),
    }


# ============================================================
# TREND HELPER
# ============================================================

def get_sensor_trend(
    trend_result: Dict[str, Any],
    sensor_name: str,
) -> str:

    sensor_trends = trend_result.get(
        "sensor_trends",
        {},
    )

    sensor_data = sensor_trends.get(
        sensor_name,
        {},
    )

    return sensor_data.get(
        "trend",
        "Stable",
    )


# ============================================================
# TREND CHANGE
# ============================================================

def get_percentage_change(
    trend_result: Dict[str, Any],
    sensor_name: str,
) -> float:

    sensor_trends = trend_result.get(
        "sensor_trends",
        {},
    )

    sensor_data = sensor_trends.get(
        sensor_name,
        {},
    )

    return safe_float(
        sensor_data.get(
            "percentage_change",
            0.0,
        )
    )


# ============================================================
# FAULT CANDIDATE
# ============================================================

def create_fault_candidate(
    fault: str,
    score: float,
    evidence: List[str],
    sensors: List[str],
) -> Dict[str, Any]:

    definition = FAULT_DEFINITIONS.get(
        fault,
        {},
    )

    return {
        "fault": fault,

        "score": round_value(
            clamp(
                score,
                0.0,
                100.0,
            )
        ),

        "confidence": round_value(
            clamp(
                score,
                0.0,
                100.0,
            )
        ),

        "description": definition.get(
            "description",
            "Possible machine fault.",
        ),

        "affected_components": definition.get(
            "components",
            [],
        ),

        "evidence": evidence,

        "sensors_involved": sensors,
    }


# ============================================================
# RULE 1
# BEARING WEAR
# ============================================================

def detect_bearing_wear(
    values: Dict[str, float],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    score = 0.0
    evidence = []
    sensors = []

    vibration = values["vibration"]
    sound = values["sound"]

    vibration_trend = get_sensor_trend(
        trend_result,
        "vibration",
    )

    sound_trend = get_sensor_trend(
        trend_result,
        "sound",
    )

    vibration_change = get_percentage_change(
        trend_result,
        "vibration",
    )

    sound_change = get_percentage_change(
        trend_result,
        "sound",
    )

    if vibration >= 1.0:
        score += 30
        sensors.append("vibration")

        evidence.append(
            f"Vibration is elevated at {vibration}."
        )

    if vibration_trend == "Increasing":
        score += 25

        evidence.append(
            "Vibration shows an increasing historical trend."
        )

    if vibration_change >= 35:
        score += 15

        evidence.append(
            f"Vibration increased by approximately "
            f"{round_value(vibration_change)}%."
        )

    if sound >= 80:
        score += 15

        if "sound" not in sensors:
            sensors.append("sound")

        evidence.append(
            f"Sound level is elevated at {sound}."
        )

    if sound_trend == "Increasing":
        score += 10

        evidence.append(
            "Acoustic level is increasing."
        )

    if sound_change >= 25:
        score += 5

        evidence.append(
            f"Sound increased by approximately "
            f"{round_value(sound_change)}%."
        )

    return create_fault_candidate(
        fault="Bearing Wear",
        score=score,
        evidence=evidence,
        sensors=sensors,
    )


# ============================================================
# RULE 2
# BEARING OVERHEATING
# ============================================================

def detect_bearing_overheating(
    values: Dict[str, float],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    score = 0.0
    evidence = []
    sensors = []

    temperature = values["temperature"]
    vibration = values["vibration"]

    temperature_trend = get_sensor_trend(
        trend_result,
        "temperature",
    )

    if temperature >= 60:
        score += 35
        sensors.append("temperature")

        evidence.append(
            f"Temperature is elevated at {temperature}°C."
        )

    if temperature_trend == "Increasing":
        score += 25

        evidence.append(
            "Temperature shows a continuous increasing trend."
        )

    if vibration >= 1.0:
        score += 25

        sensors.append("vibration")

        evidence.append(
            f"Vibration is elevated at {vibration}."
        )

    if vibration >= 1.8:
        score += 15

    return create_fault_candidate(
        fault="Bearing Overheating",
        score=score,
        evidence=evidence,
        sensors=list(dict.fromkeys(sensors)),
    )


# ============================================================
# RULE 3
# MOTOR OVERLOAD
# ============================================================

def detect_motor_overload(
    values: Dict[str, float],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    score = 0.0
    evidence = []
    sensors = []

    current = values["current"]
    temperature = values["temperature"]

    current_trend = get_sensor_trend(
        trend_result,
        "current",
    )

    temperature_trend = get_sensor_trend(
        trend_result,
        "temperature",
    )

    if current >= 3.0:
        score += 40
        sensors.append("current")

        evidence.append(
            f"Motor current is elevated at {current} A."
        )

    if current >= 4.0:
        score += 20

    if current_trend == "Increasing":
        score += 20

        evidence.append(
            "Motor current shows an increasing trend."
        )

    if temperature >= 60:
        score += 15

        sensors.append("temperature")

        evidence.append(
            f"Temperature is also elevated at {temperature}°C."
        )

    if temperature_trend == "Increasing":
        score += 5

    return create_fault_candidate(
        fault="Motor Overload",
        score=score,
        evidence=evidence,
        sensors=list(dict.fromkeys(sensors)),
    )


# ============================================================
# RULE 4
# MECHANICAL IMBALANCE
# ============================================================

def detect_mechanical_imbalance(
    values: Dict[str, float],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    score = 0.0
    evidence = []
    sensors = []

    vibration = values["vibration"]
    current = values["current"]

    vibration_trend = get_sensor_trend(
        trend_result,
        "vibration",
    )

    if vibration >= 1.0:
        score += 40
        sensors.append("vibration")

        evidence.append(
            f"Vibration is elevated at {vibration}."
        )

    if vibration >= 1.8:
        score += 20

    if vibration_trend == "Increasing":
        score += 25

        evidence.append(
            "Vibration is progressively increasing."
        )

    # A significant vibration problem without
    # equally high electrical loading increases
    # the likelihood of a mechanical issue.
    if vibration >= 1.0 and current < 3.0:
        score += 15

        evidence.append(
            "Vibration is elevated while current remains "
            "below the overload range."
        )

    return create_fault_candidate(
        fault="Mechanical Imbalance",
        score=score,
        evidence=evidence,
        sensors=list(dict.fromkeys(sensors)),
    )


# ============================================================
# RULE 5
# MISALIGNMENT
# ============================================================

def detect_misalignment(
    values: Dict[str, float],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    score = 0.0
    evidence = []
    sensors = []

    vibration = values["vibration"]
    temperature = values["temperature"]

    vibration_trend = get_sensor_trend(
        trend_result,
        "vibration",
    )

    temperature_trend = get_sensor_trend(
        trend_result,
        "temperature",
    )

    if vibration >= 1.0:
        score += 35
        sensors.append("vibration")

        evidence.append(
            "Elevated vibration may indicate rotating "
            "assembly misalignment."
        )

    if vibration_trend == "Increasing":
        score += 25

        evidence.append(
            "Vibration is progressively increasing."
        )

    if temperature >= 60:
        score += 20
        sensors.append("temperature")

        evidence.append(
            "Temperature is elevated."
        )

    if temperature_trend == "Increasing":
        score += 10

    if vibration >= 1.8:
        score += 10

    return create_fault_candidate(
        fault="Misalignment",
        score=score,
        evidence=evidence,
        sensors=list(dict.fromkeys(sensors)),
    )


# ============================================================
# RULE 6
# MECHANICAL FRICTION
# ============================================================

def detect_mechanical_friction(
    values: Dict[str, float],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    score = 0.0
    evidence = []
    sensors = []

    temperature = values["temperature"]
    vibration = values["vibration"]
    current = values["current"]

    temperature_trend = get_sensor_trend(
        trend_result,
        "temperature",
    )

    vibration_trend = get_sensor_trend(
        trend_result,
        "vibration",
    )

    current_trend = get_sensor_trend(
        trend_result,
        "current",
    )

    if temperature >= 60:
        score += 25
        sensors.append("temperature")

        evidence.append(
            "Temperature is elevated."
        )

    if vibration >= 1.0:
        score += 25
        sensors.append("vibration")

        evidence.append(
            "Vibration is elevated."
        )

    if current >= 3.0:
        score += 25
        sensors.append("current")

        evidence.append(
            "Current is elevated."
        )

    if (
        temperature_trend == "Increasing"
        and vibration_trend == "Increasing"
    ):
        score += 15

        evidence.append(
            "Temperature and vibration are both increasing."
        )

    if current_trend == "Increasing":
        score += 10

    return create_fault_candidate(
        fault="Mechanical Friction",
        score=score,
        evidence=evidence,
        sensors=list(dict.fromkeys(sensors)),
    )


# ============================================================
# RULE 7
# ACOUSTIC ABNORMALITY
# ============================================================

def detect_acoustic_abnormality(
    values: Dict[str, float],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    score = 0.0
    evidence = []
    sensors = []

    sound = values["sound"]
    vibration = values["vibration"]

    sound_trend = get_sensor_trend(
        trend_result,
        "sound",
    )

    if sound >= 80:
        score += 45
        sensors.append("sound")

        evidence.append(
            f"Sound level is elevated at {sound}."
        )

    if sound >= 100:
        score += 20

    if sound_trend == "Increasing":
        score += 20

        evidence.append(
            "Sound level is progressively increasing."
        )

    if vibration >= 1.0:
        score += 15
        sensors.append("vibration")

        evidence.append(
            "Elevated vibration supports the acoustic abnormality."
        )

    return create_fault_candidate(
        fault="Acoustic Abnormality",
        score=score,
        evidence=evidence,
        sensors=list(dict.fromkeys(sensors)),
    )


# ============================================================
# RULE 8
# THERMAL STRESS
# ============================================================

def detect_thermal_stress(
    values: Dict[str, float],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    score = 0.0
    evidence = []
    sensors = []

    temperature = values["temperature"]

    temperature_trend = get_sensor_trend(
        trend_result,
        "temperature",
    )

    if temperature >= 60:
        score += 45
        sensors.append("temperature")

        evidence.append(
            f"Temperature is elevated at {temperature}°C."
        )

    if temperature >= 75:
        score += 20

    if temperature_trend == "Increasing":
        score += 25

        evidence.append(
            "Temperature is continuously increasing."
        )

    if temperature >= 90:
        score += 10

    return create_fault_candidate(
        fault="Thermal Stress",
        score=score,
        evidence=evidence,
        sensors=sensors,
    )


# ============================================================
# SENSOR CONSISTENCY CHECK
# ============================================================

def detect_sensor_inconsistency(
    values: Dict[str, float],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:

    score = 0.0
    evidence = []
    sensors = []

    temperature = values["temperature"]
    vibration = values["vibration"]
    current = values["current"]
    sound = values["sound"]

    # Example:
    # Very high temperature with completely normal
    # vibration/current/sound can warrant sensor verification.

    high_temperature = temperature >= 75
    normal_vibration = vibration < 0.5
    normal_current = current <= 2.0
    normal_sound = sound <= 65

    if (
        high_temperature
        and normal_vibration
        and normal_current
        and normal_sound
    ):
        score += 75

        sensors.append("temperature")

        evidence.append(
            "Temperature is unusually high while the other "
            "monitored parameters remain near their normal ranges."
        )

    high_vibration = vibration >= 1.8

    if (
        high_vibration
        and normal_current
        and normal_sound
        and temperature < 45
    ):
        score += 45

        sensors.append("vibration")

        evidence.append(
            "Vibration is significantly elevated without "
            "corresponding changes in the other parameters."
        )

    return create_fault_candidate(
        fault="Possible Sensor Anomaly",
        score=score,
        evidence=evidence,
        sensors=list(dict.fromkeys(sensors)),
    )


# ============================================================
# GENERATE ALL FAULT CANDIDATES
# ============================================================

def generate_fault_candidates(
    values: Dict[str, float],
    trend_result: Dict[str, Any],
) -> List[Dict[str, Any]]:

    candidates = [
        detect_bearing_wear(
            values,
            trend_result,
        ),

        detect_bearing_overheating(
            values,
            trend_result,
        ),

        detect_motor_overload(
            values,
            trend_result,
        ),

        detect_mechanical_imbalance(
            values,
            trend_result,
        ),

        detect_misalignment(
            values,
            trend_result,
        ),

        detect_mechanical_friction(
            values,
            trend_result,
        ),

        detect_acoustic_abnormality(
            values,
            trend_result,
        ),

        detect_thermal_stress(
            values,
            trend_result,
        ),

        detect_sensor_inconsistency(
            values,
            trend_result,
        ),
    ]

    return sorted(
        candidates,
        key=lambda item: item["score"],
        reverse=True,
    )


# ============================================================
# FAULT SEVERITY
# ============================================================

def determine_fault_severity(
    score: float,
    values: Dict[str, float],
) -> str:

    emergency_sensor_count = 0
    critical_sensor_count = 0

    for sensor_name, value in values.items():

        severity = get_sensor_severity(
            sensor_name,
            value,
        )

        if severity == "Emergency":
            emergency_sensor_count += 1

        elif severity == "Critical":
            critical_sensor_count += 1

    if emergency_sensor_count >= 1:
        return "Emergency"

    if critical_sensor_count >= 2:
        return "Critical"

    if score >= 75:
        return "Critical"

    if score >= 50:
        return "Warning"

    if score >= 30:
        return "Watch"

    return "Normal"


# ============================================================
# MAIN FAULT DETECTION ENGINE
# ============================================================

def detect_fault(
    readings: List[Any],
    trend_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Main PredictX AI fault-detection engine.

    Returns the most likely fault, confidence,
    evidence, affected components and alternative
    fault candidates.
    """

    # --------------------------------------------------------
    # NO DATA
    # --------------------------------------------------------

    if not readings:

        return {
            "fault": "Insufficient Data",
            "confidence": 0.0,
            "severity": "Unknown",
            "description": (
                "No sensor readings are available "
                "for fault diagnosis."
            ),
            "evidence": [],
            "affected_components": [],
            "sensors_involved": [],
            "alternative_faults": [],
            "diagnosis_status": "Insufficient data",
        }


    # --------------------------------------------------------
    # LATEST VALUES
    # --------------------------------------------------------

    values = get_latest_values(
        readings
    )


    # --------------------------------------------------------
    # GENERATE CANDIDATES
    # --------------------------------------------------------

    candidates = generate_fault_candidates(
        values=values,
        trend_result=trend_result,
    )


    # --------------------------------------------------------
    # BEST CANDIDATE
    # --------------------------------------------------------

    best_candidate = candidates[0]


    # --------------------------------------------------------
    # MINIMUM CONFIDENCE
    # --------------------------------------------------------

    if best_candidate["score"] < 30:

        return {
            "fault": "No Significant Fault Detected",

            "confidence": round_value(
                best_candidate["score"]
            ),

            "severity": "Normal",

            "description": (
                "Current sensor patterns do not provide "
                "strong evidence of a specific machine fault."
            ),

            "evidence": [
                "No fault pattern exceeded the diagnostic confidence threshold."
            ],

            "affected_components": [],

            "sensors_involved": [],

            "alternative_faults": [],

            "diagnosis_status": "Normal monitoring",
        }


    # --------------------------------------------------------
    # SEVERITY
    # --------------------------------------------------------

    severity = determine_fault_severity(
        score=best_candidate["score"],
        values=values,
    )


    # --------------------------------------------------------
    # ALTERNATIVE FAULTS
    # --------------------------------------------------------

    alternatives = []

    for candidate in candidates[1:4]:

        if candidate["score"] >= 30:

            alternatives.append(
                {
                    "fault": candidate["fault"],
                    "confidence": candidate["confidence"],
                }
            )


    # --------------------------------------------------------
    # DIAGNOSIS STATUS
    # --------------------------------------------------------

    if severity == "Emergency":

        diagnosis_status = (
            "Immediate inspection required"
        )

    elif severity == "Critical":

        diagnosis_status = (
            "Urgent maintenance inspection required"
        )

    elif severity == "Warning":

        diagnosis_status = (
            "Preventive maintenance recommended"
        )

    elif severity == "Watch":

        diagnosis_status = (
            "Continue monitoring"
        )

    else:

        diagnosis_status = (
            "Normal monitoring"
        )


    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {
        "fault": best_candidate["fault"],

        "confidence": best_candidate["confidence"],

        "severity": severity,

        "description": best_candidate[
            "description"
        ],

        "evidence": best_candidate[
            "evidence"
        ],

        "affected_components": best_candidate[
            "affected_components"
        ],

        "sensors_involved": best_candidate[
            "sensors_involved"
        ],

        "alternative_faults": alternatives,

        "diagnosis_status": diagnosis_status,

        "latest_values": {
            key: round_value(value)
            for key, value in values.items()
        },
    }


# ============================================================
# DIAGNOSTIC RECOMMENDATION
# ============================================================

def generate_fault_recommendation(
    fault_result: Dict[str, Any],
) -> str:
    """
    Converts the diagnostic result into a practical
    maintenance recommendation.
    """

    fault = fault_result.get(
        "fault",
        "Unknown",
    )

    severity = fault_result.get(
        "severity",
        "Normal",
    )

    components = fault_result.get(
        "affected_components",
        [],
    )

    component_text = ", ".join(
        components[:3]
    )

    if fault == "No Significant Fault Detected":

        return (
            "Continue normal condition monitoring and "
            "inspect the machine according to the routine "
            "maintenance schedule."
        )

    if fault == "Insufficient Data":

        return (
            "Collect additional sensor readings before "
            "making a machine fault diagnosis."
        )

    if severity == "Emergency":

        return (
            f"Stop the machine if operationally safe. "
            f"Immediately inspect {component_text or 'the suspected components'} "
            f"and verify the sensor readings before restart."
        )

    if severity == "Critical":

        return (
            f"Schedule urgent maintenance inspection of "
            f"{component_text or 'the suspected machine components'}. "
            f"Check the underlying mechanical and electrical condition "
            f"before continued operation."
        )

    if severity == "Warning":

        return (
            f"Schedule preventive inspection of "
            f"{component_text or 'the suspected components'} "
            f"and continue monitoring the affected sensor trends."
        )

    return (
        f"Continue monitoring the machine and inspect "
        f"{component_text or 'the suspected components'} "
        f"during the next scheduled maintenance."
    )

