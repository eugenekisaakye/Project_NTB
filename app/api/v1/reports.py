"""
reports.py — NTB Report API routes

Handles the full lifecycle of NTB report submissions and case management.

BASE URL: /api/v1/reports  (prefix set in main.py — uncomment the router there to activate)

PLANNED ENDPOINTS:
  POST   /                    → Submit a new NTB report (trader or guest)
  GET    /                    → List reports (filtered/paginated; scope depends on role)
  GET    /{report_id}         → Get a single report's full detail
  PATCH  /{report_id}/status  → Change a case's status (MDA officer / admin only)
  POST   /{report_id}/assign  → Assign a case to an MDA organization (admin only)
  DELETE /{report_id}         → Soft-delete / reject a report (admin only)

ACCESS CONTROL:
  - Traders      → can submit reports; can only read their own
  - MDA officers → can read cases assigned to their org; can update status
  - Admins       → full access to all reports and all actions
  Use the require_* dependencies from app.core.dependencies to enforce this.

BUSINESS RULES TO ENFORCE (from SRS):
  - Guest submissions (no account) are allowed — reporter_id can be NULL
  - case_id must be generated in the format NTB-YYYY-NNNNN before insert
  - Rejection requires a non-empty rejection_reason
  - GPS coordinates must fall within Uganda's bounding box if provided
  - Every status change must write a CaseTimeline row
  - Every status change must write an AuditLog row

RELATED FILES:
  app/models/ntb_report.py     → NTBReport model + CaseStatus enum
  app/schemas/ntb_report.py    → Pydantic request/response schemas (create these)
  app/services/report_service.py → Business logic (create this)
"""

from fastapi import APIRouter

router = APIRouter()

# ---------------------------------------------------------------------------
# TODO: Implement the following endpoints
# ---------------------------------------------------------------------------

# @router.post("/", response_model=ReportResponse, status_code=201)
# def submit_report(payload: ReportCreate, db: Session = Depends(get_db)):
#     """Submit a new NTB report. Open to traders and guests."""
#     ...

# @router.get("/", response_model=PaginatedReportList)
# def list_reports(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
#     """
#     List reports. Results are scoped by role:
#       - trader      → only their own reports
#       - mda_officer → only cases assigned to their organization
#       - admin       → all reports
#     """
#     ...

# @router.get("/{report_id}", response_model=ReportDetailResponse)
# def get_report(report_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
#     """Get full detail of a single NTB report, including timeline and responses."""
#     ...

# @router.patch("/{report_id}/status")
# def update_status(report_id: UUID, payload: StatusUpdateRequest,
#                   db: Session = Depends(get_db), user: User = Depends(require_mda_officer)):
#     """
#     Move a case to a new status.
#     Writes a CaseTimeline row and an AuditLog row.
#     Enforces valid state transitions (e.g. can't go from resolved → submitted).
#     """
#     ...

# @router.post("/{report_id}/assign")
# def assign_report(report_id: UUID, payload: AssignRequest,
#                   db: Session = Depends(get_db), user: User = Depends(require_admin)):
#     """Assign a case to an MDA organization. Sets assigned_org_id and assigned_at."""
#     ...