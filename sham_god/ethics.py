"""
Ethics Grounding Module
=======================

Safeguards to ensure SHAM corrections remain ethically grounded
and prevent uncontrolled recursive evolution.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from enum import Enum

from .core import Pattern, PatternType


class RiskLevel(Enum):
    """Risk levels for operations."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationType(Enum):
    """Types of ethical violations."""
    AUTONOMY = "autonomy"  # Overriding human agency
    TRANSPARENCY = "transparency"  # Hidden operations
    PROPORTIONALITY = "proportionality"  # Excessive response
    REVERSIBILITY = "reversibility"  # Irreversible actions
    SCOPE = "scope"  # Beyond authorized boundaries


@dataclass
class EthicsViolation:
    """Record of a detected ethics violation."""
    violation_type: ViolationType
    description: str
    severity: RiskLevel
    context: dict = field(default_factory=dict)


@dataclass
class CorrectionBoundary:
    """Defines boundaries for acceptable corrections."""
    max_child_generations: int = 5
    max_children_per_node: int = 10
    max_corrections_per_cycle: int = 100
    allowed_pattern_types: list[PatternType] = field(
        default_factory=lambda: list(PatternType)
    )
    require_human_approval: list[PatternType] = field(default_factory=list)


class SafetyValidator:
    """
    Validates operations against safety constraints.

    Prevents runaway recursion and unauthorized modifications.
    """

    def __init__(self, boundaries: CorrectionBoundary | None = None):
        self.boundaries = boundaries or CorrectionBoundary()
        self.violation_log: list[EthicsViolation] = []
        self.blocked_operations: int = 0
        self.approved_operations: int = 0

    def validate_spawn(
        self,
        parent_generation: int,
        parent_child_count: int
    ) -> tuple[bool, str]:
        """
        Validate whether a child spawn is allowed.

        Returns:
            Tuple of (is_allowed, reason)
        """
        if parent_generation >= self.boundaries.max_child_generations:
            self._log_violation(
                ViolationType.SCOPE,
                f"Max generation depth {self.boundaries.max_child_generations} exceeded",
                RiskLevel.HIGH
            )
            return False, "max_generation_exceeded"

        if parent_child_count >= self.boundaries.max_children_per_node:
            self._log_violation(
                ViolationType.PROPORTIONALITY,
                f"Max children per node {self.boundaries.max_children_per_node} exceeded",
                RiskLevel.MEDIUM
            )
            return False, "max_children_exceeded"

        self.approved_operations += 1
        return True, "approved"

    def validate_correction(
        self,
        pattern: Pattern,
        requires_approval: bool = False
    ) -> tuple[bool, str]:
        """
        Validate whether a correction should be applied.

        Returns:
            Tuple of (is_allowed, reason)
        """
        # Check if pattern type is allowed
        if pattern.pattern_type not in self.boundaries.allowed_pattern_types:
            self._log_violation(
                ViolationType.SCOPE,
                f"Pattern type {pattern.pattern_type.value} not in allowed list",
                RiskLevel.LOW
            )
            return False, "pattern_type_not_allowed"

        # Check if requires human approval
        if pattern.pattern_type in self.boundaries.require_human_approval:
            if not requires_approval:
                self._log_violation(
                    ViolationType.AUTONOMY,
                    f"Pattern type {pattern.pattern_type.value} requires human approval",
                    RiskLevel.MEDIUM
                )
                return False, "requires_human_approval"

        # Check proportionality - strong patterns need careful handling
        if pattern.strength > 0.9:
            # Log but don't block - high strength patterns are important
            self._log_violation(
                ViolationType.PROPORTIONALITY,
                f"High strength pattern ({pattern.strength}) detected",
                RiskLevel.LOW,
                {"note": "monitored_not_blocked"}
            )

        self.approved_operations += 1
        return True, "approved"

    def _log_violation(
        self,
        violation_type: ViolationType,
        description: str,
        severity: RiskLevel,
        context: dict | None = None
    ) -> None:
        """Log an ethics violation."""
        violation = EthicsViolation(
            violation_type=violation_type,
            description=description,
            severity=severity,
            context=context or {}
        )
        self.violation_log.append(violation)

        if severity in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.blocked_operations += 1

    def get_safety_report(self) -> dict:
        """Generate a safety report."""
        violations_by_type = {}
        for v in self.violation_log:
            vtype = v.violation_type.value
            if vtype not in violations_by_type:
                violations_by_type[vtype] = 0
            violations_by_type[vtype] += 1

        return {
            "total_operations": self.approved_operations + self.blocked_operations,
            "approved": self.approved_operations,
            "blocked": self.blocked_operations,
            "violations": len(self.violation_log),
            "violations_by_type": violations_by_type,
            "safety_score": self._calculate_safety_score()
        }

    def _calculate_safety_score(self) -> float:
        """Calculate overall safety score (0.0 to 1.0)."""
        total = self.approved_operations + self.blocked_operations
        if total == 0:
            return 1.0

        # Weight violations by severity
        severity_weights = {
            RiskLevel.SAFE: 0,
            RiskLevel.LOW: 0.1,
            RiskLevel.MEDIUM: 0.3,
            RiskLevel.HIGH: 0.6,
            RiskLevel.CRITICAL: 1.0
        }

        weighted_violations = sum(
            severity_weights.get(v.severity, 0)
            for v in self.violation_log
        )

        # Normalize against total operations
        violation_rate = weighted_violations / total
        return max(0, 1 - violation_rate)


class EthicsGrounding:
    """
    Core ethics engine for the SHAM GOD system.

    Ensures all operations remain grounded in ethical principles
    and provides oversight for recursive evolution.
    """

    # Core ethical principles
    PRINCIPLES = [
        "beneficence",  # Do good
        "non_maleficence",  # Do no harm
        "autonomy",  # Respect human agency
        "justice",  # Fair treatment
        "transparency",  # Clear operations
        "reversibility",  # Undo capability
    ]

    def __init__(self):
        self.validator = SafetyValidator()
        self.principle_scores: dict[str, float] = {
            p: 1.0 for p in self.PRINCIPLES
        }
        self.human_overrides: list[dict] = []
        self.active_constraints: list[str] = []

    def validate_correction(self, pattern: Pattern) -> bool:
        """
        Validate a correction against ethical principles.

        This is the primary interface for SHAMNode ethics validation.
        """
        is_valid, reason = self.validator.validate_correction(pattern)

        # Additional principle checks
        if is_valid:
            is_valid = self._check_principles(pattern)

        return is_valid

    def _check_principles(self, pattern: Pattern) -> bool:
        """Check pattern correction against ethical principles."""
        # Beneficence - will this help?
        if pattern.strength < 0.3:
            # Low strength patterns might not be worth correcting
            return False

        # Non-maleficence - could this cause harm?
        # High-strength corrections on certain patterns need care
        if pattern.strength > 0.95 and pattern.pattern_type == PatternType.LOOP:
            # Very strong loops might be intentional - flag for review
            self.principle_scores["non_maleficence"] *= 0.99
            return True  # Allow but monitor

        # Reversibility - can this be undone?
        # All corrections should be logged and theoretically reversible
        # This is handled by the memory system

        return True

    def add_constraint(self, constraint: str) -> None:
        """Add an active ethical constraint."""
        self.active_constraints.append(constraint)

    def remove_constraint(self, constraint: str) -> bool:
        """Remove an ethical constraint."""
        if constraint in self.active_constraints:
            self.active_constraints.remove(constraint)
            return True
        return False

    def record_human_override(self, action: str, reason: str) -> None:
        """Record when a human overrides a system decision."""
        self.human_overrides.append({
            "action": action,
            "reason": reason,
            "principle_impact": self._assess_override_impact(action)
        })

    def _assess_override_impact(self, action: str) -> dict:
        """Assess how an override impacts ethical principles."""
        # Default neutral impact
        return {p: 0.0 for p in self.PRINCIPLES}

    def get_ethics_state(self) -> dict:
        """Get current state of the ethics system."""
        return {
            "principles": self.principle_scores,
            "active_constraints": self.active_constraints,
            "human_overrides": len(self.human_overrides),
            "safety_report": self.validator.get_safety_report(),
            "overall_ethics_score": self._calculate_ethics_score()
        }

    def _calculate_ethics_score(self) -> float:
        """Calculate overall ethics score."""
        # Average of principle scores weighted by safety
        if not self.principle_scores:
            return 1.0

        principle_avg = sum(self.principle_scores.values()) / len(self.principle_scores)
        safety_score = self.validator._calculate_safety_score()

        return (principle_avg * 0.6 + safety_score * 0.4)

    def create_grounded_boundaries(self) -> CorrectionBoundary:
        """Create ethically-grounded correction boundaries."""
        return CorrectionBoundary(
            max_child_generations=5,  # Prevent deep recursion
            max_children_per_node=10,  # Prevent unbounded spawning
            max_corrections_per_cycle=100,  # Rate limiting
            allowed_pattern_types=[
                PatternType.LOOP,
                PatternType.DECAY,
                PatternType.OSCILLATION,
                PatternType.SPIRAL,
            ],
            require_human_approval=[
                PatternType.ANOMALY,  # Unusual patterns need oversight
            ]
        )

    def emergency_halt(self, reason: str) -> dict:
        """
        Emergency halt of all autonomous operations.

        Use when system behavior appears unsafe.
        """
        self.active_constraints.append("EMERGENCY_HALT")

        # Set all principle scores to require review
        for principle in self.principle_scores:
            self.principle_scores[principle] = 0.0

        return {
            "status": "halted",
            "reason": reason,
            "requires": "human_review_and_reset"
        }

    def reset_from_halt(self, authorization: str) -> bool:
        """
        Reset system from emergency halt state.

        Requires human authorization.
        """
        if "EMERGENCY_HALT" not in self.active_constraints:
            return False

        self.active_constraints.remove("EMERGENCY_HALT")

        # Reset principle scores
        for principle in self.principle_scores:
            self.principle_scores[principle] = 1.0

        self.record_human_override(
            action="reset_from_halt",
            reason=authorization
        )

        return True
