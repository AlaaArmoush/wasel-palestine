from datetime import datetime
from uuid import UUID
import re

from pydantic import BaseModel, field_validator, ConfigDict

from app.db.base import Base
from app.models.user import UserRole


class UserOut(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: str | None
    role: UserRole
    is_active: bool
    credibility_score: int
    created_at: datetime

    # pydantic expects dictionary this allows reading data from database objects
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: str | None = None
    username: str | None = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, value):
        if value is not None and not re.match(r"^[a-zA-z0-9_]{3,50}$", value):
            raise ValueError(
                "Username must be 3-50 chars, letters/numbers/underscores only"
            )
        return value


class UserRoleUpdate(BaseModel):
    role: UserRole
