"""
Organization schemas — request/response validation for the Organization model.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.organization import OrgType


# ---------------------------------------------------------------------------
# Shared base
# ---------------------------------------------------------------------------
class OrganizationBase(BaseModel):
    name:          str      = Field(..., min_length=2, max_length=255)
    type:          OrgType
    contact_email: EmailStr


# ---------------------------------------------------------------------------
# Create (POST /admin/organizations)
# ---------------------------------------------------------------------------
class OrganizationCreate(OrganizationBase):
    pass


# ---------------------------------------------------------------------------
# Update (PATCH /admin/organizations/{id})
# ---------------------------------------------------------------------------
class OrganizationUpdate(BaseModel):
    name:          Optional[str]      = Field(None, min_length=2, max_length=255)
    contact_email: Optional[EmailStr] = None
    is_active:     Optional[bool]     = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class OrganizationResponse(BaseModel):
    id:            uuid.UUID
    name:          str
    type:          OrgType
    contact_email: EmailStr
    is_active:     bool
    created_at:    datetime
    updated_at:    datetime

    model_config = {"from_attributes": True}


class OrganizationSummary(BaseModel):
    """Lightweight org info embedded in other responses."""
    id:   uuid.UUID
    name: str
    type: OrgType

    model_config = {"from_attributes": True}