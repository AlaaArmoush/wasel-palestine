from uuid import UUID
from fastapi import APIRouter, status
from app.core.dependencies import DB, CurrentUser, ModeratorOrAdmin, AdminOnly
from app.utils.pagination import PaginationDep, PaginatedResponse
from app.utils.responses import success_response, APIResponse
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentOut
from app.models.incident import IncidentType, IncidentSeverity, IncidentStatus
from app.services import incidents as service

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=APIResponse[IncidentOut])
def create_incident(payload: IncidentCreate, db: DB, current_user: CurrentUser):
    item = service.create_incident(db, payload, str(current_user.id))
    return success_response(
        data=IncidentOut.model_validate(item),
        message="Incident created"
    )

@router.get("/{incident_id}", response_model=APIResponse[IncidentOut])
def get_incident(incident_id: UUID, db: DB):
    item = service.get_incident_by_id(db, incident_id)
    return success_response(
        data=IncidentOut.model_validate(item),
        message="Incident retrieved"
    )

@router.get("/", response_model=APIResponse[PaginatedResponse[IncidentOut]])
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


@router.patch("/{incident_id}", dependencies=[ModeratorOrAdmin], response_model=APIResponse[IncidentOut])
def update_incident(
    incident_id: UUID,
    payload: IncidentUpdate,
    db: DB,
):
    item = service.update_incident(db, incident_id, payload)
    return success_response(
        data=IncidentOut.model_validate(item),
        message="Incident updated"
    )


@router.patch("/{incident_id}/resolve", dependencies=[ModeratorOrAdmin], response_model=APIResponse[IncidentOut])
def resolve_incident(incident_id: UUID, db: DB):
    item = service.resolve_incident(db, incident_id)
    return success_response(
        data=IncidentOut.model_validate(item),
        message="Incident marked as resolved"
    )


@router.patch("/{incident_id}/verify", dependencies=[ModeratorOrAdmin], response_model=APIResponse[IncidentOut])
def verify_incident(incident_id: UUID, db: DB, current_user: CurrentUser):
    item = service.verify_incident(db, incident_id, str(current_user.id))
    return success_response(
        data=IncidentOut.model_validate(item),
        message="Incident verified and alert triggered"
    )


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[AdminOnly])
def delete_incident(incident_id: UUID, db: DB):
    service.delete_incident(db, incident_id)
