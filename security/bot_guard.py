"""
security/bot_guard.py — Browser trap / bot detection layer.

Honeypot endpoints that flag and temporarily block IPs that probe
common attack surfaces (/.env, /admin, /wp-admin, etc.).
"""

import time
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# In-memory store — replace with Redis in production
_FLAGGED_IPS: dict[str, float] = {}
_FLAG_DURATION_SECONDS = 3600  # Block for 1 hour

HONEYPOT_PATHS = [
    "/.well-known/trap",
    "/admin",
    "/wp-admin",
    "/phpmyadmin",
    "/.env",
    "/config.php",
]


class BotGuardMiddleware(BaseHTTPMiddleware):
    """Block IPs that have been flagged by honeypot endpoints."""

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # If IP is flagged and block has not expired
        if ip in _FLAGGED_IPS:
            if time.time() - _FLAGGED_IPS[ip] < _FLAG_DURATION_SECONDS:
                raise HTTPException(status_code=403, detail="Forbidden")
            else:
                del _FLAGGED_IPS[ip]

        # Flag any IP hitting honeypot paths
        if path in HONEYPOT_PATHS:
            _FLAGGED_IPS[ip] = time.time()
            # Serve a decoy response (don't reveal the trap)
            return await call_next(request)

        return await call_next(request)


def add_honeypot_routes(app: FastAPI):
    """Register honeypot endpoints that look legitimate but flag crawlers."""

    @app.get("/.well-known/trap")
    async def honeypot_trap():
        return {"status": "ok", "message": "Service running"}

    @app.get("/admin")
    async def honeypot_admin():
        return {"status": "ok", "login": "required"}
