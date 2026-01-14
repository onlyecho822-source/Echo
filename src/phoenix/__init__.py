"""
PHOENIX GLOBAL NETWORK - Core Package
Specification: Echo Integration Topology v1.0

Components:
- PathwayUtilityFunction: Computes U(P) = V(P) - C(P) - R(P)
- PhoenixDiscoveryEngine: Guided pathway search with protections
- EvidenceIntegrityLedger: Tamper-evident append-only ledger
- GlobalKillPlane: Emergency halt system

Author: Manus AI
Date: 2026-01-14
"""

from .pathway_utility import (
    Action,
    ActionTier,
    Pathway,
    PathwayCategory,
    PathwayDiscoveryEngine,
    PathwayUtilityFunction,
    UtilityResult,
    create_eil_logger_pathway,
    create_gkp_activation_pathway,
    create_lead_funnel_pathway,
    create_notification_pathway,
    create_pr_review_pathway,
)

from .discovery_engine import (
    DeterministicMerger,
    ExecutionResult,
    ExecutionStatus,
    GKPAuthority,
    GlobalKillPlane,
    IdempotencyKey,
    MergeResult,
    PhoenixDiscoveryEngine,
    ReplayProtection,
)

from .evidence_ledger import (
    EILConnector,
    EvidenceIntegrityLedger,
    EvidenceRecord,
    EvidenceType,
    ValidityStatus,
)

__version__ = "1.0.0"
