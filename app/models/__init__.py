"""
app/models/__init__.py

Import all models here in FK dependency order so that:
  1. Base.metadata.create_all() in main.py sees every table
  2. SQLAlchemy can resolve all relationships at startup
  3. There are no circular import issues

Add each model as you create it — DO NOT skip this step or
create_all() will silently miss tables.
"""

# 1. No FK dependencies
from app.models.organization import Organization, OrgType
from app.models.ntb_category import NTBCategory

# 2. Depends on Organization
from app.models.user import User, UserRole

# 3. Depends on User, Organization, NTBCategory
from app.models.ntb_report import NTBReport, CaseStatus

# 4. Depends on NTBReport
from app.models.case_attachment import CaseAttachment
from app.models.case_timeline import CaseTimeline
from app.models.case_response import CaseResponse

# 5. Depends on User (append-only)
from app.models.audit_log import AuditLog, AuditResourceType