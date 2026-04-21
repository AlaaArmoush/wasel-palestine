from fastapi import APIRouter, Query
from uuid import UUID

from app.core.dependencies import DB, AdminOnly, CurrentUser, ModeratorOrAdmin
from app.schemas.checkpoint import CheckpointOut, CheckpointDetailOut, CheckpointStatusHistoryOut, CheckpointCreate, CheckpointUpdate, CheckpointStatusUpdate
from app.services import checkpoints as service
from app.utils.responses import success_response, APIResponse
from app.schemas.common import ErrorResponse
from app.utils.pagination import PaginationDep, PaginatedResponse
from app.models.checkpoint import CheckpointStatus

router = APIRouter()


@router.get(
    "/",
    summary="List checkpoints",
    description="Paginated list of checkpoints. Filterable by name (Arabic or English), status, and active state.",
    response_model=APIResponse[PaginatedResponse[CheckpointOut]],
)
def get_checkpoints(
    db: DB, 
    pagination: PaginationDep,
    name: str | None = Query(None, description="Filter by name (Arabic or English)"),
    status: CheckpointStatus | None = Query(None, description="Filter by current status"),
    is_active: bool | None = Query(None, description="Filter by active status")
):
    items, total = service.get_checkpoints(
        db=db,
        skip=pagination.offset,
        limit=pagination.page_size,
        name=name,
        status=status,
        is_active=is_active
    )
    
    items_out = [CheckpointOut.model_validate(item) for item in items]
    paginated_data = PaginatedResponse.create(items_out, total, pagination)
    
    return success_response(
        data=paginated_data, 
        message="Checkpoints Retrieved"
    )


@router.post(
    "/",
    summary="Create checkpoint",
    description="Admin only. Add a new checkpoint to the system.",
    dependencies=[AdminOnly],
    status_code=201,
    response_model=APIResponse[CheckpointDetailOut],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin only"},
    },
)
def create_checkpoint(
    payload: CheckpointCreate, 
    db: DB,
    current_user: CurrentUser
):
    checkpoint = service.create_checkpoint(
        db=db, 
        obj_in=payload, 
        current_user_id=current_user.id
    )
    return success_response(
        data=CheckpointDetailOut.model_validate(checkpoint), 
        message="Checkpoint Created"
    )


@router.get(
    "/{checkpoint_id}",
    summary="Get checkpoint",
    description="Retrieve full details of a specific checkpoint by UUID.",
    response_model=APIResponse[CheckpointDetailOut],
    responses={404: {"model": ErrorResponse, "description": "Checkpoint not found"}},
)
def get_checkpoint(checkpoint_id: UUID, db: DB):
    checkpoint = service.get_checkpoint_by_id(db, checkpoint_id)
    return success_response(
        data=CheckpointDetailOut.model_validate(checkpoint), 
        message="Checkpoint Retrieved"
    )


@router.patch(
    "/{checkpoint_id}",
    summary="Update checkpoint",
    description="Admin only. Update checkpoint metadata fields.",
    dependencies=[AdminOnly],
    response_model=APIResponse[CheckpointDetailOut],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin only"},
        404: {"model": ErrorResponse, "description": "Checkpoint not found"},
    },
)
def update_checkpoint(
    checkpoint_id: UUID,
    payload: CheckpointUpdate,
    db: DB,
    current_user: CurrentUser
):
    checkpoint = service.update_checkpoint(
        db=db,
        checkpoint_id=checkpoint_id,
        obj_in=payload,
        current_user_id=current_user.id
    )
    return success_response(
        data=CheckpointDetailOut.model_validate(checkpoint),
        message="Checkpoint Updated"
    )


@router.patch(
    "/{checkpoint_id}/status",
    summary="Update checkpoint status",
    description="Moderator or admin only. Update the operational status of a checkpoint and record the change in history.",
    dependencies=[ModeratorOrAdmin],
    response_model=APIResponse[CheckpointDetailOut],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Moderator or admin only"},
        404: {"model": ErrorResponse, "description": "Checkpoint not found"},
    },
)
def update_checkpoint_status(
    checkpoint_id: UUID,
    payload: CheckpointStatusUpdate,
    db: DB,
    current_user: CurrentUser
):
    checkpoint = service.update_checkpoint_status(
        db=db,
        checkpoint_id=checkpoint_id,
        status_in=payload,
        current_user_id=current_user.id
    )
    return success_response(
        data=CheckpointDetailOut.model_validate(checkpoint),
        message="Checkpoint Status Updated"
    )


@router.get(
    "/{id}/history",
    summary="Get checkpoint history",
    description="Retrieve the full status change history for a checkpoint, ordered most-recent first.",
    response_model=APIResponse[PaginatedResponse[CheckpointStatusHistoryOut]],
    responses={404: {"model": ErrorResponse, "description": "Checkpoint not found"}},
)
def get_checkpoint_history(
    id: UUID, 
    db: DB,
    pagination: PaginationDep
):
    items, total = service.get_checkpoint_history(
        db=db,
        checkpoint_id=id,
        skip=pagination.offset,
        limit=pagination.page_size
    )
    
    items_out = [CheckpointStatusHistoryOut.model_validate(item) for item in items]
    paginated_data = PaginatedResponse.create(items_out, total, pagination)
    
    return success_response(
        data=paginated_data, 
        message="Checkpoint History Retrieved"
    )






@router.delete(
    "/{checkpoint_id}",
    summary="Delete checkpoint",
    description="Admin only. Permanently removes a checkpoint from the system.",
    dependencies=[AdminOnly],
    response_model=APIResponse[None],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin only"},
        404: {"model": ErrorResponse, "description": "Checkpoint not found"},
    },
)
def delete_checkpoint(
    checkpoint_id: UUID,
    db: DB
):
    service.delete_checkpoint(db=db, checkpoint_id=checkpoint_id)
    return success_response(
        data=None,
        message="Checkpoint Deleted Successfully"
    )
