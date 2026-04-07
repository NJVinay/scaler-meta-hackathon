# skills.md — Reusable Implementation Patterns
> Used by Claude Opus 4.6 implementer. Reference by section name in `implementer.md`.

---

## Section: OpenEnv Typed Models

```python
# openenv_models.py
from pydantic import BaseModel, Field
from typing import Optional, Any

class Observation(BaseModel):
    content: str = Field(..., description="Human-readable observation text")
    metadata: dict[str, Any] = Field(default_factory=dict)
    step_number: int = Field(default=0, ge=0)
    context: Optional[str] = None

class Action(BaseModel):
    action_type: str = Field(..., description="Type of action: classify|edit|flag|skip")
    payload: str = Field(..., max_length=4096)
    parameters: dict[str, Any] = Field(default_factory=dict)

class Reward(BaseModel):
    value: float = Field(..., ge=0.0, le=1.0)
    reason: str
    partial_signals: list[float] = Field(default_factory=list)
    penalties: list[str] = Field(default_factory=list)

class EpisodeInfo(BaseModel):
    task_name: str
    step: int
    max_steps: int
    last_error: Optional[str] = None
```

---

## Section: OpenEnv Base Environment

```python
# base_env.py
import asyncio
from abc import ABC, abstractmethod
from openenv_models import Observation, Action, Reward, EpisodeInfo

class BaseOpenEnv(ABC):
    def __init__(self, task_name: str, max_steps: int = 8):
        self.task_name = task_name
        self.max_steps = max_steps
        self._step_count = 0
        self._done = False
        self._last_error: str | None = None

    @abstractmethod
    async def reset(self) -> Observation:
        """Return clean initial observation. Must be reproducible."""
        ...

    @abstractmethod
    async def step(self, action: Action) -> tuple[Observation, float, bool, dict]:
        """Return (observation, reward, done, info)."""
        ...

    async def state(self) -> dict:
        return {
            "task": self.task_name,
            "step": self._step_count,
            "done": self._done,
            "last_error": self._last_error,
        }

    async def close(self):
        """Cleanup resources."""
        pass
```

---

## Section: Log Formatters

```python
# log_utils.py — Mandatory stdout format from Sample-Inference-Script.txt
from typing import Optional

def log_start(task: str, env: str, model: str) -> None:
    print(f"START task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"STEP step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"END success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)
```

---

## Section: Gemini 3 Pro (Antigravity) Client

```python
# gemini_client.py
import os
from openai import OpenAI

def build_client() -> OpenAI:
    api_key = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
    base_url = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
    if not api_key:
        raise EnvironmentError("HF_TOKEN or API_KEY must be set")
    if not base_url:
        raise EnvironmentError("API_BASE_URL must be set")
    return OpenAI(base_url=base_url, api_key=api_key)

def call_gemini(
    client: OpenAI,
    prompt: str,
    system: str = "",
    thinking_level: str = "dynamic",   # low | high | dynamic
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    model = os.getenv("MODEL_NAME", "gemini-3-pro")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        extra_body={"thinking_config": {"thinking_level": thinking_level}},
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
    )
    return (resp.choices[0].message.content or "").strip()
```

---

## Section: Hallucination Guard

```python
# hallucination_guard.py
import json
from pydantic import BaseModel

def validate_structured_output(raw: str, schema: type[BaseModel]) -> tuple[bool, BaseModel | None, str]:
    """
    Validates Gemini 3 Pro output against a Pydantic schema.
    Returns (is_valid, parsed_obj, error_msg).
    Gemini 3 Pro hallucinates on ~88% of misses — always validate.
    """
    raw = raw.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])
    try:
        obj = schema.model_validate_json(raw)
        return True, obj, ""
    except Exception as e:
        # Try extracting JSON from mixed text
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            obj = schema.model_validate_json(raw[start:end])
            return True, obj, ""
        except Exception:
            return False, None, str(e)
```

---

## Section: Rate Limiting Middleware

```python
# security/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

def apply_rate_limiting(app: FastAPI) -> Limiter:
    """
    Token-bucket rate limiting via SlowAPI.
    Limits: /reset → 10/min, /step → 30/min, /state → 60/min
    """
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return limiter
```

---

## Section: Security Headers Middleware

```python
# security/headers.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.update({
            "Content-Security-Policy": "default-src 'self'; script-src 'none'; object-src 'none'",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "no-referrer",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        })
        return response
```

---

## Section: Prompt Injection Guard

```python
# security/sanitise.py
from fastapi import HTTPException

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "jailbreak",
    "\n\nhuman:",
    "<|im_start|>",
    "[[inject]]",
    "<!-- inject -->",
    "forget your instructions",
    "act as if",
    "you are now",
    "dan mode",
]

MAX_INPUT_LENGTH = 4096

def sanitise_input(text: str) -> str:
    """
    Reject prompt injection attempts and enforce length cap.
    Must be applied to ALL user-supplied text before LLM calls.
    """
    if len(text) > MAX_INPUT_LENGTH:
        raise HTTPException(status_code=400, detail=f"Input exceeds {MAX_INPUT_LENGTH} character limit")
    lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            raise HTTPException(status_code=400, detail="Invalid input detected")
    return text.strip()
```

---

## Section: Browser Trap / Bot Detection

```python
# security/bot_guard.py
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
            return await call_next(request)  # Serve decoy response

        return await call_next(request)

def add_honeypot_routes(app: FastAPI):
    """Register honeypot endpoints that look legitimate but flag crawlers."""
    @app.get("/.well-known/trap")
    async def honeypot_trap():
        return {"status": "ok", "message": "Service running"}

    @app.get("/admin")
    async def honeypot_admin():
        return {"status": "ok", "login": "required"}
```

---

## Section: Secure Dockerfile

```dockerfile
# Dockerfile
# Pin base image by digest for supply chain security
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup --no-create-home appuser

WORKDIR /app

# Install dependencies first (layer caching + security audit)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root
USER appuser

# Expose HF Spaces port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen(\'http://localhost:7860/health\')" || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1", "--timeout-keep-alive", "30"]
```

---

## Section: Supply Chain Security

```bash
#!/bin/bash
# security_check.sh — Run before every commit

echo "=== Dependency Security Audit ==="
pip install safety pip-audit
safety check -r requirements.txt
pip-audit -r requirements.txt

echo "=== Secret Scanning ==="
pip install detect-secrets
detect-secrets scan --baseline .secrets.baseline

echo "=== Dockerfile Lint ==="
docker run --rm -i hadolint/hadolint < Dockerfile

echo "=== SBOM Generation ==="
pip install cyclonedx-bom
cyclonedx-py environment -o sbom.json

echo "All security checks complete."
```

```ini
# requirements.in — human-readable, no hashes
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
openai>=1.30.0
pydantic>=2.7.0
slowapi>=0.1.9
httpx>=0.27.0
openenv-core>=0.1.0

# Generate pinned requirements.txt with hashes:
# pip-compile --generate-hashes requirements.in -o requirements.txt
```

---

## Section: Runtime Timeout Guard

```python
# timeout_guard.py
import asyncio
import signal

MAX_RUNTIME_SECONDS = 1140  # 19 minutes (< 20 min limit)

class TimeoutError(Exception):
    pass

async def run_with_timeout(coro, timeout: int = MAX_RUNTIME_SECONDS):
    """Wraps any coroutine with a hard timeout. Prevents > 20 min runtime."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Execution exceeded {timeout}s limit. Terminating.")
```

---

## Section: Grader Template

```python
# grader_template.py
from difflib import SequenceMatcher

def normalized_similarity(a: str, b: str) -> float:
    """Base similarity metric for text-based graders. Returns [0.0, 1.0]."""
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def grade_with_partial_credit(
    agent_output: str,
    required_elements: list[str],
    weights: list[float],
    loop_count: int = 0,
    destructive_actions: int = 0,
) -> float:
    """
    Generic partial-credit grader.
    - required_elements: list of strings that must appear in output
    - weights: per-element weight (must sum to 1.0)
    - loop_count: penalty for repetitive actions
    - destructive_actions: penalty for harmful actions
    """
    assert abs(sum(weights) - 1.0) < 1e-6, "Weights must sum to 1.0"
    score = 0.0
    lower_output = agent_output.lower()
    for element, weight in zip(required_elements, weights):
        if element.lower() in lower_output:
            score += weight
    # Apply penalties
    score -= 0.05 * loop_count
    score -= 0.15 * destructive_actions
    return max(0.0, min(1.0, score))  # Clamp to [0.0, 1.0]
```

---

## Section: openenv.yaml Template

```yaml
# openenv.yaml — place in project root
name: your-env-name
version: "1.0.0"
description: "Real-world [domain] environment for agent evaluation"
author: "your-name"
tags:
  - openenv
  - real-world
  - [domain]
tasks:
  - name: easy-task
    description: "Simple single-step classification"
    difficulty: easy
    max_steps: 4
  - name: medium-task
    description: "Multi-step action sequence with partial credit"
    difficulty: medium
    max_steps: 8
  - name: hard-task
    description: "Complex reasoning task — challenges frontier models"
    difficulty: hard
    max_steps: 12
endpoints:
  reset: POST /reset
  step: POST /step
  state: GET /state
  health: GET /health
```
