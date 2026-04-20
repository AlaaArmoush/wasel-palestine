from fastapi import APIRouter
from app.core.dependencies import DB, CurrentUser
from app.schemas.route import RouteRequest, RouteResponse
from app.utils.responses import success_response, APIResponse
from app.services import routes as service

router = APIRouter()


@router.post("/estimate", response_model=APIResponse[RouteResponse])
async def estimate_route(payload: RouteRequest, db: DB):
    result = await service.estimate_route(db, payload)
    return success_response(
        data=RouteResponse(**result),
        message="Route estimated"
    )
