"""
organization.py — Organization model

An Organization is a body that either:
  - Investigates and resolves NTB cases (type = MDA, e.g. Uganda Revenue Authority)
  - Represents the private sector in the reporting process (type = PRIVATE_SECTOR)

Traders do NOT belong to an organization — only MDA officers and
private-sector users are linked to one.

DB TABLE: organizations
SRS REFERENCE: Table 5.3
"""

import uuid
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, String, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------------------------------------------------------------------
# OrgType enum — the two categories of organization in the system
# ---------------------------------------------------------------------------
class OrgType(str, PyEnum):
    MDA            = "mda"             # Ministry, Department, or Agency (government body)
    PRIVATE_SECTOR = "private_sector"  # Business association or chamber of commerce


# ---------------------------------------------------------------------------
# Organization model
# ---------------------------------------------------------------------------
class Organization(Base):
    __tablename__ = "organizations"

    # Unique identifier — UUID so IDs are safe to expose in URLs
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Organization display name — must be unique across the system
    name = Column(String(255), unique=True, nullable=False)

    # Whether this is a government body (MDA) or private-sector body
    type = Column(Enum(OrgType, name="org_type_enum"), nullable=False)

    # Primary contact email for the organization (used for notifications)
    contact_email = Column(String(255), nullable=False)

    # Soft delete — deactivated orgs are hidden from new case assignments
    # but their historical data (cases, users) is preserved
    is_active = Column(Boolean, default=True, nullable=False)

    # Auto-managed timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    # Users who belong to this organization (MDA officers, private-sector reps)
    users = relationship("User", back_populates="organization")

    # NTB cases that have been assigned to this organization for investigation
    ntb_reports = relationship("NTBReport", back_populates="assigned_org")

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name} type={self.type}>"