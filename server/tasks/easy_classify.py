"""
server/tasks/easy_classify.py — Task 1: Single Clause Classification

The agent receives one contract clause and must classify it into one of 10
predefined clause types. This is a single-step task.

Difficulty: Easy
Max steps:  1
"""
import random
from server.data.contracts import CLAUSES, CLAUSE_TYPES


# Clauses suitable for easy classification (low/medium risk, clear type)
EASY_CLAUSE_IDS = [
    "clause_001",  # indemnification
    "clause_002",  # limitation-of-liability
    "clause_003",  # termination
    "clause_004",  # confidentiality
    "clause_008",  # warranty
    "clause_010",  # dispute-resolution
]


def get_task_config() -> dict:
    """Return static task configuration."""
    return {
        "name": "clause-classify",
        "description": "Classify a single contract clause into the correct legal category.",
        "difficulty": "easy",
        "max_steps": 1,
        "available_actions": ["classify"],
    }


def generate_episode(seed: int | None = None) -> dict:
    """Generate a new classification episode.

    Returns:
        dict with:
          clause:       the clause dict from the dataset
          instructions: what the agent should do
          expected:     ground-truth clause_type
    """
    if seed is not None:
        random.seed(seed)

    # Pick a clause suitable for easy classification
    eligible = [c for c in CLAUSES if c["id"] in EASY_CLAUSE_IDS]
    clause = random.choice(eligible)

    instructions = (
        f"Classify the following contract clause into exactly one of these categories:\n"
        f"{', '.join(CLAUSE_TYPES)}\n\n"
        f"Respond with ONLY the category name — no explanation, no extra text."
    )

    return {
        "clause": clause,
        "instructions": instructions,
        "expected": clause["clause_type"],
    }
