"""
security.py — Password hashing and JWT token utilities

This module is the single place for all cryptographic operations.
Nothing outside this file should call bcrypt or jose directly.

FUNCTIONS AT A GLANCE:
  hash_password(plain)                    → bcrypt hash string (store this in DB)
  verify_password(plain, hashed)          → True/False (use during login)
  create_access_token(user_id)            → short-lived JWT for API access
  create_refresh_token(user_id)           → long-lived JWT to obtain new access tokens
  create_email_verification_token(user_id)→ 24-hour JWT for email confirm links
  decode_token(token, expected_type)      → returns user_id string or None if invalid

TOKEN TYPES:
  All tokens are JWTs signed with the same SECRET_KEY but carry a "type" claim
  that prevents one type being used where another is expected
  (e.g. an email verification token cannot be used as an access token).

  "access"       → API requests (Authorization: Bearer <token>)
  "refresh"      → Obtain a new access token when the current one expires
  "email_verify" → One-time link in the registration confirmation email

JWT PAYLOAD STRUCTURE:
  {
    "sub":  "<user_id as string>",   # Subject — who this token represents
    "type": "<token_type>",          # Guards against token type confusion
    "exp":  <unix timestamp>,        # When this token expires
    "jti":  "<uuid>",                # Unique token ID (for future revocation support)
  }

BCRYPT NOTE:
  bcrypt has a hard 72-byte input limit. We slice plain[:72] before hashing
  to ensure consistent behaviour — passwords longer than 72 bytes would
  otherwise silently produce identical hashes.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    Returns a string safe to store in the database.
    Never store or log the plain-text password.
    """
    return bcrypt.hashpw(plain.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Check whether a plain-text password matches a stored bcrypt hash.
    Use this during login — NEVER compare passwords with == directly.
    Returns True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))


# ---------------------------------------------------------------------------
# JWT creation (internal helper)
# ---------------------------------------------------------------------------

def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """
    Internal helper that builds and signs a JWT.
    Not intended to be called directly — use the public create_*_token functions.

    Args:
        subject:       The user's UUID as a string — stored in the "sub" claim.
        token_type:    One of "access", "refresh", "email_verify".
        expires_delta: How long until this token expires.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub":  subject,            # Who this token belongs to
        "type": token_type,         # Prevents cross-type token abuse
        "exp":  expire,             # Expiry — jose enforces this automatically on decode
        "jti":  str(uuid.uuid4()),  # Unique ID per token (enables future revocation)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ---------------------------------------------------------------------------
# Public token creation functions
# ---------------------------------------------------------------------------

def create_access_token(user_id: uuid.UUID) -> str:
    """
    Create a short-lived access token for API authentication.
    Sent to the client on login; client includes it in the
    Authorization: Bearer <token> header on every request.
    Expires after settings.ACCESS_TOKEN_EXPIRE_MINUTES (default: 30 min).
    """
    return _create_token(
        str(user_id),
        "access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: uuid.UUID) -> str:
    """
    Create a long-lived refresh token.
    Used to obtain a new access token when the current one expires,
    without requiring the user to log in again.
    Expires after settings.REFRESH_TOKEN_EXPIRE_DAYS (default: 7 days).

    NOTE: Refresh token rotation and revocation are not yet implemented.
    When added, store the jti in the DB and check it on use.
    """
    return _create_token(
        str(user_id),
        "refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_email_verification_token(user_id: uuid.UUID) -> str:
    """
    Create a 24-hour token embedded in the email verification link.
    The link sent to the user looks like:
        <FRONTEND_URL>/verify-email?token=<this token>
    The /verify-email endpoint decodes it and marks the account as verified.
    """
    return _create_token(str(user_id), "email_verify", timedelta(hours=24))


# ---------------------------------------------------------------------------
# Token decoding / validation
# ---------------------------------------------------------------------------

def decode_token(token: str, expected_type: str) -> Optional[str]:
    """
    Decode and validate a JWT.

    Returns the user_id string (the "sub" claim) if the token is:
      - Cryptographically valid (correct signature)
      - Not expired
      - Of the expected type (access / refresh / email_verify)

    Returns None in ALL failure cases (expired, wrong type, tampered, malformed).
    The caller should treat None as an authentication failure.

    Args:
        token:         The raw JWT string.
        expected_type: The "type" claim value we require (e.g. "access").
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Reject tokens of the wrong type even if the signature is valid
        if payload.get("type") != expected_type:
            return None
        return payload.get("sub")  # The user's UUID as a string
    except JWTError:
        # Covers: expired tokens, bad signatures, malformed JWTs
        return None