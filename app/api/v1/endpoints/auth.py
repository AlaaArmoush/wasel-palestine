from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status, Depends
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)
from app.db.session import get_db
from app.models.user import User, RefreshToken
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest
from app.utils.responses import success_response

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return success_response(
        data={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
        },
        message="User registered successfully",
    )


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    access_token = create_access_token(str(user.id), user.role.value)
    refresh_token = create_refresh_token(str(user.id))

    db_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(db_token)
    db.commit()

    return success_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        },
        message="Login successful",
    )


@router.post("/refresh")
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid refresh token",
    )

    try:
        token_data = decode_token(payload.refresh_token)
        if token_data.get("type") != "refresh":
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    token_hash = hash_token(payload.refresh_token)

    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked.is_(False),
        )
        .first()
    )

    if not db_token:
        raise credentials_exception

    if db_token.expires_at <= datetime.now(timezone.utc):
        raise credentials_exception

    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user or not user.is_active:
        raise credentials_exception

    new_access_token = create_access_token(str(user.id), user.role.value)

    return success_response(
        data={
            "access_token": new_access_token,
            "token_type": "bearer",
        },
        message="Token refreshed",
    )


@router.post("/logout")
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = hash_token(payload.refresh_token)

    db_token = (
        db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    )

    if db_token:
        db_token.is_revoked = True
        db.commit()

    return success_response(message="Logged out successfully")
