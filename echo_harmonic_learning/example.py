#!/usr/bin/env python3
"""
Echo Harmonic Learning - Example Usage

Demonstrates the error-driven learning loop:
1. Predict → generate output
2. Observe → compare prediction vs. truth
3. Reflect → analyze tension (the anomaly)
4. Integrate → adjust until coherence emerges
"""

from echo_harmonic_learning import (
    EchoHarmonicLearningLoop,
    Policy,
    FactualityPlaybook,
    ReasoningPlaybook
)


def create_evaluators():
    """Create sample evaluators for error detection."""

    def factuality_evaluator(prediction, ground_truth, context):
        """Check factual accuracy."""
        if not ground_truth:
            return {"error": 0.0}

        # Simple check - would use semantic similarity in production
        pred_text = str(prediction.get("text", "")).lower()
        truth_text = str(ground_truth.get("text", "")).lower()

        # Check for key terms
        if truth_text and truth_text not in pred_text:
            return {
                "error": 0.6,
                "class": "factuality",
                "severity": "S2"
            }
        return {"error": 0.0}

    def citation_evaluator(prediction, ground_truth, context):
        """Check for proper citations."""
        has_sources = bool(ground_truth and ground_truth.get("source_refs"))
        has_citations = "citation" in str(prediction).lower() or "ref" in str(prediction).lower()

        if has_sources and not has_citations:
            return {
                "error": 0.4,
                "class": "faithfulness",
                "severity": "S2"
            }
        return {"error": 0.0}

    return {
        "factuality": factuality_evaluator,
        "citation": citation_evaluator
    }


def main():
    """Run example learning loop."""
    print("∇θ Echo Harmonic Learning - Example")
    print("=" * 50)
    print()

    # Initialize the learning loop
    loop = EchoHarmonicLearningLoop(
        error_threshold=0.3,
        harmony_threshold=0.5,
        target_exploration=0.5
    )

    # Register evaluators
    for name, evaluator in create_evaluators().items():
        loop.register_evaluator(name, evaluator)

    # Register playbooks
    factuality_pb = FactualityPlaybook()
    reasoning_pb = ReasoningPlaybook()
    loop.register_playbook("retrieval_patch", factuality_pb.execute)
    loop.register_playbook("tool_insertion", reasoning_pb.execute)

    # Register policies
    loop.register_policy(Policy(
        name="balanced",
        prompt_template="Answer the question with citations.",
        tools=["retrieval"],
        model_config={"temperature": 0.3}
    ))

    loop.register_policy(Policy(
        name="exploratory",
        prompt_template="Explore multiple perspectives on the question.",
        tools=["retrieval", "web_search"],
        model_config={"temperature": 0.7}
    ))

    loop.register_policy(Policy(
        name="precise",
        prompt_template="Provide a precise, verified answer.",
        tools=["retrieval", "calculator"],
        model_config={"temperature": 0.1}
    ))

    # Example inputs
    inputs = [
        (
            {"query": "What is the capital of France?"},
            {"task": "factual_qa", "domain": "geography"},
            {"text": "Paris", "source_refs": ["doc://geography/france"]}
        ),
        (
            {"query": "Calculate the compound interest on $1000 at 5% for 3 years"},
            {"task": "calculation", "requires_tools": True},
            {"text": "$1157.63", "source_refs": []}
        ),
        (
            {"query": "Explain quantum entanglement"},
            {"task": "explanation", "expected_depth": "moderate"},
            {"text": "Quantum entanglement is a phenomenon...", "source_refs": ["doc://physics/quantum"]}
        )
    ]

    # Run the learning loop
    print("Running learning loop iterations...")
    print()

    for i, (input_data, context, ground_truth) in enumerate(inputs):
        print(f"Iteration {i + 1}: {context.get('task', 'unknown')}")
        print("-" * 40)

        result = loop.iterate(input_data, context, ground_truth)

        # Report results
        harmony = result.harmony_state
        print(f"  Harmony Score: {harmony.harmony_score:.3f}")
        print(f"  Error: {harmony.error:.3f}")
        print(f"  Phase Alignment (φ): {harmony.phi:.3f}")
        print(f"  Exploration (ξ): {harmony.xi:.3f}")
        print(f"  Target (ξ*): {harmony.xi_star:.3f}")

        if result.should_handoff:
            print(f"  ⚠ Handoff required: {result.handoff_reason}")

        if result.event:
            print(f"  📝 Learning event created: {result.event.id[:8]}...")
            print(f"     Error classes: {result.event.error_classes}")

        if result.correction:
            print(f"  🔧 Correction queued: {result.correction.intervention.type}")

        print()

    # Final state report
    print("=" * 50)
    print("Final Loop State:")
    state = loop.get_state()
    print(f"  Total events: {state['total_events']}")
    print(f"  Total corrections: {state['total_corrections']}")
    print(f"  System healthy: {state['healthy']}")

    if state['oscillation'].get('current_harmony'):
        print(f"  Current harmony: {state['oscillation']['current_harmony']:.3f}")

    print()
    print("∇θ — chain sealed, truth preserved")


if __name__ == "__main__":
    main()
