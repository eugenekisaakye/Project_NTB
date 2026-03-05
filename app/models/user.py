"""
User model — Table 5.2 of the Uganda NTB SRS
"""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Enum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Role enum — matches SRS RBAC matrix exactly
# ---------------------------------------------------------------------------
class UserRole(str, PyEnum):
    TRADER         = "trader"
    MDA_OFFICER    = "mda_officer"
    PRIVATE_SECTOR = "private_sector"
    ADMIN          = "admin"


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Identity
    email         = Column(String(255), unique=True, nullable=False, index=True)
    phone         = Column(String(20),  nullable=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt; never plain text
    full_name     = Column(String(255), nullable=False)

    # RBAC
    role = Column(
        Enum(UserRole, name="user_role_enum"),
        nullable=False,
    )

    # Organization link — NULL for traders, required for MDA / private sector
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )

    # Account state
    is_active         = Column(Boolean, default=True,  nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)

    # Security — account lockout (SRS: 5 failed attempts → 30 min lock)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until          = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships (uncomment as sibling models are created)
    # ---------------------------------------------------------------------------
    organization   = relationship("Organization", back_populates="users")
    ntb_reports = relationship("NTBReport", back_populates="reporter")
    case_responses = relationship("CaseResponse", foreign_keys="[CaseResponse.author_id]", back_populates="author")
    case_timeline  = relationship("CaseTimeline", foreign_keys="[CaseTimeline.changed_by]", back_populates="changed_by_user")
    audit_logs     = relationship("AuditLog",     foreign_keys="[AuditLog.user_id]",        back_populates="user")

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    def is_locked(self) -> bool:
        """Returns True if the account is currently locked out."""
        locked_until: Any = self.locked_until
        if locked_until is None:
            return False
        return datetime.now(timezone.utc) < locked_until

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"