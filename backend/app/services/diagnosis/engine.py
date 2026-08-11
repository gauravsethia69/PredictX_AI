from typing import Dict, List

from app.services.diagnosis.fault_models import (
    DiagnosisResult,
    FaultMatch,
)
from app.services.diagnosis.fault_rules import (
    FAULT_LIBRARY,
)
from app.services.diagnosis.scorer import (
    score_all_faults,
)


HEALTHY_FAULT_CODE = "HLT001"

MAX_ALTERNATIVE_FAULTS = 3

SECONDARY_MINIMUM_CONFIDENCE = 58.0

SECONDARY_MAXIMUM_GAP = 18.0


def get_healthy_match(
    matches: List[FaultMatch],
) -> FaultMatch:
    """
    Returns the Healthy Operating Condition match.
    """

    for match in matches:
        if match.rule.code == HEALTHY_FAULT_CODE:
            return match

    raise RuntimeError(
        "Healthy operating condition rule is missing "
        "from the fault library."
    )


def is_similar_fault(
    first_match: FaultMatch,
    second_match: FaultMatch,
) -> bool:
    """
    Prevents closely related diagnoses from being shown
    as primary and secondary faults at the same time.

    Example:
    Bearing Wear + Bearing Lubrication Failure may be
    related, but can still be useful together.

    Identical fault codes or names are always duplicates.
    """

    if first_match.rule.code == second_match.rule.code:
        return True

    if (
        first_match.rule.name.strip().lower()
        == second_match.rule.name.strip().lower()
    ):
        return True

    return False


def choose_primary_fault(
    matches: List[FaultMatch],
) -> FaultMatch:
    """
    Selects the most suitable primary diagnosis.

    A fault must meet its own minimum confidence.
    If no abnormal fault qualifies, healthy condition
    becomes the primary result.
    """

    healthy_match = get_healthy_match(matches)

    abnormal_matches = [
        match
        for match in matches
        if (
            match.rule.code != HEALTHY_FAULT_CODE
            and match.is_valid_match
        )
    ]

    if not abnormal_matches:
        return healthy_match

    strongest_fault = abnormal_matches[0]

    healthy_is_stronger = (
        healthy_match.is_valid_match
        and healthy_match.confidence
        > strongest_fault.confidence
    )

    if healthy_is_stronger:
        return healthy_match

    return strongest_fault


def choose_secondary_fault(
    primary_fault: FaultMatch,
    matches: List[FaultMatch],
) -> FaultMatch | None:
    """
    Selects a secondary fault only when it is meaningful.

    Conditions:
    - Primary must not be healthy.
    - Secondary must not be the healthy rule.
    - Secondary confidence must be sufficiently high.
    - Confidence must be reasonably close to primary.
    - It must not be an exact duplicate.
    """

    if primary_fault.rule.code == HEALTHY_FAULT_CODE:
        return None

    for match in matches:
        if match.rule.code == HEALTHY_FAULT_CODE:
            continue

        if is_similar_fault(primary_fault, match):
            continue

        confidence_gap = (
            primary_fault.confidence
            - match.confidence
        )

        if (
            match.confidence
            >= SECONDARY_MINIMUM_CONFIDENCE
            and confidence_gap
            <= SECONDARY_MAXIMUM_GAP
        ):
            return match

    return None


def choose_alternative_faults(
    primary_fault: FaultMatch,
    secondary_fault: FaultMatch | None,
    matches: List[FaultMatch],
) -> List[FaultMatch]:
    """
    Returns additional probable diagnoses for explainability.
    """

    if primary_fault.rule.code == HEALTHY_FAULT_CODE:
        return []

    excluded_codes = {
        primary_fault.rule.code,
        HEALTHY_FAULT_CODE,
    }

    if secondary_fault is not None:
        excluded_codes.add(
            secondary_fault.rule.code
        )

    alternatives: List[FaultMatch] = []

    for match in matches:
        if match.rule.code in excluded_codes:
            continue

        if not match.is_valid_match:
            continue

        if is_similar_fault(primary_fault, match):
            continue

        alternatives.append(match)

        if len(alternatives) >= MAX_ALTERNATIVE_FAULTS:
            break

    return alternatives


def diagnose_machine(
    temperature: float,
    vibration: float,
    current: float,
    sound: float,
) -> DiagnosisResult:
    """
    Main public function for the diagnosis system.
    """

    sensor_values: Dict[str, float] = {
        "temperature": temperature,
        "vibration": vibration,
        "current": current,
        "sound": sound,
    }

    matches = score_all_faults(
        fault_library=FAULT_LIBRARY,
        sensor_values=sensor_values,
    )

    primary_fault = choose_primary_fault(
        matches=matches,
    )

    secondary_fault = choose_secondary_fault(
        primary_fault=primary_fault,
        matches=matches,
    )

    alternative_faults = choose_alternative_faults(
        primary_fault=primary_fault,
        secondary_fault=secondary_fault,
        matches=matches,
    )

    return DiagnosisResult(
        primary_fault=primary_fault,
        secondary_fault=secondary_fault,
        alternative_faults=alternative_faults,
    )