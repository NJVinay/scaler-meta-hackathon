"""
server/tasks/medium_risk.py — Task 2: Multi-Clause Risk Assessment

The agent receives a set of 3–4 contract clauses and must:
  1. Identify which clauses have risk issues
  2. Assign a risk level (low/medium/high) to each
  3. List the specific issues found

This is a multi-step task where the agent assesses clauses one at a time.

Difficulty: Medium
Max steps:  4
"""
import random
from server.data.contracts import CLAUSES


# Clauses suitable for risk assessment (mix of risk levels)
RISK_ASSESSMENT_POOLS = [
    # Pool A: indemnification (low), termination (medium), force-majeure (high)
    ["clause_001", "clause_003", "clause_005"],
    # Pool B: confidentiality (low), IP (medium), non-compete (high)
    ["clause_004", "clause_006", "clause_007"],
    # Pool C: warranty (low), payment terms (high), dispute resolution (medium)
    ["clause_008", "clause_009", "clause_010"],
    # Pool D: limitation-of-liability (low), termination (medium), payment (high), non-compete (high)
    ["clause_002", "clause_003", "clause_009", "clause_007"],
]


def get_task_config() -> dict:
    return {
        "name": "risk-assess",
        "description": (
            "Assess the risk level of each clause in a contract snippet. "
            "For each clause, assign low/medium/high and list specific issues."
        ),
        "difficulty": "medium",
        "max_steps": 4,
        "available_actions": ["assess_risk"],
    }


def generate_episode(seed: int | None = None) -> dict:
    """Generate a new risk assessment episode.

    Returns:
        dict with:
          clauses:       list of clause dicts (3-4 clauses)
          instructions:  what the agent should do
          expected:      list of {clause_id, risk_level, issues}
    """
    if seed is not None:
        random.seed(seed)

    pool_ids = random.choice(RISK_ASSESSMENT_POOLS)
    clauses = []
    expected = []

    for cid in pool_ids:
        clause = next(c for c in CLAUSES if c["id"] == cid)
        clauses.append(clause)
        expected.append({
            "clause_id": cid,
            "risk_level": clause["risk_level"],
            "issues": clause["issues"],
        })

    instructions = (
        "You will review contract clauses one at a time. For each clause:\n"
        "1. Assign a risk level: 'low', 'medium', or 'high'\n"
        "2. List any specific legal issues you identify\n\n"
        "Respond in this exact format:\n"
        "RISK: <low|medium|high>\n"
        "ISSUES:\n"
        "- <issue 1>\n"
        "- <issue 2>\n"
        "(or 'ISSUES: none' if no issues found)"
    )

    return {
        "clauses": clauses,
        "instructions": instructions,
        "expected": expected,
    }
