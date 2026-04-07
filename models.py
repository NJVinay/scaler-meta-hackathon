"""
models.py — Typed Pydantic models for the Contract Clause Analyzer OpenEnv.

Inherits from openenv.core.env_server base classes:
  - Action:      has no predefined fields (extend freely)
  - Observation: has `done: bool` and `reward: Optional[float]`
  - State:       has `episode_id: Optional[str]` and `step_count: int`
"""

from typing import List, Any
from openenv.core.env_server import Action, Observation, State


# ──────────────────────────────────────────────────────────────
# Actions the agent can take
# ──────────────────────────────────────────────────────────────
class ContractAction(Action):
    """Agent submits an action against the current contract clause(s)."""

    action_type: str  # "classify" | "assess_risk" | "rewrite"
    payload: str  # The agent's answer / rewrite text
    reasoning: str = ""  # Optional chain-of-thought justification


# ──────────────────────────────────────────────────────────────
# Observations the agent receives
# ──────────────────────────────────────────────────────────────
class ContractObservation(Observation):
    """What the agent sees each step. `done` and `reward` inherited."""

    task_name: str = ""
    clause_text: str = ""  # The clause(s) to analyse
    instructions: str = ""  # What the agent should do
    available_actions: List[str] = []  # Valid action_type values
    feedback: str = ""  # Grader feedback after a step
    step_number: int = 0
    max_steps: int = 1
    metadata: dict[str, Any] = {}


# ──────────────────────────────────────────────────────────────
# Internal state (exposed via GET /state)
# ──────────────────────────────────────────────────────────────
class ContractState(State):
    """Server-side state. `episode_id` and `step_count` inherited."""

    task_name: str = ""
    current_clause_index: int = 0
    total_clauses: int = 0
    cumulative_reward: float = 0.0
    is_done: bool = False
    action_history: List[str] = []
