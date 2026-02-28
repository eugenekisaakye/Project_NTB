"""
CaseResponse model — Table 5.8 of the Uganda NTB SRS

Stores both public responses (visible to the reporting trader) and
internal notes (visible to MDA officers and admins only).

Business rules enforced at the application layer:
  - content length: 10–5,000 characters (SRS BR-response-length)
  - Only MDA officers and admins may post responses (SRS RBAC matrix)
  - Traders may only read responses where is_internal = False (SRS BR-006/007)

No updated_at — responses are immutable after posting.
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CaseResponse(Base):
    __tablename__ = "case_responses"

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

    # Author — always a registered user; guests cannot post responses
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    # Response body — 10–5,000 chars enforced by Pydantic
    content = Column(Text, nullable=False)

    # Visibility flag:
    #   False (default) → public response, visible to the reporting trader
    #   True            → internal note, visible to MDA officers and admins only
    is_internal = Column(Boolean, default=False, nullable=False)

    # Immutable timestamp — no updated_at
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    report = relationship("NTBReport", back_populates="responses")
    author = relationship("User", foreign_keys=[author_id])

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    @property
    def is_public(self) -> bool:
        """True when this response is visible to the reporting trader."""
        return not self.is_internal

    def __repr__(self) -> str:
        visibility = "internal" if self.is_internal else "public"
        return f"<CaseResponse id={self.id} report_id={self.report_id} {visibility}>"