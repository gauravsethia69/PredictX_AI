from typing import Any, Dict, Optional
from pydantic import BaseModel

class DashboardResponse(BaseModel):
    machine_id: str
    latest: Any
    historical_analysis: Dict[str, Any]
    alert_count: int
