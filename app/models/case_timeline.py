"""
case_timeline.py — CaseTimeline model

Every time a case's status changes, one row is written here.
This gives a complete, ordered history of a case's journey through
the system — who moved it, when, from what status, to what status,
and optionally why.

APPEND-ONLY — rows are NEVER updated or deleted.
There is no updated_at column. Treat this table like a log file.

EXAMPLE TIMELINE for case NTB-2024-00042:
  1. NULL → submitted        (system, on creation)
  2. submitted → under_review   (admin: Alice)
  3. under_review → assigned    (admin: Alice, comment: "Assigned to URA")
  4. assigned → under_investigation  (mda_officer: Bob)
  5. under_investigation → resolved  (mda_officer: Bob, comment: "Barrier removed")

SYSTEM TRANSITIONS:
  changed_by = NULL means the transition was triggered automatically,
  e.g. by an SLA auto-escalation job, not by a human user.

DB TABLE: case_timeline
SRS REFERENCE: Table 5.7
"""

import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
# CaseStatus lives in ntb_report.py — always import from there
from app.models.ntb_report import CaseStatus


class CaseTimeline(Base):
    __tablename__ = "case_timeline"

    # Unique identifier
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Which report this timeline entry belongs to
    report_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ntb_reports.id"),
        nullable=False,
        index=True,
    )

    # The status the case was in BEFORE this transition.
    # NULL on the very first entry (initial "submitted" state has no predecessor).
    from_status = Column(
        Enum(CaseStatus, name="case_status_enum"),
        nullable=True,
    )

    # The status the case moved INTO with this transition.
    to_status = Column(
        Enum(CaseStatus, name="case_status_enum"),
        nullable=False,
    )

    # The user who triggered this status change.
    # NULL = system-triggered (e.g. automated SLA escalation).
    changed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Optional note explaining the reason for this transition
    # (e.g. the summary of why a case was rejected or escalated)
    comment = Column(Text, nullable=True)

    # When this transition occurred — immutable, no updated_at
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    # The parent NTB report
    report = relationship("NTBReport", back_populates="timeline")

    # The user who made this change (None for system-triggered transitions)
    changed_by_user = relationship(
        "User",
        foreign_keys=[changed_by],
        back_populates="case_timeline",
    )

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    @property
    def is_system_transition(self) -> bool:
        """True when this status change was triggered automatically, not by a user."""
        return self.changed_by is None

    def __repr__(self) -> str:
        return (
            f"<CaseTimeline report_id={self.report_id} "
            f"{self.from_status} → {self.to_status}>"
        )