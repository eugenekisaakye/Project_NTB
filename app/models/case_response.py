"""
case_response.py — CaseResponse model

Stores written responses and internal notes posted on an NTB case.

VISIBILITY:
  is_internal = False → PUBLIC response, visible to the reporting trader
  is_internal = True  → INTERNAL note, visible to MDA officers and admins only

  The trader-facing API must filter out internal notes before returning
  responses (SRS BR-006/007). This is enforced in the service/route layer,
  NOT in the DB — so be careful not to expose is_internal=True rows to traders.

WHO CAN POST:
  Only MDA officers and admins may post responses (SRS RBAC matrix).
  Traders can READ public responses but cannot create them.
  This is enforced in the route layer via role checks.

CONTENT LENGTH:
  10 to 5,000 characters — validated by Pydantic before saving.

IMMUTABILITY:
  Responses cannot be edited or deleted after posting.
  There is no updated_at column. This preserves the integrity of the
  communication record between the platform and the trader.

DB TABLE: case_responses
SRS REFERENCE: Table 5.8
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CaseResponse(Base):
    __tablename__ = "case_responses"

    # Unique identifier
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Which NTB report this response is posted on
    report_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ntb_reports.id"),
        nullable=False,
        index=True,
    )

    # The MDA officer or admin who wrote this response
    # (guests and traders cannot post responses)
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    # The response body — 10 to 5,000 characters, enforced by Pydantic
    content = Column(Text, nullable=False)

    # Visibility flag:
    #   False (default) = public, shown to the trader who filed the report
    #   True            = internal note, shown only to MDA officers and admins
    # The API MUST check this flag before returning responses to a trader.
    is_internal = Column(Boolean, default=False, nullable=False)

    # Timestamp of when the response was posted — immutable, no updated_at
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    # The parent NTB report
    report = relationship("NTBReport", back_populates="responses")

    # The officer/admin who authored this response
    author = relationship("User", foreign_keys=[author_id], back_populates="case_responses")

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    @property
    def is_public(self) -> bool:
        """True when this response is visible to the reporting trader."""
        return not bool(self.is_internal)

    def __repr__(self) -> str:
        visibility = "internal" if bool(self.is_internal) else "public"
        return f"<CaseResponse id={self.id} report_id={self.report_id} {visibility}>"