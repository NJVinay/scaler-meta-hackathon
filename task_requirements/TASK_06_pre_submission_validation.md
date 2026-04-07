# TASK 06 — Pre-Submission Validation

**Source:** `task_requirements/Pre-Validation-Script.txt`, `task_requirements/The-Task.md`

## Objective
Run the official pre-submission validation script and resolve all failures **before** submitting.

## Steps

Run the validator script with your HF Space URL:
```bash
bash pre-validate.sh https://your-space.hf.space ./
```

The script performs **3 automated checks** in sequence:

### Step 1 — Ping HF Space
```bash
curl -X POST https://your-space.hf.space/reset --max-time 30
```
- ✅ HTTP 200 → Pass
- ❌ HTTP 000 (unreachable) or non-200 → **Stop — fix before continuing**

### Step 2 — Docker Build
```bash
docker build ./   # or ./server/ if Dockerfile is there
```
- ✅ Build completes within 600 seconds → Pass
- ❌ Build fails or times out → **Stop**

### Step 3 — openenv validate
```bash
cd <repo> && openenv validate
```
- ✅ All checks pass → Pass
- ❌ Any failure → **Stop**

## Full Pre-Submission Checklist (from The-Task.md)

| Check | Requirement |
|-------|------------|
| HF Space deploys | `POST /reset` returns 200 |
| OpenEnv spec compliance | `openenv.yaml`, typed models, all 3 endpoints |
| Dockerfile builds | `docker build` succeeds |
| Baseline reproduces | `inference.py` runs without error, produces scores |
| 3 tasks with graders | All grader scores in `[0.0, 1.0]` |

## Disqualification Criteria
- Environment does not deploy or respond
- Plagiarized or trivially modified existing environments
- Graders that always return the same score
- No `inference.py` baseline script

## Evaluation Phases (Post-Submission)
1. **Phase 1 — Automated Validation** (pass/fail gate)
2. **Phase 2 — Agentic Evaluation** (LLM agent scored against all envs)
3. **Phase 3 — Human Review** by Meta and Hugging Face engineers
