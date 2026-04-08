"""
log_utils.py — Mandatory stdout log format from Sample-Inference-Script.txt.

Strict format:
  START task=<taskname> env=<benchmark> model=<modelname>
  STEP step=<n> action=<actionstr> reward=<0.00> done=<true|false> error=<msg|null>
  END success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

from typing import Optional


def log_start(task: str, env: str, model: str) -> None:
    """Emit START line. One per episode."""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(
    step: int,
    action: str,
    reward: float,
    done: bool,
    error: Optional[str] = None,
) -> None:
    """Emit STEP line. One per env.step() call."""
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Sanitize action to single line
    action_clean = action.replace("\n", " ").replace("\r", "")[:200]
    print(
        f"[STEP] step={step} action={action_clean} "
        f"reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(
    success: bool,
    steps: int,
    score: float,
    rewards: list[float],
) -> None:
    """Emit END line. One per episode, always emitted even on exception."""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.2f} rewards={rewards_str}",
        flush=True,
    )
