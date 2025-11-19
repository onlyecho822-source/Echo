"""
Improvement Module - Recursive Self-Improvement Control
=======================================================

Manages the pipeline: Propose → Prove → Simulate → Review → Deploy → Monitor
ensuring capability gains preserve all alignment invariants.
"""

from .improvement_controller import ImprovementController
from .proposal_validator import ProposalValidator
from .simulation_engine import SimulationEngine

__all__ = ['ImprovementController', 'ProposalValidator', 'SimulationEngine']
