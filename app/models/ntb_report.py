"""
NTB Report model — Table 5.5 of the Uganda NTB SRS
Also defines CaseStatus enum used by case_timeline.py
"""

import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Case status enum — matches the state machine in SRS Section 3.2 exactly
# ---------------------------------------------------------------------------
class CaseStatus(str, PyEnum):
    SUBMITTED           = "submitted"
    UNDER_REVIEW        = "under_review"
    ASSIGNED            = "assigned"
    UNDER_INVESTIGATION = "under_investigation"
    ESCALATED           = "escalated"
    RESOLVED            = "resolved"
    REJECTED            = "rejected"
    CLOSED              = "closed"


# ---------------------------------------------------------------------------
# NTBReport model
# ---------------------------------------------------------------------------
class NTBReport(Base):
    __tablename__ = "ntb_reports"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Human-readable case ID — format NTB-YYYY-NNNNN (SRS Appendix 15.3)
    # Generated at the application layer before insert; never auto-incremented
    # in the DB so it remains portable across environments.
    case_id = Column(String(20), unique=True, nullable=False, index=True)

    # ---------------------------------------------------------------------------
    # Reporter — registered user OR anonymous guest (both are valid, SRS BR-guest)
    # ---------------------------------------------------------------------------
    reporter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,   # NULL for guest submissions
        index=True,
    )
    guest_email = Column(String(255), nullable=True)   # contact for guest reporters
    guest_phone = Column(String(20),  nullable=True)

    # ---------------------------------------------------------------------------
    # NTB details
    # ---------------------------------------------------------------------------
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ntb_categories.id"),
        nullable=False,
        index=True,
    )

    description   = Column(Text,        nullable=False)   # 10–2,000 chars enforced by Pydantic
    incident_date = Column(Date,        nullable=False)

    # Location — district is mandatory; detail + GPS are optional
    location_district = Column(String(100), nullable=False, index=True)
    location_detail   = Column(String(255), nullable=True)

    # GPS coordinates — Uganda bounds: lat -1.5→4.3, lon 29.5→35.1
    # Validated at the application layer via Pydantic, stored as-is here.
    latitude  = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)

    # ---------------------------------------------------------------------------
    # Case management
    # ---------------------------------------------------------------------------
    status = Column(
        Enum(CaseStatus, name="case_status_enum"),
        nullable=False,
        default=CaseStatus.SUBMITTED,
        index=True,
    )

    assigned_org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )
    assigned_at      = Column(DateTime(timezone=True), nullable=True)
    resolved_at      = Column(DateTime(timezone=True), nullable=True)

    # Mandatory when status = REJECTED (enforced at application layer, SRS BR-015)
    rejection_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    reporter     = relationship("User", foreign_keys=[reporter_id], back_populates="ntb_reports")
    category     = relationship("NTBCategory",  back_populates="ntb_reports")
    assigned_org = relationship("Organization", foreign_keys=[assigned_org_id], back_populates="ntb_reports")

    attachments = relationship("CaseAttachment", back_populates="report", cascade="all, delete-orphan")
    timeline    = relationship("CaseTimeline",   back_populates="report", cascade="all, delete-orphan", order_by="CaseTimeline.created_at")
    responses   = relationship("CaseResponse",   back_populates="report", cascade="all, delete-orphan", order_by="CaseResponse.created_at")

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    @property
    def is_guest_submission(self) -> bool:
        return self.reporter_id is None

    def __repr__(self) -> str:
        return f"<NTBReport case_id={self.case_id} status={self.status}>"