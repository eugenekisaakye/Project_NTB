"""
app/api/v1/auth.py

Authentication endpoints:
  POST /api/v1/auth/register        — create account
  POST /api/v1/auth/login           — get access token
  GET  /api/v1/auth/verify-email    — verify email via token link
  GET  /api/v1/auth/me              — return current user profile
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth_service import login_user, register_user, verify_email

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user account",
)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    return register_user(db, payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive a JWT access token",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return login_user(db, payload)


@router.get(
    "/verify-email",
    summary="Verify email address via token link",
)
def verify_email_route(
    token: str = Query(..., description="Verification token from the email link"),
    db: Session = Depends(get_db),
) -> dict:
    return verify_email(db, token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current authenticated user's profile",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)