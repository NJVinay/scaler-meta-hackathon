"""
server/environment.py — Core OpenEnv Environment for Contract Clause Analysis.

Implements the 3 required methods:
  - reset()  → ContractObservation
  - step()   → ContractObservation (with done, reward)
  - state    → ContractState (property)

Routes actions to the appropriate task handler (easy/medium/hard).
"""

import uuid
import random
from typing import Optional

from openenv.core.env_server import Environment
from models import ContractAction, ContractObservation, ContractState
from server.tasks import easy_classify, medium_risk, hard_rewrite
from server.graders import classify_grader, risk_grader, rewrite_grader


class ContractEnvironment(Environment):
    """OpenEnv environment for contract clause analysis tasks."""

    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        self._state = ContractState()
        self._task_name: str = ""
        self._episode_data: dict = {}
        self._step_outputs: list[str] = []
        self._action_history: list[str] = []
        self._rewards: list[float] = []
        self._current_step: int = 0
        self._max_steps: int = 1
        self._done: bool = False

    # ──────────────────────────────────────────────────────────
    # reset() — start a new episode
    # ──────────────────────────────────────────────────────────
    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_name: Optional[str] = None,
        **kwargs,
    ) -> ContractObservation:
        """Reset and start a new episode.

        Args:
            seed:        Random seed for reproducibility.
            episode_id:  Custom episode ID (auto-generated if None).
            task_name:   Which task to run: "clause-classify", "risk-assess",
                         or "clause-rewrite". Defaults to random.
        """
        # Select task
        if task_name is None:
            task_name = random.choice(
                [
                    "clause-classify",
                    "risk-assess",
                    "clause-rewrite",
                ]
            )
        self._task_name = task_name

        # Reset internal state
        self._step_outputs = []
        self._action_history = []
        self._rewards = []
        self._current_step = 0
        self._done = False

        # Generate episode data for the selected task
        if task_name == "clause-classify":
            config = easy_classify.get_task_config()
            self._episode_data = easy_classify.generate_episode(seed)
            self._max_steps = config["max_steps"]
            clause_text = self._episode_data["clause"]["text"]
            instructions = self._episode_data["instructions"]
            available_actions = config["available_actions"]

        elif task_name == "risk-assess":
            config = medium_risk.get_task_config()
            self._episode_data = medium_risk.generate_episode(seed)
            self._max_steps = config["max_steps"]
            # Show first clause
            clause_text = self._episode_data["clauses"][0]["text"]
            instructions = self._episode_data["instructions"]
            available_actions = config["available_actions"]

        elif task_name == "clause-rewrite":
            config = hard_rewrite.get_task_config()
            self._episode_data = hard_rewrite.generate_episode(seed)
            self._max_steps = config["max_steps"]
            clause_text = self._episode_data["clause"]["text"]
            instructions = self._episode_data["step_instructions"][0]
            available_actions = config["available_actions"]

        else:
            raise ValueError(f"Unknown task: {task_name}")

        # Update state
        eid = episode_id or str(uuid.uuid4())
        self._state = ContractState(
            episode_id=eid,
            step_count=0,
            task_name=self._task_name,
            current_clause_index=0,
            total_clauses=(
                len(self._episode_data.get("clauses", []))
                if task_name == "risk-assess"
                else 1
            ),
            cumulative_reward=0.0,
            is_done=False,
            action_history=[],
        )

        return ContractObservation(
            done=False,
            reward=None,
            task_name=self._task_name,
            clause_text=clause_text,
            instructions=instructions,
            available_actions=available_actions,
            feedback="",
            step_number=0,
            max_steps=self._max_steps,
        )

    # ──────────────────────────────────────────────────────────
    # step() — process an agent action
    # ──────────────────────────────────────────────────────────
    def step(
        self,
        action: ContractAction,
        timeout_s: Optional[float] = None,
        **kwargs,
    ) -> ContractObservation:
        """Process one agent action and return observation + reward."""
        if self._done:
            return ContractObservation(
                done=True,
                reward=0.0,
                task_name=self._task_name,
                clause_text="",
                instructions="Episode is already complete.",
                available_actions=[],
                feedback="Episode already ended.",
                step_number=self._current_step,
                max_steps=self._max_steps,
            )

        self._current_step += 1
        self._state.step_count = self._current_step
        self._action_history.append(action.payload)
        self._state.action_history = self._action_history.copy()

        # ── Task 1: Clause Classification ──
        if self._task_name == "clause-classify":
            score, feedback = classify_grader.grade(
                action.payload,
                self._episode_data["expected"],
            )
            self._step_outputs.append(action.payload)
            self._rewards.append(score)
            self._done = True

            self._state.cumulative_reward = score
            self._state.is_done = True

            return ContractObservation(
                done=True,
                reward=score,
                task_name=self._task_name,
                clause_text="",
                instructions="",
                available_actions=[],
                feedback=feedback,
                step_number=self._current_step,
                max_steps=self._max_steps,
            )

        # ── Task 2: Risk Assessment ──
        elif self._task_name == "risk-assess":
            clause_idx = self._current_step - 1
            clauses = self._episode_data["clauses"]
            expected_list = self._episode_data["expected"]

            self._step_outputs.append(action.payload)

            # Grade this individual clause
            if clause_idx < len(expected_list):
                step_score, step_feedback = risk_grader.grade_single_clause(
                    action.payload,
                    expected_list[clause_idx]["risk_level"],
                    expected_list[clause_idx]["issues"],
                )
            else:
                step_score = 0.0
                step_feedback = "Extra step — no clause to assess."

            self._rewards.append(step_score)
            self._state.cumulative_reward = sum(self._rewards) / len(self._rewards)
            self._state.current_clause_index = clause_idx + 1

            # Check if episode is done
            is_last = self._current_step >= self._max_steps or clause_idx + 1 >= len(
                clauses
            )
            self._done = is_last
            self._state.is_done = is_last

            # Next clause text (if not done)
            next_clause_text = ""
            next_instructions = ""
            if not is_last and clause_idx + 1 < len(clauses):
                next_clause_text = clauses[clause_idx + 1]["text"]
                next_instructions = self._episode_data["instructions"]

            if is_last:
                # Final episode grade
                final_score, final_feedback = risk_grader.grade_episode(
                    self._step_outputs,
                    expected_list,
                    self._action_history,
                )
                return ContractObservation(
                    done=True,
                    reward=final_score,
                    task_name=self._task_name,
                    clause_text="",
                    instructions="",
                    available_actions=[],
                    feedback=f"Step: {step_feedback} | Final: {final_feedback}",
                    step_number=self._current_step,
                    max_steps=self._max_steps,
                )

            return ContractObservation(
                done=False,
                reward=step_score,
                task_name=self._task_name,
                clause_text=next_clause_text,
                instructions=next_instructions,
                available_actions=["assess_risk"],
                feedback=step_feedback,
                step_number=self._current_step,
                max_steps=self._max_steps,
            )

        # ── Task 3: Clause Rewrite ──
        elif self._task_name == "clause-rewrite":
            self._step_outputs.append(action.payload)

            step_idx = self._current_step - 1
            step_instructions_list = self._episode_data["step_instructions"]

            # Per-step scoring
            if step_idx == 0:
                step_score, step_feedback = rewrite_grader.grade_step1_issues(
                    action.payload,
                    self._episode_data["expected_issues"],
                )
            elif step_idx == 1:
                step_score, step_feedback = rewrite_grader.grade_step2_rewrite(
                    action.payload,
                    self._episode_data["expected_rewrite"],
                    self._episode_data["expected_issues"],
                    self._episode_data["key_terms"],
                    self._episode_data["clause"]["text"],
                )
            elif step_idx == 2:
                step_score, step_feedback = rewrite_grader.grade_step3_justification(
                    action.payload,
                    self._episode_data["expected_issues"],
                )
            else:
                step_score = 0.0
                step_feedback = "Extra step — task complete."

            self._rewards.append(step_score)

            is_last = self._current_step >= self._max_steps
            self._done = is_last

            if is_last:
                final_score, final_feedback = rewrite_grader.grade_episode(
                    self._step_outputs,
                    self._episode_data["expected_issues"],
                    self._episode_data["expected_rewrite"],
                    self._episode_data["key_terms"],
                    self._episode_data["clause"]["text"],
                )
                self._state.cumulative_reward = final_score
                self._state.is_done = True

                return ContractObservation(
                    done=True,
                    reward=final_score,
                    task_name=self._task_name,
                    clause_text="",
                    instructions="",
                    available_actions=[],
                    feedback=f"Step: {step_feedback} | Final: {final_feedback}",
                    step_number=self._current_step,
                    max_steps=self._max_steps,
                )

            # Continue to next step
            next_instructions = (
                step_instructions_list[self._current_step]
                if self._current_step < len(step_instructions_list)
                else "Continue with the task."
            )
            self._state.cumulative_reward = sum(self._rewards) / len(self._rewards)

            return ContractObservation(
                done=False,
                reward=step_score,
                task_name=self._task_name,
                clause_text=self._episode_data["clause"]["text"],
                instructions=next_instructions,
                available_actions=["rewrite"],
                feedback=step_feedback,
                step_number=self._current_step,
                max_steps=self._max_steps,
            )

        else:
            raise ValueError(f"Unknown task: {self._task_name}")

    # ──────────────────────────────────────────────────────────
    # state — current internal state (property)
    # ──────────────────────────────────────────────────────────
    @property
    def state(self) -> ContractState:
        return self._state
