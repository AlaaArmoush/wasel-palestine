from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    checkpoints,
    incidents,
    reports,
    routes,
    alerts,
)
from app.api.v1.endpoints.reports import moderation_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(
    checkpoints.router, prefix="/checkpoints", tags=["Checkpoints"]
)
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(moderation_router, prefix="/moderation", tags=["Moderation"])
api_router.include_router(routes.router, prefix="/routes", tags=["Route Estimation"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
