"""
Uganda NTB Reporting & Response Platform
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager





from app.database import engine, Base



# ---------------------------------------------------------------------------
# Import all models here so Base.metadata knows about them before create_all()
# ---------------------------------------------------------------------------
#from app.models import (
    # user,
    # organization,
    # ntb_category,
    # ntb_report,
    # case_attachment,
    # case_timeline,
    # case_response,
    # audit_log,
#)

# ---------------------------------------------------------------------------
# Import routers (uncomment as you build each module)
# ---------------------------------------------------------------------------
# from app.api.v1 import auth, reports, responses, analytics, admin


# ---------------------------------------------------------------------------
# Lifespan: runs on startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables verified / created.")
    yield
    # Shutdown — add any cleanup here (close connections, etc.)
    print("🛑 Application shutting down.")


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Uganda NTB Reporting & Response Platform",
    description="API for reporting and managing Non-Tariff Barriers in Uganda.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: lock down to your frontend URL before production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routers — all endpoints live under /api/v1/
# ---------------------------------------------------------------------------
# app.include_router(auth.router,      prefix="/api/v1/auth",      tags=["Auth"])
# app.include_router(reports.router,   prefix="/api/v1/reports",   tags=["Reports"])
# app.include_router(responses.router, prefix="/api/v1/responses", tags=["Responses"])
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
# app.include_router(admin.router,     prefix="/api/v1/admin",     tags=["Admin"])


# ---------------------------------------------------------------------------
# Health check — verified by deployment pipeline before going live
# ---------------------------------------------------------------------------
@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Root redirect hint
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
def root():
    return {"message": "Uganda NTB Platform API. Visit /api/docs for documentation."}