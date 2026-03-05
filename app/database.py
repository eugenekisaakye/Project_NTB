"""
database.py — Database connection setup

This is the single place where we configure SQLAlchemy.
Every other file that needs a DB session imports from here.

HOW IT WORKS:
  - We read the DATABASE_URL from the .env file (e.g. postgresql://user:pass@localhost/ntb_db)
  - We create a shared 'engine' (the low-level connection pool)
  - We create a 'SessionLocal' factory — call it to get a session you can query with
  - 'Base' is the class all our models inherit from so SQLAlchemy knows about their tables

USAGE IN ROUTES (FastAPI dependency injection):
    from app.database import get_db
    from sqlalchemy.orm import Session
    from fastapi import Depends

    @router.get("/something")
    def my_route(db: Session = Depends(get_db)):
        # db is a live session — use it, then it auto-closes when the request ends
        ...
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
load_dotenv()

# Pull the connection string — fail fast if it's missing rather than
# getting a confusing error later when we first try to query
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

# The engine manages the underlying connection pool.
# For async support in the future, swap to create_async_engine + asyncpg.
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory: each call gives you a new DB session.
# autocommit=False → we control when transactions are committed (safer)
# autoflush=False  → SQLAlchemy won't auto-push changes to DB mid-transaction
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# Base is the parent class for ALL our ORM models (User, NTBReport, etc.)
# When we call Base.metadata.create_all(), SQLAlchemy creates every table
# whose model has been imported.
Base = declarative_base()


# ---------------------------------------------------------------------------
# FastAPI dependency — use this in every route that needs the database
# ---------------------------------------------------------------------------
def get_db():
    """
    Yields a database session and guarantees it is closed when the
    request finishes — even if an exception is raised mid-request.

    Always use via FastAPI's Depends():
        def my_route(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()