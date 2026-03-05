"""
app/core/config.py
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_ENV:     str = "development"
    DEBUG:       bool = True
    APP_VERSION: str = "1.0.0"

    # --- Database ---
    DATABASE_URL: str

    # --- JWT ---
    SECRET_KEY:                  str
    ALGORITHM:                   str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS:   int = 7

    # --- Email ---
    SMTP_HOST:       str = "smtp.gmail.com"
    SMTP_PORT:       int = 587
    SMTP_USER:       str = ""
    SMTP_PASSWORD:   str = ""
    EMAIL_FROM:      str = ""
    EMAIL_FROM_NAME: str = "Uganda NTB Platform"

    # --- Security ---
    FAILED_LOGIN_MAX_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES:   int = 30

    # --- Frontend ---
    FRONTEND_URL: str = "http://localhost:3000"

    # --- File uploads ---
    UPLOAD_DIR:           str = "./uploads"
    MAX_FILE_SIZE_MB:     int = 5
    MAX_FILES_PER_REPORT: int = 5

    # --- Pagination ---
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE:     int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()