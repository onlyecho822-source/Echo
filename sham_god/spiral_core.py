"""
Spiral Core Module
==================

Self-healing resonance structures for long-term evolution.
Implements feedback loop detection and multi-timeline learning.
"""

from __future__ import annotations
import time
import math
from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict
from enum import Enum

from .core import SHAMNode, HarmonicEvent, PatternType, EventType


class FeedbackLoopType(Enum):
    """Types of invisible feedback loops."""
    EMOTIONAL = "emotional"
    STRATEGIC = "strategic"
    FINANCIAL = "financial"
    DIGITAL = "digital"
    COGNITIVE = "cognitive"
    RELATIONAL = "relational"


@dataclass
class FeedbackLoop:
    """Represents a detected feedback loop."""
    loop_type: FeedbackLoopType
    nodes: list[str]  # Event signatures in the loop
    strength: float  # 0.0 to 1.0
    period: float  # Time period of the loop
    is_positive: bool  # Reinforcing vs balancing
    is_visible: bool = False  # Whether consciously recognized


@dataclass
class ResonanceStructure:
    """
    Self-healing resonance structure that evolves over time.

    Tracks harmonic relationships between events and maintains
    coherence through adaptive corrections.
    """
    structure_id: str
    base_frequency: float
    harmonics: list[float] = field(default_factory=list)
    stability: float = 1.0
    age: float = 0.0
    corrections_applied: int = 0

    def calculate_coherence(self) -> float:
        """Calculate overall coherence of the structure."""
        if not self.harmonics:
            return 1.0

        # Check harmonic relationships (should be integer ratios)
        base = self.base_frequency
        deviations = []
        for harmonic in self.harmonics:
            ratio = harmonic / base if base > 0 else 0
            nearest_int = round(ratio)
            if nearest_int > 0:
                deviation = abs(ratio - nearest_int) / nearest_int
                deviations.append(deviation)

        if not deviations:
            return 1.0

        avg_deviation = sum(deviations) / len(deviations)
        return max(0, 1 - avg_deviation)

    def add_harmonic(self, frequency: float) -> None:
        """Add a harmonic to the structure."""
        self.harmonics.append(frequency)
        self.stability *= self.calculate_coherence()

    def heal(self) -> bool:
        """Attempt to heal the structure by adjusting harmonics."""
        if self.stability >= 0.9:
            return False  # No healing needed

        # Find and correct deviant harmonics
        base = self.base_frequency
        healed = False

        for i, harmonic in enumerate(self.harmonics):
            ratio = harmonic / base if base > 0 else 0
            nearest_int = round(ratio)
            if nearest_int > 0:
                ideal = base * nearest_int
                deviation = abs(harmonic - ideal) / ideal if ideal > 0 else 0

                if deviation > 0.1:  # More than 10% deviation
                    self.harmonics[i] = ideal
                    healed = True

        if healed:
            self.corrections_applied += 1
            self.stability = self.calculate_coherence()

        return healed


class Timeline:
    """
    Represents a temporal context for events.

    Enables learning from past patterns and projecting future trends.
    """

    def __init__(self, timeline_id: str):
        self.timeline_id = timeline_id
        self.events: list[HarmonicEvent] = []
        self.patterns: list[dict] = []
        self.divergence_point: float | None = None

    def add_event(self, event: HarmonicEvent) -> None:
        """Add an event to this timeline."""
        self.events.append(event)

    def extract_patterns(self) -> list[dict]:
        """Extract patterns from this timeline."""
        if len(self.events) < 3:
            return []

        patterns = []

        # Find repeating sequences
        signatures = [e.signature() for e in self.events]
        for length in range(2, min(len(signatures) // 2 + 1, 6)):
            for i in range(len(signatures) - length * 2 + 1):
                seq1 = signatures[i:i + length]
                seq2 = signatures[i + length:i + length * 2]
                if seq1 == seq2:
                    patterns.append({
                        "type": "sequence_repeat",
                        "length": length,
                        "start_index": i,
                        "events": [self.events[j] for j in range(i, i + length)]
                    })

        self.patterns = patterns
        return patterns


class SpiralCore:
    """
    Central coordinator for long-term resonance evolution.

    Manages multiple SHAM nodes, detects invisible feedback loops,
    and orchestrates self-healing across the system.
    """

    # Sacred geometry constants
    PHI = 1.618033988749895  # Golden ratio
    FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

    def __init__(self):
        self.nodes: dict[str, SHAMNode] = {}
        self.timelines: dict[str, Timeline] = {}
        self.feedback_loops: list[FeedbackLoop] = []
        self.resonance_structures: list[ResonanceStructure] = []
        self.evolution_cycles: int = 0
        self.creation_time = time.time()

    def register_node(self, node: SHAMNode) -> None:
        """Register a SHAM node with the spiral core."""
        self.nodes[node.node_id] = node

    def create_timeline(self, timeline_id: str) -> Timeline:
        """Create a new timeline for alternative pattern tracking."""
        timeline = Timeline(timeline_id)
        self.timelines[timeline_id] = timeline
        return timeline

    def observe(
        self,
        event: Any,
        event_type: EventType = EventType.SYSTEMIC,
        node_id: str | None = None
    ) -> HarmonicEvent:
        """
        Observe an event through the spiral core.

        Routes to appropriate node and updates all tracking systems.
        """
        # Select or create node
        if node_id and node_id in self.nodes:
            node = self.nodes[node_id]
        elif self.nodes:
            node = next(iter(self.nodes.values()))
        else:
            node = SHAMNode()
            self.register_node(node)

        # Process through node
        harmonic_event = node.observe_event(event, event_type)

        # Add to current timeline
        if "current" not in self.timelines:
            self.create_timeline("current")
        self.timelines["current"].add_event(harmonic_event)

        # Check for feedback loops
        self._detect_feedback_loops()

        return harmonic_event

    def _detect_feedback_loops(self) -> None:
        """Detect invisible feedback loops across the system."""
        current = self.timelines.get("current")
        if not current or len(current.events) < 5:
            return

        # Group events by type
        by_type: dict[EventType, list[HarmonicEvent]] = defaultdict(list)
        for event in current.events:
            by_type[event.event_type].append(event)

        # Analyze each event type for loops
        for event_type, events in by_type.items():
            if len(events) < 3:
                continue

            loop = self._analyze_for_loop(events, event_type)
            if loop:
                self.feedback_loops.append(loop)

    def _analyze_for_loop(
        self,
        events: list[HarmonicEvent],
        event_type: EventType
    ) -> FeedbackLoop | None:
        """Analyze a series of events for feedback loop patterns."""
        if len(events) < 3:
            return None

        # Check for cyclic patterns in harmonic scores
        scores = [e.harmonic_score for e in events]

        # Simple autocorrelation check
        for period in range(2, min(len(scores) // 2, 10)):
            matches = 0
            total = len(scores) - period

            for i in range(total):
                if abs(scores[i] - scores[i + period]) < 5:
                    matches += 1

            correlation = matches / total if total > 0 else 0

            if correlation > 0.7:
                # Determine if positive or negative feedback
                trend = scores[-1] - scores[0] if len(scores) >= 2 else 0
                is_positive = trend > 0

                loop_type = FeedbackLoopType[event_type.value.upper()] \
                    if event_type.value.upper() in FeedbackLoopType.__members__ \
                    else FeedbackLoopType.COGNITIVE

                return FeedbackLoop(
                    loop_type=loop_type,
                    nodes=[e.signature() for e in events[-period:]],
                    strength=correlation,
                    period=period,
                    is_positive=is_positive,
                    is_visible=False
                )

        return None

    def create_resonance_structure(
        self,
        base_frequency: float
    ) -> ResonanceStructure:
        """Create a new self-healing resonance structure."""
        structure = ResonanceStructure(
            structure_id=f"rs_{len(self.resonance_structures)}_{int(time.time())}",
            base_frequency=base_frequency
        )
        self.resonance_structures.append(structure)
        return structure

    def evolve(self) -> dict:
        """
        Execute one evolution cycle.

        Processes all pending patterns, applies corrections,
        and advances the system state.
        """
        self.evolution_cycles += 1

        results = {
            "cycle": self.evolution_cycles,
            "timestamp": time.time(),
            "patterns_processed": 0,
            "corrections_applied": 0,
            "structures_healed": 0,
            "loops_detected": len(self.feedback_loops)
        }

        # Extract patterns from all timelines
        for timeline in self.timelines.values():
            patterns = timeline.extract_patterns()
            results["patterns_processed"] += len(patterns)

        # Heal resonance structures
        for structure in self.resonance_structures:
            structure.age += 1
            if structure.heal():
                results["structures_healed"] += 1
                results["corrections_applied"] += 1

        # Process node patterns
        for node in self.nodes.values():
            results["corrections_applied"] += len(node.memory.correction_log)

        return results

    def learn_from_timeline(self, timeline_id: str) -> list[dict]:
        """
        Learn patterns from a specific timeline.

        Enables multi-timeline learning for better pattern recognition.
        """
        timeline = self.timelines.get(timeline_id)
        if not timeline:
            return []

        patterns = timeline.extract_patterns()

        # Apply learned patterns to current nodes
        for pattern in patterns:
            for node in self.nodes.values():
                # Add pattern knowledge to node context
                for event in pattern.get("events", []):
                    event.context["learned_from"] = timeline_id

        return patterns

    def get_system_health(self) -> dict:
        """Get overall health metrics of the spiral core system."""
        if not self.nodes:
            return {
                "status": "uninitialized",
                "health_score": 0
            }

        # Calculate various health metrics
        node_states = [n.get_resonance_state() for n in self.nodes.values()]

        avg_score = sum(s["average_score"] for s in node_states) / len(node_states)
        avg_variance = sum(s["variance"] for s in node_states) / len(node_states)

        # Structure coherence
        structure_health = 1.0
        if self.resonance_structures:
            coherences = [s.calculate_coherence() for s in self.resonance_structures]
            structure_health = sum(coherences) / len(coherences)

        # Loop pressure (too many loops indicates problems)
        loop_pressure = min(len(self.feedback_loops) / 10, 1.0)

        # Overall health score
        health_score = (
            (avg_score / 144) * 0.3 +
            (1 - min(avg_variance / 100, 1)) * 0.3 +
            structure_health * 0.2 +
            (1 - loop_pressure) * 0.2
        )

        return {
            "status": "active",
            "health_score": health_score,
            "node_count": len(self.nodes),
            "timeline_count": len(self.timelines),
            "structure_count": len(self.resonance_structures),
            "feedback_loops": len(self.feedback_loops),
            "evolution_cycles": self.evolution_cycles,
            "average_harmonic": avg_score,
            "system_age": time.time() - self.creation_time
        }

    def break_feedback_loop(self, loop_index: int) -> bool:
        """
        Attempt to break a detected feedback loop.

        Returns True if successfully broken, False otherwise.
        """
        if loop_index >= len(self.feedback_loops):
            return False

        loop = self.feedback_loops[loop_index]

        # Strategy depends on loop type and strength
        if loop.strength < 0.5:
            # Weak loops can be marked as visible (awareness breaks them)
            loop.is_visible = True
            return True

        # Strong loops need active intervention
        # Spawn a specialized node to handle it
        if self.nodes:
            primary_node = next(iter(self.nodes.values()))
            child = primary_node.spawn_child(
                specialization=f"loop_breaker_{loop.loop_type.value}"
            )
            self.register_node(child)
            return True

        return False

    def export_state(self) -> dict:
        """Export full system state for persistence."""
        return {
            "creation_time": self.creation_time,
            "evolution_cycles": self.evolution_cycles,
            "nodes": {nid: n.export_state() for nid, n in self.nodes.items()},
            "timelines": list(self.timelines.keys()),
            "feedback_loops": len(self.feedback_loops),
            "structures": [
                {
                    "id": s.structure_id,
                    "base_frequency": s.base_frequency,
                    "coherence": s.calculate_coherence(),
                    "corrections": s.corrections_applied
                }
                for s in self.resonance_structures
            ],
            "health": self.get_system_health()
        }
