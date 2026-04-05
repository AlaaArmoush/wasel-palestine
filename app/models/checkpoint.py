import uuid
import enum
from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    DateTime,
    Enum,
    Text,
    Integer,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class CheckpointStatus(str, enum.Enum):
    open = "open"
    closed = "closed"
    restricted = "restricted"
    unknown = "unknown"


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=True)  # Arabic name
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    current_status = Column(Enum(CheckpointStatus), default=CheckpointStatus.unknown)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    status_history = relationship(
        "CheckpointStatusHistory", back_populates="checkpoint"
    )
    incidents = relationship("Incident", back_populates="checkpoint")


class CheckpointStatusHistory(Base):
    """Tracks every status change for a checkpoint over time"""

    __tablename__ = "checkpoint_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    checkpoint_id = Column(
        UUID(as_uuid=True), ForeignKey("checkpoints.id", ondelete="CASCADE")
    )
    previous_status = Column(Enum(CheckpointStatus), nullable=True)
    new_status = Column(Enum(CheckpointStatus), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    changed_by_user = relationship("User", foreign_keys=[changed_by])
    reason = Column(Text, nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    checkpoint = relationship("Checkpoint", back_populates="status_history")
