from fastapi import HTTPException, status
from uuid import UUID
from typing import Tuple, List
from sqlalchemy.orm import Session
from app.models.alert import Alert,AlertSubscription
from app.utils.pagination import PaginationParams
from app.schemas.alert import AlertSubscriptionCreate

def get_active_alerts(db: Session, pagination: PaginationParams) -> Tuple[int, List[Alert]]:
    """
    Fetches paginated active alerts from the database, sorted from most recent to least.
    """
    query = db.query(Alert).filter(Alert.is_active == True)
    
    total = query.count()
    items = query.order_by(Alert.created_at.desc()) \
                 .offset(pagination.offset) \
                 .limit(pagination.page_size) \
                 .all()
                 
    return total, items


def get_alert_by_id(db:Session,alert_id: UUID):
    """
    Getting an alert from the database based on its id
    """
    alertIdQuery = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alertIdQuery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"There is no alert with the id {alert_id}"  
        )
    return alertIdQuery


def create_subscription(db:Session , user_id:UUID , payload: AlertSubscriptionCreate):
    """ 
    Subscribing to alerts for a certain area
    """
    new_sub =AlertSubscription(
        user_id=user_id,
        latitude = payload.latitude,
        longitude = payload.longitude,
        radius_km = payload.radius_km
    )


    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)  # for UUID creation and timestamp
    return new_sub       
