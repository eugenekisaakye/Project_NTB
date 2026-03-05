"""
config.py — Application-wide settings

All configuration is read from the .env file in the project root.
Pydantic's BaseSettings handles the reading, type-casting, and validation
automatically — if a required variable is missing, the app fails fast on startup
with a clear error rather than crashing later with a confusing message.

The single `settings` instance at the bottom is imported everywhere:
    from app.core.config import settings
    print(settings.DATABASE_URL)

ADDING A NEW SETTING:
  1. Add the field here with a type annotation and an optional default.
  2. Add the variable to .env (and .env.example for the team).
  3. Import `settings` and use settings.YOUR_FIELD wherever needed.

REQUIRED (no default — app will not start without these in .env):
  DATABASE_URL, SECRET_KEY

ALL OTHERS have sensible defaults for local development but should be
explicitly set in staging/production .env files.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ---------------------------------------------------------------------------
    # Application
    # ---------------------------------------------------------------------------
    APP_ENV:     str  = "development"   # "development" | "staging" | "production"
    DEBUG:       bool = True            # Set False in production — disables extra logging
    APP_VERSION: str  = "1.0.0"

    # ---------------------------------------------------------------------------
    # Database
    # ---------------------------------------------------------------------------
    # Full PostgreSQL connection string.
    # Format: postgresql://USER:PASSWORD@HOST:PORT/DB_NAME
    # Example: postgresql://ntb_user:secret@localhost:5432/ntb_db
    # REQUIRED — no default.
    DATABASE_URL: str

    # ---------------------------------------------------------------------------
    # JWT (JSON Web Tokens) — used for user authentication
    # ---------------------------------------------------------------------------
    # A long random string used to sign tokens. Generate with:
    #   python -c "import secrets; print(secrets.token_hex(32))"
    # REQUIRED — no default. Never commit this to git.
    SECRET_KEY: str

    # Signing algorithm — HS256 is standard for symmetric JWTs
    ALGORITHM: str = "HS256"

    # How long an access token stays valid (short-lived by design)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # How long a refresh token stays valid (used to issue new access tokens)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---------------------------------------------------------------------------
    # Email / SMTP — used for email verification and notifications
    # ---------------------------------------------------------------------------
    SMTP_HOST:     str = "smtp.gmail.com"
    SMTP_PORT:     int = 587              # 587 = TLS (STARTTLS); 465 = SSL
    SMTP_USER:     str = ""              # Your Gmail address (or other provider)
    SMTP_PASSWORD: str = ""              # Gmail app password (NOT your account password)
    EMAIL_FROM:    str = ""              # The "From:" address in sent emails
    EMAIL_FROM_NAME: str = "Uganda NTB Platform"  # The "From:" display name

    # ---------------------------------------------------------------------------
    # Security — account lockout (mirrors the SRS NFR-security rules)
    # ---------------------------------------------------------------------------
    # Lock account after this many consecutive failed login attempts
    FAILED_LOGIN_MAX_ATTEMPTS: int = 5

    # How long (minutes) the account stays locked before auto-unlocking
    ACCOUNT_LOCKOUT_MINUTES: int = 30

    # ---------------------------------------------------------------------------
    # Frontend — used to build links in emails (e.g. verify-email links)
    # ---------------------------------------------------------------------------
    FRONTEND_URL: str = "http://localhost:3000"  # Change to production URL in .env

    # ---------------------------------------------------------------------------
    # File uploads
    # ---------------------------------------------------------------------------
    # Server-side directory where uploaded files are stored.
    # MUST be outside the web root in production (e.g. /var/ntb_uploads/).
    UPLOAD_DIR: str = "./uploads"

    MAX_FILE_SIZE_MB:     int = 5   # Per-file size limit (mirrors case_attachment.py)
    MAX_FILES_PER_REPORT: int = 5   # Max attachments per NTB report

    # ---------------------------------------------------------------------------
    # Pagination defaults (used in list endpoints)
    # ---------------------------------------------------------------------------
    DEFAULT_PAGE_SIZE: int = 20   # Records returned per page if not specified
    MAX_PAGE_SIZE:     int = 100  # Absolute ceiling — prevents giant queries

    # ---------------------------------------------------------------------------
    # Pydantic settings config
    # ---------------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",            # Load from .env in the project root
        env_file_encoding="utf-8",
        case_sensitive=True,        # DATABASE_URL ≠ database_url
        extra="ignore",             # Silently ignore unknown .env variables
    )


# Single shared instance — import this everywhere, don't instantiate Settings() again
settings = Settings()