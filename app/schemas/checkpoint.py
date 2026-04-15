from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from app.models.checkpoint import CheckpointStatus

class CheckpointOut(BaseModel):
    id: UUID
    name: str
    name_ar: str | None = None
    description: str | None = None
    latitude: float
    longitude: float
    current_status: CheckpointStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

   
    model_config = ConfigDict(from_attributes=True)


class CheckpointDetailOut(CheckpointOut):
   
    pass
