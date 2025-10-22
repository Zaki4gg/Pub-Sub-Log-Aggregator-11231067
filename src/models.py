from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any

class Event(BaseModel):
    topic: str = Field(..., json_schema_extra={"example": "system.logs"})
    event_id: str = Field(..., json_schema_extra={"example": "abc123"})
    timestamp: datetime
    source: str
    payload: Dict[str, Any]
