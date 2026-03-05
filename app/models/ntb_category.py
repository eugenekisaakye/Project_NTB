"""
ntb_category.py — NTB Category model

Categories classify what kind of Non-Tariff Barrier a report is about.
Examples: "Import Licensing", "Customs Procedures", "Rules of Origin", etc.

Each category has a short code (e.g. NTB-01) shown in the UI and reports,
plus a human-readable name and optional description to guide traders when
they're filling out a report.

SOFT DELETE BEHAVIOUR:
  Deactivated categories (is_active = False) remain linked to all existing
  cases — we never break historical data. They are simply hidden from the
  dropdown when a new report is being submitted.

DB TABLE: ntb_categories
SRS REFERENCE: Table 5.4
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class NTBCategory(Base):
    __tablename__ = "ntb_categories"

    # Unique identifier
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Short machine-friendly code shown in exports and case IDs (e.g. "NTB-01")
    code = Column(String(20), unique=True, nullable=False, index=True)

    # Full display name shown in the UI (e.g. "Import Licensing Restrictions")
    name = Column(String(255), nullable=False)

    # Optional longer explanation shown as a tooltip/helper text in the report form
    # to help traders understand which category best fits their situation
    description = Column(Text, nullable=True)

    # Soft delete — False hides this category from new submissions only
    is_active = Column(Boolean, default=True, nullable=False)

    # Auto-managed timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    # All NTB reports filed under this category
    ntb_reports = relationship("NTBReport", back_populates="category")

    def __repr__(self) -> str:
        return f"<NTBCategory code={self.code} name={self.name}>"