# app/schemas/report.py

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


class ModerationLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    moderator_id: UUID
    report_id: Optional[UUID] = None
    action: str
    reason: Optional[str] = None
    created_at: datetime