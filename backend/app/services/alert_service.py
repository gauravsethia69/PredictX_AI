from datetime import datetime, timezone


def build_alerts(readings):
    """
    Historical alert analysis only.
    This does not alter Arduino prediction values.
    """
    alerts = []

    ordered = sorted(readings, key=lambda r: r.timestamp, reverse=True)[:50]

    for r in ordered:
        if r.status.upper() in {"CRITICAL", "STOP", "EMERGENCY"} or r.health_score < 50:
            alerts.append({
                "id": f"reading-{r.id}-critical",
                "machine_id": r.machine_id,
                "timestamp": r.timestamp,
                "severity": "CRITICAL",
                "parameter": "machine_health",
                "description": f"Machine health is {r.health_score:.0f}%. Status: {r.status}.",
                "recommended_action": r.recommendation,
            })
        elif r.failure_risk >= 70 or r.health_score < 70:
            alerts.append({
                "id": f"reading-{r.id}-warning",
                "machine_id": r.machine_id,
                "timestamp": r.timestamp,
                "severity": "WARNING",
                "parameter": "failure_risk",
                "description": f"Arduino reports failure probability of {r.failure_risk:.0f}%. Diagnosis: {r.detected_fault}.",
                "recommended_action": r.recommendation,
            })

        if r.current > 0:
            # Only create a historical event when a current reading is unusually high
            # relative to the recent sample window; comparison is done by the route.
            pass

    return alerts


def utcnow():
    return datetime.now(timezone.utc)
