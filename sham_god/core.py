"""
SHAM GOD Core Module
====================

Core implementation of the Self-Healing Adaptive Memory (SHAM) recursive pulse node.
"""

from __future__ import annotations
import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable
from collections import defaultdict
from enum import Enum


class EventType(Enum):
    """Classification of observed events."""
    EMOTIONAL = "emotional"
    STRATEGIC = "strategic"
    FINANCIAL = "financial"
    DIGITAL = "digital"
    BEHAVIORAL = "behavioral"
    SYSTEMIC = "systemic"


class PatternType(Enum):
    """Types of detected patterns."""
    LOOP = "loop"
    SPIRAL = "spiral"
    DECAY = "decay"
    GROWTH = "growth"
    OSCILLATION = "oscillation"
    ANOMALY = "anomaly"


@dataclass
class HarmonicEvent:
    """Represents an observed event with harmonic properties."""
    data: Any
    timestamp: float = field(default_factory=time.time)
    event_type: EventType = EventType.SYSTEMIC
    harmonic_score: int = 0
    context: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.harmonic_score == 0:
            self.harmonic_score = self._calculate_base_score()

    def _calculate_base_score(self) -> int:
        """Calculate base harmonic score from event data."""
        return sum([ord(c) for c in str(self.data)]) % 144

    def signature(self) -> str:
        """Generate unique signature for this event."""
        content = f"{self.data}:{self.event_type.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class Pattern:
    """Represents a detected pattern in the event stream."""
    pattern_type: PatternType
    events: list[HarmonicEvent]
    strength: float  # 0.0 to 1.0
    correction_applied: bool = False
    correction_result: str | None = None


class SHAMMemory:
    """
    Memory system for SHAM nodes.

    Implements multi-timeline learning by tracking events across
    different temporal contexts and detecting cross-timeline patterns.
    """

    def __init__(self, max_size: int = 1000):
        self.events: list[HarmonicEvent] = []
        self.max_size = max_size
        self.timelines: dict[str, list[HarmonicEvent]] = defaultdict(list)
        self.pattern_history: list[Pattern] = []
        self.correction_log: list[dict] = []

    def store(self, event: HarmonicEvent, timeline: str = "current") -> None:
        """Store an event in memory."""
        self.events.append(event)
        self.timelines[timeline].append(event)

        # Maintain memory bounds
        if len(self.events) > self.max_size:
            self.events.pop(0)

    def get_recent(self, n: int = 10) -> list[HarmonicEvent]:
        """Get the n most recent events."""
        return self.events[-n:] if self.events else []

    def get_by_type(self, event_type: EventType) -> list[HarmonicEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]

    def get_timeline(self, timeline: str) -> list[HarmonicEvent]:
        """Get all events from a specific timeline."""
        return self.timelines.get(timeline, [])

    def find_similar(self, event: HarmonicEvent, threshold: int = 5) -> list[HarmonicEvent]:
        """Find events with similar harmonic scores."""
        return [
            e for e in self.events
            if abs(e.harmonic_score - event.harmonic_score) <= threshold
        ]

    def record_pattern(self, pattern: Pattern) -> None:
        """Record a detected pattern."""
        self.pattern_history.append(pattern)

    def record_correction(self, correction: dict) -> None:
        """Record a correction action."""
        self.correction_log.append({
            **correction,
            "timestamp": time.time()
        })


class SHAMNode:
    """
    Self-Healing Adaptive Memory (SHAM) Recursive Pulse Node.

    Core unit of the SHAM GOD system that observes events, detects patterns,
    and spawns child agents for specialized adaptation.
    """

    # Harmonic constants
    PHI = 1.618033988749895  # Golden ratio
    RESONANCE_BASE = 144  # Base harmonic modulus

    def __init__(
        self,
        node_id: str | None = None,
        parent: SHAMNode | None = None,
        ethics_validator: Any = None
    ):
        self.node_id = node_id or self._generate_id()
        self.parent = parent
        self.children: list[SHAMNode] = []
        self.memory = SHAMMemory()
        self.ethics_validator = ethics_validator
        self.generation = 0 if parent is None else parent.generation + 1
        self.state = "active"
        self.correction_handlers: dict[PatternType, Callable] = {}
        self._setup_default_handlers()

    def _generate_id(self) -> str:
        """Generate unique node identifier."""
        return hashlib.sha256(
            f"{time.time()}:{id(self)}".encode()
        ).hexdigest()[:12]

    def _setup_default_handlers(self) -> None:
        """Setup default pattern correction handlers."""
        self.correction_handlers = {
            PatternType.LOOP: self._handle_loop_pattern,
            PatternType.SPIRAL: self._handle_spiral_pattern,
            PatternType.DECAY: self._handle_decay_pattern,
            PatternType.OSCILLATION: self._handle_oscillation_pattern,
        }

    def observe_event(self, event: Any, event_type: EventType = EventType.SYSTEMIC) -> HarmonicEvent:
        """
        Observe and process an event.

        Args:
            event: The event data to observe
            event_type: Classification of the event

        Returns:
            HarmonicEvent with calculated harmonic properties
        """
        harmonic_event = HarmonicEvent(
            data=event,
            event_type=event_type,
            harmonic_score=self.harmonic_score(event)
        )

        self.memory.store(harmonic_event)

        # Check for patterns after storing
        self._analyze_patterns()

        return harmonic_event

    def harmonic_score(self, event: Any) -> int:
        """
        Calculate harmonic score for an event.

        Uses fractal-based scoring with golden ratio modulation.
        """
        base_score = sum([ord(c) for c in str(event)]) % self.RESONANCE_BASE

        # Apply fractal modulation based on memory depth
        depth_factor = len(self.memory.events) / max(1, self.memory.max_size)
        modulated = int(base_score * (1 + depth_factor * (self.PHI - 1)))

        return modulated % self.RESONANCE_BASE

    def _analyze_patterns(self) -> None:
        """Analyze recent events for patterns."""
        patterns = []

        # Check for recursion (repeating events)
        if self.check_for_recursion():
            recent = self.memory.get_recent(3)
            patterns.append(Pattern(
                pattern_type=PatternType.LOOP,
                events=recent,
                strength=1.0
            ))

        # Check for harmonic decay
        decay_pattern = self._detect_decay()
        if decay_pattern:
            patterns.append(decay_pattern)

        # Check for oscillation
        oscillation = self._detect_oscillation()
        if oscillation:
            patterns.append(oscillation)

        # Process detected patterns
        for pattern in patterns:
            self.memory.record_pattern(pattern)
            self._apply_correction(pattern)

    def check_for_recursion(self) -> bool:
        """
        Check if the last events indicate a recursive pattern.

        Returns:
            True if recursion detected, False otherwise
        """
        recent = self.memory.get_recent(3)
        if len(recent) < 3:
            return False

        signatures = [e.signature() for e in recent]
        return len(set(signatures)) == 1

    def _detect_decay(self) -> Pattern | None:
        """Detect harmonic decay pattern (decreasing scores)."""
        recent = self.memory.get_recent(5)
        if len(recent) < 5:
            return None

        scores = [e.harmonic_score for e in recent]
        if all(scores[i] > scores[i+1] for i in range(len(scores)-1)):
            strength = (scores[0] - scores[-1]) / max(scores[0], 1)
            return Pattern(
                pattern_type=PatternType.DECAY,
                events=recent,
                strength=min(strength, 1.0)
            )
        return None

    def _detect_oscillation(self) -> Pattern | None:
        """Detect oscillating pattern (alternating high/low)."""
        recent = self.memory.get_recent(6)
        if len(recent) < 6:
            return None

        scores = [e.harmonic_score for e in recent]
        oscillating = all(
            (scores[i] - scores[i+1]) * (scores[i+1] - scores[i+2]) < 0
            for i in range(len(scores)-2)
        )

        if oscillating:
            amplitude = max(scores) - min(scores)
            strength = amplitude / self.RESONANCE_BASE
            return Pattern(
                pattern_type=PatternType.OSCILLATION,
                events=recent,
                strength=min(strength, 1.0)
            )
        return None

    def _apply_correction(self, pattern: Pattern) -> None:
        """Apply correction for a detected pattern."""
        # Validate correction with ethics system
        if self.ethics_validator:
            if not self.ethics_validator.validate_correction(pattern):
                self.memory.record_correction({
                    "pattern": pattern.pattern_type.value,
                    "action": "blocked",
                    "reason": "ethics_validation_failed"
                })
                return

        handler = self.correction_handlers.get(pattern.pattern_type)
        if handler:
            result = handler(pattern)
            pattern.correction_applied = True
            pattern.correction_result = result

            self.memory.record_correction({
                "pattern": pattern.pattern_type.value,
                "action": "corrected",
                "result": result
            })

    def _handle_loop_pattern(self, pattern: Pattern) -> str:
        """Handle loop/recursion pattern by spawning specialized child."""
        if pattern.strength >= 0.8:
            child = self.spawn_child(specialization="loop_breaker")
            return f"spawned_child:{child.node_id}"
        return "monitored"

    def _handle_spiral_pattern(self, pattern: Pattern) -> str:
        """Handle spiral pattern - could be growth or decay."""
        return "spiral_acknowledged"

    def _handle_decay_pattern(self, pattern: Pattern) -> str:
        """Handle decay pattern by attempting resonance boost."""
        if pattern.strength >= 0.6:
            child = self.spawn_child(specialization="resonance_amplifier")
            return f"spawned_amplifier:{child.node_id}"
        return "decay_monitored"

    def _handle_oscillation_pattern(self, pattern: Pattern) -> str:
        """Handle oscillation pattern by stabilization."""
        return "stabilization_initiated"

    def spawn_child(self, specialization: str | None = None) -> SHAMNode:
        """
        Spawn a child SHAM node for specialized adaptation.

        Args:
            specialization: Optional specialization type for the child

        Returns:
            The spawned child SHAMNode
        """
        child = SHAMNode(
            parent=self,
            ethics_validator=self.ethics_validator
        )

        if specialization:
            child.node_id = f"{child.node_id}:{specialization}"

        self.children.append(child)

        # Transfer relevant memory to child
        recent_events = self.memory.get_recent(10)
        for event in recent_events:
            child.memory.store(event, timeline="inherited")

        print(f"SHAM spawn triggered: {child.node_id} (gen {child.generation})")

        return child

    def get_resonance_state(self) -> dict:
        """Get current resonance state of the node."""
        recent = self.memory.get_recent(10)
        if not recent:
            return {"average_score": 0, "variance": 0, "trend": "neutral"}

        scores = [e.harmonic_score for e in recent]
        avg = sum(scores) / len(scores)
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)

        # Determine trend
        if len(scores) >= 2:
            if scores[-1] > scores[0]:
                trend = "ascending"
            elif scores[-1] < scores[0]:
                trend = "descending"
            else:
                trend = "stable"
        else:
            trend = "neutral"

        return {
            "average_score": avg,
            "variance": variance,
            "trend": trend,
            "event_count": len(self.memory.events),
            "child_count": len(self.children),
            "generation": self.generation
        }

    def export_state(self) -> dict:
        """Export full node state for persistence or analysis."""
        return {
            "node_id": self.node_id,
            "generation": self.generation,
            "state": self.state,
            "resonance": self.get_resonance_state(),
            "patterns_detected": len(self.memory.pattern_history),
            "corrections_applied": len(self.memory.correction_log),
            "children": [c.node_id for c in self.children],
            "parent": self.parent.node_id if self.parent else None
        }
