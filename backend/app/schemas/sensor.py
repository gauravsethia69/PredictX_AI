from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, AliasChoices

class SensorDataCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    machine_id: str
    temperature: float
    vibration: float
    current: float
    sound: float
    motor_running: bool = True
    source: str = "esp32"

    health: float
    machine_status: str = Field(
        validation_alias=AliasChoices("machine_status", "machineStatus")
    )
    failure_probability: float = Field(
        validation_alias=AliasChoices("failure_probability", "failureProbability")
    )
    diagnosis: str = Field(
        validation_alias=AliasChoices("diagnosis", "aiReport")
    )
    recommendation: str
    failure_stage: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("failure_stage", "failureStage")
    )
    remaining_life_hours: Optional[float] = Field(
        default=None,
        validation_alias=AliasChoices("remaining_life_hours", "remainingOperatingHours")
    )
    prediction_explanation: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("prediction_explanation", "predictionExplanation")
    )

class SensorReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    machine_id: str
    timestamp: datetime
    temperature: float
    vibration: float
    current: float
    sound: float
    motor_running: bool
    source: str
    health: float
    machine_status: str
    failure_probability: float
    diagnosis: str
    recommendation: str
    failure_stage: Optional[str]
    remaining_life_hours: Optional[float]
    prediction_explanation: Optional[str]
