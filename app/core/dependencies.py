"""
app/core/dependencies.py

FastAPI dependencies — inject the current authenticated user into route handlers.
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User, UserRole

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Decode the Bearer token and return the active User, or raise 401."""
    token = credentials.credentials
    user_id_str = decode_token(token, expected_type="access")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user_id_str:
        raise credentials_exception

    user = db.query(User).filter(User.id == uuid.UUID(user_id_str)).first()
    if not user or not user.is_active:
        raise credentials_exception

    return user


def require_role(*roles: UserRole):
    """Factory — returns a dependency that enforces one of the given roles."""
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user
    return _check


# ---------------------------------------------------------------------------
# Convenience role dependencies
# ---------------------------------------------------------------------------
require_admin       = require_role(UserRole.ADMIN)
require_mda_officer = require_role(UserRole.MDA_OFFICER, UserRole.ADMIN)
require_staff       = require_role(UserRole.MDA_OFFICER, UserRole.PRIVATE_SECTOR, UserRole.ADMIN)