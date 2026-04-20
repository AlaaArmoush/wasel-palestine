from app.models.alert import Alert
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import text
from app.models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentOut
from app.utils.geo import haversine_distance
from app.services import alerts as alerts_service
from uuid import UUID
from fastapi import HTTPException, status


def create_incident(db: Session, payload: IncidentCreate, user_id: str) -> Incident:
    incident = Incident(**payload.model_dump(), reported_by=user_id)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def get_incident_by_id(db: Session, incident_id: UUID):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident

def get_all_incidents(
    db: Session,
    skip: int,
    limit: int,
    incident_type: IncidentType | None = None,
    severity: IncidentSeverity | None = None,
    status: IncidentStatus | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float | None = None,
):
    # Build a dynamic parameterised WHERE clause with raw SQL
    conditions = ["1=1"]
    params: dict = {"limit": limit, "skip": skip}

    if incident_type:
        conditions.append("incident_type = :incident_type")
        params["incident_type"] = incident_type.value

    if severity:
        conditions.append("severity = :severity")
        params["severity"] = severity.value

    if status:
        conditions.append("status = :status")
        params["status"] = status.value

    where = " AND ".join(conditions)

    total = db.execute(
        text(f"SELECT COUNT(*) FROM incidents WHERE {where}"),
        params,
    ).scalar()

    rows = db.execute(
        text(
            f"SELECT id FROM incidents WHERE {where}"
            f" ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
        ),
        params,
    ).mappings().all()

    ids = [row["id"] for row in rows]
    if not ids:
        return [], total

    # Reload as ORM objects so relationships and Pydantic serialisation work
    items = db.query(Incident).filter(Incident.id.in_(ids)).all()
    items.sort(key=lambda i: [str(r["id"]) for r in rows].index(str(i.id)))

    # Geo-radius post-filter stays in Python (haversine is application logic)
    if lat and lng and radius_km:
        items = [i for i in items if haversine_distance(lat, lng, i.latitude, i.longitude) <= radius_km]

    return items, total


def update_incident(db: Session, incident_id: UUID, payload: IncidentUpdate) -> Incident:
    incident = get_incident_by_id(db, incident_id)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(incident, field, value)

    db.commit()
    db.refresh(incident)
    return incident


def resolve_incident(db: Session, incident_id: UUID) -> Incident:
    incident = get_incident_by_id(db, incident_id)

    if incident.status == IncidentStatus.resolved:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Incident is already resolved"
        )

    incident.status = IncidentStatus.resolved
    incident.resolved_at = func.now()
    db.commit()
    db.refresh(incident)
    return incident


def verify_incident(db: Session, incident_id: UUID, verified_by: str) -> Incident:
    incident = get_incident_by_id(db, incident_id)

    if incident.status == IncidentStatus.verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Incident is already verified"
        )

    incident.status = IncidentStatus.verified
    incident.verified_by = verified_by
    incident.verified_at = func.now()

    # no commit inside, stays in the same transaction
    alerts_service.trigger_alert_for_incident(db, incident)

    db.commit()
    db.refresh(incident)
    return incident


def delete_incident(db: Session, incident_id: UUID) -> None:
    incident = get_incident_by_id(db, incident_id)
    # Null out linked alerts before deleting
    db.query(Alert).filter(Alert.incident_id == incident_id).update({"incident_id": None})
    db.delete(incident)
    db.commit()