"""
client.py — EnvClient for remote consumers of the Contract Clause Analyzer.

Translates between typed models and the WebSocket wire format.
Users import this to interact with a deployed instance.
"""

from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from models import ContractAction, ContractObservation, ContractState


class ContractEnv(EnvClient[ContractAction, ContractObservation, ContractState]):
    """Typed client for interacting with a deployed Contract Clause Analyzer."""

    def _step_payload(self, action: ContractAction) -> dict:
        """Convert a ContractAction into the wire-format dict."""
        return {
            "action_type": action.action_type,
            "payload": action.payload,
            "reasoning": action.reasoning,
        }

    def _parse_result(self, payload: dict) -> StepResult:
        """Parse a step response from the server into a StepResult."""
        obs_data = payload.get("observation", payload)
        return StepResult(
            observation=ContractObservation(
                done=payload.get("done", False),
                reward=payload.get("reward"),
                task_name=obs_data.get("task_name", ""),
                clause_text=obs_data.get("clause_text", ""),
                instructions=obs_data.get("instructions", ""),
                available_actions=obs_data.get("available_actions", []),
                feedback=obs_data.get("feedback", ""),
                step_number=obs_data.get("step_number", 0),
                max_steps=obs_data.get("max_steps", 1),
                metadata=obs_data.get("metadata", {}),
            ),
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> ContractState:
        """Parse a state response from the server."""
        return ContractState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            task_name=payload.get("task_name", ""),
            current_clause_index=payload.get("current_clause_index", 0),
            total_clauses=payload.get("total_clauses", 0),
            cumulative_reward=payload.get("cumulative_reward", 0.0),
            is_done=payload.get("is_done", False),
            action_history=payload.get("action_history", []),
        )
