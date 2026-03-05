"""
user.py — User model

Represents every person who can log into the platform.
There are four roles with different levels of access (see UserRole below).

ROLE SUMMARY:
  trader         → submits NTB reports; can track their own cases
  mda_officer    → investigates cases assigned to their organization; posts responses
  private_sector → similar to trader but represents a business body
  admin          → full system access: manage users, orgs, categories, view all data

ACCOUNT LOCKOUT (SRS NFR-security):
  After 5 consecutive failed login attempts, the account is locked for 30 minutes.
  This is tracked via failed_login_attempts and locked_until. The is_locked()
  helper makes it easy to check this in the auth service.

DB TABLE: users
SRS REFERENCE: Table 5.2
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
# UserRole enum — maps directly to the RBAC matrix in the SRS
# ---------------------------------------------------------------------------
class UserRole(str, PyEnum):
    TRADER         = "trader"          # General public / importing business
    MDA_OFFICER    = "mda_officer"     # Government investigator
    PRIVATE_SECTOR = "private_sector"  # Private sector association rep
    ADMIN          = "admin"           # Platform administrator


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    # Unique identifier — UUID avoids exposing sequential IDs in the API
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # --- Identity fields ---
    email         = Column(String(255), unique=True, nullable=False, index=True)
    phone         = Column(String(20),  nullable=True)
    password_hash = Column(String(255), nullable=False)  # ALWAYS bcrypt — never store plain text
    full_name     = Column(String(255), nullable=False)

    # --- Role-based access control ---
    role = Column(
        Enum(UserRole, name="user_role_enum"),
        nullable=False,
    )

    # Which organization this user belongs to.
    # NULL is valid for traders — they are not affiliated with any org.
    # MDA officers and private-sector users MUST have an org (enforced in the service layer).
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )

    # --- Account state ---
    is_active         = Column(Boolean, default=True,  nullable=False)  # False = deactivated/banned
    is_email_verified = Column(Boolean, default=False, nullable=False)  # Must be True before login

    # --- Security: brute-force lockout ---
    # Increment on each failed login; reset to 0 on successful login.
    # When this hits 5, set locked_until = now + 30 minutes.
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until          = Column(DateTime(timezone=True), nullable=True)  # NULL = not locked

    # --- Timestamps ---
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships — each connects this user to a related table
    # ---------------------------------------------------------------------------
    # The organization this user belongs to (NULL for traders)
    organization = relationship("Organization", back_populates="users")

    # All NTB reports this user has submitted
    ntb_reports = relationship("NTBReport", back_populates="reporter")

    # Responses/notes this user has posted on cases
    case_responses = relationship(
        "CaseResponse",
        foreign_keys="[CaseResponse.author_id]",
        back_populates="author",
    )

    # Status changes this user has made on cases (e.g. assigned → under investigation)
    case_timeline = relationship(
        "CaseTimeline",
        foreign_keys="[CaseTimeline.changed_by]",
        back_populates="changed_by_user",
    )

    # System audit trail entries where this user was the actor
    audit_logs = relationship(
        "AuditLog",
        foreign_keys="[AuditLog.user_id]",
        back_populates="user",
    )

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    def is_locked(self) -> bool:
        """
        Returns True if this account is currently locked out due to too many
        failed login attempts. The auth service should call this before
        allowing a login attempt to proceed.
        """
        locked_until: Any = self.locked_until
        if locked_until is None:
            return False
        return datetime.now(timezone.utc) < locked_until

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"