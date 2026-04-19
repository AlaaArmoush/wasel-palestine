from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
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


class CheckpointStatusHistoryOut(BaseModel):
    id: UUID
    checkpoint_id: UUID
    previous_status: CheckpointStatus | None = None
    new_status: CheckpointStatus
    changed_by: UUID | None = None
    reason: str | None = None
    changed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)





    


#for post method
class CheckpointCreate(BaseModel):
    name: str = Field(..., min_length=1)
    name_ar: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    latitude: float | None = None
    longitude: float | None = None
    current_status: CheckpointStatus = Field(..., min_length=1)
    is_active: bool


class CheckpointUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    name_ar: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    latitude: float | None = None
    longitude: float | None = None
    current_status: CheckpointStatus | None = None
    is_active: bool | None = None
