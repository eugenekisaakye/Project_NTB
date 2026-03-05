"""
app/services/auth_service.py

Authentication business logic — registration, login, email verification.
All DB access goes through the SQLAlchemy session passed in as a dependency.
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_email_verification_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def _get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------
def register_user(db: Session, payload: UserCreate) -> UserResponse:
    # Duplicate email check
    if _get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # MDA / private-sector users must belong to an organisation
    if payload.role in (UserRole.MDA_OFFICER, UserRole.PRIVATE_SECTOR):
        if not payload.organization_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="organization_id is required for MDA and private-sector users.",
            )

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=payload.role,
        organization_id=payload.organization_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # TODO: send verification email (notifications service)
    # verification_token = create_email_verification_token(user.id)
    # email_service.send_verification(user.email, verification_token)

    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
def login_user(db: Session, payload: LoginRequest) -> TokenResponse:
    user = _get_user_by_email(db, payload.email)

    # Generic error — don't reveal whether email exists
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise invalid_credentials

    # Account lockout check
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked. Please try again later.",
        )

    # Wrong password
    if not verify_password(payload.password, str(user.password_hash)):
        user.failed_login_attempts = int(user.failed_login_attempts or 0) + 1  # type: ignore[assignment]
        if user.failed_login_attempts >= settings.FAILED_LOGIN_MAX_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(  # type: ignore[assignment]
                minutes=settings.ACCOUNT_LOCKOUT_MINUTES
            )
        db.commit()
        raise invalid_credentials

    # Inactive account
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support.",
        )

    # Success — reset failed attempts
    user.failed_login_attempts = 0  # type: ignore[assignment]
    user.locked_until = None        # type: ignore[assignment]
    db.commit()

    return TokenResponse(
        access_token=create_access_token(user.id),   # type: ignore[arg-type]
        refresh_token="",  # refresh endpoint added in next iteration
    )


# ---------------------------------------------------------------------------
# Email verification
# ---------------------------------------------------------------------------
def verify_email(db: Session, token: str) -> dict:
    user_id_str = decode_token(token, expected_type="email_verify")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link.",
        )

    user = _get_user_by_id(db, uuid.UUID(user_id_str))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.is_email_verified:
        return {"message": "Email already verified."}

    user.is_email_verified = True  # type: ignore[assignment]
    db.commit()
    return {"message": "Email verified successfully."}