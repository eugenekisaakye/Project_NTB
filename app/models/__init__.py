"""
app/models/__init__.py — Model registry

WHY THIS FILE EXISTS:
  SQLAlchemy only knows about a table if the model class has been *imported*
  before Base.metadata.create_all() is called. This file is the single place
  where we guarantee that import happens in the correct order.

  main.py does `import app.models` which triggers this file, which in turn
  imports every model. After that, create_all() can see all tables.

IMPORT ORDER RULES (follow this when adding new models):
  Import models from least dependent → most dependent.
  A model must be imported AFTER every model it has a ForeignKey pointing to.

  Current dependency chain:
    Organization, NTBCategory   (no FKs to other models)
        ↓
    User                        (FK → Organization)
        ↓
    NTBReport                   (FK → User, Organization, NTBCategory)
        ↓
    CaseAttachment              (FK → NTBReport)
    CaseTimeline                (FK → NTBReport, User)
    CaseResponse                (FK → NTBReport, User)
        ↓
    AuditLog                    (FK → User)

ADDING A NEW MODEL:
  1. Create the model file in app/models/
  2. Add its import below in the correct position in the dependency chain
  3. If it introduces a new enum, export that too so other modules can import
     from app.models instead of the individual file
"""

# 1. No FK dependencies — safe to import first
from app.models.organization import Organization, OrgType
from app.models.ntb_category import NTBCategory

# 2. Depends on Organization
from app.models.user import User, UserRole

# 3. Depends on User, Organization, NTBCategory
from app.models.ntb_report import NTBReport, CaseStatus

# 4. Depend on NTBReport (and some also on User)
from app.models.case_attachment import CaseAttachment
from app.models.case_timeline import CaseTimeline
from app.models.case_response import CaseResponse

# 5. Depends on User (append-only audit trail)
from app.models.audit_log import AuditLog, AuditResourceType