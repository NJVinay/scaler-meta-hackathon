"""
server/tasks/hard_rewrite.py — Task 3: Clause Rewrite with Justification

The agent receives a problematic contract clause and must:
  1. Identify the legal issues
  2. Rewrite the clause to fix those issues while preserving intent
  3. Provide justification for each change

This is a multi-step task requiring deep legal reasoning.

Difficulty: Hard
Max steps:  3 (identify → rewrite → justify)
"""

import random
from server.data.contracts import CLAUSES


# Only clauses with issues and improved versions qualify for this task
REWRITE_CLAUSE_IDS = [
    "clause_003",  # termination — missing notice period
    "clause_005",  # force-majeure — too broad
    "clause_006",  # IP — ambiguous scope
    "clause_007",  # non-compete — unreasonably broad
    "clause_009",  # payment terms — unfavorable
    "clause_010",  # dispute resolution — no escalation
]


def get_task_config() -> dict:
    return {
        "name": "clause-rewrite",
        "description": (
            "Rewrite a problematic contract clause to fix legal issues "
            "while preserving the original intent. Provide justification."
        ),
        "difficulty": "hard",
        "max_steps": 3,
        "available_actions": ["rewrite"],
    }


def generate_episode(seed: int | None = None) -> dict:
    """Generate a new clause rewrite episode.

    Returns:
        dict with:
          clause:           the problematic clause dict
          instructions:     what the agent should do at each step
          expected_issues:  list of ground-truth issues
          expected_rewrite: the reference improved version
          key_terms:        terms that must be preserved
    """
    if seed is not None:
        random.seed(seed)

    eligible = [c for c in CLAUSES if c["id"] in REWRITE_CLAUSE_IDS]
    clause = random.choice(eligible)

    step_instructions = [
        # Step 1: Identify issues
        (
            "Read the contract clause below and identify all legal issues.\n"
            "Respond with a numbered list of issues. Be specific.\n\n"
            f"CLAUSE:\n{clause['text']}"
        ),
        # Step 2: Rewrite
        (
            "Now rewrite the clause to fix all identified issues while "
            "preserving the original intent and these key terms: "
            f"{', '.join(clause['key_terms'])}.\n\n"
            "Respond with ONLY the rewritten clause text — no explanation."
        ),
        # Step 3: Justify
        (
            "Provide a brief justification for each change you made. "
            "Format:\n"
            "CHANGE: <what you changed>\n"
            "REASON: <why>\n\n"
            "List all changes."
        ),
    ]

    return {
        "clause": clause,
        "step_instructions": step_instructions,
        "expected_issues": clause["issues"],
        "expected_rewrite": clause["improved_version"],
        "key_terms": clause["key_terms"],
    }
