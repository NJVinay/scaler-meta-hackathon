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
        response.headers.update({
            "Content-Security-Policy": (
                "default-src 'self'; script-src 'none'; object-src 'none'"
            ),
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "no-referrer",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Strict-Transport-Security": (
                "max-age=31536000; includeSubDomains"
            ),
        })
        return response
