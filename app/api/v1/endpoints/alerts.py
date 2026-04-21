from fastapi import APIRouter
from app.core.dependencies import DB
from app.utils.pagination import PaginationDep, PaginatedResponse
from app.utils.responses import success_response, APIResponse
from app.schemas.common import ErrorResponse
from app.schemas.alert import AlertResponse,AlertSubscriptionCreate,AlertSubscriptionResponse
from app.services import alerts as alert_service
from uuid import UUID


from app.core.dependencies import CurrentUser


router = APIRouter()

@router.get(
    "/",
    summary="List active alerts",
    description="Retrieve a paginated list of currently active system alerts.",
    response_model=APIResponse[PaginatedResponse[AlertResponse]],
)
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






@router.get(
    "/mySubscriptions",
    summary="List my subscriptions",
    description="Authenticated users can view their own active alert subscriptions.",
    response_model=APIResponse[PaginatedResponse[AlertSubscriptionResponse]],
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
def get_my_alert_subscriptions (db:DB,pagination: PaginationDep,currentUser: CurrentUser):
    total,items = alert_service.get_my_subscriptions(db,currentUser.id,pagination)

    validated_items = [AlertSubscriptionResponse.model_validate(item) for item in items]
    
    paginated_data = PaginatedResponse[AlertSubscriptionResponse].create(
        items=validated_items,
        total=total,
        pagination=pagination
    )



    return success_response(data=paginated_data, message="Subscriptions Retrieved")

@router.post(
    "/subscriptions",
    summary="Create alert subscription",
    description="Authenticated users can subscribe to alerts for a geographic area and optional incident category.",
    response_model=APIResponse[AlertSubscriptionResponse],
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
def create_alert_sub(db:DB,currentUser:CurrentUser,payload:AlertSubscriptionCreate):
    subscription = alert_service.create_subscription(db,currentUser.id,payload)
    return success_response(
        data=AlertSubscriptionResponse.model_validate(subscription), 
        message="Subscribed to area successfully!"
    )



@router.delete(
    "/subscriptions/{subscription_id}",
    summary="Delete alert subscription",
    description="Authenticated users can cancel one of their own alert subscriptions.",
    response_model=APIResponse[None],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Subscription not found"},
    },
)
def delete_alert_subscription(
    subscription_id: UUID, db: DB, current_user: CurrentUser):
    alert_service.delete_subscription(db, current_user.id, subscription_id)
    
    return success_response(
        data=None, 
        message="Subscription deleted successfully!"
    )



@router.get(
    "/{alert_id}",
    summary="Get alert",
    description="Retrieve full details of a specific alert by UUID.",
    response_model=APIResponse[AlertResponse],
    responses={404: {"model": ErrorResponse, "description": "Alert not found"}},
)
def get_alert_by_id (db:DB,alert_id: UUID):
    alert = alert_service.get_alert_by_id(db,alert_id)

    return success_response(data=AlertResponse.model_validate(alert), message="Alert Retrieved")

