"""
app/core/__init__.py

The core package contains shared infrastructure used across the entire application.
Nothing in here is specific to any one feature — these are the building blocks
every other module depends on.

CONTENTS:
  config.py       → All settings loaded from .env (DATABASE_URL, SECRET_KEY, etc.)
  security.py     → Password hashing (bcrypt) and JWT creation/validation
  dependencies.py → FastAPI Depends() helpers for authentication and role enforcement

IMPORT PATTERN:
  Other modules should import directly from the specific file, not from this package:
    from app.core.config import settings
    from app.core.security import hash_password, verify_password
    from app.core.dependencies import get_current_user, require_admin

  This keeps imports explicit and makes it easy to find where things come from.
"""