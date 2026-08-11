from typing import Dict

from app.services.diagnosis.fault_models import (
    FaultMatch,
    FaultRule,
    SensorMatch,
    SensorRange,
)


def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    return max(minimum, min(value, maximum))


def calculate_sensor_score(
    actual_value: float,
    expected_range: SensorRange,
) -> float:
    """
    Calculates how closely a sensor value matches a fault range.

    Scoring behaviour:
    - Inside expected range: 80–100
    - Slightly outside range: gradually decreases
    - Far outside range: approaches 0
    """

    minimum = expected_range.minimum
    maximum = expected_range.maximum

    if minimum == maximum:
        return 100.0 if actual_value == minimum else 0.0

    range_width = maximum - minimum
    midpoint = (minimum + maximum) / 2

    if minimum <= actual_value <= maximum:
        distance_from_midpoint = abs(actual_value - midpoint)
        half_width = range_width / 2

        if half_width == 0:
            return 100.0

        midpoint_similarity = 1 - (
            distance_from_midpoint / half_width
        )

        score = 80 + (midpoint_similarity * 20)

        return round(
            clamp(score, 80, 100),
            2,
        )

    if actual_value < minimum:
        distance_outside = minimum - actual_value
    else:
        distance_outside = actual_value - maximum

    normalised_distance = distance_outside / range_width

    score = 80 * (1 - normalised_distance)

    return round(
        clamp(score, 0, 79.99),
        2,
    )


def score_fault_rule(
    rule: FaultRule,
    sensor_values: Dict[str, float],
) -> FaultMatch:
    """
    Scores one fault rule against the provided sensor values.
    """

    sensor_matches: Dict[str, SensorMatch] = {}

    total_weighted_score = 0.0
    total_weight = 0.0
    matched_sensor_count = 0

    for sensor_name, expected_range in rule.sensor_ranges.items():
        if sensor_name not in sensor_values:
            continue

        actual_value = sensor_values[sensor_name]

        score = calculate_sensor_score(
            actual_value=actual_value,
            expected_range=expected_range,
        )

        matched = (
            expected_range.minimum
            <= actual_value
            <= expected_range.maximum
        )

        if matched:
            matched_sensor_count += 1

        weighted_sensor_score = (
            score * expected_range.weight
        )

        total_weighted_score += weighted_sensor_score
        total_weight += expected_range.weight

        sensor_matches[sensor_name] = SensorMatch(
            sensor_name=sensor_name,
            actual_value=actual_value,
            expected_minimum=expected_range.minimum,
            expected_maximum=expected_range.maximum,
            score=score,
            weight=expected_range.weight,
            matched=matched,
        )

    if total_weight == 0:
        confidence = 0.0
        weighted_score = 0.0
    else:
        weighted_score = total_weighted_score / total_weight

        coverage_ratio = (
            len(sensor_matches)
            / len(rule.sensor_ranges)
        )

        confidence = weighted_score * coverage_ratio

    return FaultMatch(
        rule=rule,
        confidence=round(
            clamp(confidence, 0, 100),
            2,
        ),
        weighted_score=round(
            clamp(weighted_score, 0, 100),
            2,
        ),
        matched_sensor_count=matched_sensor_count,
        total_sensor_count=len(rule.sensor_ranges),
        sensor_matches=sensor_matches,
    )


def score_all_faults(
    fault_library: list[FaultRule],
    sensor_values: Dict[str, float],
) -> list[FaultMatch]:
    """
    Scores all fault rules and sorts them from highest
    confidence to lowest confidence.
    """

    matches = [
        score_fault_rule(
            rule=rule,
            sensor_values=sensor_values,
        )
        for rule in fault_library
    ]

    return sorted(
        matches,
        key=lambda match: match.confidence,
        reverse=True,
    )