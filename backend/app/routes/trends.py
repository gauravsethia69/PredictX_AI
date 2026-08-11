from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SensorReading
from app.services.machine2_simulation import simulate_machine_2

router = APIRouter(prefix="/api", tags=["Trends"])


def direction(values, rising="Rising", falling="Falling", stable="Stable"):
    if len(values) < 2:
        return stable
    third = max(1, len(values) // 3)
    first = sum(values[:third]) / len(values[:third])
    last = sum(values[-third:]) / len(values[-third:])
    delta = last - first
    scale = max(abs(first), 1)
    if delta > scale * 0.05:
        return rising
    if delta < -scale * 0.05:
        return falling
    return stable


@router.get("/trends/{machine_id}")
def trends(machine_id: str, limit: int = Query(default=200, ge=1, le=500), db: Session = Depends(get_db)):
    source_id = "MACHINE-001" if machine_id == "MACHINE-002" else machine_id
    rows = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == source_id)
        .order_by(SensorReading.timestamp.desc(), SensorReading.id.desc())
        .limit(limit)
        .all()
    )
    rows.reverse()

    data = []
    for r in rows:
        if machine_id == "MACHINE-002":
            sim = simulate_machine_2(r.temperature, r.vibration, r.current, r.sound)
            data.append({
                "timestamp": r.timestamp,
                "temperature": sim["temperature"],
                "vibration": sim["vibration"],
                "current": sim["current"],
                "sound": sim["sound"],
                "health": sim["health"],
                "failure_probability": sim["failure_probability"],
                "machine_status": sim["machine_status"],
            })
        else:
            data.append({
                "timestamp": r.timestamp,
                "temperature": r.temperature,
                "vibration": r.vibration,
                "current": r.current,
                "sound": r.sound,
                "health": r.health,
                "failure_probability": r.failure_probability,
                "machine_status": r.machine_status,
            })

    return {
        "machine_id": machine_id,
        "count": len(data),
        "data": data,
        "health_trend": direction([r["health"] for r in data]),
        "failure_risk_trend": direction([r["failure_probability"] for r in data]),
        "temperature_trend": direction([r["temperature"] for r in data]),
        "current_trend": direction([r["current"] for r in data]),
        "sound_trend": direction([r["sound"] for r in data]),
        "vibration_trend": direction([r["vibration"] for r in data]),
    }
