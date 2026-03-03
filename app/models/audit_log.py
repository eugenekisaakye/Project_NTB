"""
AuditLog model — Table 5.9 of the Uganda NTB SRS

Append-only, immutable record of every sensitive action in the system.
No updated_at — rows must never be modified or deleted (SRS NFR-audit).

Action naming convention: <resource>.<verb>
  e.g. case.assign, case.reject, case.status_change,
       user.create, user.deactivate,
       organization.create,
       category.deactivate
"""

import uuid
from enum import Enum as PyEnum
from typing import Optional, cast

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Resource type enum — constrains resource_type to known entity types
# ---------------------------------------------------------------------------
class AuditResourceType(str, PyEnum):
    REPORT       = "report"
    USER         = "user"
    ORGANIZATION = "organization"
    CATEGORY     = "category"


class AuditLog(Base):
    __tablename__ = "audit_log"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Actor — NULL for system-initiated actions (e.g. auto-escalation, auto-close)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # Action performed — dot-namespaced string, e.g. "case.assign"
    action = Column(String(100), nullable=False)

    # Affected entity
    resource_type = Column(String(50), nullable=False)   # AuditResourceType value
    resource_id   = Column(UUID(as_uuid=True), nullable=False)

    # Structured context — before/after values, metadata, extra identifiers.
    # JSONB allows efficient querying of nested fields in PostgreSQL.
    # Example: {"before": {"status": "submitted"}, "after": {"status": "assigned"},
    #            "assigned_org_id": "<uuid>"}
    details = Column(JSONB, nullable=True)

    # Client IP — stored for security investigations; supports IPv4 and IPv6
    ip_address = Column(String(45), nullable=True)

    # Immutable timestamp — no updated_at
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    user = relationship("User", foreign_keys=[user_id], back_populates="audit_logs")

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    @property
    def is_system_action(self) -> bool:
        """True when the action was triggered by the system, not a human user."""
        return self.user_id is None

    def __repr__(self) -> str:
        uid: Optional[uuid.UUID] = cast(Optional[uuid.UUID], self.user_id)
        actor = str(uid) if uid is not None else "system"
        return (
            f"<AuditLog action={self.action} "
            f"resource={self.resource_type}/{self.resource_id} "
            f"actor={actor}>"
        )