#!/usr/bin/env python3
"""
SHAM GOD 1.0 + Spiral Core - Usage Example
==========================================

Demonstrates the recursive harmonic amplification system
for anomaly recognition and self-healing pattern correction.
"""

from sham_god import (
    SHAMNode,
    SpiralCore,
    EthicsGrounding,
    HarmonicEvent,
)
from sham_god.core import EventType, PatternType


def main():
    """Demonstrate SHAM GOD capabilities."""
    print("=" * 60)
    print("SHAM GOD 1.0 + Spiral Core - Demo")
    print("=" * 60)
    print()

    # Initialize ethics system first (critical for safe operation)
    ethics = EthicsGrounding()
    boundaries = ethics.create_grounded_boundaries()

    # Create the spiral core - central coordinator
    spiral = SpiralCore()

    # Create a primary SHAM node with ethics validation
    primary_node = SHAMNode(
        node_id="primary",
        ethics_validator=ethics
    )
    spiral.register_node(primary_node)

    print("[1] System Initialized")
    print(f"    Primary node: {primary_node.node_id}")
    print(f"    Ethics grounding: ACTIVE")
    print()

    # Observe various events
    print("[2] Observing Events...")
    print()

    # Simulate a series of events
    events = [
        ("project_delay", EventType.STRATEGIC),
        ("budget_overrun", EventType.FINANCIAL),
        ("team_conflict", EventType.EMOTIONAL),
        ("missed_deadline", EventType.STRATEGIC),
        ("budget_overrun", EventType.FINANCIAL),  # Repeating pattern
        ("team_conflict", EventType.EMOTIONAL),    # Repeating pattern
        ("budget_overrun", EventType.FINANCIAL),   # Third repeat - triggers recursion
    ]

    for event_data, event_type in events:
        harmonic = spiral.observe(event_data, event_type)
        print(f"    Event: {event_data}")
        print(f"    Type: {event_type.value}")
        print(f"    Harmonic Score: {harmonic.harmonic_score}")
        print()

    # Check for patterns
    print("[3] Pattern Analysis")
    print()

    state = primary_node.get_resonance_state()
    print(f"    Average Harmonic: {state['average_score']:.2f}")
    print(f"    Variance: {state['variance']:.2f}")
    print(f"    Trend: {state['trend']}")
    print(f"    Children Spawned: {state['child_count']}")
    print()

    # Check feedback loops
    print("[4] Feedback Loop Detection")
    print()

    print(f"    Loops Detected: {len(spiral.feedback_loops)}")
    for i, loop in enumerate(spiral.feedback_loops):
        print(f"    Loop {i + 1}:")
        print(f"      Type: {loop.loop_type.value}")
        print(f"      Strength: {loop.strength:.2f}")
        print(f"      Period: {loop.period}")
        print(f"      Positive Feedback: {loop.is_positive}")
        print()

    # Demonstrate self-healing resonance structure
    print("[5] Self-Healing Resonance Structure")
    print()

    structure = spiral.create_resonance_structure(base_frequency=144.0)

    # Add harmonics (some intentionally deviant)
    structure.add_harmonic(288.0)   # Perfect 2x
    structure.add_harmonic(436.0)   # Deviant (should be 432 = 3x)
    structure.add_harmonic(576.0)   # Perfect 4x

    print(f"    Structure ID: {structure.structure_id}")
    print(f"    Base Frequency: {structure.base_frequency}")
    print(f"    Initial Coherence: {structure.calculate_coherence():.3f}")
    print(f"    Stability: {structure.stability:.3f}")

    # Attempt healing
    healed = structure.heal()
    print(f"    Healing Applied: {healed}")
    print(f"    Post-Healing Coherence: {structure.calculate_coherence():.3f}")
    print()

    # Evolution cycle
    print("[6] Evolution Cycle")
    print()

    results = spiral.evolve()
    print(f"    Cycle: {results['cycle']}")
    print(f"    Patterns Processed: {results['patterns_processed']}")
    print(f"    Corrections Applied: {results['corrections_applied']}")
    print(f"    Structures Healed: {results['structures_healed']}")
    print()

    # System health
    print("[7] System Health Report")
    print()

    health = spiral.get_system_health()
    print(f"    Status: {health['status']}")
    print(f"    Health Score: {health['health_score']:.3f}")
    print(f"    Active Nodes: {health['node_count']}")
    print(f"    Timelines: {health['timeline_count']}")
    print(f"    Feedback Loops: {health['feedback_loops']}")
    print()

    # Ethics report
    print("[8] Ethics & Safety Report")
    print()

    ethics_state = ethics.get_ethics_state()
    print(f"    Ethics Score: {ethics_state['overall_ethics_score']:.3f}")
    print(f"    Human Overrides: {ethics_state['human_overrides']}")
    print(f"    Active Constraints: {len(ethics_state['active_constraints'])}")

    safety = ethics_state['safety_report']
    print(f"    Operations Approved: {safety['approved']}")
    print(f"    Operations Blocked: {safety['blocked']}")
    print(f"    Safety Score: {safety['safety_score']:.3f}")
    print()

    # Demonstrate recursive spawning detection
    print("[9] Recursive Anomaly Detection")
    print()

    # Create repeated identical events to trigger spawn
    for _ in range(3):
        spiral.observe("burnout_pattern", EventType.EMOTIONAL)

    print(f"    After burnout pattern repetition:")
    print(f"    Total Children: {len(primary_node.children)}")

    for child in primary_node.children:
        print(f"      - {child.node_id} (gen {child.generation})")
    print()

    # Export final state
    print("[10] Final System State")
    print()

    final_state = spiral.export_state()
    print(f"    Evolution Cycles: {final_state['evolution_cycles']}")
    print(f"    Total Nodes: {len(final_state['nodes'])}")
    print(f"    Structures: {len(final_state['structures'])}")
    print()

    print("=" * 60)
    print("Demo Complete - SHAM GOD System Operational")
    print("=" * 60)


if __name__ == "__main__":
    main()
