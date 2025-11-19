"""
Aletheia AGI Framework
======================

A conceptual framework for provably safe, aligned, recursively self-improving AGI.

This framework embodies the architectural principles for an aligned AGI system that serves
as a meta-governor for truth engines—continuously verifying pipelines, detecting bias and
manipulation, and proposing safer upgrades while remaining corrigible to human oversight.

IMPORTANT DISCLAIMER:
--------------------
This is a conceptual/educational framework demonstrating alignment architecture principles.
It is NOT actual AGI—artificial general intelligence remains an unsolved research problem.
The code provides interfaces, constraints, and scaffolding that embody alignment principles
which could theoretically be built upon as the field advances.

Core Principles:
---------------
1. Value Learning (CIRL) - Learn human values through cooperative inverse reinforcement learning
2. Corrigibility - Remain interruptible and deferential to human oversight
3. Transparency - All reasoning and actions must be interpretable and auditable
4. Formal Verification - Changes ship with machine-checked proofs for safety invariants

Architecture:
------------
- Formal Core: Verified runtime, proof-carrying code, sandboxed self-edit stages
- Value Learning: CIRL, inverse RL, preference aggregation with uncertainty tracking
- Corrigibility: Interruptibility protocols, override channels, tripwires
- Interpretability: Mechanistic analysis, causal tracing, public audit logs
- Recursive Improvement: Propose → prove → simulate → review → deploy → monitor

Author: Echo Civilization Framework
License: For research and educational purposes
"""

__version__ = "0.1.0"
__author__ = "Echo Civilization Framework"

from .aletheia import AletheiaAGI
from .core.alignment_invariants import AlignmentInvariants
from .core.formal_verifier import FormalVerifier
from .values.value_learner import ValueLearner
from .corrigibility.corrigibility_engine import CorrigibilityEngine
from .interpretability.audit_system import AuditSystem
from .improvement.improvement_controller import ImprovementController
from .governance.governance_stack import GovernanceStack

__all__ = [
    'AletheiaAGI',
    'AlignmentInvariants',
    'FormalVerifier',
    'ValueLearner',
    'CorrigibilityEngine',
    'AuditSystem',
    'ImprovementController',
    'GovernanceStack',
]
