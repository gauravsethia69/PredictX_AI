from statistics import mean


def direction(values: list[float], threshold: float = 0.0) -> str:
    if len(values) < 2:
        return "Stable"

    mid = len(values) // 2
    first = mean(values[:mid])
    second = mean(values[mid:])

    if second > first + threshold:
        return "Rising"
    if second < first - threshold:
        return "Falling"
    return "Stable"


def calculate_historical_analysis(readings):
    if not readings:
        return {
            "reading_count": 0,
            "health_trend": "Stable",
            "failure_risk_trend": "Stable",
            "temperature_trend": "Stable",
            "current_trend": "Stable",
            "sound_trend": "Stable",
            "vibration_trend": "Stable",
            "health_change": 0,
        }

    ordered = sorted(readings, key=lambda r: r.timestamp)
    recent = ordered[-20:]

    health = [r.health_score for r in recent]
    risk = [r.failure_risk for r in recent]
    temperature = [r.temperature for r in recent]
    current = [r.current for r in recent]
    sound = [r.sound for r in recent]
    vibration = [r.vibration for r in recent]

    return {
        "reading_count": len(ordered),
        "health_trend": direction(health, 1),
        "failure_risk_trend": direction(risk, 1),
        "temperature_trend": direction(temperature, 0.5),
        "current_trend": direction(current, 0.05),
        "sound_trend": direction(sound, 20),
        "vibration_trend": direction(vibration, 0.1),
        "health_change": round(health[-1] - health[0], 2),
    }
