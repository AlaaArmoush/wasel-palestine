from fastapi import APIRouter

from app.core.dependencies import DB, CurrentUser
from app.schemas.user import UserOut, UserUpdate
from app.services import users as service
from app.utils.responses import success_response

router = APIRouter()


@router.get("/me")
def get_my_profile(current_user: CurrentUser):
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
