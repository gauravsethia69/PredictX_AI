"""
PredictX AI - two-machine emergency demo model.

MACHINE-001 is the real ESP32 feed.
MACHINE-002 is a transparent backend-derived mechanical-fault simulation.

The current vibration channel is known to be unreliable, so Machine 2's
fault state does not inherit the ESP32 health/failure values that were
calculated from that bad channel.
"""

from typing import Any, Dict

MACHINE_2_ID = "MACHINE-002"
FAULT_NAME = "SHAFT_RESISTANCE"

# Baseline measured from the healthy motor on 2026-08-10.
HEALTHY_TEMP = 25.85
HEALTHY_CURRENT = 1.3475
HEALTHY_SOUND = 1631.5


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(float(value), maximum))


def normalize_machine_1(
    temperature: float,
    current: float,
    sound: float,
) -> Dict[str, Any]:
    """Create a health result using only the trusted channels.

    Vibration is intentionally excluded because the current SW-420/KP08
    channel is producing false detections in the prototype.
    """

    temp_penalty = min(abs(float(temperature) - HEALTHY_TEMP) * 1.2, 12.0)
    current_penalty = min(abs(float(current) - HEALTHY_CURRENT) / 0.10 * 2.0, 12.0)
    sound_penalty = min(abs(float(sound) - HEALTHY_SOUND) / 100.0 * 2.0, 12.0)

    health = clamp(97.0 - temp_penalty - current_penalty - sound_penalty, 82.0, 99.0)
    failure_probability = clamp(100.0 - health, 1.0, 18.0)

    return {
        "health": round(health, 2),
        "failure_probability": round(failure_probability, 2),
        "machine_status": "Healthy" if health >= 90 else "Warning",
        "diagnosis": "Normal operation - trusted sensor channels stable",
        "failure_stage": "Normal Operation",
        "remaining_life_hours": 120.0,
        "recommendation": "Continue normal operation and routine monitoring.",
        "prediction_explanation": (
            "Prototype health uses temperature, current and sound. "
            "The vibration channel is excluded from health scoring because "
            "the current sensor/module is unreliable."
        ),
    }


def simulate_machine_2(
    temperature: float,
    vibration: float,
    current: float,
    sound: float,
    health: float | None = None,
    failure_probability: float | None = None,
) -> Dict[str, Any]:
    """Derive a repeatable shaft-resistance demo from a live Machine 1 reading.

    The transformation is deterministic, so every new ESP32 reading creates a
    slightly different Machine 2 value and the frontend remains dynamic.
    """

    # Mechanical resistance / near-stall demo profile.
    # User requested vibration and sound to be reduced in the backend.
    simulated_vibration = max(0.0, float(vibration) * 0.15)
    simulated_sound = max(0.0, float(sound) * 0.65)

    # A restricted shaft normally increases electrical load. This gives the
    # demo a physically understandable signal even while vibration is unusable.
    simulated_current = max(0.0, float(current) * 1.35)

    # Short demos do not create a large temperature rise immediately, so only
    # a modest thermal increase is modeled.
    simulated_temperature = float(temperature) + 2.5

    sound_drop_pct = 35.0
    current_rise_pct = 35.0
    fault_severity = clamp(
        25.0 + sound_drop_pct * 0.45 + current_rise_pct * 0.65,
        0.0,
        100.0,
    )

    # Add a small live component so readings move with the real machine.
    live_current_delta = abs(float(current) - HEALTHY_CURRENT) / max(HEALTHY_CURRENT, 0.01)
    live_sound_delta = abs(float(sound) - HEALTHY_SOUND) / max(HEALTHY_SOUND, 1.0)
    fault_severity = clamp(
        fault_severity + live_current_delta * 20.0 + live_sound_delta * 10.0,
        0.0,
        100.0,
    )

    machine2_health = clamp(100.0 - fault_severity, 32.0, 42.0)
    machine2_failure_probability = clamp(78.0 + (42.0 - machine2_health) * 0.8, 78.0, 88.0)

    return {
        "machine_id": MACHINE_2_ID,
        "mode": "FAULT_SIMULATION",
        "fault_scenario": FAULT_NAME,
        "temperature": round(simulated_temperature, 2),
        "vibration": round(simulated_vibration, 2),
        "current": round(simulated_current, 2),
        "sound": round(simulated_sound, 2),
        "health": round(machine2_health, 2),
        "failure_probability": round(machine2_failure_probability, 2),
        "machine_status": "Critical",
        "diagnosis": "Mechanical shaft resistance / bearing stall suspected",
        "failure_stage": "Maintenance Required",
        "remaining_life_hours": 8.0,
        "recommendation": (
            "Stop the motor and inspect the shaft, bearing and coupling for "
            "mechanical resistance or jamming."
        ),
        "simulation_note": (
            "Demo fault simulation derived from live MACHINE-001 data. "
            "Sound and vibration are reduced in the backend; current and "
            "temperature are adjusted to model shaft resistance."
        ),
    }
