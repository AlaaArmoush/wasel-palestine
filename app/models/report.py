import uuid
import enum
from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    Enum,
    Text,
    Integer,
    ForeignKey,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class ReportCategory(str, enum.Enum):
    checkpoint_delay = "checkpoint_delay"
    road_closure = "road_closure"
    accident = "accident"
    weather = "weather"
    military = "military"
    other = "other"


class ReportStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    duplicate = "duplicate"


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category = Column(Enum(ReportCategory), nullable=False)
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.pending)
    confidence_score = Column(Integer, default=0)  # increases with upvotes
    duplicate_of = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    original_report = relationship(
        "Report", remote_side=[id], backref="duplicate_reports"
    )

    # Relationships
    author = relationship("User", back_populates="reports")
    votes = relationship("ReportVote", back_populates="report")
    moderation_logs = relationship("ModerationLog", back_populates="report")


class ReportVote(Base):
    """Community voting to increase/decrease report credibility"""

    __tablename__ = "report_votes"
    __table_args__ = (
        UniqueConstraint("report_id", "user_id", name="uq_report_vote_report_user"),
    )
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    is_upvote = Column(Boolean, nullable=False)  # True = upvote, False = downvote
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    report = relationship("Report", back_populates="votes")
    user = relationship("User", back_populates="report_votes")


class ModerationLog(Base):
    """Every moderation action is recorded here — required by the project"""

    __tablename__ = "moderation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    moderator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=True)
    action = Column(
        String(100), nullable=False
    )  # "approved", "rejected", "marked_duplicate"
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    incident = relationship("Incident")
    moderator = relationship("User", back_populates="moderation_logs")
    report = relationship("Report", back_populates="moderation_logs")
