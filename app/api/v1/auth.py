"""
auth.py — Authentication API routes

Handles everything related to user identity: registration, login,
email verification, and fetching the current user's own profile.

BASE URL: /api/v1/auth  (prefix set in main.py)

ENDPOINTS:
  POST /register        → Create a new user account
  POST /login           → Exchange credentials for a JWT access token
  GET  /verify-email    → Confirm an email address via the link sent on registration
  GET  /me              → Return the currently logged-in user's profile

FLOW FOR A NEW USER:
  1. POST /register     → account created, verification email sent
  2. GET  /verify-email → user clicks the link; is_email_verified set to True
  3. POST /login        → user receives an access token
  4. GET  /me           → user can view their profile (token required)

BUSINESS LOGIC:
  All the actual work (DB queries, password hashing, token creation, etc.)
  lives in app/services/auth_service.py — routes here are intentionally thin.
  Routes handle HTTP concerns only: parsing input, calling the service, returning output.

AUTHENTICATION:
  /register, /login, /verify-email are PUBLIC — no token required.
  /me is PROTECTED — requires a valid Bearer token (via get_current_user).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth_service import login_user, register_user, verify_email

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,                          # 201 Created on success
    summary="Register a new user account",
)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Create a new user account.

    Accepts: email, password, full_name, role, and optional organization_id.
    On success:
      - Hashes the password and saves the user
      - Sends a verification email to the provided address
      - Returns the new user profile (no token yet — email must be verified first)

    Raises 400 if the email is already registered.
    Raises 422 if the payload fails Pydantic validation (e.g. weak password).
    """
    return register_user(db, payload)


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive a JWT access token",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Authenticate a user and return a JWT access token.

    Accepts: email and password.
    On success: returns {"access_token": "...", "token_type": "bearer"}

    Raises 401 if credentials are wrong or the account is locked.
    Raises 403 if the email has not been verified yet.

    The returned access token should be sent in the Authorization header
    on all subsequent protected requests:
        Authorization: Bearer <access_token>
    """
    return login_user(db, payload)


# ---------------------------------------------------------------------------
# GET /verify-email
# ---------------------------------------------------------------------------
@router.get(
    "/verify-email",
    summary="Verify email address via token link",
)
def verify_email_route(
    token: str = Query(..., description="Verification token from the email link"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Confirm a user's email address using the token from the verification email.

    The link in the email looks like:
        <FRONTEND_URL>/verify-email?token=<jwt>

    The frontend extracts the token and calls this endpoint.
    On success: sets is_email_verified = True on the user and returns a confirmation message.
    Raises 400 if the token is expired, already used, or invalid.
    """
    return verify_email(db, token)


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current authenticated user's profile",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    Return the profile of the currently authenticated user.

    Requires a valid Bearer token in the Authorization header.
    get_current_user (injected via Depends) handles token validation and
    raises 401 automatically if the token is missing or invalid.

    Returns the user's id, email, full_name, role, and organization details.
    """
    return UserResponse.model_validate(current_user)