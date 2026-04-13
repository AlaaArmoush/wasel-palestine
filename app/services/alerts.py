from typing import Tuple, List
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.utils.pagination import PaginationParams

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
