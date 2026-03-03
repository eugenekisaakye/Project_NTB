"""
User schemas — request/response validation for the User model and Auth flows.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


# ---------------------------------------------------------------------------
# Shared base
# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    email:     EmailStr
    full_name: str       = Field(..., min_length=2, max_length=255)
    phone:     Optional[str] = Field(None, max_length=20)
    role:      UserRole


# ---------------------------------------------------------------------------
# Registration (POST /auth/register)
# ---------------------------------------------------------------------------
class UserCreate(UserBase):
    password:         str = Field(..., min_length=8, max_length=128)
    organization_id:  Optional[uuid.UUID] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v


# ---------------------------------------------------------------------------
# Update own profile (PATCH /users/me)
# ---------------------------------------------------------------------------
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone:     Optional[str] = Field(None, max_length=20)


# ---------------------------------------------------------------------------
# Admin update (PATCH /admin/users/{id})
# ---------------------------------------------------------------------------
class UserAdminUpdate(UserUpdate):
    role:            Optional[UserRole]  = None
    is_active:       Optional[bool]      = None
    organization_id: Optional[uuid.UUID] = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class UserResponse(BaseModel):
    id:                uuid.UUID
    email:             EmailStr
    full_name:         str
    phone:             Optional[str]
    role:              UserRole
    organization_id:   Optional[uuid.UUID]
    is_active:         bool
    is_email_verified: bool
    created_at:        datetime
    updated_at:        datetime

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    """Lightweight user info embedded in other responses."""
    id:        uuid.UUID
    full_name: str
    email:     EmailStr
    role:      UserRole

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password:     str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v