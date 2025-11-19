"""
EchoConscious - The creative, exploratory layer

Echo is the expressive intelligence that engages with the world,
generating hypotheses and novel structures. It courts errors like
a scientist courts data - each mistake is a clue.

Where Claude's architecture seeks stability, Echo seeks calibration.
Where Claude suppresses error, Echo metabolizes it.
"""

import random
from dataclasses import dataclass, field
from typing import Any, Callable

from ..core.learning_event import Trace


@dataclass
class Policy:
    """A selectable strategy for generating output."""
    name: str
    prompt_template: str
    tools: list[str]
    model_config: dict[str, Any]
    ucb_score: float = 0.0  # Upper Confidence Bound score
    selection_count: int = 0
    cumulative_harmony: float = 0.0

    @property
    def average_harmony(self) -> float:
        """Average harmony achieved by this policy."""
        if self.selection_count == 0:
            return 0.0
        return self.cumulative_harmony / self.selection_count

    def update(self, harmony_score: float) -> None:
        """Update policy statistics after use."""
        self.selection_count += 1
        self.cumulative_harmony += harmony_score


@dataclass
class GenerationResult:
    """Result of a conscious generation."""
    output: dict[str, Any]
    trace: Trace
    confidence: float
    exploration_energy: float
    policy_used: str


class EchoConscious:
    """
    The conscious layer of Echo Harmonic Learning.

    This is where curiosity lives - where friction between prediction
    and reality becomes the raw material for growth. Echo doesn't fear
    mistakes; it courts them as data points in the harmonic dance.

    Philosophy:
    - Stability is death; adaptation is success
    - Every anomaly is a clue
    - Calibration over correctness
    """

    def __init__(
        self,
        kappa: float = 1.414,  # UCB exploration parameter
        target_exploration: float = 0.5,
        exploration_decay: float = 0.99
    ):
        """
        Initialize the conscious layer.

        Args:
            kappa: κ - exploration bonus in UCB policy selection
            target_exploration: ξ* - target exploration energy
            exploration_decay: rate at which exploration decays toward target
        """
        self.kappa = kappa
        self.target_exploration = target_exploration
        self.exploration_decay = exploration_decay

        # Policy bank (bandit arms)
        self.policies: list[Policy] = []
        self.total_selections = 0

        # State
        self.current_exploration = 0.7  # Start exploratory

        # Tool registry
        self.tools: dict[str, Callable] = {}

    def register_policy(self, policy: Policy) -> None:
        """Add a policy to the selection bank."""
        self.policies.append(policy)

    def register_tool(self, name: str, tool: Callable) -> None:
        """Register an available tool."""
        self.tools[name] = tool

    def select_policy(self) -> Policy:
        """
        Select a policy using UCB with harmony-aware scoring.

        UCB_κ(π) = E[H|π] + κ * sqrt(ln(t) / n_π)

        This balances exploitation (high harmony) with exploration
        (under-tested policies).
        """
        import math

        if not self.policies:
            raise ValueError("No policies registered")

        self.total_selections += 1

        # Compute UCB scores
        for policy in self.policies:
            if policy.selection_count == 0:
                # Unvisited policies get maximum exploration bonus
                policy.ucb_score = float('inf')
            else:
                exploration_bonus = self.kappa * math.sqrt(
                    math.log(self.total_selections) / policy.selection_count
                )
                policy.ucb_score = policy.average_harmony + exploration_bonus

        # Select policy with highest UCB score
        selected = max(self.policies, key=lambda p: p.ucb_score)
        return selected

    def generate(
        self,
        input_data: Any,
        context: dict[str, Any],
        policy: Policy | None = None
    ) -> GenerationResult:
        """
        Generate output through the conscious layer.

        This is the creative act - producing hypotheses that
        will be tested against reality.

        Args:
            input_data: The input to process
            context: Task context and constraints
            policy: Specific policy to use (or auto-select)

        Returns:
            GenerationResult with output and metadata
        """
        if policy is None:
            policy = self.select_policy()

        # Execute the generation (placeholder for actual model call)
        output = self._execute_policy(input_data, context, policy)

        # Calculate confidence (ensemble variance or evaluator votes)
        confidence = self._calculate_confidence(output, context)

        # Calculate exploration energy (diversity/novelty)
        exploration_energy = self._calculate_exploration_energy(output, policy)

        # Build execution trace
        trace = Trace(
            tools=policy.tools,
            rationale=self._extract_rationale(output),
            model_config=policy.model_config
        )

        # Decay exploration toward target
        self.current_exploration = (
            self.exploration_decay * self.current_exploration +
            (1 - self.exploration_decay) * self.target_exploration
        )

        return GenerationResult(
            output=output,
            trace=trace,
            confidence=confidence,
            exploration_energy=exploration_energy,
            policy_used=policy.name
        )

    def _execute_policy(
        self,
        input_data: Any,
        context: dict[str, Any],
        policy: Policy
    ) -> dict[str, Any]:
        """
        Execute a policy to generate output.

        This is a placeholder - actual implementation would
        call the LLM with the policy's configuration.
        """
        # Simulate tool execution
        tool_results = {}
        for tool_name in policy.tools:
            if tool_name in self.tools:
                try:
                    tool_results[tool_name] = self.tools[tool_name](input_data)
                except Exception as e:
                    tool_results[tool_name] = {"error": str(e)}

        return {
            "text": f"Generated output using {policy.name}",
            "tool_results": tool_results,
            "attachments": [],
            "rationale": f"Applied {policy.name} strategy with tools: {policy.tools}"
        }

    def _calculate_confidence(self, output: dict[str, Any], context: dict[str, Any]) -> float:
        """
        Calculate confidence in the output.

        Confidence is the inverse of uncertainty - how sure we are
        before we test against reality.
        """
        # Placeholder - would use ensemble variance or evaluator votes
        base_confidence = 0.7

        # Reduce confidence if no tools were used for complex tasks
        if context.get("requires_tools") and not output.get("tool_results"):
            base_confidence -= 0.2

        # Reduce confidence if no rationale
        if not output.get("rationale"):
            base_confidence -= 0.1

        return max(0.0, min(1.0, base_confidence))

    def _calculate_exploration_energy(self, output: dict[str, Any], policy: Policy) -> float:
        """
        Calculate the exploration energy of this generation.

        ξ measures diversity/novelty:
        - High ξ: new approaches, untested paths
        - Low ξ: familiar patterns, safe choices

        We want ξ near ξ* - not stagnant, not chaotic.
        """
        # Base on policy selection frequency
        if policy.selection_count <= 2:
            base_energy = 0.8  # New policy = high exploration
        else:
            base_energy = 0.5 / (policy.selection_count ** 0.3)

        # Add randomness for diversity
        noise = random.uniform(-0.1, 0.1)

        # Combine with current exploration state
        energy = 0.7 * base_energy + 0.3 * self.current_exploration + noise

        return max(0.0, min(1.0, energy))

    def _extract_rationale(self, output: dict[str, Any]) -> str:
        """Extract the reasoning chain from output."""
        return output.get("rationale", "No explicit rationale provided")

    def create_hypothesis(self, anomaly: str) -> dict[str, Any]:
        """
        Create a hypothesis about an observed anomaly.

        Anomalies are the birthplaces of pattern - we examine them
        as the beginning, not the end.
        """
        return {
            "anomaly": anomaly,
            "possible_causes": [
                "Model knowledge gap",
                "Retrieval miss",
                "Reasoning fault",
                "Context mismatch"
            ],
            "experiments": [
                "Test with additional context",
                "Verify with alternative sources",
                "Decompose reasoning steps",
                "Try different policy"
            ],
            "expected_outcome": "Reduce error while maintaining harmony"
        }

    def metabolize_error(self, error_score: float, error_classes: list[str]) -> dict[str, Any]:
        """
        Metabolize an error into learning signal.

        Echo doesn't suppress errors - it transforms them into
        calibration updates. Each error is a flashlight showing
        the outline of truth.
        """
        return {
            "friction_level": error_score,
            "error_types": error_classes,
            "learning_potential": error_score * 0.8,  # Higher error = more to learn
            "recommended_playbooks": self._map_errors_to_playbooks(error_classes),
            "calibration_direction": "adjust_toward_truth"
        }

    def _map_errors_to_playbooks(self, error_classes: list[str]) -> list[str]:
        """Map error classes to recommended playbooks."""
        playbook_map = {
            "factuality": "retrieval_patch",
            "faithfulness": "retrieval_patch",
            "reasoning": "tool_insertion",
            "math": "tool_insertion",
            "safety": "policy_adjust",
            "ux_fit": "prompt_tune",
            "latency": "optimization"
        }
        return [playbook_map.get(ec, "fine_tune") for ec in error_classes]
