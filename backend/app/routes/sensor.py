from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import SensorReading
from app.schemas.sensor import (
    SensorDataCreate,
    SensorReadingResponse,
)
from app.services.machine2_simulation import simulate_machine_2, normalize_machine_1


router = APIRouter(
    prefix="/api",
    tags=["Sensor Data"],
)


# ============================================================
# RECEIVE SENSOR DATA
# ============================================================

@router.post(
    "/sensor-data",
    response_model=SensorReadingResponse,
    status_code=201,
)
def receive_sensor_data(
    data: SensorDataCreate,
    db: Session = Depends(get_db),
):
    """
    Store a new ESP32 sensor reading.

    Prediction values are accepted as supplied by the
    ESP32/backend. The frontend does not modify them.
    """

    # MACHINE-001 uses the real ESP32 sensor values, but its health result is
    # recalculated from the trusted channels. The prototype vibration channel
    # is intentionally excluded because it currently produces false events.
    if data.machine_id == "MACHINE-001":
        trusted = normalize_machine_1(
            temperature=data.temperature,
            current=data.current,
            sound=data.sound,
        )
    else:
        trusted = {
            "health": data.health,
            "machine_status": data.machine_status,
            "failure_probability": data.failure_probability,
            "diagnosis": data.diagnosis,
            "recommendation": data.recommendation,
            "failure_stage": data.failure_stage,
            "remaining_life_hours": data.remaining_life_hours,
            "prediction_explanation": data.prediction_explanation,
        }

    reading = SensorReading(
        machine_id=data.machine_id,
        temperature=data.temperature,
        vibration=data.vibration,
        current=data.current,
        sound=data.sound,
        motor_running=data.motor_running,
        source=data.source,
        health=trusted["health"],
        machine_status=trusted["machine_status"],
        failure_probability=trusted["failure_probability"],
        diagnosis=trusted["diagnosis"],
        recommendation=trusted["recommendation"],
        failure_stage=trusted["failure_stage"],
        remaining_life_hours=trusted["remaining_life_hours"],
        prediction_explanation=trusted["prediction_explanation"],
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return reading


# ============================================================
# LATEST READING
# ============================================================

@router.get(
    "/readings/latest/{machine_id}",
    response_model=SensorReadingResponse,
)
def latest_reading(
    machine_id: str,
    db: Session = Depends(get_db),
):
    """
    Return the newest reading for a machine.

    MACHINE-001:
        Returns the latest real database reading.

    MACHINE-002:
        Returns the existing backend-derived simulation
        based on the latest MACHINE-001 reading.
    """

    # --------------------------------------------------------
    # MACHINE-002 BACKEND SIMULATION
    # --------------------------------------------------------

    if machine_id == "MACHINE-002":

        latest_machine_1 = (
            db.query(SensorReading)
            .filter(
                SensorReading.machine_id
                == "MACHINE-001"
            )
            .order_by(
                SensorReading.timestamp.desc(),
                SensorReading.id.desc(),
            )
            .first()
        )

        if latest_machine_1 is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No MACHINE-001 sensor data "
                    "available for MACHINE-002 simulation."
                ),
            )

        simulated = simulate_machine_2(
            temperature=latest_machine_1.temperature,
            vibration=latest_machine_1.vibration,
            current=latest_machine_1.current,
            sound=latest_machine_1.sound,
            health=latest_machine_1.health,
            failure_probability=(
                latest_machine_1.failure_probability
            ),
        )

        return {
            "id": latest_machine_1.id,
            "machine_id": "MACHINE-002",
            "timestamp": latest_machine_1.timestamp,

            "temperature": simulated["temperature"],
            "vibration": simulated["vibration"],
            "current": simulated["current"],
            "sound": simulated["sound"],

            "motor_running": False,
            "source": "machine-2-simulation",

            "health": simulated["health"],
            "machine_status": simulated["machine_status"],
            "failure_probability": (
                simulated["failure_probability"]
            ),
            "diagnosis": simulated["diagnosis"],
            "recommendation": simulated["recommendation"],
            "failure_stage": simulated["failure_stage"],
            "remaining_life_hours": (
                simulated["remaining_life_hours"]
            ),
            "prediction_explanation": (
                simulated["simulation_note"]
            ),
        }

    # --------------------------------------------------------
    # EXISTING DATABASE LOGIC
    # --------------------------------------------------------

    reading = (
        db.query(SensorReading)
        .filter(
            SensorReading.machine_id == machine_id
        )
        .order_by(
            SensorReading.timestamp.desc(),
            SensorReading.id.desc(),
        )
        .first()
    )

    if reading is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No sensor data found for machine "
                f"{machine_id}"
            ),
        )

    return reading


# ============================================================
# ALL READINGS
# ============================================================

@router.get("/readings")
def readings(
    machine_id: str | None = Query(
        default=None
    ),
    limit: int = Query(
        default=200,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    """
    Return readings.

    If machine_id is supplied:
        return readings for that machine.

    If machine_id is omitted:
        return readings for all machines.

    This also allows the frontend to discover machines
    through the readings endpoint if necessary.
    """

    # MACHINE-002 has no separate sensor hardware. Build its history from the
    # real MACHINE-001 stream so charts remain live and dynamic.
    if machine_id == "MACHINE-002":
        source_rows = (
            db.query(SensorReading)
            .filter(SensorReading.machine_id == "MACHINE-001")
            .order_by(SensorReading.timestamp.desc(), SensorReading.id.desc())
            .limit(limit)
            .all()
        )
        source_rows.reverse()
        derived_rows = []
        for row in source_rows:
            simulated = simulate_machine_2(
                temperature=row.temperature,
                vibration=row.vibration,
                current=row.current,
                sound=row.sound,
            )
            derived_rows.append({
                "id": row.id,
                "machine_id": "MACHINE-002",
                "timestamp": row.timestamp,
                "temperature": simulated["temperature"],
                "vibration": simulated["vibration"],
                "current": simulated["current"],
                "sound": simulated["sound"],
                "motor_running": True,
                "source": "demo-fault-simulation",
                "health": simulated["health"],
                "machine_status": simulated["machine_status"],
                "failure_probability": simulated["failure_probability"],
                "diagnosis": simulated["diagnosis"],
                "recommendation": simulated["recommendation"],
                "failure_stage": simulated["failure_stage"],
                "remaining_life_hours": simulated["remaining_life_hours"],
                "prediction_explanation": simulated["simulation_note"],
            })
        return {
            "machine_id": machine_id,
            "count": len(derived_rows),
            "readings": derived_rows,
        }

    query = db.query(SensorReading)

    if machine_id:
        query = query.filter(SensorReading.machine_id == machine_id)

    rows = (
        query
        .order_by(SensorReading.timestamp.desc(), SensorReading.id.desc())
        .limit(limit)
        .all()
    )
    rows.reverse()
    return {
        "machine_id": machine_id,
        "count": len(rows),
        "readings": rows,
    }


# ============================================================
# SENSOR HISTORY
# ============================================================

@router.get(
    "/sensor-data/history/{machine_id}"
)
def sensor_history(
    machine_id: str,
    limit: int = Query(
        default=200,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    return readings(
        machine_id=machine_id,
        limit=limit,
        db=db,
    )


# ============================================================
# MACHINE-2 SIMULATION
# ============================================================

@router.get("/simulation/machine-2")
def get_machine_2_simulation(
    db: Session = Depends(get_db),
):
    """
    Generate the MACHINE-002 shaft-jam simulation
    from the latest MACHINE-001 reading.
    """

    latest = (
        db.query(SensorReading)
        .filter(
            SensorReading.machine_id
            == "MACHINE-001"
        )
        .order_by(
            SensorReading.timestamp.desc(),
            SensorReading.id.desc(),
        )
        .first()
    )

    if latest is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No MACHINE-001 sensor data "
                "available yet."
            ),
        )

    return simulate_machine_2(
        temperature=latest.temperature,
        vibration=latest.vibration,
        current=latest.current,
        sound=latest.sound,
        health=latest.health,
        failure_probability=(
            latest.failure_probability
        ),
    )