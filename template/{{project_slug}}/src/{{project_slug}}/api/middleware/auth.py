"""
API key authentication middleware.

Simple bearer token validation. Extensible to OAuth/JWT for enterprise.

Usage:
    Set API_KEY in .env:  API_KEY=your-secret-key
    Clients pass:         Authorization: Bearer your-secret-key

    To disable auth (dev mode): leave API_KEY unset or empty.

Security:
    - In production (ENV=production), API_KEY is REQUIRED. The app will
      log a critical warning on startup if it's missing.
    - In development, auth is optional for convenience.
"""

import logging
import os

from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=False)

_startup_warning_logged = False


def get_api_key() -> str | None:
    """Load API key from environment. Returns None if auth is disabled."""
    return os.environ.get("API_KEY", "").strip() or None


def _is_production() -> bool:
    """Check if running in production mode."""
    env = os.environ.get("ENV", os.environ.get("ENVIRONMENT", "development"))
    return env.lower() in ("production", "prod", "staging")


def check_production_auth() -> None:
    """
    Call on startup to verify auth is configured in production.

    Logs a CRITICAL warning if API_KEY is not set in production mode.
    Does not block startup (to avoid breaking deploys) but makes the risk visible.
    """
    global _startup_warning_logged
    if _is_production() and get_api_key() is None and not _startup_warning_logged:
        logger.critical(
            "[Auth] SECURITY WARNING: API_KEY is not set in production mode. "
            "All endpoints are unauthenticated. Set API_KEY in .env or environment."
        )
        _startup_warning_logged = True


async def verify_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(security_scheme),
) -> str | None:
    """
    Verify the API key from the Authorization header.

    If API_KEY is not set in the environment, auth is disabled (dev mode).
    If API_KEY is set, requests must include: Authorization: Bearer <key>
    """
    expected_key = get_api_key()

    if expected_key is None:
        return None

    if credentials is None:
        logger.warning(f"[Auth] Missing credentials from {request.client.host}")
        raise HTTPException(status_code=401, detail="Missing API key")

    if credentials.credentials != expected_key:
        logger.warning(f"[Auth] Invalid API key from {request.client.host}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    return credentials.credentials
