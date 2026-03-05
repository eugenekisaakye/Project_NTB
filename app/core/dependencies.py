"""
dependencies.py — FastAPI authentication and authorization dependencies

This file provides reusable "dependencies" that are injected into route
handlers via FastAPI's Depends() system. They handle two things:

  1. AUTHENTICATION — "Is this request from a valid, active user?"
     → get_current_user()

  2. AUTHORIZATION — "Does this user have the right role for this action?"
     → require_role() factory + the convenience shortcuts below it

HOW TO USE IN ROUTES:

  # Any authenticated user (all roles)
  from app.core.dependencies import get_current_user
  @router.get("/me")
  def my_route(user: User = Depends(get_current_user)): ...

  # Only admins
  from app.core.dependencies import require_admin
  @router.delete("/users/{id}")
  def delete_user(user: User = Depends(require_admin)): ...

  # MDA officers OR admins
  from app.core.dependencies import require_mda_officer
  @router.post("/cases/{id}/respond")
  def post_response(user: User = Depends(require_mda_officer)): ...

  # Custom combination of roles
  from app.core.dependencies import require_role
  from app.models.user import UserRole
  @router.get("/something")
  def custom_route(user: User = Depends(require_role(UserRole.TRADER, UserRole.ADMIN))): ...

ROLE HIERARCHY (from most to least privileged):
  admin          → everything
  mda_officer    → case management, responses, investigations
  private_sector → similar to trader; represents a business body
  trader         → submit reports, track own cases
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User, UserRole

# HTTPBearer extracts the token from the "Authorization: Bearer <token>" header.
# FastAPI will automatically return 403 if the header is missing.
_bearer = HTTPBearer()


# ---------------------------------------------------------------------------
# Authentication dependency
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the Bearer token from the Authorization header and return the
    corresponding active User object.

    Raises HTTP 401 if:
      - The token is missing, expired, or has an invalid signature
      - The user_id in the token doesn't match any DB record
      - The user account has been deactivated (is_active = False)

    Inject this into any route that requires a logged-in user:
        def my_route(user: User = Depends(get_current_user)): ...
    """
    token = credentials.credentials

    # decode_token returns the user_id string, or None if the token is invalid
    user_id_str = decode_token(token, expected_type="access")

    # Reusable 401 exception — same message for all failure modes to avoid
    # leaking information about whether the user exists
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},  # Required by OAuth2 spec
    )

    if not user_id_str:
        raise credentials_exception  # Token was invalid or expired

    # Look up the user in the DB
    user = db.query(User).filter(User.id == uuid.UUID(user_id_str)).first()

    # Reject if the user doesn't exist OR their account has been deactivated
    if not user or not user.is_active:
        raise credentials_exception

    return user


# ---------------------------------------------------------------------------
# Authorization dependency factory
# ---------------------------------------------------------------------------

def require_role(*roles: UserRole):
    """
    Returns a FastAPI dependency that allows only users with one of the
    specified roles. Raises HTTP 403 for any other role.

    This is a factory — call it with the allowed roles to get a dependency:
        Depends(require_role(UserRole.ADMIN, UserRole.MDA_OFFICER))

    The returned dependency also runs get_current_user, so you get both
    authentication AND authorization in one Depends() call.
    """
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user
    return _check


# ---------------------------------------------------------------------------
# Convenience shortcuts — use these in routes instead of calling require_role()
# directly each time. Add new ones here as the role matrix grows.
# ---------------------------------------------------------------------------

# Only platform admins
require_admin = require_role(UserRole.ADMIN)

# MDA officers and admins (most case-management endpoints)
require_mda_officer = require_role(UserRole.MDA_OFFICER, UserRole.ADMIN)

# Any internal staff member (MDA, private sector, or admin) — excludes plain traders
require_staff = require_role(UserRole.MDA_OFFICER, UserRole.PRIVATE_SECTOR, UserRole.ADMIN)