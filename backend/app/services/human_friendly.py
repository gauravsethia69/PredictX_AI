from __future__ import annotations

from typing import Any, Dict, List


ANALYSIS_VERSION = "rule-engine-2.2"


def round_value(value: float) -> float:
    return round(float(value), 2)


def get_confidence_details(
    confidence: float,
    fault_code: str,
) -> Dict[str, str]:
    confidence = round_value(confidence)

    if fault_code == "SAF001":
        return {
            "level": "High",
            "type": "Safety limit confidence",
            "message": (
                "The system is certain that configured safety limits were "
                "exceeded. A physical inspection is required to identify "
                "the underlying component fault."
            ),
        }

    if confidence >= 80:
        return {
            "level": "High",
            "type": "Fault-pattern confidence",
            "message": (
                "The current sensor pattern strongly matches this condition, "
                "but a physical inspection is still recommended."
            ),
        }

    if confidence >= 55:
        return {
            "level": "Moderate",
            "type": "Fault-pattern confidence",
            "message": (
                "The sensor pattern partially matches this condition. More "
                "readings or a physical inspection are needed before confirmation."
            ),
        }

    return {
        "level": "Low",
        "type": "Fault-pattern confidence",
        "message": (
            "The available readings are not strong enough to confirm a specific "
            "fault. Continue monitoring for a repeated pattern."
        ),
    }


def get_diagnosis_state(
    status: str,
    fault_code: str,
    confidence: float,
) -> str:
    if status == "Healthy":
        return "Normal"

    if fault_code == "SAF001":
        return "Safety event confirmed"

    if fault_code == "MON001" or confidence < 55:
        return "Observation required"

    if confidence >= 80 and status in {"Critical", "Emergency"}:
        return "Probable"

    return "Suspected"


def build_user_message(analysis_result: Dict[str, Any]) -> str:
    status = analysis_result["status"]
    abnormal = analysis_result.get("abnormal_parameters", [])

    if status == "Healthy":
        return (
            "The machine is operating normally. Current readings do not show "
            "a recognised fault pattern, and no immediate maintenance is required."
        )

    if abnormal:
        names = [item["display_name"].lower() for item in abnormal]
        if len(names) == 1:
            affected = names[0]
        else:
            affected = ", ".join(names[:-1]) + f" and {names[-1]}"
    else:
        affected = "one or more readings"

    if status == "Warning":
        verb = "needs" if len(abnormal) == 1 else "need"
        return (
            f"The machine is still operating, but {affected} {verb} attention. "
            "This is an early condition warning, not a confirmed component failure."
        )

    if status == "Critical":
        return (
            f"The machine condition is deteriorating and {affected} are outside "
            "the expected range. Arrange an inspection before continued operation."
        )

    return (
        "The machine has crossed a configured safety limit. Stop operation and "
        "inspect the machine before restarting it."
    )


def build_why_this_result(
    analysis_result: Dict[str, Any],
) -> List[str]:
    reasons: List[str] = []
    abnormal_names = set()

    for item in analysis_result.get("abnormal_parameters", []):
        abnormal_names.add(item["parameter"])
        reasons.append(item["message"])

    sensor_analysis = analysis_result.get("sensor_analysis", {})
    normal_sensors = []
    labels = {
        "temperature": "Temperature",
        "vibration": "Vibration",
        "current": "Current",
        "sound": "Sound",
    }

    for sensor_name, details in sensor_analysis.items():
        if sensor_name not in abnormal_names and details.get("condition") == "normal":
            normal_sensors.append(labels.get(sensor_name, sensor_name.title()))

    if normal_sensors:
        if len(normal_sensors) == 1:
            joined = normal_sensors[0]
        else:
            joined = ", ".join(normal_sensors[:-1]) + f" and {normal_sensors[-1]}"
        reasons.append(f"{joined} remain within the expected operating range.")

    if not reasons:
        reasons.append("All available sensor readings are within the expected range.")

    return reasons


def build_recommended_action(
    analysis_result: Dict[str, Any],
) -> Dict[str, Any]:
    status = analysis_result["status"]
    recommendation = analysis_result["recommendation"]

    if status == "Healthy":
        return {
            "action": "Continue normal operation and routine condition monitoring.",
            "timeframe": "No immediate action required.",
            "machine_can_continue": True,
            "service_time_estimate": "Not required",
            "estimate_note": "No maintenance intervention is currently indicated.",
        }

    if status == "Warning":
        return {
            "action": recommendation,
            "timeframe": "Monitor the next readings and inspect within 24–48 hours if the condition persists.",
            "machine_can_continue": True,
            "service_time_estimate": analysis_result["estimated_downtime"],
            "estimate_note": (
                "This is a preliminary estimate. Actual service time depends on "
                "inspection findings and spare-part availability."
            ),
        }

    if status == "Critical":
        return {
            "action": recommendation,
            "timeframe": "Inspect as soon as possible and before the next production cycle.",
            "machine_can_continue": False,
            "service_time_estimate": analysis_result["estimated_downtime"],
            "estimate_note": (
                "This is a preliminary estimate. Actual service time depends on "
                "inspection findings and spare-part availability."
            ),
        }

    return {
        "action": recommendation,
        "timeframe": "Stop operation and inspect immediately.",
        "machine_can_continue": False,
        "service_time_estimate": analysis_result["estimated_downtime"],
        "estimate_note": (
            "Safety takes priority. Actual repair time can only be determined "
            "after physical inspection."
        ),
    }


def build_sensor_overview(
    analysis_result: Dict[str, Any],
) -> List[Dict[str, Any]]:
    labels = {
        "temperature": ("Temperature", "°C"),
        "vibration": ("Vibration", "prototype unit"),
        "current": ("Current", "A"),
        "sound": ("Sound", "dB"),
    }

    status_map = {
        "normal": "Normal",
        "below_normal": "Attention",
        "warning": "Warning",
        "critical": "Critical",
        "emergency": "Emergency",
    }

    overview: List[Dict[str, Any]] = []
    for sensor_name, details in analysis_result.get("sensor_analysis", {}).items():
        name, unit = labels.get(sensor_name, (sensor_name.title(), ""))
        condition = str(details.get("condition", "normal"))
        status = status_map.get(condition, "Attention")

        if condition == "normal":
            message = f"{name} is within the expected operating range."
        elif condition == "warning":
            message = f"{name} is slightly outside the expected operating range."
        elif condition == "critical":
            message = f"{name} is in a critical operating range."
        elif condition == "emergency":
            message = f"{name} has crossed the configured safety limit."
        else:
            message = str(details.get("message", f"{name} needs attention."))

        overview.append({
            "name": name,
            "value": round_value(details.get("value", 0.0)),
            "unit": unit,
            "status": status,
            "message": message,
        })

    return overview


def build_data_source(source: str) -> Dict[str, Any]:
    source_value = str(source or "unknown").strip().lower()

    if source_value == "esp32":
        return {
            "type": "esp32",
            "is_live": True,
            "message": "Live data received from the connected monitoring device.",
        }

    if source_value in {"simulator", "simulation"}:
        return {
            "type": "simulator",
            "is_live": False,
            "message": "This result was generated using simulated sensor data.",
        }

    if source_value in {"manual", "manual_test"}:
        return {
            "type": "manual_test",
            "is_live": False,
            "message": "This result was generated from manually entered test data.",
        }

    return {
        "type": source_value or "unknown",
        "is_live": False,
        "message": "The source of this sensor reading has not been identified as live hardware.",
    }


def build_test_context(
    source: str,
    analysis_result: Dict[str, Any],
) -> Dict[str, Any]:
    source_value = str(source or "unknown").strip().lower()
    is_simulated = source_value in {"simulator", "simulation", "manual", "manual_test"}

    if not is_simulated:
        return {
            "is_simulated": False,
            "scenario": None,
            "message": "This reading is not labelled as simulated test data.",
        }

    if analysis_result.get("status") == "Emergency":
        scenario = "Extreme emergency test"
        message = (
            "These values represent a simulated safety-limit test and should "
            "not be interpreted as a normal operating sample."
        )
    elif analysis_result.get("status") == "Critical":
        scenario = "Critical-condition test"
        message = "These values represent a simulated critical-condition test."
    elif analysis_result.get("status") == "Warning":
        scenario = "Warning-condition test"
        message = "These values represent a simulated early-warning test."
    else:
        scenario = "Normal-operation test"
        message = "These values represent a simulated normal-operation test."

    return {
        "is_simulated": True,
        "scenario": scenario,
        "message": message,
    }


def build_analysis_note(status: str) -> str:
    if status == "Healthy":
        return (
            "The current readings do not indicate a recognised fault pattern. "
            "Continue routine monitoring."
        )

    if status == "Warning":
        return (
            "This is an early condition assessment, not a confirmed component "
            "failure. Observe the next readings and inspect if the pattern persists."
        )

    return (
        "This is a preliminary condition assessment based on available sensor "
        "readings. A physical inspection is recommended before replacing components."
    )


def humanise_analysis(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    confidence_details = get_confidence_details(
        confidence=analysis_result["confidence"],
        fault_code=analysis_result["fault_code"],
    )

    return {
        "user_message": build_user_message(analysis_result),
        "diagnosis_state": get_diagnosis_state(
            status=analysis_result["status"],
            fault_code=analysis_result["fault_code"],
            confidence=analysis_result["confidence"],
        ),
        "confidence_level": confidence_details["level"],
        "confidence_type": confidence_details["type"],
        "confidence_message": confidence_details["message"],
        "why_this_result": build_why_this_result(analysis_result),
        "recommended_action": build_recommended_action(analysis_result),
        "sensor_overview": build_sensor_overview(analysis_result),
        "analysis_note": build_analysis_note(analysis_result["status"]),
        "analysis_version": ANALYSIS_VERSION,
    }