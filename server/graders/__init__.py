# server/graders package
def clip_score(score: float) -> float:
    """Ensure score is strictly between 0 and 1, as required by the validator."""
    return max(0.01, min(0.99, float(score)))
