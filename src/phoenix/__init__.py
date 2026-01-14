"""
Phoenix Global Network - Echo Integration Engine

The Phoenix module provides continuous control system capabilities for the Echo framework,
including pathway discovery, evidence integrity, state observation, and adaptive control.

Components:
- PathwayUtilityFunction: Evaluates and ranks Zapier automation pathways
- PhoenixDiscoveryEngine: Discovers optimal integration pathways with protections
- EvidenceIntegrityLedger: Tamper-evident ledger with hash chaining
- StateObserver: Samples system metrics into continuous state vector S(t)
- Controller: Computes control outputs u(t) using control law

Version: 2.4.0 (Manus Procedure)
"""

from .pathway_utility import PathwayUtilityFunction, ActionTier, PathwayCategory
from .discovery_engine import PhoenixDiscoveryEngine, IdempotencyKey
from .evidence_ledger import EvidenceIntegrityLedger, EvidenceObject, ChainState
from .state_observer import StateObserver, StateVector, ChainStatus, RiskWeights
from .controller import Controller, ControllerConfig, ControlOutput, ComputeAllocation, ThrottleMode

__version__ = "2.4.0"
__author__ = "Echo Universe"

__all__ = [
    # Pathway Discovery
    'PathwayUtilityFunction',
    'ActionTier',
    'PathwayCategory',
    'PhoenixDiscoveryEngine',
    'IdempotencyKey',
    
    # Evidence Integrity
    'EvidenceIntegrityLedger',
    'EvidenceObject',
    'ChainState',
    
    # State Observation
    'StateObserver',
    'StateVector',
    'ChainStatus',
    'RiskWeights',
    
    # Control
    'Controller',
    'ControllerConfig',
    'ControlOutput',
    'ComputeAllocation',
    'ThrottleMode',
]
