from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AccidentCreate(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None
    severity: Optional[str] = None


class AccidentResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    address: Optional[str] = None
    severity: Optional[str] = None
    status: str
    detections_count: int
    first_seen: Optional[datetime] = None

    class Config:
        from_attributes = True