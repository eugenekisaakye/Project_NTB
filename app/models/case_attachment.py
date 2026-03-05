"""
case_attachment.py — CaseAttachment model

Stores metadata about files uploaded alongside an NTB report
(e.g. a photo of a blocked shipment, a PDF of a rejected customs form).

IMPORTANT — the actual file bytes are NOT stored in the database.
Only the metadata is stored here. The file lives on the server at
stored_path, which must be outside the web root so it cannot be
accessed directly via a URL (SRS NFR-security).

LIMITS (enforced in the upload service, not the DB):
  - Max 5 attachments per report       → MAX_ATTACHMENTS_PER_REPORT
  - Max 5 MB per file                  → MAX_FILE_SIZE_BYTES
  - Only JPEG, PNG, PDF are accepted   → ALLOWED_MIME_TYPES

These constants are defined here as the single source of truth so the
upload service, validators, and any future checks all use the same values.

Attachments are IMMUTABLE after upload — there is no updated_at.

DB TABLE: case_attachments
SRS REFERENCE: Table 5.6
"""

import uuid
from typing import cast

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base

# ---------------------------------------------------------------------------
# Upload constraints — import these into the upload service instead of
# hardcoding the same numbers in multiple places
# ---------------------------------------------------------------------------
ALLOWED_MIME_TYPES: frozenset[str] = frozenset({
    "image/jpeg",
    "image/png",
    "application/pdf",
})

MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024   # 5 MB in bytes
MAX_ATTACHMENTS_PER_REPORT: int = 5


class CaseAttachment(Base):
    __tablename__ = "case_attachments"

    # Unique identifier
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Which report this file belongs to
    report_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ntb_reports.id"),
        nullable=False,
        index=True,
    )

    # The original filename, sanitized to remove path traversal characters
    # (e.g. "../../etc/passwd" must be rejected at the service layer)
    filename = Column(String(255), nullable=False)

    # Absolute server-side path to the stored file.
    # Must be outside the web root (e.g. /var/ntb_uploads/, NOT /var/www/)
    stored_path = Column(String(500), nullable=False)

    # MIME type as detected/validated during upload. Must be in ALLOWED_MIME_TYPES.
    mime_type = Column(String(100), nullable=False)

    # File size in bytes. Must be ≤ MAX_FILE_SIZE_BYTES.
    file_size = Column(Integer, nullable=False)

    # Upload timestamp — immutable, no updated_at
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------
    # Back-reference to the parent report
    report = relationship("NTBReport", back_populates="attachments")

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    @property
    def file_size_kb(self) -> float:
        """Returns file size in kilobytes — handy for display in the UI."""
        return round(cast(int, self.file_size) / 1024, 2)

    def __repr__(self) -> str:
        return f"<CaseAttachment id={self.id} filename={self.filename} report_id={self.report_id}>"