# app/schemas/report.py
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.report import ReportCategory, ReportStatus


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    author_id: UUID
    category: ReportCategory
    description: str
    latitude: float
    longitude: float
    status: ReportStatus
    confidence_score: int
    duplicate_of: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class ReportCreateOut(ReportOut):
    potential_duplicate_of: Optional[UUID] = None


class ReportReject(BaseModel):
    reason: str


class ReportMarkDuplicate(BaseModel):
    duplicate_of: UUID


class VoteCreate(BaseModel):
    is_upvote: bool


class VoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    user_id: UUID
    is_upvote: bool
    created_at: datetime
    confidence_score: int  # updated score from the parent report


class ModerationLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    moderator_id: UUID
    report_id: Optional[UUID] = None
    action: str
    reason: Optional[str] = None
    created_at: datetime


class ReportCreate(BaseModel):
    category: ReportCategory
    description: str = Field(..., min_length=1)
    latitude: float
    longitude: float