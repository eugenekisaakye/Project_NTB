"""
CaseAttachment model — Table 5.6 of the Uganda NTB SRS

Business rules enforced at the application layer (Pydantic / service):
  - Max 5 attachments per report (SRS BR-attach-count)
  - Max file size 5 MB per file (SRS BR-attach-size)
  - Allowed MIME types: image/jpeg, image/png, application/pdf (SRS BR-attach-type)
  - stored_path must be outside the web root (SRS NFR-security)
"""

import uuid
from typing import cast

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base

# Allowed MIME types — kept here as the single source of truth so the
# upload service and any validators can import from one place.
ALLOWED_MIME_TYPES: frozenset[str] = frozenset({
    "image/jpeg",
    "image/png",
    "application/pdf",
})

MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024   # 5 MB
MAX_ATTACHMENTS_PER_REPORT: int = 5


class CaseAttachment(Base):
    __tablename__ = "case_attachments"

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

    # File metadata
    filename    = Column(String(255), nullable=False)   # sanitized original filename
    stored_path = Column(String(500), nullable=False)   # absolute server path, outside web root
    mime_type   = Column(String(100), nullable=False)   # validated against ALLOWED_MIME_TYPES
    file_size   = Column(Integer,     nullable=False)   # bytes; validated ≤ MAX_FILE_SIZE_BYTES

    # Timestamp — no updated_at; attachments are immutable after upload
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    report = relationship("NTBReport", back_populates="attachments")

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    @property
    def file_size_kb(self) -> float:
        """Convenience property — returns file size in kilobytes."""
        return round(cast(int, self.file_size) / 1024, 2)

    def __repr__(self) -> str:
        return f"<CaseAttachment id={self.id} filename={self.filename} report_id={self.report_id}>"