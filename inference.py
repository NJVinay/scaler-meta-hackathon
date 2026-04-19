"""
inference.py — Root-level inference script for OpenEnv Contract Clause Analyzer.

MANDATORY FILE — must be in project root.
Runs an LLM agent (Gemini 3 Pro via OpenAI-compatible SDK) against all 3 tasks
and emits structured stdout logs in strict START/STEP/END format.

Usage:
    python inference.py

Required environment variables:
    API_BASE_URL  — LLM API endpoint
    MODEL_NAME    — Model identifier
    HF_TOKEN      — API key (or API_KEY)
"""

import os
import sys
import time
import traceback
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Strict Hackathon Static Check Requirements:
API_BASE_URL = os.getenv("API_BASE_URL", "<your-active-endpoint>")
MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model>")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional - if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gemini_client import build_client, call_gemini
from hallucination_guard import extract_text_answer
from log_utils import log_start, log_step, log_end
from timeout_guard import MAX_RUNTIME_SECONDS

# Import environment directly (no server needed for local inference)
from server.environment import ContractEnvironment
from models import ContractAction


# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────
ENV_NAME = "contract-clause-analyzer"
TASK_NAMES = ["clause-classify", "risk-assess", "clause-rewrite"]
MAX_RETRIES = 2  # Retries per LLM call on failure


def run_task(env: ContractEnvironment, client, model_name: str, task_name: str) -> None:
    """Run a single task episode with the LLM agent.

    Emits START, STEP (per step), and END lines to stdout.
    END is always emitted, even on exception.
    """
    rewards = []
    steps = 0
    success = False
    score = 0.0

    log_start(task=task_name, env=ENV_NAME, model=model_name)

    try:
        # ── Reset ──
        obs = env.reset(task_name=task_name, seed=42)
        done = obs.done

        system_prompt = (
            "You are a legal contract analysis expert. "
            "Follow the instructions precisely. "
            "Respond concisely and in the exact format requested. "
            "Do not add explanations unless explicitly asked."
        )

        while not done:
            steps += 1

            # Build the prompt from the observation
            prompt = _build_prompt(obs)

            # Call the LLM with retries
            error_msg = None
            raw_response = ""
            for attempt in range(MAX_RETRIES + 1):
                try:
                    raw_response = call_gemini(
                        client=client,
                        prompt=prompt,
                        system=system_prompt,
                        thinking_level="dynamic",
                        max_tokens=2048,
                    )
                    break
                except Exception as e:
                    if attempt < MAX_RETRIES:
                        time.sleep(2**attempt)  # Exponential backoff
                        continue
                    error_msg = str(e)[:200]
                    raw_response = ""

            # Clean up the response
            answer = extract_text_answer(raw_response) if raw_response else ""

            # Create action
            action_type = _infer_action_type(task_name)
            action = ContractAction(
                action_type=action_type,
                payload=answer,
                reasoning="",
            )

            # Step the environment
            try:
                obs, reward, done = env.step(action)
                reward = reward if reward is not None else 0.0
                rewards.append(reward)
            except Exception as e:
                error_msg = str(e)[:200]
                reward = 0.0
                done = True
                rewards.append(reward)

            log_step(
                step=steps,
                action=answer[:200] if answer else "(empty)",
                reward=reward,
                done=done,
                error=error_msg,
            )

            # Safety: prevent infinite loops
            if steps >= 10:
                done = True

        # Calculate final score
        score = rewards[-1] if rewards else 0.0
        success = score > 0.0

    except Exception:
        error_trace = traceback.format_exc()
        print(f"# ERROR in task {task_name}: {error_trace}", file=sys.stderr)
        # Ensure we still have valid data for END line
        if not rewards:
            rewards = [0.0]

    finally:
        # END line is ALWAYS emitted
        log_end(
            success=success,
            steps=steps,
            score=score,
            rewards=rewards,
        )


def _build_prompt(obs) -> str:
    """Build an LLM prompt from a ContractObservation."""
    parts = []

    if obs.instructions:
        parts.append(obs.instructions)

    if obs.clause_text:
        parts.append(f"\nCLAUSE:\n{obs.clause_text}")

    if obs.feedback:
        parts.append(f"\nPREVIOUS FEEDBACK:\n{obs.feedback}")

    if obs.step_number > 0:
        parts.append(f"\n(Step {obs.step_number}/{obs.max_steps})")

    return "\n".join(parts)


def _infer_action_type(task_name: str) -> str:
    """Map task name to its expected action type."""
    return {
        "clause-classify": "classify",
        "risk-assess": "assess_risk",
        "clause-rewrite": "rewrite",
    }.get(task_name, "classify")


# ──────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────
def main():
    start_time = time.time()
    model_name = os.getenv("MODEL_NAME", "gemini-3-pro")

    # Build LLM client
    try:
        client = build_client()
    except EnvironmentError as e:
        print(f"# FATAL: {e}", file=sys.stderr)
        # Emit END lines for all tasks to satisfy format requirements
        for task in TASK_NAMES:
            log_start(task=task, env=ENV_NAME, model=model_name)
            log_end(success=False, steps=0, score=0.0, rewards=[0.0])
        sys.exit(1)

    # Create environment instance
    env = ContractEnvironment()

    # Run all 3 tasks
    for task_name in TASK_NAMES:
        elapsed = time.time() - start_time
        if elapsed > MAX_RUNTIME_SECONDS:
            print(
                f"# WARNING: Approaching timeout ({elapsed:.0f}s elapsed). "
                f"Skipping remaining tasks.",
                file=sys.stderr,
            )
            log_start(task=task_name, env=ENV_NAME, model=model_name)
            log_end(success=False, steps=0, score=0.0, rewards=[0.0])
            continue

        run_task(env, client, model_name, task_name)

    total_time = time.time() - start_time
    print(f"# Total inference time: {total_time:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
