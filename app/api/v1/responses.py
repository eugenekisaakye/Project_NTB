"""
responses.py — Case Response API routes

Handles MDA officers and admins posting responses and internal notes on NTB cases.

BASE URL: /api/v1/responses  (prefix set in main.py — uncomment the router to activate)

PLANNED ENDPOINTS:
  POST /                       → Post a response or internal note on a report
  GET  /{report_id}/responses  → List responses for a report (filtered by visibility)

ACCESS CONTROL:
  - Traders      → can READ public responses (is_internal = False) on their own cases only
  - MDA officers → can READ all responses on assigned cases; can POST responses
  - Admins       → full access; can post internal notes

CRITICAL VISIBILITY RULE (SRS BR-006/007):
  When returning responses to a trader, the service layer MUST filter out
  any rows where is_internal = True. Never expose internal notes to traders.

BUSINESS RULES:
  - Content must be 10–5,000 characters (enforced by Pydantic schema)
  - Responses are immutable after posting — no edit or delete endpoints
  - Each post should write an AuditLog entry (action: "case.response_added")

RELATED FILES:
  app/models/case_response.py     → CaseResponse model
  app/schemas/case_response.py    → Pydantic schemas (create these)
  app/services/response_service.py → Business logic (create this)
"""

from fastapi import APIRouter

router = APIRouter()

# ---------------------------------------------------------------------------
# TODO: Implement the following endpoints
# ---------------------------------------------------------------------------

# @router.post("/", response_model=CaseResponseOut, status_code=201)
# def post_response(payload: CaseResponseCreate, db: Session = Depends(get_db),
#                   user: User = Depends(require_mda_officer)):
#     """
#     Post a response or internal note on a case.
#     Set is_internal=True for notes that should not be visible to the trader.
#     """
#     ...

# @router.get("/{report_id}/responses", response_model=list[CaseResponseOut])
# def get_responses(report_id: UUID, db: Session = Depends(get_db),
#                   user: User = Depends(get_current_user)):
#     """
#     Return all responses for a report.
#     IMPORTANT: If the requesting user is a trader, exclude is_internal=True rows.
#     """
#     ...