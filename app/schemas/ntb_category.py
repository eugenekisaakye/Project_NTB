"""
NTBCategory schemas — request/response validation for the NTBCategory model.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared base
# ---------------------------------------------------------------------------
class NTBCategoryBase(BaseModel):
    code:        str           = Field(..., min_length=2, max_length=20)
    name:        str           = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


# ---------------------------------------------------------------------------
# Create (POST /admin/categories)
# ---------------------------------------------------------------------------
class NTBCategoryCreate(NTBCategoryBase):
    pass


# ---------------------------------------------------------------------------
# Update (PATCH /admin/categories/{id})
# ---------------------------------------------------------------------------
class NTBCategoryUpdate(BaseModel):
    name:        Optional[str]  = Field(None, min_length=2, max_length=255)
    description: Optional[str]  = Field(None, max_length=2000)
    is_active:   Optional[bool] = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class NTBCategoryResponse(BaseModel):
    id:          uuid.UUID
    code:        str
    name:        str
    description: Optional[str]
    is_active:   bool
    created_at:  datetime
    updated_at:  datetime

    model_config = {"from_attributes": True}


class NTBCategorySummary(BaseModel):
    """Lightweight category info embedded in report responses."""
    id:   uuid.UUID
    code: str
    name: str

    model_config = {"from_attributes": True}