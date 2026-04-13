from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class AlertResponse(BaseModel):
    id: UUID
    incident_id: Optional[UUID] = None
    title: str
    message: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = None
    is_active: bool
    created_at: datetime
    
    # Required in Pydantic v2 to load data from SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)
