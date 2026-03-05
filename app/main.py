"""
Uganda NTB Reporting & Response Platform
FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

import app.models  # noqa: F401

from app.api.v1 import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("✅ Database tables verified / created.")
    yield
    print("🛑 Application shutting down.")


app = FastAPI(
    title="Uganda NTB Reporting & Response Platform",
    description="API for reporting and managing Non-Tariff Barriers in Uganda.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers — uncomment as you build each module
# ---------------------------------------------------------------------------
app.include_router(auth.router,      prefix="/api/v1/auth",      tags=["Auth"])
# app.include_router(reports.router,   prefix="/api/v1/reports",   tags=["Reports"])
# app.include_router(responses.router, prefix="/api/v1/responses", tags=["Responses"])
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
# app.include_router(admin.router,     prefix="/api/v1/admin",     tags=["Admin"])


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Uganda NTB Platform API. Visit /api/docs for documentation."}