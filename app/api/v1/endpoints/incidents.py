from uuid import UUID
from fastapi import APIRouter, status
from app.core.dependencies import DB, CurrentUser, ModeratorOrAdmin, AdminOnly
from app.utils.pagination import PaginationDep, PaginatedResponse
from app.utils.responses import success_response, APIResponse
from app.schemas.common import ErrorResponse
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentOut
from app.models.incident import IncidentType, IncidentSeverity, IncidentStatus
from app.services import incidents as service

router = APIRouter()

@router.post(
    "/",
    summary="Create incident",
    description="Authenticated users can report a new incident. Starts with 'active' status.",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse[IncidentOut],
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
def create_incident(payload: IncidentCreate, db: DB, current_user: CurrentUser):
    item = service.create_incident(db, payload, str(current_user.id))
    return success_response(
        data=IncidentOut.model_validate(item),
        message="Incident created"
    )

@router.get(
    "/{incident_id}",
    summary="Get incident",
    description="Retrieve full details of a single incident by UUID.",
    response_model=APIResponse[IncidentOut],
    responses={404: {"model": ErrorResponse, "description": "Incident not found"}},
)
def get_incident(incident_id: UUID, db: DB):
    item = service.get_incident_by_id(db, incident_id)
    return success_response(
        data=IncidentOut.model_validate(item),
        message="Incident retrieved"
    )

@router.get(
    "/",
    summary="List incidents",
    description="Paginated list of incidents. Filterable by type, severity, status, and geo-radius.",
    response_model=APIResponse[PaginatedResponse[IncidentOut]],
)
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


@router.patch(
    "/{incident_id}",
    summary="Update incident",
    description="Moderator or admin only. Update editable fields of an incident.",
    dependencies=[ModeratorOrAdmin],
    response_model=APIResponse[IncidentOut],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Moderator or admin only"},
        404: {"model": ErrorResponse, "description": "Incident not found"},
    },
)
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


@router.patch(
    "/{incident_id}/resolve",
    summary="Resolve incident",
    description="Moderator or admin only. Marks an incident as resolved and records the resolution timestamp.",
    dependencies=[ModeratorOrAdmin],
    response_model=APIResponse[IncidentOut],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Moderator or admin only"},
        404: {"model": ErrorResponse, "description": "Incident not found"},
        409: {"model": ErrorResponse, "description": "Incident already resolved"},
    },
)
def resolve_incident(incident_id: UUID, db: DB):
    item = service.resolve_incident(db, incident_id)
    return success_response(
        data=IncidentOut.model_validate(item),
        message="Incident marked as resolved"
    )


@router.patch(
    "/{incident_id}/verify",
    summary="Verify incident",
    description="Moderator or admin only. Marks an incident as verified, sets verification metadata, and triggers alert creation.",
    dependencies=[ModeratorOrAdmin],
    response_model=APIResponse[IncidentOut],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Moderator or admin only"},
        404: {"model": ErrorResponse, "description": "Incident not found"},
        409: {"model": ErrorResponse, "description": "Incident already verified"},
    },
)
def verify_incident(incident_id: UUID, db: DB, current_user: CurrentUser):
    item = service.verify_incident(db, incident_id, str(current_user.id))
    return success_response(
        data=IncidentOut.model_validate(item),
        message="Incident verified and alert triggered"
    )


@router.delete(
    "/{incident_id}",
    summary="Delete incident",
    description="Admin only. Permanently removes an incident and nullifies all linked alerts.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[AdminOnly],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin only"},
        404: {"model": ErrorResponse, "description": "Incident not found"},
    },
)
def delete_incident(incident_id: UUID, db: DB):
    service.delete_incident(db, incident_id)
