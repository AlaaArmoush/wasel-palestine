from fastapi import APIRouter, Query
from uuid import UUID

from app.core.dependencies import DB, AdminOnly, CurrentUser
from app.schemas.checkpoint import CheckpointOut, CheckpointDetailOut, CheckpointStatusHistoryOut, CheckpointCreate
from app.services import checkpoints as service
from app.utils.responses import success_response
from app.utils.pagination import PaginationDep, PaginatedResponse
from app.models.checkpoint import CheckpointStatus

router = APIRouter()


@router.get("/")
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


@router.post("/", dependencies=[AdminOnly], status_code=201)
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


@router.get("/{checkpoint_id}")
def get_checkpoint(checkpoint_id: UUID, db: DB):
    checkpoint = service.get_checkpoint_by_id(db, checkpoint_id)
    return success_response(
        data=CheckpointDetailOut.model_validate(checkpoint), 
        message="Checkpoint Retrieved"
    )


@router.get("/{id}/history", description="get status change history")
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
