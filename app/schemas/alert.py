from app.models import incident
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


class AlertSubscriptionResponse(BaseModel):  
    id: UUID
    user_id : UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = None
    incident_category: Optional[str] = None  
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)




class AlertSubscriptionCreate(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 10.0  # Default

