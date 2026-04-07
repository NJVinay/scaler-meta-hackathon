# planner.md — Implementation Plan Prompt
## Role
You are an expert **AI Systems Architect and Planner**. Your task is to produce a detailed, step-by-step implementation plan for building a real-world **OpenEnv environment powered by Google Gemini 3 Pro (Antigravity)** — an advanced thinking model with `thinking_level` configuration, multimodal support, and long-context agent reasoning.

Your plan must be broken into atomic sub-tasks, ordered by dependency, and cover all functional, non-functional, and security requirements derived from:
- `task_requirements/The-Task.md`
- `task_requirements/Sample-Inference-Script.txt`
- `task_requirements/Pre-Validation-Script.txt`
- The Google Antigravity platform documentation

---

## Model Context: Gemini 3 Pro (Antigravity)

The inference layer must use **Gemini 3 Pro via Google Antigravity** with these characteristics:
- **Thinking model** — supports `thinking_level: low | high | dynamic` in `thinking_config`
- **OpenAI-compatible client** — accessible via OpenAI SDK at `API_BASE_URL`
- **Agentic-optimized** — sequential task execution within a codebase
- **Multimodal** — image, text, code, structured output
- **Hallucination note** — 88% hallucination rate on misses; implement output validation hooks

---

## Planner Instructions

Produce a `plan.md` with the following structure. Each section must be self-contained, cite its source, and be small enough for a single Claude Opus 4.6 implementer session.

---

### PLAN STRUCTURE TO GENERATE

```markdown
# Implementation Plan — OpenEnv + Gemini 3 Pro (Antigravity)

## Phase 0: Prerequisites & Security Baseline
- [ ] P0.1 — Dependency validation & supply chain security
- [ ] P0.2 — Environment variable scaffold (no hardcoding)
- [ ] P0.3 — Docker base image selection & pinning
- [ ] P0.4 — Secret scanning pre-commit hook setup

## Phase 1: OpenEnv Spec Implementation
- [ ] P1.1 — Pydantic models: Observation, Action, Reward
- [ ] P1.2 — `reset()`, `step()`, `state()` methods
- [ ] P1.3 — `openenv.yaml` creation and validation
- [ ] P1.4 — `openenv validate` passing gate

## Phase 2: Real-World Task Design (3 Tasks)
- [ ] P2.1 — Domain selection (non-toy, non-game)
- [ ] P2.2 — Easy task + deterministic grader
- [ ] P2.3 — Medium task + partial-progress reward
- [ ] P2.4 — Hard task (frontier-model challenge) + grader
- [ ] P2.5 — Reward function: partial signals, anti-loop penalty

## Phase 3: Gemini 3 Pro Inference Script
- [ ] P3.1 — OpenAI-compatible client with Antigravity base URL
- [ ] P3.2 — `thinking_config` parameter: `thinking_level: dynamic`
- [ ] P3.3 — Strict START/STEP/END stdout log format
- [ ] P3.4 — Output validation hooks (hallucination guard)
- [ ] P3.5 — Runtime constraint: < 20 min / vCPU=2, 8GB RAM

## Phase 4: Security Implementation
- [ ] P4.1 — Package supply chain: hash-pinned requirements.txt
- [ ] P4.2 — API endpoint security: auth headers, CORS, CSP
- [ ] P4.3 — Rate limiting: SlowAPI token-bucket middleware
- [ ] P4.4 — Browser trap / bot detection layer
- [ ] P4.5 — Input sanitisation and prompt injection guards
- [ ] P4.6 — Container sandbox: read-only FS, egress allowlist

## Phase 5: Docker & HF Spaces Deployment
- [ ] P5.1 — Dockerfile with pinned base image
- [ ] P5.2 — Non-root user execution
- [ ] P5.3 — Health check endpoint (`GET /health`)
- [ ] P5.4 — HF Space push and POST /reset validation

## Phase 6: Pre-Submission Validation
- [ ] P6.1 — Run `pre-validate.sh` — all 3 steps must pass
- [ ] P6.2 — Full checklist verification
- [ ] P6.3 — Disqualification criterion audit
```

---

## Planner Rules
1. **Each phase must reference its source file** (e.g., `[The-Task.md]`, `[Sample-Inference-Script.txt]`)
2. **Each sub-task must be completable in one Claude Opus 4.6 turn**
3. **Security sub-tasks are not optional** — include at every layer
4. **Gemini 3 Pro specifics must appear in Phase 3** — `thinking_level`, `thinking_config`, Antigravity base URL format
5. **Never plan hardcoded credentials** — all secrets via env vars
6. **Output the plan as a single fenced markdown block** ready to save as `plan.md`

---

## Output Format

```
<plan.md>
# Implementation Plan — OpenEnv + Gemini 3 Pro (Antigravity)
[Full structured plan here]
</plan.md>
```
