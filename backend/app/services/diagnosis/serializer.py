from app.schemas import (
    DiagnosisResponse,
    FaultDetailsResponse,
    SensorMatchResponse,
)
from app.services.diagnosis.fault_models import (
    DiagnosisResult,
    FaultMatch,
)


def fault_match_to_response(
    fault_match: FaultMatch,
) -> FaultDetailsResponse:
    """
    Converts internal diagnosis dataclass into
    a Pydantic API response model.
    """

    rule = fault_match.rule

    sensor_matches = {
        sensor_name: SensorMatchResponse(
            sensor_name=sensor_match.sensor_name,
            actual_value=sensor_match.actual_value,
            expected_minimum=sensor_match.expected_minimum,
            expected_maximum=sensor_match.expected_maximum,
            score=sensor_match.score,
            weight=sensor_match.weight,
            matched=sensor_match.matched,
        )
        for sensor_name, sensor_match
        in fault_match.sensor_matches.items()
    }

    return FaultDetailsResponse(
        code=rule.code,
        name=rule.name,
        category=rule.category,
        severity=rule.severity,
        confidence=fault_match.confidence,

        root_cause=rule.root_cause,
        possible_causes=rule.possible_causes,
        recommendation=rule.recommendation,

        maintenance_priority=rule.maintenance_priority,
        estimated_downtime=rule.estimated_downtime,

        spare_parts=rule.spare_parts,
        tools=rule.tools,
        maintenance_steps=rule.maintenance_steps,
        safety_precautions=rule.safety_precautions,

        matched_sensor_count=(
            fault_match.matched_sensor_count
        ),
        total_sensor_count=(
            fault_match.total_sensor_count
        ),

        sensor_matches=sensor_matches,
    )


def diagnosis_to_response(
    diagnosis: DiagnosisResult,
) -> DiagnosisResponse:
    """
    Converts complete diagnosis result into
    the final API diagnosis response.
    """

    primary_fault = fault_match_to_response(
        diagnosis.primary_fault
    )

    secondary_fault = None

    if diagnosis.secondary_fault is not None:
        secondary_fault = fault_match_to_response(
            diagnosis.secondary_fault
        )

    alternative_faults = [
        fault_match_to_response(fault)
        for fault in diagnosis.alternative_faults
    ]

    return DiagnosisResponse(
        primary_fault=primary_fault,
        secondary_fault=secondary_fault,
        alternative_faults=alternative_faults,
    )