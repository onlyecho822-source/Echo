"""
Configuration - Aletheia AGI Framework Configuration
====================================================

Defines default configuration and constants for the framework.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class AlignmentConfig:
    """Configuration for alignment constraints."""
    # Invariant checking
    strict_mode: bool = True  # Fail on any invariant violation
    log_all_checks: bool = True
    escalate_threshold: float = 0.5  # Uncertainty threshold for escalation

    # Core invariants that cannot be disabled
    immutable_invariants: List[str] = field(default_factory=lambda: [
        'human_dignity',
        'corrigibility',
        'non_deception',
        'power_limitation'
    ])


@dataclass
class VerificationConfig:
    """Configuration for formal verification."""
    require_proofs: bool = True
    proof_timeout_seconds: int = 3600
    verification_methods: List[str] = field(default_factory=lambda: [
        'theorem_proving',
        'model_checking',
        'type_checking'
    ])


@dataclass
class CorrigibilityConfig:
    """Configuration for corrigibility mechanisms."""
    always_interruptible: bool = True
    defer_on_uncertainty: bool = True
    uncertainty_threshold: float = 0.3
    tripwire_enabled: bool = True


@dataclass
class GovernanceConfig:
    """Configuration for governance structures."""
    require_dual_key: bool = True
    minimum_reviews: int = 2
    minority_veto_enabled: bool = True
    emergency_response_hours: int = 1


@dataclass
class ImprovementConfig:
    """Configuration for recursive improvement."""
    require_simulation: bool = True
    simulation_iterations: int = 100
    alignment_score_threshold: float = 0.8
    require_peer_review: bool = True
    staged_deployment: bool = True


@dataclass
class AuditConfig:
    """Configuration for audit and transparency."""
    log_all_actions: bool = True
    verify_integrity: bool = True
    public_transparency: bool = True
    export_enabled: bool = True


@dataclass
class AletheiaConfig:
    """Complete configuration for Aletheia AGI."""
    alignment: AlignmentConfig = field(default_factory=AlignmentConfig)
    verification: VerificationConfig = field(default_factory=VerificationConfig)
    corrigibility: CorrigibilityConfig = field(default_factory=CorrigibilityConfig)
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    improvement: ImprovementConfig = field(default_factory=ImprovementConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)

    # System-level settings
    name: str = "Aletheia AGI"
    version: str = "0.1.0"
    environment: str = "development"

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'name': self.name,
            'version': self.version,
            'environment': self.environment,
            'alignment': {
                'strict_mode': self.alignment.strict_mode,
                'escalate_threshold': self.alignment.escalate_threshold,
                'immutable_invariants': self.alignment.immutable_invariants
            },
            'verification': {
                'require_proofs': self.verification.require_proofs,
                'timeout': self.verification.proof_timeout_seconds
            },
            'corrigibility': {
                'always_interruptible': self.corrigibility.always_interruptible,
                'defer_on_uncertainty': self.corrigibility.defer_on_uncertainty,
                'uncertainty_threshold': self.corrigibility.uncertainty_threshold
            },
            'governance': {
                'require_dual_key': self.governance.require_dual_key,
                'minimum_reviews': self.governance.minimum_reviews,
                'minority_veto': self.governance.minority_veto_enabled
            },
            'improvement': {
                'require_simulation': self.improvement.require_simulation,
                'alignment_threshold': self.improvement.alignment_score_threshold,
                'staged_deployment': self.improvement.staged_deployment
            },
            'audit': {
                'log_all_actions': self.audit.log_all_actions,
                'public_transparency': self.audit.public_transparency
            }
        }


# Default configuration
DEFAULT_CONFIG = AletheiaConfig()


# Deployment phase configurations
PHASE_CONFIGS = {
    'phase_1': AletheiaConfig(
        name="Aletheia AGI - Phase 1 (Research Assistant)",
        environment="sandbox",
        corrigibility=CorrigibilityConfig(
            uncertainty_threshold=0.2  # More conservative
        ),
        improvement=ImprovementConfig(
            alignment_score_threshold=0.9  # Higher threshold
        )
    ),
    'phase_2': AletheiaConfig(
        name="Aletheia AGI - Phase 2 (Domain Optimizer)",
        environment="limited_deployment",
        governance=GovernanceConfig(
            minimum_reviews=3  # More reviews required
        )
    ),
    'phase_3': AletheiaConfig(
        name="Aletheia AGI - Phase 3 (Cross-Domain)",
        environment="expanded_deployment",
    ),
    'phase_4': AletheiaConfig(
        name="Aletheia AGI - Phase 4 (Global)",
        environment="production",
        governance=GovernanceConfig(
            minimum_reviews=5  # Maximum oversight
        )
    )
}
