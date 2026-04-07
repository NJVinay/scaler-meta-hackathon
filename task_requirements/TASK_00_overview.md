# TASK 00 — Project Overview & Task Map

**Source:** `task_requirements/The-Task.md`, [raun/openenv-course GitHub](https://github.com/raun/openenv-course/tree/main?tab=readme-ov-file)

## Goal
Build a complete, real-world **OpenEnv environment** that an AI agent can learn from through the standard `step / reset / state` API, and deploy it to Hugging Face Spaces.

## Evaluation Weights

| Criterion | Weight | Key Question |
|-----------|--------|-------------|
| Real-world utility | 30% | Is this a task humans actually do? |
| Task grader quality | 25% | Are the 3 graders accurate, fair, deterministic? |
| Environment design | 20% | Clean state, sensible spaces, good reward shaping? |
| Code quality / spec compliance | 15% | Does `openenv validate` pass? Does Docker build? |
| Creativity & novelty | 10% | Is this a domain not seen before in OpenEnv? |

## Task Execution Order

```
TASK 01 → Environment Setup & Prerequisites
TASK 02 → OpenEnv Spec Implementation
TASK 03 → 3 Tasks with Agent Graders
TASK 04 → inference.py Script
TASK 05 → Docker + HF Spaces Deployment
TASK 06 → Pre-Submission Validation
```

## Key Constraints Summary
- **File:** `inference.py` must be in project root
- **File:** `openenv.yaml` must be in project root
- **File:** `Dockerfile` must be in project root (or `./server/`)
- **Runtime:** inference < 20 min on vCPU=2, 8GB RAM
- **Logs:** Strict `START / STEP / END` stdout format required
- **Env vars:** `API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN` — never hardcoded

## Reference Links
- [OpenEnv GitHub](https://github.com/meta-pytorch/OpenEnv)
- [Course Repository](https://github.com/raun/openenv-course/tree/main)
- [Module 4 — Building Your Own Environment](https://github.com/raun/openenv-course/blob/main/module-4/README.md)
- [Module 3 — Deploying Environments](https://github.com/raun/openenv-course/blob/main/module-3/README.md)
- [HF Environment Hub](https://huggingface.co/collections/openenv/environment-hub)
