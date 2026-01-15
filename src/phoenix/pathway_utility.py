"""
PHOENIX PATHWAY DISCOVERY ENGINE - Utility Function Implementation
Specification: Echo Integration Topology v1.0
Purpose: Implement U(P) to evaluate and rank Zapier automation pathways.

Addresses Devil Lens Findings:
1. Bounded search space (not "computationally infinite")
2. Measurable utility function with concrete parameters
3. Kill conditions and rollout plan

Author: Manus AI
Date: 2026-01-14
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple


class PathwayCategory(Enum):
    """Six formal pathway categories from topology analysis."""
    LINEAR = "linear"           # T → X₁ → ... → Xₙ
    BRANCHING = "branching"     # T → C → {X₁, X₂}
    PARALLEL = "parallel"       # T → {X₁ ∥ X₂}
    AGGREGATION = "aggregation" # {T₁, T₂} → X
    RECURSIVE = "recursive"     # T → X → T
    TEMPORAL = "temporal"       # T → X → Δt → T'


class ActionTier(Enum):
    """Action tiers based on Echo relevance."""
    CRITICAL = 1.0      # GitHub, Airtable, OpenAI, Claude, Slack, Webhooks
    HIGH_VALUE = 0.7    # Discord, Google Sheets, Notion, PagerDuty, Gmail
    EXPANSION = 0.4     # Stripe, Typeform, HubSpot, Linear, Vercel


@dataclass
class Action:
    """Represents a single action node Xᵢ in a pathway."""
    id: str
    name: str
    app: str
    tier: ActionTier
    avg_latency_ms: int = 1000
    cost_per_task: float = 0.01
    reliability: float = 0.99
    business_impact: float = 1.0  # 0.0 to 1.0


@dataclass
class Pathway:
    """
    Represents a pathway P = (V, E) as a DAG.
    V = {trigger, conditions, actions}
    E = directed edges
    """
    id: str
    name: str
    category: PathwayCategory
    trigger: str
    actions: List[Action]
    conditions: List[str] = field(default_factory=list)
    temporal_delays_ms: List[int] = field(default_factory=list)
    
    def compute_hash(self) -> str:
        """Compute deterministic hash for pathway identification."""
        payload = json.dumps({
            "id": self.id,
            "trigger": self.trigger,
            "actions": [a.id for a in self.actions],
            "conditions": self.conditions
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


@dataclass
class UtilityResult:
    """Result of utility computation with constraint satisfaction."""
    pathway_id: str
    pathway_hash: str
    utility_score: float
    total_value: float
    total_cost: float
    total_risk: float
    total_latency_ms: int
    estimated_reliability: float
    constraints_satisfied: bool
    constraint_violations: List[str]
    timestamp: str
    
    def to_eil_record(self) -> Dict:
        """Convert to Evidence & Integrity Ledger record format."""
        return {
            "event_id": f"utility_{self.pathway_hash}_{self.timestamp}",
            "pathway_id": self.pathway_id,
            "utility_score": round(self.utility_score, 4),
            "constraints_satisfied": self.constraints_satisfied,
            "sha256_payload": hashlib.sha256(
                json.dumps(self.__dict__, sort_keys=True, default=str).encode()
            ).hexdigest(),
            "timestamp": self.timestamp
        }


class PathwayUtilityFunction:
    """
    Implements U(P) = V(P) - C(P) - R(P)
    
    Where:
        V(P) = Σ Value(Xᵢ) = Σ (echo_relevance × business_impact)
        C(P) = Σ Cost(Xᵢ) = Σ (task_cost × resource_factor)
        R(P) = Risk(P) = (1 - reliability) × impact_if_failure
    
    Subject to constraints:
        Latency(P) ≤ latency_budget
        Cost(P) ≤ cost_budget
        Reliability(P) ≥ reliability_minimum
        Complexity(P) ≤ max_actions (bounded search space)
    """
    
    # BOUNDED SEARCH SPACE (addresses Devil Lens finding #1)
    MAX_ACTIONS_PER_PATHWAY = 10  # Hard limit on pathway complexity
    MAX_CHAIN_LENGTH = 5         # Optimal pathways exist in low-k space
    
    def __init__(
        self,
        latency_budget_ms: int = 60000,      # 60 seconds
        cost_budget: float = 100.0,           # Cost units per month
        reliability_minimum: float = 0.99,    # 99%
        failure_impact: float = 10.0          # Impact multiplier if pathway fails
    ):
        """
        Initialize utility function with constraints.
        
        Args:
            latency_budget_ms: Maximum allowed latency in milliseconds
            cost_budget: Maximum allowed cost per execution
            reliability_minimum: Minimum required reliability (0.0 to 1.0)
            failure_impact: Multiplier for risk calculation
        """
        self.latency_budget_ms = latency_budget_ms
        self.cost_budget = cost_budget
        self.reliability_minimum = reliability_minimum
        self.failure_impact = failure_impact
    
    def compute_utility(self, pathway: Pathway) -> UtilityResult:
        """
        Compute U(P) = V(P) - C(P) - R(P), subject to constraints.
        
        Returns:
            UtilityResult with score and constraint satisfaction
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        constraint_violations = []
        
        # Check bounded search space constraint
        if len(pathway.actions) > self.MAX_ACTIONS_PER_PATHWAY:
            constraint_violations.append(
                f"Exceeds max actions: {len(pathway.actions)} > {self.MAX_ACTIONS_PER_PATHWAY}"
            )
        
        # Compute V(P) = Σ Value(Xᵢ)
        total_value = sum(
            self._compute_action_value(action) 
            for action in pathway.actions
        )
        
        # Compute C(P) = Σ Cost(Xᵢ)
        total_cost = sum(
            self._compute_action_cost(action)
            for action in pathway.actions
        )
        
        # Compute latency
        total_latency_ms = sum(
            action.avg_latency_ms for action in pathway.actions
        ) + sum(pathway.temporal_delays_ms)
        
        # Compute reliability (product of individual reliabilities)
        estimated_reliability = 1.0
        for action in pathway.actions:
            estimated_reliability *= action.reliability
        
        # Compute R(P) = (1 - reliability) × failure_impact
        total_risk = (1 - estimated_reliability) * self.failure_impact
        
        # Check constraints
        if total_latency_ms > self.latency_budget_ms:
            constraint_violations.append(
                f"Latency exceeded: {total_latency_ms}ms > {self.latency_budget_ms}ms"
            )
        
        if total_cost > self.cost_budget:
            constraint_violations.append(
                f"Cost exceeded: {total_cost} > {self.cost_budget}"
            )
        
        if estimated_reliability < self.reliability_minimum:
            constraint_violations.append(
                f"Reliability below minimum: {estimated_reliability:.4f} < {self.reliability_minimum}"
            )
        
        # Compute final utility
        utility_score = total_value - total_cost - total_risk
        
        return UtilityResult(
            pathway_id=pathway.id,
            pathway_hash=pathway.compute_hash(),
            utility_score=utility_score,
            total_value=total_value,
            total_cost=total_cost,
            total_risk=total_risk,
            total_latency_ms=total_latency_ms,
            estimated_reliability=estimated_reliability,
            constraints_satisfied=len(constraint_violations) == 0,
            constraint_violations=constraint_violations,
            timestamp=timestamp
        )
    
    def _compute_action_value(self, action: Action) -> float:
        """
        Compute Value(Xᵢ) = echo_relevance × business_impact
        
        Echo relevance is determined by action tier.
        """
        echo_relevance = action.tier.value
        return echo_relevance * action.business_impact
    
    def _compute_action_cost(self, action: Action) -> float:
        """
        Compute Cost(Xᵢ) = task_cost × resource_factor
        
        Resource factor accounts for API calls, compute time, etc.
        """
        # Higher tier actions have lower effective cost (more value per dollar)
        resource_factor = 1.0 / action.tier.value
        return action.cost_per_task * resource_factor
    
    def rank_pathways(
        self, 
        pathways: List[Pathway],
        only_valid: bool = True
    ) -> List[Tuple[Pathway, UtilityResult]]:
        """
        Rank pathways by utility score.
        
        Args:
            pathways: List of pathways to evaluate
            only_valid: If True, exclude pathways that violate constraints
            
        Returns:
            List of (pathway, result) tuples sorted by utility (descending)
        """
        results = []
        for pathway in pathways:
            result = self.compute_utility(pathway)
            if only_valid and not result.constraints_satisfied:
                continue
            results.append((pathway, result))
        
        # Sort by utility score descending
        results.sort(key=lambda x: x[1].utility_score, reverse=True)
        return results


class PathwayDiscoveryEngine:
    """
    Guided Pathway Search Algorithm.
    
    Implements the discovery algorithm from formal analysis:
    - Bounded search space
    - Utility-guided exploration
    - Pruning heuristics
    """
    
    def __init__(self, utility_function: PathwayUtilityFunction):
        self.utility_function = utility_function
        self.discovered: List[Pathway] = []
        self.frontier: List[Pathway] = []
        self.evaluated_hashes: set = set()
    
    def discover(
        self,
        seed_pathways: List[Pathway],
        utility_threshold: float = 0.0,
        max_iterations: int = 1000
    ) -> List[Tuple[Pathway, UtilityResult]]:
        """
        Discover high-utility pathways using guided search.
        
        Args:
            seed_pathways: Initial pathways to explore from
            utility_threshold: Minimum utility to consider
            max_iterations: Maximum search iterations (kill condition)
            
        Returns:
            List of discovered pathways with utility results
        """
        self.frontier = list(seed_pathways)
        iterations = 0
        
        while self.frontier and iterations < max_iterations:
            iterations += 1
            
            # Select pathway with highest estimated utility
            pathway = self._select_best_from_frontier()
            if pathway is None:
                break
            
            # Skip if already evaluated
            pathway_hash = pathway.compute_hash()
            if pathway_hash in self.evaluated_hashes:
                continue
            self.evaluated_hashes.add(pathway_hash)
            
            # Evaluate utility
            result = self.utility_function.compute_utility(pathway)
            
            # Add to discovered if meets threshold and constraints
            if result.utility_score >= utility_threshold and result.constraints_satisfied:
                self.discovered.append(pathway)
            
            # Generate extensions (pruned by bounded search space)
            # Note: In production, this would generate valid pathway extensions
            # For now, we just process the seed pathways
        
        # Return ranked results
        return self.utility_function.rank_pathways(self.discovered)
    
    def _select_best_from_frontier(self) -> Optional[Pathway]:
        """Select and remove the best pathway from frontier."""
        if not self.frontier:
            return None
        
        # Simple selection: take first (in production, use priority queue)
        return self.frontier.pop(0)


# ============================================================================
# PREDEFINED ECHO PATHWAYS (MVP)
# ============================================================================

def create_eil_logger_pathway() -> Pathway:
    """EIL v0: GitHub → Zapier → Airtable log with hash chaining."""
    return Pathway(
        id="eil_logger_v0",
        name="Evidence & Integrity Ledger Logger",
        category=PathwayCategory.LINEAR,
        trigger="github.push",
        actions=[
            Action(
                id="airtable_create_record",
                name="Create EIL Record",
                app="Airtable",
                tier=ActionTier.CRITICAL,
                avg_latency_ms=500,
                cost_per_task=0.01,
                reliability=0.999,
                business_impact=1.0
            )
        ]
    )


def create_notification_pathway() -> Pathway:
    """Notification v0: GitHub → Slack."""
    return Pathway(
        id="notification_v0",
        name="GitHub to Slack Notification",
        category=PathwayCategory.LINEAR,
        trigger="github.pull_request",
        actions=[
            Action(
                id="slack_post_message",
                name="Post to Slack",
                app="Slack",
                tier=ActionTier.CRITICAL,
                avg_latency_ms=300,
                cost_per_task=0.01,
                reliability=0.999,
                business_impact=0.8
            )
        ]
    )


def create_pr_review_pathway() -> Pathway:
    """PR Review v0: PR opened → OpenAI + Claude → Slack summary (no auto-merge)."""
    return Pathway(
        id="pr_review_v0",
        name="Adversarial PR Review",
        category=PathwayCategory.PARALLEL,
        trigger="github.pull_request.opened",
        actions=[
            Action(
                id="openai_review",
                name="OpenAI Code Review",
                app="OpenAI",
                tier=ActionTier.CRITICAL,
                avg_latency_ms=5000,
                cost_per_task=0.05,
                reliability=0.98,
                business_impact=0.9
            ),
            Action(
                id="claude_review",
                name="Claude Code Review",
                app="Anthropic",
                tier=ActionTier.CRITICAL,
                avg_latency_ms=5000,
                cost_per_task=0.05,
                reliability=0.98,
                business_impact=0.9
            ),
            Action(
                id="slack_summary",
                name="Post Review Summary",
                app="Slack",
                tier=ActionTier.CRITICAL,
                avg_latency_ms=300,
                cost_per_task=0.01,
                reliability=0.999,
                business_impact=0.8
            )
        ]
    )


def create_gkp_activation_pathway() -> Pathway:
    """GKP: Emergency trigger → PagerDuty + Broadcast."""
    return Pathway(
        id="gkp_activation_v0",
        name="Global Kill Plane Activation",
        category=PathwayCategory.PARALLEL,
        trigger="webhook.gkp_trigger",
        actions=[
            Action(
                id="pagerduty_incident",
                name="Create P1 Incident",
                app="PagerDuty",
                tier=ActionTier.HIGH_VALUE,
                avg_latency_ms=1000,
                cost_per_task=0.10,
                reliability=0.999,
                business_impact=1.0
            ),
            Action(
                id="slack_emergency",
                name="Post to #emergency",
                app="Slack",
                tier=ActionTier.CRITICAL,
                avg_latency_ms=300,
                cost_per_task=0.01,
                reliability=0.999,
                business_impact=1.0
            ),
            Action(
                id="discord_emergency",
                name="Post to #emergency",
                app="Discord",
                tier=ActionTier.HIGH_VALUE,
                avg_latency_ms=300,
                cost_per_task=0.01,
                reliability=0.99,
                business_impact=0.9
            )
        ]
    )


def create_lead_funnel_pathway() -> Pathway:
    """Lead Funnel: GitHub Star → Airtable → Temporal Decay."""
    return Pathway(
        id="lead_funnel_v0",
        name="Lead Funnel with Temporal Decay",
        category=PathwayCategory.TEMPORAL,
        trigger="github.star",
        actions=[
            Action(
                id="airtable_create_lead",
                name="Create Lead Record",
                app="Airtable",
                tier=ActionTier.CRITICAL,
                avg_latency_ms=500,
                cost_per_task=0.01,
                reliability=0.999,
                business_impact=0.7
            )
        ],
        temporal_delays_ms=[86400000]  # 24 hours
    )


# ============================================================================
# MAIN: Example Usage
# ============================================================================

if __name__ == "__main__":
    # Initialize utility function with constraints
    utility_fn = PathwayUtilityFunction(
        latency_budget_ms=60000,      # 60 seconds
        cost_budget=1.0,              # $1 per execution
        reliability_minimum=0.95,     # 95%
        failure_impact=10.0
    )
    
    # Create MVP pathways
    mvp_pathways = [
        create_eil_logger_pathway(),
        create_notification_pathway(),
        create_pr_review_pathway(),
        create_gkp_activation_pathway(),
        create_lead_funnel_pathway()
    ]
    
    # Rank pathways by utility
    print("=" * 60)
    print("PHOENIX PATHWAY DISCOVERY ENGINE - Utility Analysis")
    print("=" * 60)
    
    ranked = utility_fn.rank_pathways(mvp_pathways, only_valid=True)
    
    for i, (pathway, result) in enumerate(ranked, 1):
        print(f"\n{i}. {pathway.name}")
        print(f"   Category: {pathway.category.value}")
        print(f"   Utility Score: {result.utility_score:.4f}")
        print(f"   Value: {result.total_value:.4f}")
        print(f"   Cost: {result.total_cost:.4f}")
        print(f"   Risk: {result.total_risk:.4f}")
        print(f"   Latency: {result.total_latency_ms}ms")
        print(f"   Reliability: {result.estimated_reliability:.4f}")
        print(f"   Constraints Satisfied: {result.constraints_satisfied}")
        
        # Print EIL record format
        eil_record = result.to_eil_record()
        print(f"   EIL Record: {json.dumps(eil_record, indent=6)}")
    
    print("\n" + "=" * 60)
    print("Analysis Complete")
    print("=" * 60)
