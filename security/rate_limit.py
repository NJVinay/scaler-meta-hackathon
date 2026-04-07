"""
security/rate_limit.py — Token-bucket rate limiting via SlowAPI.

Limits:
  /reset → 10/min
  /step  → 30/min
  /state → 60/min
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI


def apply_rate_limiting(app: FastAPI) -> Limiter:
    """Attach SlowAPI rate limiter to the FastAPI application."""
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return limiter
