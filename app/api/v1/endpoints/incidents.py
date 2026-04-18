from fastapi import APIRouter
from app.core.dependencies import DB
from app.utils.pagination import PaginationDep, PaginatedResponse
from app.utils.responses import success_response
from app.schemas.incident import IncidentOut
from app.models.incident import IncidentType, IncidentSeverity, IncidentStatus
from app.services import incidents as service

router = APIRouter()

@router.get("/")
def list_incidents(
    db: DB, pagination: PaginationDep,
    incident_type: IncidentType | None = None,
    severity: IncidentSeverity | None = None,
    status: IncidentStatus | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float | None = None
):
    items, total = service.get_all_incidents(
        db, pagination.offset, pagination.page_size,
        incident_type, severity, status, lat, lng, radius_km
    )
    return success_response(
        data=PaginatedResponse.create([IncidentOut.model_validate(i) for i in items], total, pagination),
        message="Incidents retrieved"
    )
