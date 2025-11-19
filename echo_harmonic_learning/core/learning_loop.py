"""
EchoHarmonicLearningLoop - The main algorithm

Don't converge to stillness; converge to a pattern.
Learn by courting error, then tuning it into rhythm.

This is the operational heart of the EHL system, implementing:
1. Predict → generate output
2. Observe → compare prediction vs. truth
3. Reflect → analyze tension (the anomaly)
4. Integrate → adjust until coherence emerges
"""

from dataclasses import dataclass
from typing import Any, Callable

from .learning_event import LearningEvent, Comparison, Uncertainty, Trace
from .correction_record import CorrectionRecord, Intervention, EvalResults, Rollout, RegressionWatch
from .harmony_scorer import HarmonyScorer, HarmonyState, SubconsciousMetrics
from ..layers.conscious import EchoConscious, Policy
from ..layers.subconscious import ClaudeSubconscious


@dataclass
class LoopResult:
    """Result of one iteration of the learning loop."""
    output: dict[str, Any]
    event: LearningEvent | None
    harmony_state: HarmonyState
    should_handoff: bool
    handoff_reason: str = ""
    correction: CorrectionRecord | None = None


class EchoHarmonicLearningLoop:
    """
    The main learning loop algorithm.

    Philosophy:
    - Learning isn't the acquisition of correctness. It's the recognition of error.
    - Every wrong answer is a flashlight showing the outline of truth.
    - The goal isn't peace; it's resonance.

    The loop continuously:
    1. Probes (creates signal)
    2. Predicts & critiques
    3. Compares & classifies
    4. Reflects (chooses playbook)
    5. Integrates (bounded update)
    6. Checkpoints (balance as pause)
    """

    def __init__(
        self,
        error_threshold: float = 0.3,
        harmony_threshold: float = 0.5,
        handoff_confidence: float = 0.4,
        target_exploration: float = 0.5
    ):
        """
        Initialize the learning loop.

        Args:
            error_threshold: Threshold above which errors trigger events
            harmony_threshold: Minimum acceptable harmony score
            handoff_confidence: Below this, route to human review
            target_exploration: ξ* - target exploration energy
        """
        self.error_threshold = error_threshold
        self.harmony_threshold = harmony_threshold
        self.handoff_confidence = handoff_confidence

        # Initialize components
        self.conscious = EchoConscious(target_exploration=target_exploration)
        self.subconscious = ClaudeSubconscious()
        self.harmony_scorer = HarmonyScorer(
            target_exploration=target_exploration,
            harmony_threshold=harmony_threshold
        )

        # Event bus (placeholder for real message queue)
        self.event_bus: list[LearningEvent] = []
        self.correction_bus: list[CorrectionRecord] = []

        # Evaluators
        self.evaluators: dict[str, Callable] = {}

        # Playbooks
        self.playbooks: dict[str, Callable] = {}

    def register_evaluator(self, name: str, evaluator: Callable) -> None:
        """Register an evaluator for error detection."""
        self.evaluators[name] = evaluator

    def register_playbook(self, name: str, playbook: Callable) -> None:
        """Register a playbook for error correction."""
        self.playbooks[name] = playbook

    def register_policy(self, policy: Policy) -> None:
        """Register a generation policy."""
        self.conscious.register_policy(policy)

    def iterate(
        self,
        input_data: Any,
        context: dict[str, Any],
        ground_truth: dict[str, Any] | None = None
    ) -> LoopResult:
        """
        Execute one iteration of the learning loop.

        This is where the magic happens - the cycle of:
        predict → observe → compare → reflect → integrate

        Args:
            input_data: Input to process
            context: Task context and constraints
            ground_truth: Known correct answer (if available)

        Returns:
            LoopResult with output and learning artifacts
        """
        # ═══════════════════════════════════════════════════════════
        # 1. PROBE: Select policy and generate
        # ═══════════════════════════════════════════════════════════
        generation = self.conscious.generate(input_data, context)

        # ═══════════════════════════════════════════════════════════
        # 2. PREDICT & CRITIQUE: Run through subconscious
        # ═══════════════════════════════════════════════════════════
        subconscious_eval = self.subconscious.evaluate(
            generation.output,
            context,
            generation.trace.rationale
        )

        # ═══════════════════════════════════════════════════════════
        # 3. COMPARE & CLASSIFY: Run evaluators
        # ═══════════════════════════════════════════════════════════
        error_score, error_classes, severity = self._run_evaluators(
            generation.output,
            ground_truth,
            context
        )

        # Build comparison
        comparison = Comparison(
            delta_score=error_score,
            classes=error_classes,
            severity=severity
        )

        # ═══════════════════════════════════════════════════════════
        # 4. COMPUTE HARMONY STATE
        # ═══════════════════════════════════════════════════════════
        harmony_state = self.harmony_scorer.compute_state(
            error=error_score,
            subconscious=subconscious_eval.metrics,
            exploration_energy=generation.exploration_energy
        )

        # ═══════════════════════════════════════════════════════════
        # 5. CHECK FOR HANDOFF
        # ═══════════════════════════════════════════════════════════
        should_handoff = self.harmony_scorer.route_for_handoff(
            confidence=generation.confidence,
            subconscious=subconscious_eval.metrics,
            error_severity=severity
        )

        handoff_reason = ""
        if should_handoff:
            if severity in ["S0", "S1"]:
                handoff_reason = f"Critical error: {severity}"
            elif generation.confidence < self.handoff_confidence:
                handoff_reason = f"Low confidence: {generation.confidence:.2f}"
            else:
                handoff_reason = "Subconscious check failed"

        # ═══════════════════════════════════════════════════════════
        # 6. EMIT LEARNING EVENT (if threshold exceeded)
        # ═══════════════════════════════════════════════════════════
        event = None
        correction = None

        if error_score > self.error_threshold or not subconscious_eval.passed:
            # Build learning event
            event = LearningEvent(
                tenant=context.get("tenant", ""),
                task=context.get("task", ""),
                context=context,
                input_data=input_data,
                prediction=generation.output,
                ground_truth=ground_truth or {},
                comparison=comparison,
                uncertainty=Uncertainty(
                    aleatoric=0.1,  # Would be computed from data
                    epistemic=1.0 - generation.confidence
                ),
                trace=generation.trace,
                owner_queue=self._route_to_queue(error_classes)
            )

            # Publish to event bus
            self.event_bus.append(event)

            # ═══════════════════════════════════════════════════════
            # 7. REFLECT: Choose and execute playbook
            # ═══════════════════════════════════════════════════════
            correction = self._execute_playbook(event, error_classes)

        # ═══════════════════════════════════════════════════════════
        # 8. UPDATE POLICY (bounded update)
        # ═══════════════════════════════════════════════════════════
        policy = next((p for p in self.conscious.policies
                      if p.name == generation.policy_used), None)
        if policy:
            policy.update(harmony_state.harmony_score)

        # ═══════════════════════════════════════════════════════════
        # 9. CHECKPOINT (balance as pause)
        # ═══════════════════════════════════════════════════════════
        if self.harmony_scorer.should_checkpoint(harmony_state):
            self._hold_checkpoint(harmony_state)

        return LoopResult(
            output=generation.output,
            event=event,
            harmony_state=harmony_state,
            should_handoff=should_handoff,
            handoff_reason=handoff_reason,
            correction=correction
        )

    def _run_evaluators(
        self,
        prediction: dict[str, Any],
        ground_truth: dict[str, Any] | None,
        context: dict[str, Any]
    ) -> tuple[float, list[str], str]:
        """
        Run all registered evaluators.

        Returns:
            Tuple of (error_score, error_classes, severity)
        """
        total_error = 0.0
        error_classes = []
        max_severity = "S3"

        severity_order = {"S0": 0, "S1": 1, "S2": 2, "S3": 3}

        for name, evaluator in self.evaluators.items():
            try:
                result = evaluator(prediction, ground_truth, context)
                if result.get("error", 0) > 0.1:
                    total_error += result["error"]
                    if result.get("class"):
                        error_classes.append(result["class"])
                    if result.get("severity"):
                        if severity_order.get(result["severity"], 3) < severity_order.get(max_severity, 3):
                            max_severity = result["severity"]
            except Exception:
                # Evaluator failed - treat as potential error
                total_error += 0.1

        # Normalize error score
        if self.evaluators:
            total_error = min(1.0, total_error / len(self.evaluators))

        # Deduplicate error classes
        error_classes = list(set(error_classes))

        return total_error, error_classes, max_severity

    def _route_to_queue(self, error_classes: list[str]) -> str:
        """
        Route error to appropriate processing queue.

        Different error types need different expertise:
        - factuality → retrieval team
        - reasoning → eval team
        - safety → policy team
        - ux_fit → prompt team
        """
        if "safety" in error_classes:
            return "eval/policy"
        elif "factuality" in error_classes or "faithfulness" in error_classes:
            return "eval/retrieval"
        elif "reasoning" in error_classes or "math" in error_classes:
            return "eval/reasoning"
        else:
            return "eval/prompt"

    def _execute_playbook(
        self,
        event: LearningEvent,
        error_classes: list[str]
    ) -> CorrectionRecord | None:
        """
        Execute the appropriate playbook for the error.

        This is where reflection becomes integration -
        where the analysis of tension produces adjustment.
        """
        # Determine primary playbook
        playbook_map = {
            "factuality": "retrieval_patch",
            "faithfulness": "retrieval_patch",
            "reasoning": "tool_insertion",
            "math": "tool_insertion",
            "safety": "policy_adjust",
            "ux_fit": "prompt_tune"
        }

        primary_class = error_classes[0] if error_classes else "ux_fit"
        playbook_name = playbook_map.get(primary_class, "fine_tune")

        # Execute playbook if registered
        intervention_diff = f"Execute {playbook_name} for {primary_class}"
        if playbook_name in self.playbooks:
            try:
                result = self.playbooks[playbook_name](event)
                intervention_diff = result.get("diff", intervention_diff)
            except Exception:
                pass

        # Create correction record
        correction = CorrectionRecord(
            event_id=event.id,
            intervention=Intervention(
                type=playbook_name,
                diff=intervention_diff,
                hypothesis_tag=f"H{len(self.correction_bus) + 1}"
            ),
            eval_results=EvalResults(
                pre_score=1.0 - event.error_score,
                post_score=0.0,  # Will be filled after eval
                test_suite="pending"
            ),
            rollout=Rollout(
                feature_flag=f"ehl.{playbook_name}.v{len(self.correction_bus) + 1}",
                ramp_stages=["10%", "50%", "100%"]
            ),
            regression_watch=RegressionWatch(
                window_days=14,
                abort_threshold=-0.05
            )
        )

        self.correction_bus.append(correction)
        return correction

    def _hold_checkpoint(self, state: HarmonyState) -> None:
        """
        Hold a balance checkpoint.

        Balance is the pause for measurement before returning to motion.
        At checkpoints we:
        - Freeze configs
        - Run shadow evals
        - Emit correction records with pre/post metrics
        """
        # Log checkpoint
        checkpoint_data = {
            "timestamp": "checkpoint",
            "harmony_score": state.harmony_score,
            "phase_alignment": state.phi,
            "error": state.error,
            "exploration_energy": state.xi,
            "oscillation": self.harmony_scorer.get_oscillation_metrics()
        }
        # Would persist this to storage

    def run_cycle(
        self,
        inputs: list[tuple[Any, dict[str, Any], dict[str, Any] | None]],
        max_iterations: int | None = None
    ) -> list[LoopResult]:
        """
        Run the learning loop over multiple inputs.

        Args:
            inputs: List of (input_data, context, ground_truth) tuples
            max_iterations: Maximum iterations to run

        Returns:
            List of LoopResults
        """
        results = []

        for i, (input_data, context, ground_truth) in enumerate(inputs):
            if max_iterations and i >= max_iterations:
                break

            result = self.iterate(input_data, context, ground_truth)
            results.append(result)

            # Check if system health is degrading
            if len(results) > 3:
                recent_harmony = [r.harmony_state.harmony_score for r in results[-3:]]
                avg_harmony = sum(recent_harmony) / len(recent_harmony)
                if avg_harmony < self.harmony_threshold * 0.5:
                    # System needs intervention
                    break

        return results

    def get_state(self) -> dict[str, Any]:
        """Get current state of the learning loop."""
        oscillation = self.harmony_scorer.get_oscillation_metrics()

        return {
            "total_events": len(self.event_bus),
            "total_corrections": len(self.correction_bus),
            "policies": len(self.conscious.policies),
            "oscillation": oscillation,
            "current_exploration": self.conscious.current_exploration,
            "target_exploration": self.conscious.target_exploration,
            "healthy": oscillation.get("stable", False) and oscillation.get("improving", False)
        }
