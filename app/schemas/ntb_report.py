"""
NTBReport schemas — request/response validation for the NTBReport model.

Includes nested schemas for attachments, timeline, and responses
so a full case detail response can be returned in one payload.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.ntb_report import CaseStatus
from app.schemas.ntb_category import NTBCategorySummary
from app.schemas.organization import OrganizationSummary
from app.schemas.user import UserSummary


# ---------------------------------------------------------------------------
# Attachment (nested, read-only)
# ---------------------------------------------------------------------------
class CaseAttachmentResponse(BaseModel):
    id:          uuid.UUID
    filename:    str
    mime_type:   str
    file_size:   int
    created_at:  datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Timeline entry (nested, read-only)
# ---------------------------------------------------------------------------
class CaseTimelineResponse(BaseModel):
    id:          uuid.UUID
    from_status: Optional[CaseStatus]
    to_status:   CaseStatus
    changed_by:  Optional[uuid.UUID]
    comment:     Optional[str]
    created_at:  datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Case response / internal note (nested)
# ---------------------------------------------------------------------------
class CaseResponseResponse(BaseModel):
    id:          uuid.UUID
    author:      UserSummary
    content:     str
    is_internal: bool
    created_at:  datetime

    model_config = {"from_attributes": True}


class CaseResponseCreate(BaseModel):
    content:     str  = Field(..., min_length=10, max_length=5000)
    is_internal: bool = False


# ---------------------------------------------------------------------------
# NTBReport — Create (POST /reports)
# ---------------------------------------------------------------------------
class NTBReportCreate(BaseModel):
    category_id:       uuid.UUID
    description:       str  = Field(..., min_length=10, max_length=2000)
    incident_date:     date
    location_district: str  = Field(..., min_length=2, max_length=100)
    location_detail:   Optional[str]     = Field(None, max_length=255)
    latitude:          Optional[Decimal] = None
    longitude:         Optional[Decimal] = None

    # Guest fields — required when submitted without an account
    guest_email: Optional[EmailStr] = None
    guest_phone: Optional[str]      = Field(None, max_length=20)

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and not (-1.5 <= float(v) <= 4.3):
            raise ValueError("Latitude must be within Uganda bounds (-1.5 to 4.3).")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and not (29.5 <= float(v) <= 35.1):
            raise ValueError("Longitude must be within Uganda bounds (29.5 to 35.1).")
        return v


# ---------------------------------------------------------------------------
# NTBReport — Status transition (PATCH /reports/{id}/status)
# ---------------------------------------------------------------------------
class CaseStatusUpdate(BaseModel):
    status:           CaseStatus
    comment:          Optional[str] = Field(None, max_length=1000)
    assigned_org_id:  Optional[uuid.UUID] = None  # required when status = ASSIGNED
    rejection_reason: Optional[str] = Field(None, max_length=2000)  # required when status = REJECTED

    @field_validator("rejection_reason")
    @classmethod
    def rejection_reason_required(cls, v: Optional[str], info: object) -> Optional[str]:
        # Validated further at the service layer where we have full context
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class NTBReportSummary(BaseModel):
    """Used in list endpoints — no nested collections."""
    id:                uuid.UUID
    case_id:           str
    status:            CaseStatus
    category:          NTBCategorySummary
    location_district: str
    incident_date:     date
    created_at:        datetime

    model_config = {"from_attributes": True}


class NTBReportResponse(BaseModel):
    """Full case detail — includes nested collections."""
    id:                uuid.UUID
    case_id:           str
    status:            CaseStatus

    # Reporter info
    reporter:    Optional[UserSummary] = None
    guest_email: Optional[str]        = None
    guest_phone: Optional[str]        = None

    # NTB details
    category:          NTBCategorySummary
    description:       str
    incident_date:     date
    location_district: str
    location_detail:   Optional[str]
    latitude:          Optional[Decimal]
    longitude:         Optional[Decimal]

    # Case management
    assigned_org:    Optional[OrganizationSummary] = None
    assigned_at:     Optional[datetime]            = None
    resolved_at:     Optional[datetime]            = None
    rejection_reason: Optional[str]               = None

    # Nested collections
    attachments: list[CaseAttachmentResponse] = []
    timeline:    list[CaseTimelineResponse]   = []
    responses:   list[CaseResponseResponse]   = []

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Paginated list wrapper
# ---------------------------------------------------------------------------
class NTBReportList(BaseModel):
    total:   int
    page:    int
    size:    int
    results: list[NTBReportSummary]