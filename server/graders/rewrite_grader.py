"""
server/graders/rewrite_grader.py — Grader for Task 3 (Clause Rewrite)

Multi-signal scoring across 3 steps:

Step 1 — Issue Identification (0.25 weight):
  Fuzzy-match agent's identified issues against ground truth.

Step 2 — Rewrite Quality (0.50 weight):
  - Key terms preserved:          0.15
  - Issues addressed in rewrite:  0.20
  - Similarity to reference:      0.15

Step 3 — Justification Quality (0.25 weight):
  Agent must reference specific changes with reasons.

Returns float in [0.0, 1.0]. Deterministic.
"""

from difflib import SequenceMatcher


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _count_key_terms(text: str, key_terms: list[str]) -> int:
    lower = text.lower()
    return sum(1 for term in key_terms if term.lower() in lower)


def grade_step1_issues(
    agent_output: str,
    expected_issues: list[str],
) -> tuple[float, str]:
    """Grade issue identification (Step 1).

    Returns (score, feedback) where score is in [0.0, 1.0].
    """
    if not expected_issues:
        return 1.0, "No issues expected."

    agent_lines = [
        line.strip().lstrip("0123456789.-) ").strip()
        for line in agent_output.strip().split("\n")
        if line.strip() and not line.strip().startswith("#")
    ]

    matched = 0
    for expected in expected_issues:
        best_sim = max(
            (_similarity(al, expected) for al in agent_lines),
            default=0.0,
        )
        if best_sim >= 0.30:
            matched += 1

    score = matched / len(expected_issues)
    feedback = f"Identified {matched}/{len(expected_issues)} issues correctly."
    return round(score, 4), feedback


def grade_step2_rewrite(
    agent_rewrite: str,
    expected_rewrite: str,
    expected_issues: list[str],
    key_terms: list[str],
    original_text: str,
) -> tuple[float, str]:
    """Grade the rewrite (Step 2).

    Scoring:
      - Key terms preserved:      0.30 weight
      - Issues addressed:         0.40 weight
      - Reference similarity:     0.30 weight

    Returns (score, feedback).
    """
    if not agent_rewrite.strip():
        return 0.0, "Empty rewrite submitted."

    # ── Key terms preserved ──
    total_terms = len(key_terms)
    preserved = _count_key_terms(agent_rewrite, key_terms)
    term_score = preserved / total_terms if total_terms > 0 else 1.0

    # ── Issues addressed ──
    # Check if the rewrite no longer contains the problematic patterns
    # and/or contains improvements
    issue_score = 0.0
    if expected_issues:
        improvements_detected = 0
        rewrite_lower = agent_rewrite.lower()
        original_lower = original_text.lower()

        for issue in expected_issues:
            issue_lower = issue.lower()
            # Heuristic: if issue mentions something being "missing" or "no",
            # check if the rewrite adds relevant content
            if "no " in issue_lower or "missing" in issue_lower:
                # The rewrite should be longer or contain new concepts
                if len(agent_rewrite) > len(original_text) * 0.8:
                    improvements_detected += 1
            elif (
                "overbroad" in issue_lower
                or "unreason" in issue_lower
                or "too broad" in issue_lower
            ):
                # The rewrite should narrow scope
                if len(agent_rewrite) != len(original_text):
                    improvements_detected += 1
            elif "vague" in issue_lower or "subjective" in issue_lower:
                # Check for more specific language
                if agent_rewrite != original_text:
                    improvements_detected += 1
            else:
                # Generic check: the rewrite differs from original
                if _similarity(agent_rewrite, original_text) < 0.90:
                    improvements_detected += 1

        issue_score = improvements_detected / len(expected_issues)

    # ── Reference similarity ──
    ref_sim = _similarity(agent_rewrite, expected_rewrite) if expected_rewrite else 0.5

    # ── Weighted total ──
    total = 0.30 * term_score + 0.40 * issue_score + 0.30 * ref_sim

    feedback = (
        f"Key terms: {preserved}/{total_terms} preserved. "
        f"Issues addressed: {issue_score:.0%}. "
        f"Reference similarity: {ref_sim:.0%}."
    )
    return round(total, 4), feedback


def grade_step3_justification(
    agent_output: str,
    expected_issues: list[str],
) -> tuple[float, str]:
    """Grade the justification (Step 3).

    Looks for structured CHANGE/REASON pairs that reference actual issues.

    Returns (score, feedback).
    """
    if not agent_output.strip():
        return 0.0, "No justification provided."

    # Count CHANGE/REASON pairs
    lines = agent_output.strip().split("\n")
    changes = 0
    reasons = 0
    for line in lines:
        upper = line.strip().upper()
        if upper.startswith("CHANGE:") or upper.startswith("CHANGE "):
            changes += 1
        if upper.startswith("REASON:") or upper.startswith("REASON "):
            reasons += 1

    # If not using the structured format, check for bullet points or numbered items
    if changes == 0:
        changes = sum(
            1
            for line in lines
            if line.strip()
            and (line.strip()[0].isdigit() or line.strip().startswith("-"))
        )
        reasons = changes  # Assume inline justification

    expected_count = max(len(expected_issues), 1)

    # Score based on how many changes were justified
    pair_count = min(changes, reasons)
    structure_score = min(pair_count / expected_count, 1.0)

    # Relevance: do the justifications reference the expected issues?
    relevance_score = 0.0
    if expected_issues:
        matched = 0
        agent_lower = agent_output.lower()
        for issue in expected_issues:
            # Check if key words from the issue appear in justification
            issue_words = set(issue.lower().split())
            significant_words = {
                w
                for w in issue_words
                if len(w) > 3
                and w not in {"the", "and", "for", "that", "with", "this", "from"}
            }
            overlap = sum(1 for w in significant_words if w in agent_lower)
            if overlap >= len(significant_words) * 0.3:
                matched += 1
        relevance_score = matched / len(expected_issues)

    total = 0.50 * structure_score + 0.50 * relevance_score

    feedback = (
        f"Justification: {pair_count} change(s) explained. "
        f"Structure: {structure_score:.0%}. Relevance: {relevance_score:.0%}."
    )
    return round(total, 4), feedback


def grade_episode(
    step_outputs: list[str],
    expected_issues: list[str],
    expected_rewrite: str,
    key_terms: list[str],
    original_text: str,
) -> tuple[float, str]:
    """Grade an entire rewrite episode across all 3 steps.

    Returns (score, feedback) where score is in [0.0, 1.0].
    """
    scores = []
    feedback_parts = []

    # Step 1: Issue identification (weight 0.25)
    if len(step_outputs) >= 1:
        s, f = grade_step1_issues(step_outputs[0], expected_issues)
        scores.append(("issues", s, 0.25))
        feedback_parts.append(f"Issues: {f}")
    else:
        scores.append(("issues", 0.0, 0.25))
        feedback_parts.append("Issues: not attempted.")

    # Step 2: Rewrite (weight 0.50)
    if len(step_outputs) >= 2:
        s, f = grade_step2_rewrite(
            step_outputs[1],
            expected_rewrite,
            expected_issues,
            key_terms,
            original_text,
        )
        scores.append(("rewrite", s, 0.50))
        feedback_parts.append(f"Rewrite: {f}")
    else:
        scores.append(("rewrite", 0.0, 0.50))
        feedback_parts.append("Rewrite: not attempted.")

    # Step 3: Justification (weight 0.25)
    if len(step_outputs) >= 3:
        s, f = grade_step3_justification(step_outputs[2], expected_issues)
        scores.append(("justification", s, 0.25))
        feedback_parts.append(f"Justify: {f}")
    else:
        scores.append(("justification", 0.0, 0.25))
        feedback_parts.append("Justify: not attempted.")

    total = sum(s * w for _, s, w in scores)
    final = max(0.0, min(1.0, total))
    return round(final, 4), " | ".join(feedback_parts)
