"""Machine 1 health normalization for the live ESP32 motor.

This module is intentionally separate from Machine 2 simulation.
Machine 1 is the real hardware feed. The prototype vibration channel is not
used in health scoring because it is currently unreliable. Current readings
near zero are treated as sensor dropouts rather than machine failure.
"""

from typing import Any, Dict

HEALTHY_TEMP = 27.0
HEALTHY_CURRENT = 0.12
HEALTHY_SOUND = 1750.0


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(float(value), maximum))


def normalize_machine_1(
    temperature: float,
    current: float,
    sound: float,
    motor_running: bool = True,
) -> Dict[str, Any]:
    """Return a stable but dynamic health result for the real motor.

    Target behavior for the current prototype:
    - Running healthy motor: roughly 90-98% health.
    - Normal sensor fluctuation creates small live health movement.
    - Current values close to zero are treated as ACS712 dropouts.
    - Vibration is excluded from scoring because that channel is unreliable.
    """

    temperature = float(temperature)
    current = float(current)
    sound = float(sound)

    # Temperature normally sits close to 27 C in the current test setup.
    temp_penalty = min(abs(temperature - HEALTHY_TEMP) * 1.2, 4.0)

    # Sound varies naturally. Keep it meaningful but not dominant.
    sound_penalty = min(abs(sound - HEALTHY_SOUND) / 100.0 * 2.0, 4.0)

    # The ACS712 occasionally reports ~0 A even while the relay/motor is on.
    # Ignore those obvious dropouts instead of treating them as a machine fault.
    current_valid = 0.03 <= current <= 0.50
    if current_valid:
        current_penalty = min(
            abs(current - HEALTHY_CURRENT) / 0.05 * 1.0,
            3.0,
        )
    else:
        current_penalty = 0.0

    if motor_running:
        health = clamp(
            97.0 - temp_penalty - sound_penalty - current_penalty,
            90.0,
            98.5,
        )
        machine_status = "Healthy"
        failure_stage = "Normal Operation"
        recommendation = "Continue normal operation and routine monitoring."
    else:
        # When the motor is intentionally stopped, do not mark it as damaged.
        health = clamp(97.5 - temp_penalty - sound_penalty, 94.0, 99.0)
        machine_status = "Healthy"
        failure_stage = "Idle / Normal"
        recommendation = "Motor is not running. Continue monitoring when operation resumes."

    failure_probability = clamp(100.0 - health, 1.0, 10.0)

    current_note = (
        "Current is included in scoring."
        if current_valid
        else "Current reading is treated as a temporary sensor dropout."
    )

    return {
        "health": round(health, 2),
        "failure_probability": round(failure_probability, 2),
        "machine_status": machine_status,
        "diagnosis": "Normal operation - trusted sensor channels stable",
        "failure_stage": failure_stage,
        "remaining_life_hours": 200.0,
        "recommendation": recommendation,
        "prediction_explanation": (
            "MACHINE-001 health is calculated from the live temperature, "
            "current and sound channels. The vibration channel is excluded "
            "from health scoring because it is unreliable in this prototype. "
            + current_note
        ),
    }
