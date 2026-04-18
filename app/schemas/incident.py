from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.models.incident import IncidentType, IncidentSeverity, IncidentStatus


class IncidentCreate(BaseModel):
    title: str
    description: str | None = None
    incident_type: IncidentType
    severity: IncidentSeverity = IncidentSeverity.medium
    latitude: float
    longitude: float
    location_description: str | None = None
    checkpoint_id: UUID | None = None


class IncidentOut(BaseModel):
    id: UUID
    title: str
    description: str | None
    incident_type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    latitude: float
    longitude: float
    location_description: str | None
    checkpoint_id: UUID | None
    reported_by: UUID | None
    created_at: datetime

    class Config:
        from_attributes = True
