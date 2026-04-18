from sqlalchemy.orm import Session
from app.models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from app.schemas.incident import IncidentCreate
from app.utils.geo import haversine_distance
from uuid import UUID
from fastapi import HTTPException, status


def create_incident(db: Session, payload: IncidentCreate, user_id: str) -> Incident:
    incident = Incident(**payload.model_dump(), reported_by=user_id)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

def get_all_incidents(db: Session, skip: int, limit: int,
    incident_type: IncidentType | None = None,
    severity: IncidentSeverity | None = None,
    status: IncidentStatus | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float | None = None
):
    query = db.query(Incident)

    if incident_type:
        query = query.filter(Incident.incident_type == incident_type)
    if severity:
        query = query.filter(Incident.severity == severity)
    if status:
        query = query.filter(Incident.status == status)

    total = query.count()
    items = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()

    if lat and lng and radius_km:
        items = [i for i in items if haversine_distance(lat, lng, i.latitude, i.longitude) <= radius_km]

    return items, total
