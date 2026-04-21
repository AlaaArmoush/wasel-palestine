from fastapi import APIRouter, status

from app.core.dependencies import DB, CurrentUser, AdminOnly
from app.models.user import UserRole
from app.schemas.user import UserOut, UserRoleUpdate, UserUpdate
from app.services import users as service
from app.utils.pagination import PaginatedResponse, PaginationDep
from app.utils.responses import success_response, APIResponse
from app.schemas.common import ErrorResponse
from uuid import UUID

router = APIRouter()


@router.get(
    "/me",
    summary="Get own profile",
    description="Returns the full profile of the currently authenticated user.",
    response_model=APIResponse[UserOut],
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
def get_own_profile(current_user: CurrentUser):
    user = service.get_own_profile(current_user)
    return success_response(
        data=UserOut.model_validate(user), message="Profile Retrieved"
    )


@router.patch(
    "/me",
    summary="Update own profile",
    description="Update the authenticated user's full name or username.",
    response_model=APIResponse[UserOut],
    responses={
        400: {"model": ErrorResponse, "description": "Username already taken"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
def update_own_profile(db: DB, current_user: CurrentUser, payload: UserUpdate):
    updated_user = service.update_own_profile(db, current_user, payload)
    return success_response(
        data=UserOut.model_validate(updated_user), message="Profile Updated"
    )


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description="Admin only. Retrieve any user's full profile by their UUID.",
    dependencies=[AdminOnly],
    response_model=APIResponse[UserOut],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin only"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
)
def get_user_by_id(user_id: UUID, db: DB):
    user = service.get_user_by_id(db, user_id)
    return success_response(data=UserOut.model_validate(user), message="User Retrieved")


@router.patch(
    "/{user_id}/role",
    summary="Update user role",
    description="Admin only. Change a user's role (e.g. promote to moderator or admin).",
    dependencies=[AdminOnly],
    response_model=APIResponse[UserOut],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin only"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
)
def update_user_role(user_id: UUID, payload: UserRoleUpdate, db: DB):
    user = service.update_user_role(db, user_id, payload)
    return success_response(
        data=UserOut.model_validate(user),
        message=f"User role updated to {user.role.value}",
    )


@router.get(
    "/",
    summary="List users",
    description="Admin only. Paginated list of all users. Filterable by role and active status.",
    dependencies=[AdminOnly],
    response_model=APIResponse[PaginatedResponse[UserOut]],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin only"},
    },
)
def list_users(
    db: DB,
    pagination: PaginationDep,
    role: UserRole | None = None,
    is_active: bool | None = None,
):
    items, total = service.get_all_users(
        db, pagination.offset, pagination.page_size, role, is_active
    )
    return success_response(
        data=PaginatedResponse.create(
            [UserOut.model_validate(u) for u in items], total, pagination
        ),
        message="Users retrieved",
    )


@router.delete(
    "/{user_id}",
    summary="Deactivate user",
    description="Admin only. Deactivates a user account (soft delete — does not remove from database).",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[AdminOnly],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Admin only"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
)
def deactivate_user(user_id: UUID, db: DB):
    service.deactivate_user(db, user_id)