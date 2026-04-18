from operator import itemgetter
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, query
from uuid import UUID
from app.models.user import User
from app.schemas.user import UserUpdate, UserRoleUpdate


def get_own_profile(user: User) -> User:
    return user


def update_own_profile(db: Session, user: User, payload: UserUpdate) -> User:
    # convert model instance into a dictionary
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        return user

    if "username" in update_data:
        exists = (
            db.query(User)
            .filter(User.username == update_data["username"], User.id != user.id)
            .first()
        )
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: UUID):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def update_user_role(db: Session, user_id: UUID, payload: UserRoleUpdate):
    user = get_user_by_id(db, user_id)
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


def get_all_users(db: Session, skip: int, limit: int, role=None, is_active=None):
    query = db.query(User)
    if role is not None:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    total = query.count()
    items = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return items, total
