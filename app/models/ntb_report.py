"""
ntb_report.py — NTB Report model + CaseStatus enum

This is the core table of the platform. An NTB Report is a complaint filed
by a trader (or anonymous guest) about a Non-Tariff Barrier they encountered.

CASE LIFECYCLE (state machine from SRS Section 3.2):

  submitted → under_review → assigned → under_investigation → resolved
                                    ↘                       ↘
                                    rejected              escalated → resolved
                                                                    ↘ closed

  Any state can move to 'closed' by an admin.
  'rejected' requires a rejection_reason (enforced in the service layer).

GUEST vs REGISTERED SUBMISSIONS:
  Registered users: reporter_id is set, guest_* fields are NULL
  Anonymous guests: reporter_id is NULL, guest_email/phone provide a contact

LOCATION:
  district is mandatory (used for regional analytics).
  GPS coordinates are optional and validated against Uganda's bounding box
  at the Pydantic layer before they reach here.

DB TABLE: ntb_reports
SRS REFERENCE: Table 5.5
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
# CaseStatus enum
# Imported by case_timeline.py too — always import from here, not there.
# ---------------------------------------------------------------------------
class CaseStatus(str, PyEnum):
    SUBMITTED           = "submitted"            # Just filed, no officer has reviewed it yet
    UNDER_REVIEW        = "under_review"         # An admin/officer is looking at it
    ASSIGNED            = "assigned"             # Handed to a specific MDA org for investigation
    UNDER_INVESTIGATION = "under_investigation"  # The assigned org is actively working it
    ESCALATED           = "escalated"            # SLA breached or complexity requires escalation
    RESOLVED            = "resolved"             # NTB addressed; outcome recorded
    REJECTED            = "rejected"             # Invalid or duplicate report; reason required
    CLOSED              = "closed"               # Archived; no further action


# ---------------------------------------------------------------------------
# NTBReport model
# ---------------------------------------------------------------------------
class NTBReport(Base):
    __tablename__ = "ntb_reports"

    # Unique identifier (internal, used for FK references)
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Human-readable case reference shown to traders and officers
    # Format: NTB-YYYY-NNNNN (e.g. NTB-2024-00042)
    # Generated in the service layer before insert — NOT auto-incremented in DB
    # so it stays consistent if the DB is migrated or restored.
    case_id = Column(String(20), unique=True, nullable=False, index=True)

    # ---------------------------------------------------------------------------
    # Who filed this report?
    # ---------------------------------------------------------------------------
    # For registered users — links to the users table
    reporter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,   # NULL = guest submission
        index=True,
    )
    # For anonymous guests — we store contact info directly on the report
    guest_email = Column(String(255), nullable=True)
    guest_phone = Column(String(20),  nullable=True)

    # ---------------------------------------------------------------------------
    # What is the barrier?
    # ---------------------------------------------------------------------------
    # Which category of NTB this falls under (e.g. "Import Licensing")
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ntb_categories.id"),
        nullable=False,
        index=True,
    )

    # Free-text description of the barrier — 10 to 2,000 chars (enforced by Pydantic)
    description = Column(Text, nullable=False)

    # When the barrier was experienced (not when the report was filed)
    incident_date = Column(Date, nullable=False)

    # ---------------------------------------------------------------------------
    # Where did it happen?
    # ---------------------------------------------------------------------------
    # Ugandan district name — mandatory; drives the regional analytics dashboard
    location_district = Column(String(100), nullable=False, index=True)

    # Optional freeform detail (e.g. "Malaba border post, lane 3")
    location_detail = Column(String(255), nullable=True)

    # Optional GPS — validated at the Pydantic layer against Uganda's bounding box:
    #   latitude:  -1.5 to  4.3
    #   longitude: 29.5 to 35.1
    latitude  = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)

    # ---------------------------------------------------------------------------
    # Case management fields (updated by MDA officers / admins)
    # ---------------------------------------------------------------------------
    # Current state in the lifecycle — see CaseStatus enum above
    status = Column(
        Enum(CaseStatus, name="case_status_enum"),
        nullable=False,
        default=CaseStatus.SUBMITTED,
        index=True,
    )

    # Which MDA organization is handling this case (set when status → assigned)
    assigned_org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )
    assigned_at  = Column(DateTime(timezone=True), nullable=True)  # Timestamp of assignment
    resolved_at  = Column(DateTime(timezone=True), nullable=True)  # Timestamp of resolution

    # REQUIRED when status = rejected. Must explain why the report was rejected.
    # Validated in the service layer (SRS BR-015).
    rejection_reason = Column(Text, nullable=True)

    # Auto-managed timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    # The user who filed this report (None for guest submissions)
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="ntb_reports")

    # The NTB category this report is classified under
    category = relationship("NTBCategory", back_populates="ntb_reports")

    # The MDA organization assigned to investigate this case
    assigned_org = relationship("Organization", foreign_keys=[assigned_org_id], back_populates="ntb_reports")

    # Files attached to this report (max 5, enforced in the service layer)
    # cascade="all, delete-orphan" means attachments are deleted if the report is deleted
    attachments = relationship(
        "CaseAttachment",
        back_populates="report",
        cascade="all, delete-orphan",
    )

    # Ordered history of every status change on this case
    timeline = relationship(
        "CaseTimeline",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="CaseTimeline.created_at",
    )

    # All responses/notes posted on this case, oldest first
    responses = relationship(
        "CaseResponse",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="CaseResponse.created_at",
    )

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    @property
    def is_guest_submission(self) -> bool:
        """True when this report was filed without a registered account."""
        return self.reporter_id is None

    def __repr__(self) -> str:
        return f"<NTBReport case_id={self.case_id} status={self.status}>"