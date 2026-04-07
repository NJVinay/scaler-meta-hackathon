# TASK 01 — Environment Setup & Prerequisites

**Source:** `task_requirements/The-Task.md`, [GitHub README](https://github.com/raun/openenv-course/tree/main?tab=readme-ov-file)

## Objective
Install all required dependencies and configure the local development environment before building the OpenEnv submission.

## Steps

1. **Install Python dependencies**
   ```bash
   pip install openenv-core openai pydantic
   ```

2. **Clone the OpenEnv core repository** (for typed environment clients)
   ```bash
   git clone https://github.com/meta-pytorch/OpenEnv.git
   ```

3. **Set required environment variables**
   ```bash
   export API_BASE_URL="your-active-endpoint"
   export MODEL_NAME="your-active-model"
   export HF_TOKEN="your-huggingface-api-key"
   ```
   > **Mandatory:** All three variables (`API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN`) must be defined before running any inference or validation.

4. **Verify openenv CLI is available**
   ```bash
   openenv --help
   ```

## Prerequisites (from GitHub course)
- Basic Python knowledge
- Familiarity with Hugging Face ecosystem
- Docker installed ([docs.docker.com/get-docker](https://docs.docker.com/get-docker/))
- No RL experience required

## Safety Rules
- Never hardcode `HF_TOKEN` in source files — always read from environment variables.
- Ensure Docker daemon is running before any build steps.
