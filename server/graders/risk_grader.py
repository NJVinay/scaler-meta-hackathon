"""
server/graders/risk_grader.py — Grader for Task 2 (Risk Assessment)

Scoring per clause (then averaged across all clauses):
  - Risk level accuracy:    0.40 weight
  - Issue identification:   0.60 weight (partial credit per issue found)

Anti-loop penalty:  -0.05 per repeated identical action
Anti-skip penalty:  -0.10 if agent submits for fewer clauses than expected

Returns float in [0.0, 1.0]. Deterministic.
"""
from difflib import SequenceMatcher


def _parse_risk_response(text: str) -> tuple[str, list[str]]:
    """Parse agent's structured response into (risk_level, issues)."""
    risk_level = ""
    issues = []

    lines = text.strip().split("\n")
    in_issues = False

    for line in lines:
        line_stripped = line.strip()
        upper = line_stripped.upper()

        if upper.startswith("RISK:"):
            risk_level = line_stripped.split(":", 1)[1].strip().lower()
            in_issues = False
        elif upper.startswith("ISSUES:"):
            rest = line_stripped.split(":", 1)[1].strip().lower()
            if rest == "none" or rest == "n/a":
                in_issues = False
            else:
                in_issues = True
                if rest and rest != "none":
                    issues.append(rest.lstrip("- ").strip())
        elif in_issues and line_stripped.startswith("-"):
            issue = line_stripped.lstrip("- ").strip()
            if issue:
                issues.append(issue)

    return risk_level, issues


def _issue_similarity(agent_issue: str, expected_issue: str) -> float:
    """Fuzzy-match an agent's described issue against the expected one."""
    return SequenceMatcher(
        None,
        agent_issue.lower(),
        expected_issue.lower(),
    ).ratio()


def grade_single_clause(
    agent_output: str,
    expected_risk: str,
    expected_issues: list[str],
) -> tuple[float, str]:
    """Grade a single clause's risk assessment.

    Returns:
        (score, feedback) where score is in [0.0, 1.0].
    """
    risk_level, agent_issues = _parse_risk_response(agent_output)

    # ── Risk level scoring (0.40 weight) ──
    risk_score = 0.0
    if risk_level == expected_risk:
        risk_score = 1.0
    elif (risk_level, expected_risk) in [
        ("low", "medium"), ("medium", "low"),
        ("medium", "high"), ("high", "medium"),
    ]:
        risk_score = 0.4  # One level off

    # ── Issue identification scoring (0.60 weight) ──
    issue_score = 0.0
    if not expected_issues:
        # No issues expected — agent should identify none
        issue_score = 1.0 if not agent_issues else 0.5
    else:
        # Match agent issues to expected issues (greedy best-match)
        matched = 0
        used = set()
        for expected in expected_issues:
            best_sim = 0.0
            best_idx = -1
            for i, agent_issue in enumerate(agent_issues):
                if i in used:
                    continue
                sim = _issue_similarity(agent_issue, expected)
                if sim > best_sim:
                    best_sim = sim
                    best_idx = i

            if best_sim >= 0.35:  # Threshold for a valid match
                matched += 1
                if best_idx >= 0:
                    used.add(best_idx)

        issue_score = matched / len(expected_issues) if expected_issues else 0.0

    # ── Weighted total ──
    total = 0.40 * risk_score + 0.60 * issue_score

    feedback_parts = []
    if risk_level == expected_risk:
        feedback_parts.append(f"Risk level correct ({expected_risk}).")
    else:
        feedback_parts.append(
            f"Risk level: you said '{risk_level}', expected '{expected_risk}'."
        )

    if expected_issues:
        feedback_parts.append(
            f"Issues: identified {len(agent_issues)} issue(s), "
            f"matched {int(issue_score * len(expected_issues))}/{len(expected_issues)}."
        )
    else:
        feedback_parts.append("No issues expected for this clause.")

    return round(total, 4), " ".join(feedback_parts)


def grade_episode(
    step_outputs: list[str],
    expected_clauses: list[dict],
    action_history: list[str],
) -> tuple[float, str]:
    """Grade an entire multi-clause risk assessment episode.

    Args:
        step_outputs:     List of agent outputs per step.
        expected_clauses: List of {clause_id, risk_level, issues}.
        action_history:   Raw action strings for loop detection.

    Returns:
        (score, feedback) where score is in [0.0, 1.0].
    """
    if not step_outputs:
        return 0.0, "No steps completed."

    clause_scores = []
    feedback_parts = []

    for i, expected in enumerate(expected_clauses):
        if i < len(step_outputs):
            score, fb = grade_single_clause(
                step_outputs[i],
                expected["risk_level"],
                expected["issues"],
            )
            clause_scores.append(score)
            feedback_parts.append(f"Clause {i + 1}: {fb} (score: {score:.2f})")
        else:
            clause_scores.append(0.0)
            feedback_parts.append(f"Clause {i + 1}: Not assessed (score: 0.00)")

    # Average across clauses
    avg_score = sum(clause_scores) / len(expected_clauses)

    # ── Anti-loop penalty ──
    loop_count = 0
    for j in range(1, len(action_history)):
        if action_history[j] == action_history[j - 1]:
            loop_count += 1
    avg_score -= 0.05 * loop_count

    # ── Anti-skip penalty ──
    if len(step_outputs) < len(expected_clauses):
        skipped = len(expected_clauses) - len(step_outputs)
        avg_score -= 0.10 * skipped

    final = max(0.0, min(1.0, avg_score))
    return round(final, 4), " | ".join(feedback_parts)
