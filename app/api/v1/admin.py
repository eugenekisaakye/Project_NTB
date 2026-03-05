"""
admin.py — Admin-only API routes

Provides platform administration endpoints: managing users, organizations,
and NTB categories. All endpoints here require the ADMIN role.

BASE URL: /api/v1/admin  (prefix set in main.py — uncomment the router to activate)

PLANNED ENDPOINTS:

  Users:
    GET    /users                   → List all users (paginated, filterable by role/status)
    GET    /users/{user_id}         → Get a single user's profile
    PATCH  /users/{user_id}         → Update user details or role
    POST   /users/{user_id}/deactivate → Soft-deactivate a user account
    POST   /users/{user_id}/unlock  → Manually unlock a locked account

  Organizations:
    GET    /organizations           → List all organizations
    POST   /organizations           → Create a new organization
    PATCH  /organizations/{org_id}  → Update organization details
    POST   /organizations/{org_id}/deactivate → Soft-deactivate an organization

  NTB Categories:
    GET    /categories              → List all categories (including inactive)
    POST   /categories              → Create a new NTB category
    PATCH  /categories/{cat_id}     → Update a category's name/description
    POST   /categories/{cat_id}/deactivate → Soft-deactivate a category

  Audit Log:
    GET    /audit-log               → Browse the immutable audit trail (filterable)

ACCESS CONTROL:
  Every endpoint here must use Depends(require_admin).
  Double-check this — admin endpoints should NEVER be reachable by other roles.

AUDIT LOGGING:
  Every mutating action (create, update, deactivate) must write an AuditLog row.
  Use the audit_service (or write directly) from the service layer, not the route.

RELATED FILES:
  app/models/user.py           → User model
  app/models/organization.py   → Organization model
  app/models/ntb_category.py   → NTBCategory model
  app/models/audit_log.py      → AuditLog model
  app/core/dependencies.py     → require_admin dependency
  app/services/admin_service.py → Business logic (create this)
"""

from fastapi import APIRouter

router = APIRouter()

# ---------------------------------------------------------------------------
# TODO: Implement the following endpoint groups
# ---------------------------------------------------------------------------

# --- User management ---

# @router.get("/users", response_model=PaginatedUserList)
# def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
#     """List all users. Supports filtering by role, is_active, organization."""
#     ...

# @router.post("/users/{user_id}/deactivate")
# def deactivate_user(user_id: UUID, db: Session = Depends(get_db),
#                     admin: User = Depends(require_admin)):
#     """
#     Deactivate a user account (sets is_active = False).
#     The user can no longer log in. Their data is preserved.
#     Writes an AuditLog entry (action: "user.deactivate").
#     """
#     ...

# @router.post("/users/{user_id}/unlock")
# def unlock_user(user_id: UUID, db: Session = Depends(get_db),
#                 admin: User = Depends(require_admin)):
#     """
#     Manually clear a brute-force lockout.
#     Resets failed_login_attempts to 0 and locked_until to NULL.
#     """
#     ...

# --- Organization management ---

# @router.post("/organizations", response_model=OrgResponse, status_code=201)
# def create_organization(payload: OrgCreate, db: Session = Depends(get_db),
#                          admin: User = Depends(require_admin)):
#     """Create a new MDA or private-sector organization."""
#     ...

# --- NTB Category management ---

# @router.post("/categories", response_model=CategoryResponse, status_code=201)
# def create_category(payload: CategoryCreate, db: Session = Depends(get_db),
#                     admin: User = Depends(require_admin)):
#     """Add a new NTB category. It will immediately appear in the submission form."""
#     ...

# @router.post("/categories/{cat_id}/deactivate")
# def deactivate_category(cat_id: UUID, db: Session = Depends(get_db),
#                          admin: User = Depends(require_admin)):
#     """
#     Soft-delete a category (sets is_active = False).
#     Existing reports keep their category link. New reports cannot use it.
#     Writes an AuditLog entry (action: "category.deactivate").
#     """
#     ...

# --- Audit log ---

# @router.get("/audit-log")
# def get_audit_log(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
#     """
#     Browse the immutable audit trail.
#     Supports filtering by user_id, resource_type, resource_id, action, date range.
#     """
#     ...