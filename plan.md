# Implementation Plan — OpenEnv + Gemini 3 Pro (Antigravity)

## Phase 0: Prerequisites & Security Baseline

- [ ] P0.1 — Dependency validation & supply chain security [TASK_01_environment_setup.md]
- [ ] P0.2 — Environment variable scaffold (no hardcoding) [TASK_01_environment_setup.md]
- [ ] P0.3 — Docker base image selection & pinning [TASK_05_docker_and_hf_deployment.md]
- [ ] P0.4 — Secret scanning pre-commit hook setup [planner.md]

## Phase 1: OpenEnv Spec Implementation

- [ ] P1.1 — Pydantic models: Observation, Action, Reward [TASK_02_openenv_spec_implementation.md]
- [ ] P1.2 — `reset()`, `step()`, `state()` methods [TASK_02_openenv_spec_implementation.md]
- [ ] P1.3 — `openenv.yaml` creation and validation [TASK_02_openenv_spec_implementation.md]
- [ ] P1.4 — `openenv validate` passing gate [TASK_02_openenv_spec_implementation.md]

## Phase 2: Real-World Task Design (3 Tasks)

- [ ] P2.1 — Domain selection (non-toy, non-game) [TASK_02_openenv_spec_implementation.md]
- [ ] P2.2 — Easy task + deterministic grader [TASK_03_tasks_and_graders.md]
- [ ] P2.3 — Medium task + partial-progress reward [TASK_03_tasks_and_graders.md]
- [ ] P2.4 — Hard task (frontier-model challenge) + grader [TASK_03_tasks_and_graders.md]
- [ ] P2.5 — Reward function: partial signals, anti-loop penalty [TASK_03_tasks_and_graders.md]

## Phase 3: Gemini 3 Pro Inference Script

- [ ] P3.1 — OpenAI-compatible client with Antigravity base URL [TASK_04_inference_script.md]
- [ ] P3.2 — `thinking_config` parameter: `thinking_level: dynamic` [planner.md]
- [ ] P3.3 — Strict START/STEP/END stdout log format [TASK_04_inference_script.md]
- [ ] P3.4 — Output validation hooks (hallucination guard) [planner.md]
- [ ] P3.5 — Runtime constraint: < 20 min / vCPU=2, 8GB RAM [TASK_00_overview.md]

## Phase 4: Security Implementation

- [ ] P4.1 — Package supply chain: hash-pinned requirements.txt [planner.md]
- [ ] P4.2 — API endpoint security: auth headers, CORS, CSP [planner.md]
- [ ] P4.3 — Rate limiting: SlowAPI token-bucket middleware [planner.md]
- [ ] P4.4 — Browser trap / bot detection layer [planner.md]
- [ ] P4.5 — Input sanitisation and prompt injection guards [planner.md]
- [ ] P4.6 — Container sandbox: read-only FS, egress allowlist [planner.md]

## Phase 5: Docker & HF Spaces Deployment

- [ ] P5.1 — Dockerfile with pinned base image [TASK_05_docker_and_hf_deployment.md]
- [ ] P5.2 — Non-root user execution [planner.md]
- [ ] P5.3 — Health check endpoint (`GET /health`) [planner.md]
- [ ] P5.4 — HF Space push and POST /reset validation [TASK_05_docker_and_hf_deployment.md]

## Phase 6: Pre-Submission Validation

- [ ] P6.1 — Run `pre-validate.sh` — all 3 steps must pass [TASK_06_pre_submission_validation.md]
- [ ] P6.2 — Full checklist verification [TASK_06_pre_submission_validation.md]
- [ ] P6.3 — Disqualification criterion audit [TASK_06_pre_submission_validation.md]
