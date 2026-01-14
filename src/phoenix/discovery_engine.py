"""
PHOENIX PATHWAY DISCOVERY ENGINE - Core Engine
Specification: Echo Integration Topology v1.0
Purpose: Guided pathway search with idempotency, deterministic merge, and replay protection.

Addresses Devil Lens Findings:
3. Concurrency/ordering hazards - Implements deterministic merge rules, idempotency keys, replay protection
5. GKP design needs explicit authority - Implements authorization model

Author: Manus AI
Date: 2026-01-14
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from .pathway_utility import (
    Action,
    ActionTier,
    Pathway,
    PathwayCategory,
    PathwayUtilityFunction,
    UtilityResult,
)


class ExecutionStatus(Enum):
    """Status of pathway execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"


class GKPAuthority(Enum):
    """Who can trigger Global Kill Plane."""
    SYSTEM = "system"           # Automated safety triggers
    HUMAN_ADMIN = "human_admin" # Authorized human administrators
    CONSENSUS = "consensus"     # Multi-agent consensus (2-of-3)


@dataclass
class IdempotencyKey:
    """
    Idempotency key for replay protection.
    
    Ensures the same operation is not executed twice.
    """
    key: str
    created_at: str
    expires_at: str
    pathway_id: str
    execution_hash: str
    
    @classmethod
    def generate(cls, pathway: Pathway, input_data: Dict) -> "IdempotencyKey":
        """Generate idempotency key from pathway and input."""
        # Create deterministic hash from pathway + input
        payload = json.dumps({
            "pathway_id": pathway.id,
            "pathway_hash": pathway.compute_hash(),
            "input_data": input_data
        }, sort_keys=True)
        execution_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        now = datetime.utcnow()
        return cls(
            key=f"idem_{execution_hash[:32]}",
            created_at=now.isoformat() + "Z",
            expires_at=(now + timedelta(hours=24)).isoformat() + "Z",
            pathway_id=pathway.id,
            execution_hash=execution_hash
        )
    
    def is_expired(self) -> bool:
        """Check if idempotency key has expired."""
        expires = datetime.fromisoformat(self.expires_at.rstrip("Z"))
        return datetime.utcnow() > expires


@dataclass
class ExecutionResult:
    """Result of a single action execution."""
    action_id: str
    status: ExecutionStatus
    output: Any
    latency_ms: int
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


@dataclass
class MergeResult:
    """
    Result of merging parallel execution results.
    
    Implements deterministic merge rule for A-CMAP.
    """
    consensus_reached: bool
    consensus_value: Optional[Any]
    dissent_detected: bool
    dissent_details: List[str]
    individual_results: List[ExecutionResult]
    merge_strategy: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ReplayProtection:
    """
    Replay protection using idempotency keys.
    
    Prevents duplicate execution of the same operation.
    """
    
    def __init__(self, max_keys: int = 10000):
        self._keys: Dict[str, IdempotencyKey] = {}
        self._max_keys = max_keys
    
    def check_and_register(self, key: IdempotencyKey) -> Tuple[bool, Optional[str]]:
        """
        Check if operation can proceed and register key.
        
        Returns:
            (can_proceed, existing_execution_hash)
        """
        # Clean expired keys
        self._cleanup_expired()
        
        if key.key in self._keys:
            existing = self._keys[key.key]
            if not existing.is_expired():
                return False, existing.execution_hash
        
        # Register new key
        self._keys[key.key] = key
        return True, None
    
    def _cleanup_expired(self):
        """Remove expired keys."""
        expired = [k for k, v in self._keys.items() if v.is_expired()]
        for k in expired:
            del self._keys[k]
        
        # Enforce max keys limit (LRU-style)
        if len(self._keys) > self._max_keys:
            # Remove oldest keys
            sorted_keys = sorted(
                self._keys.items(),
                key=lambda x: x[1].created_at
            )
            for k, _ in sorted_keys[:len(self._keys) - self._max_keys]:
                del self._keys[k]


class DeterministicMerger:
    """
    Deterministic merge rules for parallel pathway execution.
    
    Implements:
    - Majority voting (2-of-3)
    - Weighted consensus
    - Dissent detection
    """
    
    @staticmethod
    def majority_vote(results: List[ExecutionResult]) -> MergeResult:
        """
        Merge using majority voting (2-of-3 for Byzantine fault tolerance).
        
        Args:
            results: List of execution results from parallel actions
            
        Returns:
            MergeResult with consensus or dissent
        """
        if len(results) < 2:
            return MergeResult(
                consensus_reached=False,
                consensus_value=None,
                dissent_detected=False,
                dissent_details=["Insufficient results for voting"],
                individual_results=results,
                merge_strategy="majority_vote"
            )
        
        # Extract outputs
        outputs = [r.output for r in results if r.status == ExecutionStatus.COMPLETED]
        
        if len(outputs) < 2:
            return MergeResult(
                consensus_reached=False,
                consensus_value=None,
                dissent_detected=False,
                dissent_details=["Insufficient successful results"],
                individual_results=results,
                merge_strategy="majority_vote"
            )
        
        # Count votes (using string representation for comparison)
        vote_counts: Dict[str, int] = {}
        vote_values: Dict[str, Any] = {}
        
        for output in outputs:
            key = json.dumps(output, sort_keys=True, default=str)
            vote_counts[key] = vote_counts.get(key, 0) + 1
            vote_values[key] = output
        
        # Find majority
        majority_threshold = len(outputs) // 2 + 1
        majority_key = None
        for key, count in vote_counts.items():
            if count >= majority_threshold:
                majority_key = key
                break
        
        # Detect dissent
        dissent_detected = len(vote_counts) > 1
        dissent_details = []
        if dissent_detected:
            for key, count in vote_counts.items():
                dissent_details.append(f"Vote '{key[:50]}...': {count} votes")
        
        if majority_key:
            return MergeResult(
                consensus_reached=True,
                consensus_value=vote_values[majority_key],
                dissent_detected=dissent_detected,
                dissent_details=dissent_details,
                individual_results=results,
                merge_strategy="majority_vote"
            )
        else:
            return MergeResult(
                consensus_reached=False,
                consensus_value=None,
                dissent_detected=True,
                dissent_details=dissent_details + ["No majority reached"],
                individual_results=results,
                merge_strategy="majority_vote"
            )
    
    @staticmethod
    def weighted_consensus(
        results: List[ExecutionResult],
        weights: Dict[str, float]
    ) -> MergeResult:
        """
        Merge using weighted consensus.
        
        Args:
            results: List of execution results
            weights: Action ID to weight mapping
            
        Returns:
            MergeResult with weighted consensus
        """
        if not results:
            return MergeResult(
                consensus_reached=False,
                consensus_value=None,
                dissent_detected=False,
                dissent_details=["No results to merge"],
                individual_results=results,
                merge_strategy="weighted_consensus"
            )
        
        # Calculate weighted scores
        weighted_outputs: Dict[str, float] = {}
        output_values: Dict[str, Any] = {}
        
        for result in results:
            if result.status != ExecutionStatus.COMPLETED:
                continue
            
            weight = weights.get(result.action_id, 1.0)
            key = json.dumps(result.output, sort_keys=True, default=str)
            weighted_outputs[key] = weighted_outputs.get(key, 0) + weight
            output_values[key] = result.output
        
        if not weighted_outputs:
            return MergeResult(
                consensus_reached=False,
                consensus_value=None,
                dissent_detected=False,
                dissent_details=["No successful results"],
                individual_results=results,
                merge_strategy="weighted_consensus"
            )
        
        # Find highest weighted output
        best_key = max(weighted_outputs, key=weighted_outputs.get)
        total_weight = sum(weighted_outputs.values())
        best_weight = weighted_outputs[best_key]
        
        # Consensus if best has >50% of total weight
        consensus_reached = best_weight > total_weight / 2
        dissent_detected = len(weighted_outputs) > 1
        
        dissent_details = []
        if dissent_detected:
            for key, weight in weighted_outputs.items():
                dissent_details.append(f"Weight {weight:.2f}: '{key[:50]}...'")
        
        return MergeResult(
            consensus_reached=consensus_reached,
            consensus_value=output_values[best_key] if consensus_reached else None,
            dissent_detected=dissent_detected,
            dissent_details=dissent_details,
            individual_results=results,
            merge_strategy="weighted_consensus"
        )


class GlobalKillPlane:
    """
    Global Kill Plane (GKP) implementation.
    
    Addresses Devil Lens finding #5:
    - Who can trigger kill? (GKPAuthority)
    - What systems get halted? (halt_targets)
    - How to unkill safely? (resume with authorization)
    """
    
    def __init__(self):
        self._active = False
        self._triggered_by: Optional[GKPAuthority] = None
        self._triggered_at: Optional[str] = None
        self._reason: Optional[str] = None
        self._halt_targets: Set[str] = set()
        self._authorized_admins: Set[str] = set()
        self._kill_log: List[Dict] = []
    
    def register_admin(self, admin_id: str):
        """Register an authorized admin who can trigger/resume GKP."""
        self._authorized_admins.add(admin_id)
    
    def trigger(
        self,
        authority: GKPAuthority,
        reason: str,
        admin_id: Optional[str] = None,
        halt_targets: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Trigger the Global Kill Plane.
        
        Args:
            authority: Who is triggering (SYSTEM, HUMAN_ADMIN, CONSENSUS)
            reason: Why the kill is being triggered
            admin_id: Required if authority is HUMAN_ADMIN
            halt_targets: Specific systems to halt (None = all)
            
        Returns:
            (success, message)
        """
        # Validate authority
        if authority == GKPAuthority.HUMAN_ADMIN:
            if admin_id is None or admin_id not in self._authorized_admins:
                return False, "Unauthorized: Admin ID not registered"
        
        self._active = True
        self._triggered_by = authority
        self._triggered_at = datetime.utcnow().isoformat() + "Z"
        self._reason = reason
        self._halt_targets = set(halt_targets) if halt_targets else set()
        
        # Log the kill event
        self._kill_log.append({
            "event": "KILL_TRIGGERED",
            "authority": authority.value,
            "admin_id": admin_id,
            "reason": reason,
            "halt_targets": list(self._halt_targets),
            "timestamp": self._triggered_at
        })
        
        return True, f"GKP activated by {authority.value}: {reason}"
    
    def is_halted(self, target: Optional[str] = None) -> bool:
        """
        Check if a target is halted.
        
        Args:
            target: Specific target to check (None = check if any halt active)
            
        Returns:
            True if halted
        """
        if not self._active:
            return False
        
        if not self._halt_targets:
            return True  # All systems halted
        
        if target is None:
            return True
        
        return target in self._halt_targets
    
    def resume(
        self,
        admin_id: str,
        reason: str
    ) -> Tuple[bool, str]:
        """
        Resume operations (unkill).
        
        Args:
            admin_id: Admin authorizing the resume
            reason: Why operations are being resumed
            
        Returns:
            (success, message)
        """
        if admin_id not in self._authorized_admins:
            return False, "Unauthorized: Admin ID not registered"
        
        if not self._active:
            return False, "GKP is not active"
        
        # Log the resume event
        self._kill_log.append({
            "event": "KILL_RESUMED",
            "admin_id": admin_id,
            "reason": reason,
            "original_kill_reason": self._reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        self._active = False
        self._triggered_by = None
        self._triggered_at = None
        self._reason = None
        self._halt_targets = set()
        
        return True, f"GKP deactivated by {admin_id}: {reason}"
    
    def get_status(self) -> Dict:
        """Get current GKP status."""
        return {
            "active": self._active,
            "triggered_by": self._triggered_by.value if self._triggered_by else None,
            "triggered_at": self._triggered_at,
            "reason": self._reason,
            "halt_targets": list(self._halt_targets),
            "authorized_admins": list(self._authorized_admins),
            "kill_log_count": len(self._kill_log)
        }


class PhoenixDiscoveryEngine:
    """
    Phoenix Pathway Discovery Engine.
    
    Integrates:
    - Utility function for pathway ranking
    - Idempotency and replay protection
    - Deterministic merge rules
    - Global Kill Plane
    """
    
    def __init__(
        self,
        utility_function: PathwayUtilityFunction,
        gkp: Optional[GlobalKillPlane] = None
    ):
        self.utility_function = utility_function
        self.gkp = gkp or GlobalKillPlane()
        self.replay_protection = ReplayProtection()
        self.merger = DeterministicMerger()
        
        # Execution state
        self._execution_log: List[Dict] = []
        self._discovered_pathways: List[Tuple[Pathway, UtilityResult]] = []
    
    def execute_pathway(
        self,
        pathway: Pathway,
        input_data: Dict,
        action_executor: Callable[[Action, Dict], ExecutionResult]
    ) -> Tuple[bool, Any, List[ExecutionResult]]:
        """
        Execute a pathway with full protection.
        
        Args:
            pathway: Pathway to execute
            input_data: Input data for the pathway
            action_executor: Function to execute individual actions
            
        Returns:
            (success, output, results)
        """
        # Check GKP
        if self.gkp.is_halted(pathway.id):
            return False, "Execution halted by GKP", []
        
        # Generate and check idempotency key
        idem_key = IdempotencyKey.generate(pathway, input_data)
        can_proceed, existing_hash = self.replay_protection.check_and_register(idem_key)
        
        if not can_proceed:
            return False, f"Duplicate execution blocked (hash: {existing_hash})", []
        
        # Execute based on pathway category
        results: List[ExecutionResult] = []
        
        if pathway.category == PathwayCategory.PARALLEL:
            # Execute actions in parallel (simulated)
            for action in pathway.actions:
                result = action_executor(action, input_data)
                results.append(result)
            
            # Merge results
            merge_result = self.merger.majority_vote(results)
            
            if merge_result.dissent_detected:
                self._log_event("DISSENT_DETECTED", {
                    "pathway_id": pathway.id,
                    "dissent_details": merge_result.dissent_details
                })
            
            if merge_result.consensus_reached:
                return True, merge_result.consensus_value, results
            else:
                return False, merge_result, results
        
        else:
            # Execute actions sequentially
            current_data = input_data
            for action in pathway.actions:
                result = action_executor(action, current_data)
                results.append(result)
                
                if result.status != ExecutionStatus.COMPLETED:
                    return False, result.error, results
                
                current_data = result.output if isinstance(result.output, dict) else {"output": result.output}
            
            return True, results[-1].output if results else None, results
    
    def discover_pathways(
        self,
        seed_pathways: List[Pathway],
        utility_threshold: float = 0.0
    ) -> List[Tuple[Pathway, UtilityResult]]:
        """
        Discover and rank pathways.
        
        Args:
            seed_pathways: Initial pathways to evaluate
            utility_threshold: Minimum utility score
            
        Returns:
            Ranked list of (pathway, utility_result) tuples
        """
        self._discovered_pathways = []
        
        for pathway in seed_pathways:
            result = self.utility_function.compute_utility(pathway)
            
            if result.utility_score >= utility_threshold and result.constraints_satisfied:
                self._discovered_pathways.append((pathway, result))
        
        # Sort by utility
        self._discovered_pathways.sort(key=lambda x: x[1].utility_score, reverse=True)
        
        return self._discovered_pathways
    
    def _log_event(self, event_type: str, data: Dict):
        """Log an event to the execution log."""
        self._execution_log.append({
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    def get_execution_log(self) -> List[Dict]:
        """Get the execution log."""
        return self._execution_log.copy()


# ============================================================================
# MAIN: Example Usage
# ============================================================================

if __name__ == "__main__":
    from .pathway_utility import (
        create_eil_logger_pathway,
        create_notification_pathway,
        create_pr_review_pathway,
        create_gkp_activation_pathway,
        create_lead_funnel_pathway,
    )
    
    # Initialize components
    utility_fn = PathwayUtilityFunction()
    gkp = GlobalKillPlane()
    gkp.register_admin("nathan_poinsette")
    
    engine = PhoenixDiscoveryEngine(utility_fn, gkp)
    
    # Create MVP pathways
    mvp_pathways = [
        create_eil_logger_pathway(),
        create_notification_pathway(),
        create_pr_review_pathway(),
        create_gkp_activation_pathway(),
        create_lead_funnel_pathway()
    ]
    
    # Discover and rank
    print("=" * 60)
    print("PHOENIX DISCOVERY ENGINE - Pathway Discovery")
    print("=" * 60)
    
    ranked = engine.discover_pathways(mvp_pathways)
    
    for i, (pathway, result) in enumerate(ranked, 1):
        print(f"\n{i}. {pathway.name}")
        print(f"   Utility: {result.utility_score:.4f}")
        print(f"   Constraints Satisfied: {result.constraints_satisfied}")
    
    # Test GKP
    print("\n" + "=" * 60)
    print("GLOBAL KILL PLANE - Test")
    print("=" * 60)
    
    print(f"\nGKP Status: {gkp.get_status()}")
    
    success, msg = gkp.trigger(
        GKPAuthority.HUMAN_ADMIN,
        "Testing GKP activation",
        admin_id="nathan_poinsette"
    )
    print(f"\nTrigger GKP: {success} - {msg}")
    print(f"GKP Status: {gkp.get_status()}")
    
    success, msg = gkp.resume("nathan_poinsette", "Test complete")
    print(f"\nResume GKP: {success} - {msg}")
    print(f"GKP Status: {gkp.get_status()}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
