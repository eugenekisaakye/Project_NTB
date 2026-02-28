"""
Organization model — Table 5.3 of the Uganda NTB SRS
"""

import uuid
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, String, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class OrgType(str, PyEnum):
    MDA            = "mda"
    PRIVATE_SECTOR = "private_sector"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    name          = Column(String(255), unique=True, nullable=False)
    type          = Column(Enum(OrgType, name="org_type_enum"), nullable=False)
    contact_email = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    users = relationship("User", back_populates="organization")
    # ntb_reports = relationship("NTBReport", back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name} type={self.type}>"