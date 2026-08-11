from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from app.db.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    machine_id = Column(
        String(80),
        index=True,
        nullable=False,
    )

    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Raw ESP32 sensor values
    temperature = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)
    current = Column(Float, nullable=False)
    sound = Column(Float, nullable=False)

    # Machine state
    motor_running = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    source = Column(
        String(30),
        default="esp32",
        nullable=False,
    )

    # Predictive-maintenance results
    health = Column(Float, nullable=False)

    machine_status = Column(
        String(50),
        nullable=False,
    )

    failure_probability = Column(
        Float,
        nullable=False,
    )

    diagnosis = Column(
        Text,
        nullable=False,
    )

    recommendation = Column(
        Text,
        nullable=False,
    )

    # Extended prediction fields
    failure_stage = Column(
        String(100),
        nullable=True,
    )

    remaining_life_hours = Column(
        Float,
        nullable=True,
    )

    prediction_explanation = Column(
        Text,
        nullable=True,
    )