
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# SENSOR INPUT FROM ARDUINO / ESP32
# ============================================================

class SensorReadingCreate(BaseModel):
    """
    Data received directly from the Arduino / ESP32.

    IMPORTANT:
    Health, status, failure probability, diagnosis and
    recommendation are calculated by Arduino.
    Backend does NOT recalculate them.
    """

    machine_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    # --------------------------------------------------------
    # Raw sensor values
    # --------------------------------------------------------

    temperature: float = Field(
        ...,
        ge=0,
        le=150,
        description="Machine temperature in degrees Celsius",
    )

    vibration: float = Field(
        ...,
        ge=0,
        le=10,
        description="Vibration value received from Arduino",
    )

    current: float = Field(
        ...,
        ge=0,
        le=20,
        description="Electrical current in amperes",
    )

    sound: float = Field(
        ...,
        ge=0,
        le=4095,
        description="Sound sensor ADC value",
    )

    motor_running: bool = True

    source: str = Field(
        default="esp32",
        min_length=1,
        max_length=100,
    )

    # ========================================================
    # ARDUINO-CALCULATED VALUES
    # ========================================================

    health: float = Field(
        ...,
        ge=0,
        le=100,
        description="Health score calculated by Arduino",
    )

    machine_status: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Machine status calculated by Arduino",
    )

    failure_probability: float = Field(
        ...,
        ge=0,
        le=100,
        description="Failure probability calculated by Arduino",
    )

    diagnosis: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="AI diagnosis calculated by Arduino",
    )

    recommendation: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Maintenance recommendation calculated by Arduino",
    )


# ============================================================
# HUMAN-FRIENDLY ANALYSIS
# ============================================================

class AbnormalParameter(BaseModel):
    parameter: str
    display_name: str
    value: float
    unit: str
    condition: str
    message: str


class SensorOverviewItem(BaseModel):
    name: str
    value: float
    unit: str
    status: str
    message: str


class RecommendedAction(BaseModel):
    action: str
    timeframe: str
    machine_can_continue: bool
    service_time_estimate: str
    estimate_note: str


class DataSourceInfo(BaseModel):
    type: str
    is_live: bool
    message: str


class TestContext(BaseModel):
    is_simulated: bool
    scenario: Optional[str] = None
    message: str


# ============================================================
# HEALTH ANALYSIS
# ============================================================

class HealthAnalysis(BaseModel):
    """
    Final analysis shown by the dashboard.

    Health, status and failure risk come from Arduino.
    Trend information is calculated by backend from history.
    """

    # --------------------------------------------------------
    # Arduino values
    # --------------------------------------------------------

    health_score: float
    status: str
    failure_risk: float
    severity: str

    shutdown_recommended: bool

    # --------------------------------------------------------
    # Arduino diagnosis
    # --------------------------------------------------------

    detected_fault: str
    detected_condition: str
    probable_fault: Optional[str] = None

    fault_code: str

    confidence: float
    confidence_level: str
    confidence_type: str
    confidence_message: str
    diagnosis_state: str

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    root_cause: str
    possible_causes: List[str]

    recommendation: str

    # --------------------------------------------------------
    # Maintenance
    # --------------------------------------------------------

    maintenance_priority: str
    estimated_downtime: str

    abnormal_parameters: List[
        AbnormalParameter
    ] = Field(default_factory=list)

    # --------------------------------------------------------
    # Human-friendly information
    # --------------------------------------------------------

    user_message: str

    why_this_result: List[str] = Field(
        default_factory=list
    )

    recommended_action: RecommendedAction

    sensor_overview: List[
        SensorOverviewItem
    ] = Field(default_factory=list)

    analysis_note: str

    analysis_version: str

    summary: str


# ============================================================
# SENSOR MATCH
# ============================================================

class SensorMatchResponse(BaseModel):
    sensor_name: str

    actual_value: float

    expected_minimum: Optional[float] = None
    expected_maximum: Optional[float] = None
    safety_limit: Optional[float] = None

    score: float
    weight: float
    matched: bool

    reason: Optional[str] = None


# ============================================================
# ARDUINO DIAGNOSIS RESPONSE
# ============================================================

class FaultDetailsResponse(BaseModel):
    """
    Diagnosis information based on Arduino AI engine.

    Backend does not independently diagnose the machine.
    """

    code: str
    name: str
    category: str
    severity: str
    confidence: float

    root_cause: str
    possible_causes: List[str]

    recommendation: str

    maintenance_priority: str
    estimated_downtime: str

    spare_parts: List[str]
    tools: List[str]

    maintenance_steps: List[str]
    safety_precautions: List[str]

    matched_sensor_count: int
    total_sensor_count: int

    sensor_matches: Dict[
        str,
        SensorMatchResponse
    ]


class DiagnosisResponse(BaseModel):
    primary_fault: FaultDetailsResponse

    secondary_fault: Optional[
        FaultDetailsResponse
    ] = None

    alternative_faults: List[
        FaultDetailsResponse
    ] = Field(default_factory=list)


# ============================================================
# TREND RESPONSE
# ============================================================

class SensorTrendResponse(BaseModel):
    """
    Historical trend calculated by backend.

    This does NOT modify Arduino calculations.
    """

    sensor: str

    first_value: float
    latest_value: float

    average_value: float

    minimum_value: float
    maximum_value: float

    absolute_change: float
    percentage_change: float

    slope: float

    trend: str


class MetricTrendResponse(BaseModel):
    """
    Trend for Arduino-generated metrics such as:
    health score and failure risk.
    """

    first_value: float
    latest_value: float

    average_value: float

    absolute_change: float
    percentage_change: float

    slope: float

    trend: str


class TrendAnalysisResponse(BaseModel):

    reading_count: int

    machine_trend: str

    trend_risk_score: float

    sensor_trends: Dict[
        str,
        SensorTrendResponse
    ]

    health_score_trend: MetricTrendResponse

    failure_risk_trend: MetricTrendResponse

    latest_anomalies: List[
        Dict[str, object]
    ]

    anomaly_count: int

    alerts: List[str]

    summary: str


# ============================================================
# ALERT RESPONSE
# ============================================================

class AlertResponse(BaseModel):

    code: str

    title: str

    message: str

    severity: str

    priority: int

    category: str

    sensor: Optional[str] = None

    action_required: str

    immediate_action: bool


class MaintenanceResponse(BaseModel):

    required: bool

    urgency: str

    timeframe: str

    action: str


class MachineAlertResponse(BaseModel):

    alert_count: int

    actionable_alert_count: int

    immediate_alert_count: int

    highest_severity: str

    maintenance: MaintenanceResponse

    alerts: List[
        AlertResponse
    ]


# ============================================================
# FINAL SENSOR API RESPONSE
# ============================================================

class SensorReadingResponse(BaseModel):
    """
    Complete response returned to frontend.

    Architecture:

        Arduino
            ↓
        Raw sensors
            ↓
        Arduino health / AI / recommendation
            ↓
        Backend stores values
            ↓
        Backend calculates history / trend / anomaly
            ↓
        Backend creates human-friendly dashboard data
            ↓
        Frontend
    """

    id: Optional[int] = None

    machine_id: str

    timestamp: datetime

    # --------------------------------------------------------
    # Raw sensor values
    # --------------------------------------------------------

    temperature: float
    vibration: float
    current: float
    sound: float

    motor_running: bool

    source: str

    # --------------------------------------------------------
    # Data source
    # --------------------------------------------------------

    data_source: DataSourceInfo

    test_context: TestContext

    # --------------------------------------------------------
    # Arduino analysis
    # --------------------------------------------------------

    analysis: HealthAnalysis

    diagnosis: DiagnosisResponse

    # --------------------------------------------------------
    # Backend historical intelligence
    # --------------------------------------------------------

    trend: Optional[
        TrendAnalysisResponse
    ] = None

    alerts: Optional[
        MachineAlertResponse
    ] = None


# ============================================================
# DASHBOARD RESPONSE
# ============================================================

class DashboardResponse(BaseModel):
    """
    Complete machine dashboard response.

    Arduino provides:
        - Health
        - Status
        - Failure probability
        - Diagnosis
        - Recommendation
        - Relay/motor state

    Backend provides:
        - History
        - Trends
        - Anomalies
        - Alerts
        - Human-friendly presentation
    """

    machine_id: str

    latest_timestamp: datetime

    # --------------------------------------------------------
    # Current Arduino values
    # --------------------------------------------------------

    machine_status: str

    health_score: float

    failure_risk: float

    diagnosis: str

    recommendation: str

    motor_running: bool

    # --------------------------------------------------------
    # Current sensor readings
    # --------------------------------------------------------

    temperature: float

    vibration: float

    current: float

    sound: float

    # --------------------------------------------------------
    # Historical backend analysis
    # --------------------------------------------------------

    machine_trend: str

    trend_risk_score: float

    reading_count: int

    sensor_trends: Dict[
        str,
        SensorTrendResponse
    ]

    health_score_trend: MetricTrendResponse

    failure_risk_trend: MetricTrendResponse

    # --------------------------------------------------------
    # Alerts
    # --------------------------------------------------------

    alert_count: int

    actionable_alert_count: int

    immediate_alert_count: int

    highest_severity: str

    alerts: List[
        AlertResponse
    ]

    # --------------------------------------------------------
    # Maintenance
    # --------------------------------------------------------

    maintenance: MaintenanceResponse

    # --------------------------------------------------------
    # Human-friendly dashboard summary
    # --------------------------------------------------------

    summary: str

