# TASK 03 — Define 3 Tasks with Agent Graders

**Source:** `task_requirements/The-Task.md`

## Objective
Implement a minimum of 3 tasks (easy / medium / hard) each with a deterministic programmatic grader that scores performance in `[0.0, 1.0]`.

## Steps

1. **Design 3 tasks with increasing difficulty**

   | Task | Difficulty | Example Objective |
   |------|-----------|-------------------|
   | Task 1 | Easy | Classify a single item correctly |
   | Task 2 | Medium | Multi-step action sequence with partial credit |
   | Task 3 | Hard | Complex reasoning, must challenge frontier models |

2. **Implement a grader for each task**
   ```python
   def grade(agent_output, expected) -> float:
       # Returns score in [0.0, 1.0]
       # Must be deterministic and reproducible
       ...
   ```

3. **Reward function must provide partial progress signals**
   - ✅ Reward intermediate correct actions — not just terminal success
   - ✅ Penalize destructive or looping actions
   - ❌ Do NOT return binary 0/1 only (sparse rewards are penalized in scoring)

## Rules & Constraints
- All grader scores **must** be in `[0.0, 1.0]` range — validated automatically in Phase 1.
- Graders must be **deterministic** — same input always returns same score.
- Hard task must genuinely challenge frontier-level LLMs.
- No graders that always return the same score (disqualification criterion).

## Scoring Weight
Task grader quality = **25%** of total evaluation score.
