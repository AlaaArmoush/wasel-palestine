from fastapi import APIRouter

from app.core.dependencies import DB, CurrentUser, AdminOnly
from app.models.user import UserRole
from app.schemas.user import UserOut, UserRoleUpdate, UserUpdate
from app.services import users as service
from app.utils.pagination import PaginatedResponse, PaginationDep
from app.utils.responses import success_response
from uuid import UUID

router = APIRouter()


@router.get("/me")
def get_own_profile(current_user: CurrentUser):
    user = service.get_own_profile(current_user)
    return success_response(
        data=UserOut.model_validate(user), message="Profile Retrieved"
    )


@router.patch("/me")
def update_own_profile(db: DB, current_user: CurrentUser, payload: UserUpdate):
    updated_user = service.update_own_profile(db, current_user, payload)
    return success_response(
        data=UserOut.model_validate(updated_user), message="Profile Updated"
    )


@router.get("/{user_id}", dependencies=[AdminOnly])
def get_user_by_id(user_id: UUID, db: DB):
    user = service.get_user_by_id(db, user_id)
    return success_response(data=UserOut.model_validate(user), message="User Retrieved")


@router.patch("/{user_id}/role", dependencies=[AdminOnly])
def update_user_role(user_id: UUID, payload: UserRoleUpdate, db: DB):
    user = service.update_user_role(db, user_id, payload)
    return success_response(
        data=UserOut.model_validate(user),
        message=f"User role updated to {user.role.value}",
    )


@router.get("/", dependencies=[AdminOnly])
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


@router.delete("/{user_id}", dependencies=[AdminOnly])
def deactivate_user(user_id: UUID, db: DB):
    user = service.deactivate_user(db, user_id)
    return success_response(
        data=UserOut.model_validate(user), message="User deactivated"
    )
