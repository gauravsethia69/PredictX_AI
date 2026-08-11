from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.db.models import SensorReading

# ============================================================
# CONSTANTS
# ============================================================

MINIMUM_TREND_READINGS = 3

SENSOR_NAMES = (
    "temperature",
    "vibration",
    "current",
    "sound",
)

ANOMALY_THRESHOLDS = {
    "temperature": {
        "absolute_change": 10.0,
        "percentage_change": 20.0,
    },
    "vibration": {
        "absolute_change": 0.45,
        "percentage_change": 35.0,
    },
    "current": {
        "absolute_change": 0.65,
        "percentage_change": 30.0,
    },
    "sound": {
        "absolute_change": 12.0,
        "percentage_change": 25.0,
    },
}


# ============================================================
# BASIC UTILITIES
# ============================================================

def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Keeps a numeric value inside the specified range.
    """

    return max(
        minimum,
        min(float(value), maximum),
    )


def round_value(
    value: float,
    digits: int = 2,
) -> float:
    """
    Safely rounds numeric values.
    """

    return round(float(value), digits)


def safe_percentage_change(
    previous: float,
    current: float,
) -> float:
    """
    Calculates percentage change while preventing
    division-by-zero errors.
    """

    previous = float(previous)
    current = float(current)

    if previous == 0:
        if current == 0:
            return 0.0

        return 100.0

    percentage_change = (
        (current - previous)
        / abs(previous)
    ) * 100.0

    return round_value(percentage_change)


def calculate_average(
    values: List[float],
) -> float:
    """
    Returns the average of a list of values.
    """

    if not values:
        return 0.0

    return round_value(
        sum(values) / len(values)
    )


# ============================================================
# SENSOR EXTRACTION
# ============================================================

def extract_sensor_values(
    readings: List[SensorReading],
    sensor_name: str,
) -> List[float]:
    """
    Extracts values for one sensor from database readings.
    """

    return [
        float(getattr(reading, sensor_name))
        for reading in readings
    ]


# ============================================================
# LINEAR TREND CALCULATION
# ============================================================

def calculate_linear_slope(
    values: List[float],
) -> float:
    """
    Calculates a simple least-squares linear slope.

    Positive slope:
        values are increasing.

    Negative slope:
        values are decreasing.

    Near-zero slope:
        values are stable.
    """

    count = len(values)

    if count < 2:
        return 0.0

    x_values = list(range(count))

    x_average = sum(x_values) / count
    y_average = sum(values) / count

    numerator = sum(
        (
            x_value - x_average
        ) * (
            y_value - y_average
        )
        for x_value, y_value
        in zip(x_values, values)
    )

    denominator = sum(
        (x_value - x_average) ** 2
        for x_value in x_values
    )

    if denominator == 0:
        return 0.0

    return round_value(
        numerator / denominator,
        4,
    )


def classify_sensor_trend(
    sensor_name: str,
    slope: float,
) -> str:
    """
    Converts a sensor slope into an understandable trend.
    """

    stability_thresholds = {
        "temperature": 0.5,
        "vibration": 0.03,
        "current": 0.05,
        "sound": 0.7,
        "health_score": 0.5,
        "failure_risk": 0.5,
    }

    threshold = stability_thresholds.get(
        sensor_name,
        0.1,
    )

    if slope > threshold:
        return "Increasing"

    if slope < -threshold:
        return "Decreasing"

    return "Stable"


# ============================================================
# SENSOR TREND ANALYSIS
# ============================================================

def analyse_sensor_trend(
    sensor_name: str,
    readings: List[SensorReading],
) -> Dict[str, Any]:
    """
    Analyses historical behaviour of one sensor.
    """

    values = extract_sensor_values(
        readings=readings,
        sensor_name=sensor_name,
    )

    if not values:
        return {
            "sensor": sensor_name,
            "first_value": 0.0,
            "latest_value": 0.0,
            "average_value": 0.0,
            "minimum_value": 0.0,
            "maximum_value": 0.0,
            "absolute_change": 0.0,
            "percentage_change": 0.0,
            "slope": 0.0,
            "trend": "Insufficient data",
        }

    first_value = values[0]
    latest_value = values[-1]

    absolute_change = latest_value - first_value

    percentage_change = safe_percentage_change(
        previous=first_value,
        current=latest_value,
    )

    slope = calculate_linear_slope(values)

    trend = classify_sensor_trend(
        sensor_name=sensor_name,
        slope=slope,
    )

    return {
        "sensor": sensor_name,
        "first_value": round_value(first_value),
        "latest_value": round_value(latest_value),
        "average_value": calculate_average(values),
        "minimum_value": round_value(min(values)),
        "maximum_value": round_value(max(values)),
        "absolute_change": round_value(
            absolute_change
        ),
        "percentage_change": percentage_change,
        "slope": slope,
        "trend": trend,
    }


# ============================================================
# ANOMALY DETECTION
# ============================================================

def detect_sensor_anomaly(
    sensor_name: str,
    previous_value: float,
    latest_value: float,
) -> Dict[str, Any]:
    """
    Detects sudden sensor changes between the latest
    two readings.
    """

    absolute_change = (
        float(latest_value)
        - float(previous_value)
    )

    percentage_change = safe_percentage_change(
        previous=previous_value,
        current=latest_value,
    )

    threshold = ANOMALY_THRESHOLDS[
        sensor_name
    ]

    absolute_limit = threshold[
        "absolute_change"
    ]

    percentage_limit = threshold[
        "percentage_change"
    ]

    is_anomaly = bool(
        abs(absolute_change) >= absolute_limit
        or abs(percentage_change) >= percentage_limit
    )

    if not is_anomaly:
        direction = "Stable"

    elif absolute_change > 0:
        direction = "Sudden increase"

    else:
        direction = "Sudden decrease"

    severity = classify_anomaly_severity(
        absolute_change=absolute_change,
        percentage_change=percentage_change,
        absolute_limit=absolute_limit,
        percentage_limit=percentage_limit,
    )

    return {
        "sensor": sensor_name,
        "previous_value": round_value(
            previous_value
        ),
        "latest_value": round_value(
            latest_value
        ),
        "absolute_change": round_value(
            absolute_change
        ),
        "percentage_change": percentage_change,
        "is_anomaly": is_anomaly,
        "direction": direction,
        "severity": severity,
    }


def classify_anomaly_severity(
    absolute_change: float,
    percentage_change: float,
    absolute_limit: float,
    percentage_limit: float,
) -> str:
    """
    Classifies anomaly intensity.
    """

    absolute_ratio = (
        abs(absolute_change)
        / max(absolute_limit, 0.001)
    )

    percentage_ratio = (
        abs(percentage_change)
        / max(percentage_limit, 0.001)
    )

    anomaly_ratio = max(
        absolute_ratio,
        percentage_ratio,
    )

    if anomaly_ratio < 1.0:
        return "None"

    if anomaly_ratio < 1.5:
        return "Low"

    if anomaly_ratio < 2.5:
        return "Moderate"

    return "High"


def detect_latest_anomalies(
    readings: List[SensorReading],
) -> List[Dict[str, Any]]:
    """
    Detects anomalies between the latest and previous reading.
    """

    if len(readings) < 2:
        return []

    previous_reading = readings[-2]
    latest_reading = readings[-1]

    anomalies = []

    for sensor_name in SENSOR_NAMES:
        anomaly = detect_sensor_anomaly(
            sensor_name=sensor_name,
            previous_value=float(
                getattr(
                    previous_reading,
                    sensor_name,
                )
            ),
            latest_value=float(
                getattr(
                    latest_reading,
                    sensor_name,
                )
            ),
        )

        anomalies.append(anomaly)

    return anomalies


# ============================================================
# HEALTH AND RISK TREND
# ============================================================

def analyse_metric_trend(
    readings: List[SensorReading],
    field_name: str,
) -> Dict[str, Any]:
    """
    Analyses database metrics such as health score
    and failure risk.
    """

    values = [
        float(getattr(reading, field_name))
        for reading in readings
        if getattr(reading, field_name) is not None
    ]

    if not values:
        return {
            "first_value": 0.0,
            "latest_value": 0.0,
            "average_value": 0.0,
            "absolute_change": 0.0,
            "percentage_change": 0.0,
            "slope": 0.0,
            "trend": "Insufficient data",
        }

    first_value = values[0]
    latest_value = values[-1]

    slope = calculate_linear_slope(values)

    trend = classify_sensor_trend(
        sensor_name=field_name,
        slope=slope,
    )

    return {
        "first_value": round_value(first_value),
        "latest_value": round_value(latest_value),
        "average_value": calculate_average(values),
        "absolute_change": round_value(
            latest_value - first_value
        ),
        "percentage_change": (
            safe_percentage_change(
                previous=first_value,
                current=latest_value,
            )
        ),
        "slope": slope,
        "trend": trend,
    }


# ============================================================
# OVERALL MACHINE TREND
# ============================================================

def determine_machine_trend(
    sensor_trends: Dict[str, Dict[str, Any]],
    health_trend: Dict[str, Any],
    risk_trend: Dict[str, Any],
) -> str:
    """
    Determines whether machine condition is improving,
    stable or degrading.
    """

    degradation_score = 0
    improvement_score = 0

    harmful_increasing_sensors = {
        "temperature",
        "vibration",
        "current",
        "sound",
    }

    for sensor_name, trend_data in (
        sensor_trends.items()
    ):
        trend = trend_data["trend"]

        if (
            sensor_name
            in harmful_increasing_sensors
            and trend == "Increasing"
        ):
            degradation_score += 1

        elif (
            sensor_name
            in harmful_increasing_sensors
            and trend == "Decreasing"
        ):
            improvement_score += 1

    if health_trend["trend"] == "Decreasing":
        degradation_score += 2

    elif health_trend["trend"] == "Increasing":
        improvement_score += 2

    if risk_trend["trend"] == "Increasing":
        degradation_score += 2

    elif risk_trend["trend"] == "Decreasing":
        improvement_score += 2

    if degradation_score >= improvement_score + 2:
        return "Degrading"

    if improvement_score >= degradation_score + 2:
        return "Improving"

    return "Stable"


# ============================================================
# TREND RISK SCORE
# ============================================================

def calculate_trend_risk_score(
    sensor_trends: Dict[str, Dict[str, Any]],
    anomalies: List[Dict[str, Any]],
    machine_trend: str,
) -> float:
    """
    Calculates a trend-based risk score from 0 to 100.
    """

    risk_score = 0.0

    for trend_data in sensor_trends.values():
        if trend_data["trend"] == "Increasing":
            risk_score += 8.0

    anomaly_weights = {
        "None": 0.0,
        "Low": 5.0,
        "Moderate": 12.0,
        "High": 22.0,
    }

    for anomaly in anomalies:
        risk_score += anomaly_weights.get(
            anomaly["severity"],
            0.0,
        )

    if machine_trend == "Degrading":
        risk_score += 25.0

    elif machine_trend == "Improving":
        risk_score -= 10.0

    return round_value(
        clamp(
            risk_score,
            0.0,
            100.0,
        )
    )


# ============================================================
# ALERT GENERATION
# ============================================================

def generate_trend_alerts(
    sensor_trends: Dict[str, Dict[str, Any]],
    anomalies: List[Dict[str, Any]],
    machine_trend: str,
) -> List[str]:
    """
    Generates understandable preventive alerts.
    """

    alerts: List[str] = []

    for sensor_name, data in sensor_trends.items():
        if data["trend"] == "Increasing":
            alerts.append(
                f"{sensor_name.replace('_', ' ').title()} "
                f"is showing a continuous upward trend."
            )

    for anomaly in anomalies:
        if not anomaly["is_anomaly"]:
            continue

        alerts.append(
            f"{anomaly['sensor'].replace('_', ' ').title()} "
            f"shows a {anomaly['direction'].lower()} "
            f"of {abs(anomaly['percentage_change'])}%."
        )

    if machine_trend == "Degrading":
        alerts.append(
            "Overall machine condition is degrading. "
            "Preventive inspection should be scheduled."
        )

    if not alerts:
        alerts.append(
            "No significant historical anomaly or harmful "
            "trend has been detected."
        )

    return alerts


# ============================================================
# SUMMARY GENERATOR
# ============================================================

def generate_trend_summary(
    machine_trend: str,
    anomaly_count: int,
    trend_risk_score: float,
    reading_count: int,
) -> str:
    """
    Generates a dashboard-friendly historical summary.
    """

    if reading_count < MINIMUM_TREND_READINGS:
        return (
            "More historical readings are required for a "
            "reliable machine trend analysis."
        )

    if machine_trend == "Degrading":
        return (
            f"Machine condition is degrading across "
            f"{reading_count} readings. "
            f"{anomaly_count} sensor anomalies were detected, "
            f"with a trend risk score of "
            f"{trend_risk_score}%."
        )

    if machine_trend == "Improving":
        return (
            f"Machine condition is improving across "
            f"{reading_count} readings. "
            f"The current trend risk score is "
            f"{trend_risk_score}%."
        )

    return (
        f"Machine condition is stable across "
        f"{reading_count} readings. "
        f"{anomaly_count} recent sensor anomalies were detected."
    )


# ============================================================
# MAIN TREND ENGINE
# ============================================================

def analyse_historical_trend(
    readings: List[SensorReading],
) -> Dict[str, Any]:
    """
    Runs complete historical trend and anomaly analysis.

    Important:
        Readings must be ordered from oldest to newest.
    """

    reading_count = len(readings)

    if reading_count == 0:
        return {
            "reading_count": 0,
            "machine_trend": "Insufficient data",
            "trend_risk_score": 0.0,
            "sensor_trends": {},
            "health_score_trend": {},
            "failure_risk_trend": {},
            "latest_anomalies": [],
            "anomaly_count": 0,
            "alerts": [
                "No sensor readings are available."
            ],
            "summary": (
                "No historical data is available for "
                "trend analysis."
            ),
        }

    sensor_trends = {
        sensor_name: analyse_sensor_trend(
            sensor_name=sensor_name,
            readings=readings,
        )
        for sensor_name in SENSOR_NAMES
    }

    health_score_trend = analyse_metric_trend(
        readings=readings,
        field_name="health_score",
    )

    failure_risk_trend = analyse_metric_trend(
        readings=readings,
        field_name="failure_risk",
    )

    latest_anomalies = detect_latest_anomalies(
        readings=readings
    )

    machine_trend = determine_machine_trend(
        sensor_trends=sensor_trends,
        health_trend=health_score_trend,
        risk_trend=failure_risk_trend,
    )

    trend_risk_score = calculate_trend_risk_score(
        sensor_trends=sensor_trends,
        anomalies=latest_anomalies,
        machine_trend=machine_trend,
    )

    anomaly_count = sum(
        1
        for anomaly in latest_anomalies
        if anomaly["is_anomaly"]
    )

    alerts = generate_trend_alerts(
        sensor_trends=sensor_trends,
        anomalies=latest_anomalies,
        machine_trend=machine_trend,
    )

    summary = generate_trend_summary(
        machine_trend=machine_trend,
        anomaly_count=anomaly_count,
        trend_risk_score=trend_risk_score,
        reading_count=reading_count,
    )

    return {
        "reading_count": reading_count,
        "machine_trend": machine_trend,
        "trend_risk_score": trend_risk_score,
        "sensor_trends": sensor_trends,
        "health_score_trend": health_score_trend,
        "failure_risk_trend": failure_risk_trend,
        "latest_anomalies": latest_anomalies,
        "anomaly_count": anomaly_count,
        "alerts": alerts,
        "summary": summary,
    }