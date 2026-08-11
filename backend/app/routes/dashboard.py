from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import SensorReading


router = APIRouter(
    prefix="/api",
    tags=["Dashboard"],
)


def direction(values):
    """
    Determine the general direction of a numeric series.

    Returns:
        Rising
        Falling
        Stable
    """

    if not values or len(values) < 2:
        return "Stable"

    numeric_values = []

    for value in values:
        try:
            numeric_values.append(float(value))
        except (TypeError, ValueError):
            continue

    if len(numeric_values) < 2:
        return "Stable"

    first = numeric_values[0]
    last = numeric_values[-1]

    difference = last - first

    # Small changes are treated as stable.
    threshold = max(abs(first) * 0.02, 0.0001)

    if difference > threshold:
        return "Rising"

    if difference < -threshold:
        return "Falling"

    return "Stable"


def serialize_reading(reading):
    """
    Convert SQLAlchemy SensorReading into JSON-safe data.
    """

    if reading is None:
        return None

    return {
        "id": reading.id,
        "machine_id": reading.machine_id,
        "timestamp": (
            reading.timestamp.isoformat()
            if reading.timestamp
            else None
        ),
        "temperature": reading.temperature,
        "vibration": reading.vibration,
        "current": reading.current,
        "sound": reading.sound,
        "motor_running": reading.motor_running,
        "source": reading.source,
        "health": reading.health,
        "machine_status": reading.machine_status,
        "failure_probability": reading.failure_probability,
        "diagnosis": reading.diagnosis,
        "recommendation": reading.recommendation,
        "failure_stage": reading.failure_stage,
        "remaining_life_hours": reading.remaining_life_hours,
        "prediction_explanation": reading.prediction_explanation,
    }


@router.get("/dashboard/{machine_id}")
def dashboard(
    machine_id: str,
    db: Session = Depends(get_db),
):
    rows = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .order_by(
            SensorReading.timestamp.asc(),
            SensorReading.id.asc(),
        )
        .all()
    )

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No sensor data found for machine {machine_id}",
        )

    latest = rows[-1]

    analysis = {
        "reading_count": len(rows),

        "health_trend": direction(
            [r.health for r in rows]
        ),

        "failure_risk_trend": direction(
            [r.failure_probability for r in rows]
        ),

        "temperature_trend": direction(
            [r.temperature for r in rows]
        ),

        "current_trend": direction(
            [r.current for r in rows]
        ),

        "sound_trend": direction(
            [r.sound for r in rows]
        ),

        "vibration_trend": direction(
            [r.vibration for r in rows]
        ),

        "summary": (
            f"Historical analysis across {len(rows)} "
            "reading(s). ESP32 prediction values are "
            "displayed as received."
        ),
    }

    return {
        "machine_id": machine_id,
        "latest": serialize_reading(latest),
        "historical_analysis": analysis,
        "alert_count": 0,
    }


# ---------------------------------------------------------
# Compatibility route for older frontend versions
# ---------------------------------------------------------

@router.get("/machine/{machine_id}/dashboard")
def legacy_dashboard(
    machine_id: str,
    db: Session = Depends(get_db),
):
    return dashboard(
        machine_id=machine_id,
        db=db,
    )