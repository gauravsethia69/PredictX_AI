from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import SensorReading


router = APIRouter(
    prefix="/api",
    tags=["Alerts"],
)


@router.get("/alerts/{machine_id}")
def alerts(
    machine_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(SensorReading)
        .filter(
            SensorReading.machine_id
            == machine_id
        )
        .order_by(
            SensorReading.timestamp.desc(),
            SensorReading.id.desc(),
        )
        .limit(limit)
        .all()
    )

    output = []

    for reading in rows:
        failure_probability = (
            reading.failure_probability
        )

        machine_status = str(
            reading.machine_status or ""
        ).upper()

        if failure_probability >= 70:
            severity = "CRITICAL"
            parameter = "Failure probability"

            description = (
                f"ESP32 reports "
                f"{failure_probability:.0f}% "
                f"failure probability."
            )

            action = reading.recommendation

        elif failure_probability >= 30:
            severity = "WARNING"
            parameter = "Failure probability"

            description = (
                "ESP32 reports elevated "
                "failure probability "
                f"({failure_probability:.0f}%)."
            )

            action = reading.recommendation

        elif machine_status not in {
            "GOOD",
            "HEALTHY",
            "NORMAL",
        }:
            severity = "WARNING"
            parameter = "Machine status"

            description = (
                "ESP32 machine status is "
                f"{reading.machine_status}."
            )

            action = reading.recommendation

        else:
            continue

        output.append(
            {
                "id": reading.id,
                "timestamp": reading.timestamp,
                "severity": severity,
                "parameter": parameter,
                "description": description,
                "recommended_action": action,
            }
        )

    return {
        "machine_id": machine_id,
        "count": len(output),
        "alerts": output,
    }