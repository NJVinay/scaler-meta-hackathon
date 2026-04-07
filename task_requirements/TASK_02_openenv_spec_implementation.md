# TASK 02 — OpenEnv Spec Implementation

**Source:** `task_requirements/The-Task.md`, [Module 4 — Building Your Own Environment](https://github.com/raun/openenv-course/blob/main/module-4/README.md)

## Objective
Implement the full OpenEnv interface with typed Pydantic models and a compliant `openenv.yaml`.

## Steps

1. **Define typed Pydantic models**
   - `Observation` model — represents what the agent sees each step
   - `Action` model — represents what the agent can do
   - `Reward` model — wraps the scalar reward signal

2. **Implement the 3 required methods**
   ```python
   async def reset() -> Observation       # Returns clean initial state
   async def step(action: Action) -> (Observation, float, bool, dict)
   async def state() -> dict              # Returns current internal state
   ```

3. **Create `openenv.yaml`** in the project root:
   ```yaml
   name: your-env-name
   version: "1.0.0"
   description: "Your environment description"
   tasks:
     - name: easy-task
     - name: medium-task
     - name: hard-task
   ```

4. **Verify with openenv CLI**
   ```bash
   openenv validate
   ```

## Rules & Constraints
- `step()` must return `(observation, reward, done, info)` — exactly this signature.
- `reset()` must return a **clean, reproducible** initial state every time.
- All models must be typed — no raw `dict` returns.
- The environment must simulate a **real-world task** (e.g., email triage, code review, data cleaning) — not games or toys.

## Validation Checklist
- [ ] `openenv validate` passes with zero errors
- [ ] All three methods are implemented and callable
- [ ] `openenv.yaml` is present in the project root
