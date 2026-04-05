import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID
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
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class IncidentType(str, enum.Enum):
    closure = "closure"
    delay = "delay"
    accident = "accident"
    weather_hazard = "weather_hazard"
    military_activity = "military_activity"
    protest = "protest"
    other = "other"


class IncidentSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentStatus(str, enum.Enum):
    active = "active"
    verified = "verified"
    resolved = "resolved"
    dismissed = "dismissed"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    incident_type = Column(Enum(IncidentType), nullable=False)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.medium)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.active)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_description = Column(String(300), nullable=True)
    checkpoint_id = Column(
        UUID(as_uuid=True), ForeignKey("checkpoints.id"), nullable=True
    )
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    checkpoint = relationship("Checkpoint", back_populates="incidents")
    alerts = relationship("Alert", back_populates="incident")
    reporter = relationship(
        "User", foreign_keys=[reported_by], back_populates="incidents_reported"
    )
    verifier = relationship(
        "User", foreign_keys=[verified_by], back_populates="incidents_verified"
    )
