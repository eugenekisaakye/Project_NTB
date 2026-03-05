"""
main.py — FastAPI application entry point

This file does three things:
  1. Creates the FastAPI app instance with metadata (title, docs URLs, etc.)
  2. Registers middleware (currently just CORS)
  3. Registers all API routers under their URL prefixes

When you add a new feature module (e.g. reports, analytics), you will:
  a) Create the router in app/api/v1/<module>.py
  b) Import it here and uncomment (or add) the app.include_router() line

STARTUP / SHUTDOWN:
  The 'lifespan' context manager runs once when the server starts and once
  when it shuts down. On startup we call create_all() to ensure every table
  exists in the DB without wiping existing data (checkfirst=True).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

# This import registers all models with Base so create_all() sees their tables.
# DO NOT remove it even though the symbol isn't used directly here.
import app.models  # noqa: F401

from app.api.v1 import auth


# ---------------------------------------------------------------------------
# Lifespan — startup and shutdown logic
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Create any missing tables (safe to run on every boot)
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("✅ Database tables verified / created.")
    yield  # <-- app runs here
    # SHUTDOWN: add cleanup logic here if needed (e.g. close background workers)
    print("🛑 Application shutting down.")


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Uganda NTB Reporting & Response Platform",
    description="API for reporting and managing Non-Tariff Barriers in Uganda.",
    version="1.0.0",
    # Interactive Swagger UI lives at /api/docs
    docs_url="/api/docs",
    # ReDoc alternative docs live at /api/redoc
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS middleware
# allow_origins=["*"] is fine for development.
# For production, replace "*" with the exact frontend domain(s),
# e.g. ["https://ntb.go.ug", "https://admin.ntb.go.ug"]
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# Each router handles one feature area. Uncomment as you build each module.
# Pattern: app.include_router(<module>.router, prefix="/api/v1/<name>", tags=["<Tag>"])
# ---------------------------------------------------------------------------
app.include_router(auth.router,      prefix="/api/v1/auth",      tags=["Auth"])
# app.include_router(reports.router,   prefix="/api/v1/reports",   tags=["Reports"])
# app.include_router(responses.router, prefix="/api/v1/responses", tags=["Responses"])
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
# app.include_router(admin.router,     prefix="/api/v1/admin",     tags=["Admin"])


# ---------------------------------------------------------------------------
# Utility endpoints
# ---------------------------------------------------------------------------
@app.get("/api/v1/health", tags=["Health"])
def health_check():
    """
    Simple liveness check. Load balancers and monitoring tools ping this
    to verify the server is up. Returns HTTP 200 when healthy.
    """
    return {"status": "ok", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
def root():
    """Redirect hint for anyone hitting the bare domain."""
    return {"message": "Uganda NTB Platform API. Visit /api/docs for documentation."}