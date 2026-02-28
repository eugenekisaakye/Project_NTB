"""
NTB Category model — Table 5.4 of the Uganda NTB SRS
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class NTBCategory(Base):
    __tablename__ = "ntb_categories"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Identity
    code        = Column(String(20),  unique=True, nullable=False, index=True)  # e.g. NTB-01
    name        = Column(String(255), nullable=False)
    description = Column(Text,        nullable=True)  # shown in UI to guide reporters

    # Soft delete — deactivated categories stay linked to existing cases
    # but are unavailable for new report submissions (SRS BR-admin)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    # ntb_reports = relationship("NTBReport", back_populates="category")  # uncomment when created

    def __repr__(self) -> str:
        return f"<NTBCategory code={self.code} name={self.name}>"