<<<<<<< HEAD
#from dns.e164 import query
=======
>>>>>>> bc2b829fd65954a587363934d97fe4aac5d99609
from fastapi import HTTPException, status
from uuid import UUID
from typing import Tuple, List
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertSubscription
from app.utils.pagination import PaginationParams
from app.schemas.alert import AlertSubscriptionCreate


def get_active_alerts(db: Session, pagination: PaginationParams) -> Tuple[int, List[Alert]]:
    """
    Fetches paginated active alerts from the database, sorted from most recent to least.
    """
    query = db.query(Alert).filter(Alert.is_active == True)

    total = query.count()
    items = (
        query.order_by(Alert.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
        .all()
    )

    return total, items


def get_alert_by_id(db: Session, alert_id: UUID):
    """
    Getting an alert from the database based on its id
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no alert with the id {alert_id}",
        )

    return alert


def trigger_alert_for_incident(db: Session, incident) -> Alert:
    alert = Alert(
        incident_id=incident.id,
        title=f"[{incident.severity.upper()}] {incident.incident_type.replace('_', ' ').title()} reported",
        message=(
            incident.description
            if incident.description
            else f"A {incident.incident_type.replace('_', ' ')} incident has been verified near {incident.location_description or 'the reported location'}."
        ),
        latitude=incident.latitude,
        longitude=incident.longitude,
        radius_km=10.0,  # default notification radius
        is_active=True,
    )
    db.add(alert)
    return alert


def get_my_subscriptions(
    db: Session, user_id: UUID, pagination: PaginationParams
) -> Tuple[int, List[AlertSubscription]]:
    """
    Get users own alert subscriptions
    """
    query = db.query(AlertSubscription).filter(AlertSubscription.user_id == user_id)

    total = query.count()
    items = query.offset(pagination.offset).limit(pagination.page_size).all()
    return total, items


def create_subscription(db: Session, user_id: UUID, payload: AlertSubscriptionCreate):
    """
    Subscribing to alerts for a certain area
    """
    new_sub = AlertSubscription(
        user_id=user_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        radius_km=payload.radius_km,
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)  # This fetches the created_at timestamp and ID from DB
    return new_sub