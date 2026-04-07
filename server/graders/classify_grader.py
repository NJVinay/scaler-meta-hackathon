"""
server/graders/classify_grader.py — Grader for Task 1 (Clause Classification)

Scoring:
  - 1.0  for exact match
  - 0.3  for a related/adjacent clause type
  - 0.0  for completely wrong

Returns float in [0.0, 1.0]. Deterministic.
"""

from server.data.contracts import CLAUSE_TYPES

# Related clause type pairs that get partial credit (0.3)
RELATED_TYPES = {
    "indemnification": ["limitation-of-liability", "warranty"],
    "limitation-of-liability": ["indemnification", "warranty"],
    "termination": ["force-majeure"],
    "confidentiality": ["intellectual-property", "non-compete"],
    "force-majeure": ["termination"],
    "intellectual-property": ["confidentiality", "non-compete"],
    "non-compete": ["confidentiality", "intellectual-property"],
    "warranty": ["indemnification", "limitation-of-liability"],
    "payment-terms": ["termination"],
    "dispute-resolution": ["termination"],
}


def grade(agent_output: str, expected: str) -> tuple[float, str]:
    """Grade a clause classification attempt.

    Args:
        agent_output: The agent's submitted classification.
        expected:     Ground-truth clause type.

    Returns:
        (score, feedback) where score is in [0.0, 1.0].
    """
    # Normalize: strip whitespace, lowercase, handle common formatting
    answer = agent_output.strip().lower().replace("_", "-").replace(" ", "-")

    # Remove any surrounding quotes or backticks
    answer = answer.strip("\"'`")

    if answer == expected:
        return 1.0, f"Correct! The clause type is '{expected}'."

    # Check for partial credit
    related = RELATED_TYPES.get(expected, [])
    if answer in related:
        return 0.3, (
            f"Close — you said '{answer}', but the correct type is '{expected}'. "
            f"These are related categories."
        )

    # Check if answer is at least a valid clause type
    if answer in CLAUSE_TYPES:
        return 0.0, (
            f"Incorrect. You said '{answer}', but the correct type is '{expected}'."
        )

    return 0.0, (
        f"Invalid answer '{answer}'. Expected one of: {', '.join(CLAUSE_TYPES)}. "
        f"The correct type is '{expected}'."
    )
