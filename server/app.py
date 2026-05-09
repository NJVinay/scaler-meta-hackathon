"""
server/app.py — FastAPI application for the Contract Clause Analyzer.

Uses openenv.core.env_server.create_fastapi_app() to wire up all standard
endpoints: /ws, /reset, /step, /state, /health, /docs.

The framework's HTTP /reset and /step are STATELESS (new env per request).
We add custom /api/reset, /api/step, /api/state endpoints that maintain
a persistent environment instance for the browser UI.
"""

import sys
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Body, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uuid

# Load variables from .env file
load_dotenv()

# Ensure project root is on the path so `models` and `server.*` resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server import create_fastapi_app
from server.environment import ContractEnvironment
from models import ContractAction, ContractObservation

# ── Create the base OpenEnv app (registers /ws, /reset, /step, etc.) ──
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


# ══════════════════════════════════════════════════════════════════════════════
# Stateful API for the browser UI
#
# OpenEnv's built-in /reset and /step are stateless (new env per request),
# which means /step on a fresh env crashes because there's no episode data.
# These /api/* endpoints maintain a single shared environment instance.
# ══════════════════════════════════════════════════════════════════════════════

_sessions: dict[str, ContractEnvironment] = {}


def _obs_to_dict(obs: ContractObservation) -> dict:
    """Serialize an observation into the wire format the frontend expects."""
    return {
        "observation": {
            "task_name": obs.task_name,
            "clause_text": obs.clause_text,
            "instructions": obs.instructions,
            "available_actions": obs.available_actions,
            "feedback": obs.feedback,
            "step_number": obs.step_number,
            "max_steps": obs.max_steps,
        },
        "reward": obs.reward,
        "done": obs.done,
    }


class UIResetRequest(BaseModel):
    task_name: Optional[str] = None
    seed: Optional[int] = None
    episode_id: Optional[str] = None
    session_id: Optional[str] = None


class UIStepRequest(BaseModel):
    action: dict
    session_id: str


@app.post("/api/reset", tags=["UI"])
async def ui_reset(req: UIResetRequest = Body(default_factory=UIResetRequest)):
    """Reset the shared environment and return the initial observation."""
    session_id = req.session_id or str(uuid.uuid4())
    env = ContractEnvironment()
    _sessions[session_id] = env
    
    obs = env.reset(
        seed=req.seed,
        episode_id=req.episode_id,
        task_name=req.task_name,
    )
    
    res = _obs_to_dict(obs)
    res["session_id"] = session_id
    return res


@app.post("/api/step", tags=["UI"])
async def ui_step(req: UIStepRequest):
    """Execute a step on the shared environment and return the result."""
    env = _sessions.get(req.session_id)
    if not env:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
        
    action = ContractAction(**req.action)
    obs, reward, done = env.step(action)
    # obs already has reward/done set, but use the returned values for clarity
    obs.reward = reward
    obs.done = done
    
    res = _obs_to_dict(obs)
    res["session_id"] = req.session_id
    return res


@app.get("/api/state", tags=["UI"])
async def ui_state(session_id: str):
    """Return the current state of the shared environment."""
    env = _sessions.get(session_id)
    if not env:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
        
    state = env.state
    return state.model_dump()


# ══════════════════════════════════════════════════════════════════════════════
# Static files + utility routes
# ══════════════════════════════════════════════════════════════════════════════

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@app.get("/")
async def root():
    index_path = os.path.join(_root, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "Contract Clause Analyzer is running!",
            "endpoints": ["/api/reset", "/api/step", "/api/state", "/health", "/docs"]}


@app.get("/app.js")
async def serve_js():
    js_path = os.path.join(_root, "app.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    return JSONResponse({"error": "app.js not found"}, status_code=404)


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
