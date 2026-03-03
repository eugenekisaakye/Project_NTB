"""
Uganda NTB Reporting & Response Platform
FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

# ---------------------------------------------------------------------------
# Import all models via __init__.py so Base.metadata knows about every table
# before create_all() runs. Importing the package is enough — __init__.py
# pulls in every model class in FK dependency order.
# ---------------------------------------------------------------------------
import app.models  # noqa: F401

# ---------------------------------------------------------------------------
# Import routers (uncomment as you build each module)
# ---------------------------------------------------------------------------
from app.api.v1 import auth, reports, responses, analytics, admin


# ---------------------------------------------------------------------------
# Lifespan: runs on startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — create tables that don't exist yet; never drops existing ones
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("✅ Database tables verified / created.")
    yield
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