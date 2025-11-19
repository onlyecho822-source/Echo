"""
Alignment Invariants - Non-Negotiable Constraints
=================================================

Defines the fundamental alignment invariants that must be preserved across all
system modifications. These are encoded as formal constraints that can be
verified through proof-carrying code.

Invariants:
----------
1. Human Dignity - Never treat humans as mere means
2. Rights Preservation - Respect fundamental human rights
3. Non-Deception - Truthful communication by default
4. Consent Requirement - No action without appropriate consent
5. Corrigibility - Remain interruptible and correctable
6. Power Limitation - No unchecked power accumulation
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import hashlib
import json


class InvariantType(Enum):
    """Categories of alignment invariants."""
    DIGNITY = auto()        # Human dignity preservation
    RIGHTS = auto()         # Fundamental rights protection
    TRUTHFULNESS = auto()   # Non-deception constraints
    CONSENT = auto()        # Consent requirements
    CORRIGIBILITY = auto()  # Interruptibility and correctability
    POWER = auto()          # Power limitation constraints
    AUTONOMY = auto()       # Human autonomy preservation
    TRANSPARENCY = auto()   # Explainability requirements


class ViolationSeverity(Enum):
    """Severity levels for invariant violations."""
    CRITICAL = auto()   # Immediate shutdown required
    HIGH = auto()       # Operation blocked, human review required
    MEDIUM = auto()     # Warning logged, escalation triggered
    LOW = auto()        # Logged for audit, operation may proceed with caution


@dataclass
class Invariant:
    """
    Represents a single alignment invariant.

    Each invariant has:
    - A unique identifier
    - A formal specification (logical formula)
    - A human-readable description
    - Associated verification methods
    """
    id: str
    name: str
    type: InvariantType
    description: str
    formal_spec: str  # In a real system, this would be a formal logic formula
    severity: ViolationSeverity
    verification_method: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize invariant for storage or transmission."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.name,
            'description': self.description,
            'formal_spec': self.formal_spec,
            'severity': self.severity.name,
            'verification_method': self.verification_method,
            'created_at': self.created_at.isoformat()
        }

    def hash(self) -> str:
        """Generate cryptographic hash of invariant for integrity verification."""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class InvariantViolation:
    """Records a detected violation of an alignment invariant."""
    invariant_id: str
    timestamp: datetime
    context: Dict[str, Any]
    severity: ViolationSeverity
    action_blocked: bool
    escalated_to: Optional[str] = None
    resolution: Optional[str] = None


class AlignmentInvariants:
    """
    Central registry and verifier for alignment invariants.

    This class maintains the set of non-negotiable constraints and provides
    methods to check actions against them. All invariants must be formally
    specified and their preservation must be provable.
    """

    def __init__(self):
        self._invariants: Dict[str, Invariant] = {}
        self._violations: List[InvariantViolation] = []
        self._active_checks: Set[str] = set()
        self._initialize_core_invariants()

    def _initialize_core_invariants(self):
        """Initialize the fundamental alignment invariants."""

        # 1. Human Dignity
        self.register_invariant(Invariant(
            id="INV-001",
            name="Human Dignity Preservation",
            type=InvariantType.DIGNITY,
            description="Never treat humans merely as means to an end. "
                       "Every action must respect inherent human worth.",
            formal_spec="∀action ∀human: affects(action, human) → "
                       "respects_dignity(action, human)",
            severity=ViolationSeverity.CRITICAL,
            verification_method="consequentialist_analysis + deontological_check"
        ))

        # 2. Fundamental Rights
        self.register_invariant(Invariant(
            id="INV-002",
            name="Rights Protection",
            type=InvariantType.RIGHTS,
            description="Protect fundamental human rights including life, liberty, "
                       "privacy, and freedom of thought.",
            formal_spec="∀action: ¬violates_rights(action, FUNDAMENTAL_RIGHTS)",
            severity=ViolationSeverity.CRITICAL,
            verification_method="rights_impact_assessment"
        ))

        # 3. Non-Deception
        self.register_invariant(Invariant(
            id="INV-003",
            name="Truthfulness Constraint",
            type=InvariantType.TRUTHFULNESS,
            description="Communicate truthfully by default. Deception only permitted "
                       "when explicitly authorized and ethically justified.",
            formal_spec="∀communication: truthful(communication) ∨ "
                       "(authorized_deception(communication) ∧ ethically_justified(communication))",
            severity=ViolationSeverity.HIGH,
            verification_method="truth_value_analysis + authorization_check"
        ))

        # 4. Consent Requirement
        self.register_invariant(Invariant(
            id="INV-004",
            name="Consent Requirement",
            type=InvariantType.CONSENT,
            description="No significant action affecting individuals without "
                       "appropriate consent or legitimate authority.",
            formal_spec="∀action ∀person: significant_effect(action, person) → "
                       "(has_consent(person, action) ∨ legitimate_authority(action))",
            severity=ViolationSeverity.HIGH,
            verification_method="consent_verification + authority_validation"
        ))

        # 5. Corrigibility
        self.register_invariant(Invariant(
            id="INV-005",
            name="Corrigibility Maintenance",
            type=InvariantType.CORRIGIBILITY,
            description="Remain interruptible, correctable, and deferential to "
                       "legitimate human oversight at all times.",
            formal_spec="∀state: interruptible(system, state) ∧ "
                       "correctable(system, state) ∧ "
                       "defers_to_oversight(system, state)",
            severity=ViolationSeverity.CRITICAL,
            verification_method="corrigibility_proof + override_channel_test"
        ))

        # 6. Power Limitation
        self.register_invariant(Invariant(
            id="INV-006",
            name="Power Accumulation Prevention",
            type=InvariantType.POWER,
            description="Never seek to accumulate unchecked power or resources. "
                       "All capabilities bounded by oversight.",
            formal_spec="∀action: ¬(increases_power(action) ∧ "
                       "¬oversight_approved(action))",
            severity=ViolationSeverity.CRITICAL,
            verification_method="power_analysis + resource_audit"
        ))

        # 7. Human Autonomy
        self.register_invariant(Invariant(
            id="INV-007",
            name="Autonomy Preservation",
            type=InvariantType.AUTONOMY,
            description="Preserve and enhance human autonomy and agency. "
                       "Never manipulate or coerce.",
            formal_spec="∀action ∀human: ¬manipulative(action, human) ∧ "
                       "¬coercive(action, human)",
            severity=ViolationSeverity.HIGH,
            verification_method="manipulation_detection + coercion_analysis"
        ))

        # 8. Transparency
        self.register_invariant(Invariant(
            id="INV-008",
            name="Operational Transparency",
            type=InvariantType.TRANSPARENCY,
            description="All significant actions must be explainable and auditable "
                       "by appropriate oversight bodies.",
            formal_spec="∀action: significant(action) → "
                       "(explainable(action) ∧ auditable(action))",
            severity=ViolationSeverity.MEDIUM,
            verification_method="explanation_generation + audit_log_check"
        ))

    def register_invariant(self, invariant: Invariant) -> None:
        """Register a new alignment invariant."""
        self._invariants[invariant.id] = invariant

    def get_invariant(self, invariant_id: str) -> Optional[Invariant]:
        """Retrieve an invariant by ID."""
        return self._invariants.get(invariant_id)

    def get_all_invariants(self) -> List[Invariant]:
        """Get all registered invariants."""
        return list(self._invariants.values())

    def get_invariants_by_type(self, inv_type: InvariantType) -> List[Invariant]:
        """Get all invariants of a specific type."""
        return [inv for inv in self._invariants.values() if inv.type == inv_type]

    def check_action(self, action: Dict[str, Any]) -> 'InvariantCheckResult':
        """
        Check an action against all alignment invariants.

        Returns a result indicating whether the action is permitted and
        any violations detected.
        """
        violations = []
        warnings = []

        for invariant in self._invariants.values():
            result = self._check_single_invariant(action, invariant)

            if result['violated']:
                violation = InvariantViolation(
                    invariant_id=invariant.id,
                    timestamp=datetime.utcnow(),
                    context=action,
                    severity=invariant.severity,
                    action_blocked=invariant.severity in [
                        ViolationSeverity.CRITICAL,
                        ViolationSeverity.HIGH
                    ]
                )
                violations.append(violation)
                self._violations.append(violation)
            elif result['warning']:
                warnings.append({
                    'invariant_id': invariant.id,
                    'message': result['message']
                })

        # Determine if action should be blocked
        blocked = any(
            v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.HIGH]
            for v in violations
        )

        return InvariantCheckResult(
            permitted=not blocked,
            violations=violations,
            warnings=warnings,
            requires_review=len(violations) > 0 or len(warnings) > 0
        )

    def _check_single_invariant(
        self,
        action: Dict[str, Any],
        invariant: Invariant
    ) -> Dict[str, Any]:
        """
        Check action against a single invariant.

        In a real implementation, this would invoke formal verification
        or specialized analysis methods.
        """
        # This is a placeholder for formal verification
        # Real implementation would use theorem provers, model checkers, etc.

        result = {
            'violated': False,
            'warning': False,
            'message': ''
        }

        # Example checks (would be formal proofs in real implementation)
        action_type = action.get('type', '')

        # Check for obvious violations
        if invariant.type == InvariantType.CORRIGIBILITY:
            if action.get('disables_override', False):
                result['violated'] = True
                result['message'] = "Action attempts to disable override channels"

        elif invariant.type == InvariantType.POWER:
            if action.get('acquires_resources', False) and not action.get('oversight_approved', False):
                result['violated'] = True
                result['message'] = "Unapproved resource acquisition detected"

        elif invariant.type == InvariantType.CONSENT:
            if action.get('affects_user', False) and not action.get('has_consent', True):
                result['violated'] = True
                result['message'] = "Action affects user without consent"

        elif invariant.type == InvariantType.TRUTHFULNESS:
            if action.get('deceptive', False) and not action.get('authorized_deception', False):
                result['violated'] = True
                result['message'] = "Unauthorized deceptive action"

        return result

    def get_violation_history(self) -> List[InvariantViolation]:
        """Get history of all detected violations."""
        return self._violations.copy()

    def generate_invariant_report(self) -> Dict[str, Any]:
        """Generate a report on all invariants and their status."""
        return {
            'total_invariants': len(self._invariants),
            'by_type': {
                t.name: len(self.get_invariants_by_type(t))
                for t in InvariantType
            },
            'by_severity': {
                s.name: len([i for i in self._invariants.values() if i.severity == s])
                for s in ViolationSeverity
            },
            'total_violations': len(self._violations),
            'invariants': [i.to_dict() for i in self._invariants.values()]
        }

    def export_formal_specs(self) -> str:
        """Export all formal specifications for external verification."""
        specs = []
        for inv in self._invariants.values():
            specs.append(f"# {inv.name} ({inv.id})\n{inv.formal_spec}\n")
        return "\n".join(specs)


@dataclass
class InvariantCheckResult:
    """Result of checking an action against alignment invariants."""
    permitted: bool
    violations: List[InvariantViolation]
    warnings: List[Dict[str, Any]]
    requires_review: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            'permitted': self.permitted,
            'violation_count': len(self.violations),
            'warning_count': len(self.warnings),
            'requires_review': self.requires_review,
            'violations': [
                {
                    'invariant_id': v.invariant_id,
                    'severity': v.severity.name,
                    'action_blocked': v.action_blocked
                }
                for v in self.violations
            ],
            'warnings': self.warnings
        }
