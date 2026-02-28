"""
CaseTimeline model — Table 5.7 of the Uganda NTB SRS

Append-only status history. Every status transition on an NTBReport
writes one row here, giving a full immutable audit trail of the case lifecycle.

No updated_at — rows are never modified after insert.
"""

import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.ntb_report import CaseStatus


class CaseTimeline(Base):
    __tablename__ = "case_timeline"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Parent report
    report_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ntb_reports.id"),
        nullable=False,
        index=True,
    )

    # Status transition — from_status is NULL for the initial "Submitted" entry
    from_status = Column(
        Enum(CaseStatus, name="case_status_enum"),
        nullable=True,
    )
    to_status = Column(
        Enum(CaseStatus, name="case_status_enum"),
        nullable=False,
    )

    # Actor — NULL means the transition was system-triggered (e.g. SLA auto-escalation)
    changed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Optional free-text note explaining the transition (e.g. rejection reason summary)
    comment = Column(Text, nullable=True)

    # Immutable timestamp — no updated_at
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    report     = relationship("NTBReport", back_populates="timeline")
    changed_by_user = relationship("User", foreign_keys=[changed_by])

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    @property
    def is_system_transition(self) -> bool:
        """True when the transition was triggered automatically (no acting user)."""
        return self.changed_by is None

    def __repr__(self) -> str:
        return (
            f"<CaseTimeline report_id={self.report_id} "
            f"{self.from_status} → {self.to_status}>"
        )