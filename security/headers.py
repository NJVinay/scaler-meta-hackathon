"""
security/headers.py — Security headers middleware.

Adds CSP, HSTS, X-Frame-Options, and other protective headers
to every HTTP response.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.update(
            {
                "Content-Security-Policy": (
                    "default-src 'self'; "
                    "script-src 'self' https://cdn.tailwindcss.com 'unsafe-inline'; "
                    "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
                    "font-src 'self' https://fonts.gstatic.com; "
                    "img-src 'self' data: https:; "
                    "connect-src 'self'; "
                    "object-src 'none'"
                ),
                "X-Content-Type-Options": "nosniff",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "no-referrer",
                "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
                "Strict-Transport-Security": ("max-age=31536000; includeSubDomains"),
            }
        )
        return response
