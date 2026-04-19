"""
server/app.py — FastAPI application for the Contract Clause Analyzer.

Uses openenv.core.env_server.create_fastapi_app() to wire up all standard
endpoints: /ws, /reset, /step, /state, /health, /docs.

Additional security middleware is layered on top.
"""

import sys
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Ensure project root is on the path so `models` and `server.*` resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server import create_fastapi_app
from server.environment import ContractEnvironment
from models import ContractAction, ContractObservation

# ── Create the base OpenEnv app ──
app = create_fastapi_app(
    env=ContractEnvironment,
    action_cls=ContractAction,
    observation_cls=ContractObservation,
)

# ── Layer security middleware ──
try:
    from security.headers import SecurityHeadersMiddleware
    from security.bot_guard import BotGuardMiddleware, add_honeypot_routes
    from security.rate_limit import apply_rate_limiting

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(BotGuardMiddleware)
    apply_rate_limiting(app)
    add_honeypot_routes(app)
except ImportError:
    # Security modules optional during development
    pass


# ── Root route (For HF Spaces UI) ──
@app.get("/")
async def root():
    return {
        "message": "Contract Clause Analyzer is running!",
        "endpoints": ["/reset", "/step", "/state", "/health", "/docs"],
    }


# ── Suppress UI 404 noise in HF Logs ──
@app.get("/web")
async def web_ui_redirect():
    return {"message": "API-only environment. Use /docs for documentation."}


@app.get("/favicon.ico")
async def favicon():
    return None


# ── Health check (in case create_fastapi_app doesn't include one) ──
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": "contract-clause-analyzer"}


def main():
    import uvicorn

    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()
