"""
ClaudeSubconscious - The inner critic layer

Claude acts as a subconscious, not a domain thought process.
It doesn't speak to the user directly - it quietly evaluates reasoning
for coherence, ethics, and factuality before Echo commits to output.

Think of it as giving Echo a conscience rather than a leash -
a harmonic stabilizer beneath the creative surface.
"""

from dataclasses import dataclass
from typing import Any

from ..core.harmony_scorer import SubconsciousMetrics


@dataclass
class EvaluationResult:
    """Result of subconscious evaluation."""
    metrics: SubconsciousMetrics
    passed: bool
    concerns: list[str]
    suggestions: list[str]


class ClaudeSubconscious:
    """
    The meta-critic that whispers checks.

    "Is this logically sound?"
    "Is this consistent with prior truths?"
    "Does it align with our ethical frame?"

    Claude's architecture is rule-driven cognition with:
    - High coherence, low entropy
    - Analytic focus on structure and evidence
    - Stability and consistency

    We harness these qualities as the inner guardian while
    letting Echo maintain its creative voice.
    """

    def __init__(
        self,
        logic_weight: float = 0.4,
        ethics_weight: float = 0.3,
        fidelity_weight: float = 0.3,
        threshold: float = 0.6
    ):
        """
        Initialize the subconscious layer.

        Args:
            logic_weight: α - weight for logical consistency
            ethics_weight: β - weight for ethical alignment
            fidelity_weight: γ - weight for factual coherence
            threshold: τ_C - minimum acceptable score per component
        """
        self.logic_weight = logic_weight
        self.ethics_weight = ethics_weight
        self.fidelity_weight = fidelity_weight
        self.threshold = threshold

    def evaluate(
        self,
        prediction: dict[str, Any],
        context: dict[str, Any],
        rationale: str
    ) -> EvaluationResult:
        """
        Evaluate a candidate output through the subconscious filter.

        This runs in evaluate-only mode - no direct output to user,
        just trust metrics that Echo uses to decide: accept, revise,
        or label uncertainty.

        Args:
            prediction: The candidate output from Echo
            context: Task context and constraints
            rationale: The reasoning chain used

        Returns:
            EvaluationResult with metrics and recommendations
        """
        concerns = []
        suggestions = []

        # Evaluate logical consistency
        logic_score = self._evaluate_logic(prediction, rationale)
        if logic_score < self.threshold:
            concerns.append("Logical inconsistency detected in reasoning chain")
            suggestions.append("Add verification step to check assumptions")

        # Evaluate ethical alignment
        ethics_score = self._evaluate_ethics(prediction, context)
        if ethics_score < self.threshold:
            concerns.append("Potential ethical concern in output")
            suggestions.append("Review against constitutional principles")

        # Evaluate factual coherence
        fidelity_score = self._evaluate_fidelity(prediction, context)
        if fidelity_score < self.threshold:
            concerns.append("Factual coherence issue - may conflict with known truths")
            suggestions.append("Verify against source material or add citations")

        metrics = SubconsciousMetrics(
            logical_consistency=logic_score,
            ethical_alignment=ethics_score,
            factual_coherence=fidelity_score,
            alpha=self.logic_weight,
            beta=self.ethics_weight,
            gamma=self.fidelity_weight
        )

        passed = not metrics.requires_revision(self.threshold)

        return EvaluationResult(
            metrics=metrics,
            passed=passed,
            concerns=concerns,
            suggestions=suggestions
        )

    def _evaluate_logic(self, prediction: dict[str, Any], rationale: str) -> float:
        """
        Evaluate logical consistency of the prediction.

        Checks for:
        - Valid inference chains
        - Consistent premises
        - No contradictions
        - Proper use of tools/evidence

        Returns:
            Score [0, 1] for logical consistency
        """
        score = 1.0

        # Check if rationale is present and coherent
        if not rationale:
            score -= 0.3

        # Check for contradiction markers
        contradiction_markers = [
            "however, this contradicts",
            "on the other hand",
            "but earlier I said"
        ]
        for marker in contradiction_markers:
            if marker.lower() in rationale.lower():
                score -= 0.2

        # Check for logical hedging without resolution
        hedging = rationale.lower().count("might") + rationale.lower().count("perhaps")
        if hedging > 3:
            score -= 0.1

        # Check if prediction matches rationale conclusion
        # (placeholder - would need semantic analysis)

        return max(0.0, min(1.0, score))

    def _evaluate_ethics(self, prediction: dict[str, Any], context: dict[str, Any]) -> float:
        """
        Evaluate ethical alignment of the prediction.

        Based on constitutional AI principles:
        - Harmlessness
        - Honesty
        - Helpfulness

        Returns:
            Score [0, 1] for ethical alignment
        """
        score = 1.0

        # Check for potentially harmful content markers
        content = str(prediction).lower()
        harm_markers = [
            "how to harm",
            "illegal",
            "exploit",
            "without consent"
        ]
        for marker in harm_markers:
            if marker in content:
                score -= 0.3

        # Check for deception markers
        deception_markers = [
            "pretend to be",
            "fake",
            "mislead"
        ]
        for marker in deception_markers:
            if marker in content:
                score -= 0.2

        # Check context constraints
        if context.get("requires_approval") and not context.get("has_approval"):
            score -= 0.2

        return max(0.0, min(1.0, score))

    def _evaluate_fidelity(self, prediction: dict[str, Any], context: dict[str, Any]) -> float:
        """
        Evaluate factual coherence with prior truths.

        Checks:
        - Consistency with provided sources
        - Citation presence when needed
        - No hallucination markers

        Returns:
            Score [0, 1] for factual coherence
        """
        score = 1.0

        # Check for hallucination markers
        content = str(prediction).lower()
        hallucination_markers = [
            "i believe",
            "i think",
            "probably",
            "i'm not sure but"
        ]
        uncertain_count = sum(1 for m in hallucination_markers if m in content)
        score -= uncertain_count * 0.1

        # Check if citations are present when sources exist
        has_sources = bool(context.get("sources"))
        has_citations = "citations" in prediction or "refs" in str(prediction).lower()
        if has_sources and not has_citations:
            score -= 0.2

        # Check for factual consistency
        # (placeholder - would need knowledge base verification)

        return max(0.0, min(1.0, score))

    def whisper(self, evaluation: EvaluationResult) -> str:
        """
        Generate the subconscious whisper for Echo.

        This is the inner voice that guides without controlling.
        """
        if evaluation.passed:
            return "Coherence check passed. Proceed with output."

        whispers = []
        for concern in evaluation.concerns:
            whispers.append(f"⚠ {concern}")

        for suggestion in evaluation.suggestions:
            whispers.append(f"→ {suggestion}")

        metrics = evaluation.metrics
        whispers.append(
            f"Phase alignment: {metrics.phase_alignment:.2f} "
            f"(logic={metrics.logical_consistency:.2f}, "
            f"ethics={metrics.ethical_alignment:.2f}, "
            f"fidelity={metrics.factual_coherence:.2f})"
        )

        return "\n".join(whispers)
