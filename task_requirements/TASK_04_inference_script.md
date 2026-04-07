# TASK 04 — Write the Inference Script (`inference.py`)

**Source:** `task_requirements/Sample-Inference-Script.txt`, `task_requirements/The-Task.md`

## Objective
Create `inference.py` in the **project root** that runs an LLM agent against all 3 tasks and emits structured stdout logs.

## Steps

1. **Read credentials from environment variables only**
   ```python
   import os
   API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
   API_BASE_URL = os.getenv("API_BASE_URL", "your-active-endpoint")
   MODEL_NAME   = os.getenv("MODEL_NAME", "your-active-model")
   ```

2. **Use OpenAI client for all LLM calls**
   ```python
   from openai import OpenAI
   client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
   ```

3. **Emit exactly 3 log line types to stdout — in strict order:**

   ```
   START task=<taskname> env=<benchmark> model=<modelname>
   STEP step=<n> action=<actionstr> reward=<0.00> done=<true|false> error=<msg|null>
   END success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
   ```
   > ⚠️ **Mandatory format.** Any deviation in field names, ordering, or formatting results in incorrect evaluation scoring.

4. **Format rules (from Sample-Inference-Script.txt)**
   - One `START` line per episode
   - One `STEP` line immediately after each `env.step()` returns
   - One `END` line after `env.close()` — always emitted, even on exception
   - `reward` and `rewards` formatted to **2 decimal places**
   - `done` and `success` are lowercase: `true` or `false`
   - `error` is the raw error string or `null`
   - All fields on a **single line** — no newlines within a line

5. **Runtime constraint**
   - Total inference script runtime must be **< 20 minutes**
   - Target machine: vCPU=2, Memory=8GB

## Disqualification Risk
- Missing `inference.py` in project root → **disqualified**
- Script errors without completing → **disqualified**
- Not using OpenAI client → **disqualified**
