from datetime import datetime
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    machine_id: str
    timestamp: datetime
    severity: str
    parameter: str
    description: str
    recommended_action: str
