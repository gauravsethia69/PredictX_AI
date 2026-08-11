from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class SensorRange:
    """
    Defines the expected operating range of one sensor
    for a particular fault pattern.
    """

    minimum: float
    maximum: float
    weight: float = 1.0

    def __post_init__(self) -> None:
        if self.minimum > self.maximum:
            raise ValueError(
                "SensorRange minimum cannot be greater than maximum."
            )

        if self.weight <= 0:
            raise ValueError(
                "SensorRange weight must be greater than zero."
            )


@dataclass(frozen=True)
class FaultRule:
    """
    Describes one industrial fault pattern.

    This model only stores fault knowledge.
    The scoring logic will be written separately.
    """

    code: str
    name: str
    category: str
    severity: str

    sensor_ranges: Dict[str, SensorRange]

    root_cause: str
    possible_causes: List[str]
    recommendation: str

    maintenance_priority: str
    estimated_downtime: str

    spare_parts: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    maintenance_steps: List[str] = field(default_factory=list)
    safety_precautions: List[str] = field(default_factory=list)

    minimum_confidence: float = 55.0

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("Fault code cannot be empty.")

        if not self.name.strip():
            raise ValueError("Fault name cannot be empty.")

        if not self.sensor_ranges:
            raise ValueError(
                f"Fault rule {self.code} must contain sensor ranges."
            )

        if not 0 <= self.minimum_confidence <= 100:
            raise ValueError(
                "minimum_confidence must be between 0 and 100."
            )


@dataclass(frozen=True)
class SensorMatch:
    """
    Stores the matching result of one sensor.
    """

    sensor_name: str
    actual_value: float
    expected_minimum: float
    expected_maximum: float
    score: float
    weight: float
    matched: bool


@dataclass(frozen=True)
class FaultMatch:
    """
    Stores the calculated result after comparing sensor
    readings against one FaultRule.
    """

    rule: FaultRule
    confidence: float
    weighted_score: float
    matched_sensor_count: int
    total_sensor_count: int
    sensor_matches: Dict[str, SensorMatch]

    @property
    def is_valid_match(self) -> bool:
        return self.confidence >= self.rule.minimum_confidence


@dataclass(frozen=True)
class DiagnosisResult:
    """
    Final result returned by the diagnosis engine.
    """

    primary_fault: FaultMatch
    secondary_fault: FaultMatch | None
    alternative_faults: List[FaultMatch] = field(default_factory=list)

    @property
    def primary_fault_name(self) -> str:
        return self.primary_fault.rule.name

    @property
    def primary_fault_code(self) -> str:
        return self.primary_fault.rule.code

    @property
    def confidence(self) -> float:
        return self.primary_fault.confidence