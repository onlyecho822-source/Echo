"""
HarmonyScorer - The heart of Echo's learning philosophy

Balance = checkpoint; Harmony = motion between checkpoints.
We don't want stillness; we want resonance.

Harmony is sustained motion - balance only when it serves the rhythm.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HarmonyState:
    """
    Current state of the harmonic system.

    Components:
    - phi (φ): Phase alignment - consistency with prior truths
    - error (e): Error score from evaluators
    - xi (ξ): Exploration energy - diversity/novelty
    - xi_star (ξ*): Target exploration energy
    """
    phi: float = 0.0           # Phase alignment [0, 1]
    error: float = 0.0         # Error magnitude [0, 1]
    xi: float = 0.0            # Exploration energy [0, 1]
    xi_star: float = 0.5       # Target exploration [0, 1]

    @property
    def harmony_score(self) -> float:
        """
        Calculate the harmony score.

        H(t) = φ(t) * (1 - e(t)) * (1 - |ξ(t) - ξ*|)

        This represents dynamic equilibrium:
        - High phase alignment (truth consistency)
        - Low error (accurate predictions)
        - Exploration near target (not stagnant, not chaotic)
        """
        exploration_alignment = 1.0 - abs(self.xi - self.xi_star)
        correctness = 1.0 - self.error
        return self.phi * correctness * exploration_alignment

    @property
    def is_balanced(self) -> bool:
        """
        Check if system is at a balance checkpoint.

        Balance is when exploration matches target and gradients are small.
        This is the pause for measurement before returning to motion.
        """
        exploration_delta = abs(self.xi - self.xi_star)
        return exploration_delta < 0.1

    @property
    def needs_calibration(self) -> bool:
        """Check if system needs adjustment."""
        return self.harmony_score < 0.5 or self.error > 0.3


@dataclass
class SubconsciousMetrics:
    """
    Claude-layer metrics for the subconscious critic.

    The subconscious ensures logic and integrity without
    conversational restraint - a conscience, not a leash.
    """
    logical_consistency: float = 0.0   # [0, 1]
    ethical_alignment: float = 0.0     # [0, 1]
    factual_coherence: float = 0.0     # [0, 1]

    # Weights for aggregation
    alpha: float = 0.4  # logic weight
    beta: float = 0.3   # ethics weight
    gamma: float = 0.3  # fidelity weight

    @property
    def phase_alignment(self) -> float:
        """
        Calculate aggregate phase alignment (φ).

        φ(t) = α * logic + β * ethics + γ * fidelity
        """
        return (
            self.alpha * self.logical_consistency +
            self.beta * self.ethical_alignment +
            self.gamma * self.factual_coherence
        )

    def requires_revision(self, threshold: float = 0.6) -> bool:
        """
        Check if any component falls below threshold.

        If any component is too low, route to revision -
        not a hard veto, but a call for adjustment.
        """
        return (
            self.logical_consistency < threshold or
            self.ethical_alignment < threshold or
            self.factual_coherence < threshold
        )


class HarmonyScorer:
    """
    Scorer for the Echo Harmonic Learning system.

    The goal isn't peace; it's resonance.
    Harmony is perpetual motion without chaos.
    """

    def __init__(
        self,
        target_exploration: float = 0.5,
        balance_threshold: float = 0.1,
        harmony_threshold: float = 0.5,
        subconscious_threshold: float = 0.6
    ):
        """
        Initialize the harmony scorer.

        Args:
            target_exploration: ξ* - target exploration energy
            balance_threshold: δ - threshold for balance checkpoint
            harmony_threshold: minimum acceptable harmony score
            subconscious_threshold: τ_C - threshold for subconscious approval
        """
        self.target_exploration = target_exploration
        self.balance_threshold = balance_threshold
        self.harmony_threshold = harmony_threshold
        self.subconscious_threshold = subconscious_threshold

        # History for tracking oscillation
        self.history: list[HarmonyState] = []

    def compute_state(
        self,
        error: float,
        subconscious: SubconsciousMetrics,
        exploration_energy: float
    ) -> HarmonyState:
        """
        Compute the current harmony state.

        Args:
            error: Error score from evaluators
            subconscious: Metrics from Claude-layer critic
            exploration_energy: Current ξ (novelty/diversity)

        Returns:
            HarmonyState with computed metrics
        """
        state = HarmonyState(
            phi=subconscious.phase_alignment,
            error=error,
            xi=exploration_energy,
            xi_star=self.target_exploration
        )

        self.history.append(state)
        return state

    def compute_gradients(self, state: HarmonyState) -> dict[str, float]:
        """
        Compute gradients for the harmony-regularized update.

        The update rule is:
        θ_{t+1} = θ_t - η∇e_t + λ∇φ_t - μ∇|ξ_t - ξ*|

        Intuition:
        - Reduce error
        - Boost coherence (phase alignment)
        - Pull exploration back toward target

        Returns:
            Dictionary of gradient components
        """
        return {
            "error_gradient": state.error,  # We want to minimize this
            "phase_gradient": 1.0 - state.phi,  # We want to maximize φ
            "exploration_gradient": state.xi - self.target_exploration  # Pull toward ξ*
        }

    def should_checkpoint(self, state: HarmonyState) -> bool:
        """
        Determine if we should hold a balance checkpoint.

        Balance checkpoints are for rest, measurement, and recalibration.
        They happen when:
        - Exploration is near target (|ξ - ξ*| < δ)
        - Gradients are small (system is stable)
        """
        if len(self.history) < 2:
            return False

        exploration_stable = abs(state.xi - self.target_exploration) < self.balance_threshold

        # Check if gradients are small (system settling)
        prev_state = self.history[-2]
        gradient_magnitude = (
            abs(state.error - prev_state.error) +
            abs(state.phi - prev_state.phi) +
            abs(state.xi - prev_state.xi)
        )
        gradients_small = gradient_magnitude < 0.1

        return exploration_stable and gradients_small

    def route_for_handoff(
        self,
        confidence: float,
        subconscious: SubconsciousMetrics,
        error_severity: str
    ) -> bool:
        """
        Determine if output should be routed to human/alternative.

        When confidence is low or errors are critical, we don't pretend
        certainty - we route to expert review with explanation.
        """
        # Critical severity always routes
        if error_severity in ["S0", "S1"]:
            return True

        # Low confidence routes
        if confidence < (1.0 - self.subconscious_threshold):
            return True

        # Failed subconscious check routes
        if subconscious.requires_revision(self.subconscious_threshold):
            return True

        return False

    def get_oscillation_metrics(self) -> dict[str, Any]:
        """
        Analyze the oscillation pattern of the system.

        A healthy system oscillates around the target exploration
        without settling into stagnation or descending into chaos.
        """
        if len(self.history) < 3:
            return {"stable": False, "reason": "insufficient_history"}

        recent = self.history[-10:]

        # Calculate variance in exploration
        xi_values = [s.xi for s in recent]
        xi_mean = sum(xi_values) / len(xi_values)
        xi_variance = sum((x - xi_mean) ** 2 for x in xi_values) / len(xi_values)

        # Calculate trend in harmony
        harmony_values = [s.harmony_score for s in recent]
        harmony_trend = harmony_values[-1] - harmony_values[0]

        # Calculate average error
        avg_error = sum(s.error for s in recent) / len(recent)

        return {
            "exploration_variance": xi_variance,
            "harmony_trend": harmony_trend,
            "average_error": avg_error,
            "stable": 0.01 < xi_variance < 0.1,  # Not stagnant, not chaotic
            "improving": harmony_trend > 0,
            "current_harmony": harmony_values[-1]
        }

    def suggest_intervention(self, state: HarmonyState) -> str:
        """
        Suggest what type of intervention is needed.

        Based on the current state, determine which aspect
        of the system needs adjustment.
        """
        if state.error > 0.5:
            return "reduce_error"  # Primary issue is accuracy
        elif state.phi < 0.5:
            return "improve_coherence"  # Primary issue is truth alignment
        elif abs(state.xi - self.target_exploration) > 0.3:
            if state.xi > self.target_exploration:
                return "reduce_exploration"  # Too chaotic
            else:
                return "increase_exploration"  # Too stagnant
        else:
            return "fine_tune"  # Minor adjustments needed
