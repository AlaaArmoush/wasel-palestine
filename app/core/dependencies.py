from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer()


# ── Database dependency ───────────────────────────────────────
# Usage in any endpoint:  db: DB = Depends(get_db)
DB = Annotated[Session, Depends(get_db)]


# ── Get current user from JWT ─────────────────────────────────
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise credentials_exception
    return user


# ── Typed dependency aliases (teammates use these) ────────────
# Usage:  current_user: CurrentUser = Depends()
CurrentUser = Annotated[User, Depends(get_current_user)]


# ── Role guards ───────────────────────────────────────────────
def require_roles(*roles: UserRole):
    """
    Usage in endpoint:
        def my_endpoint(current_user: CurrentUser, _=Depends(require_roles(UserRole.admin))):
    """

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access restricted. Required role: {[r.value for r in roles]}",
            )
        return current_user

    return checker


# ── Convenience role deps teammates can import directly ───────
AdminOnly = Depends(require_roles(UserRole.admin))
ModeratorOrAdmin = Depends(require_roles(UserRole.moderator, UserRole.admin))
