from fastapi import APIRouter
from app.core.dependencies import DB
from app.utils.pagination import PaginationDep, PaginatedResponse
from app.utils.responses import success_response
from app.schemas.alert import AlertResponse,AlertSubscriptionCreate,AlertSubscriptionResponse
from app.services import alerts as alert_service
from uuid import UUID

from app.core.dependencies import CurrentUser


router = APIRouter()

@router.get("/")
def get_alerts(db: DB, pagination: PaginationDep):
    total, items = alert_service.get_active_alerts(db, pagination)
    
    # Validate ORM models to Pydantic responses just like users.py does
    validated_items = [AlertResponse.model_validate(item) for item in items]
    
    paginated_data = PaginatedResponse[AlertResponse].create(
        items=validated_items,
        total=total,
        pagination=pagination
    )
    
    return success_response(
        data=paginated_data, message="Alerts Retrieved"
    )


@router.get("/{alert_id}")
def get_alert_by_id (db:DB,alert_id: UUID):
    alert = alert_service.get_alert_by_id(db,alert_id)

    return success_response(data=AlertResponse.model_validate(alert), message="Alert Retrieved")


@router.post("/subscriptions")
def create_alert_sub(db:DB,currentUser:CurrentUser,payload:AlertSubscriptionCreate):
    subscription = alert_service.create_subscription(db,currentUser.id,payload)
    return success_response(
        data=AlertSubscriptionResponse.model_validate(subscription), 
        message="Subscribed to area successfully!"
    )





