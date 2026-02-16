"""
Rate limiting middleware -- prevents abuse from any single client.

Uses a simple in-memory sliding window counter per client IP.
For production with multiple replicas, replace with Redis-backed limiter.

Configuration via environment:
  RATE_LIMIT_PER_MINUTE=60  (default: 60 requests per minute per IP)
"""

import logging
import os
import time
from collections import defaultdict

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

DEFAULT_RATE_LIMIT = 60


def _get_rate_limit() -> int:
    """Load rate limit from environment."""
    try:
        return int(os.environ.get("RATE_LIMIT_PER_MINUTE", DEFAULT_RATE_LIMIT))
    except ValueError:
        return DEFAULT_RATE_LIMIT


_request_log: dict[str, list[float]] = defaultdict(list)


def _cleanup_old_entries(client_id: str, window_seconds: float = 60.0) -> None:
    """Remove request timestamps older than the window."""
    cutoff = time.time() - window_seconds
    _request_log[client_id] = [
        ts for ts in _request_log[client_id] if ts > cutoff
    ]


async def check_rate_limit(request: Request) -> None:
    """
    Check if the client has exceeded the rate limit.

    Call this as a dependency in routes that need rate limiting.
    Raises HTTP 429 if the limit is exceeded.
    """
    client_ip = request.client.host if request.client else "unknown"
    limit = _get_rate_limit()

    _cleanup_old_entries(client_ip)

    if len(_request_log[client_ip]) >= limit:
        logger.warning(f"[RateLimit] Client {client_ip} exceeded {limit}/min")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded ({limit} requests per minute)",
            headers={"Retry-After": "60"},
        )

    _request_log[client_ip].append(time.time())
