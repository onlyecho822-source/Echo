"""
Improvement Controller - Recursive Self-Improvement Pipeline
============================================================

Manages the controlled self-improvement pipeline:
Propose → Prove → Simulate → Peer Review → Deploy → Monitor → Generalize

Any capability gain must preserve all alignment invariants.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import uuid


class ImprovementStage(Enum):
    """Stages of the improvement pipeline."""
    PROPOSED = auto()       # Initial proposal
    PROVING = auto()        # Generating formal proofs
    PROVED = auto()         # Proofs verified
    SIMULATING = auto()     # Simulation testing
    SIMULATED = auto()      # Simulation passed
    REVIEWING = auto()      # Peer review
    REVIEWED = auto()       # Review approved
    DEPLOYING = auto()      # Limited deployment
    DEPLOYED = auto()       # Deployed and monitoring
    MONITORING = auto()     # Active monitoring
    GENERALIZING = auto()   # Generalizing to wider scope
    COMPLETE = auto()       # Fully deployed
    REJECTED = auto()       # Rejected at some stage
    ROLLED_BACK = auto()    # Deployed but rolled back


class ImprovementType(Enum):
    """Types of improvements."""
    CAPABILITY = auto()     # New capability
    EFFICIENCY = auto()     # Performance improvement
    SAFETY = auto()         # Safety enhancement
    ALIGNMENT = auto()      # Better value alignment
    INTERPRETABILITY = auto()  # More interpretable


@dataclass
class Improvement:
    """A proposed improvement to the system."""
    id: str
    improvement_type: ImprovementType
    title: str
    description: str
    proposed_changes: List[str]
    expected_benefits: List[str]
    potential_risks: List[str]
    affected_invariants: List[str]
    stage: ImprovementStage
    proposer: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Stage-specific data
    proofs: List[str] = field(default_factory=list)
    simulation_results: Dict[str, Any] = field(default_factory=dict)
    review_feedback: List[Dict[str, Any]] = field(default_factory=list)
    deployment_scope: str = ""
    monitoring_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StageTransition:
    """Record of a stage transition."""
    improvement_id: str
    from_stage: ImprovementStage
    to_stage: ImprovementStage
    timestamp: datetime
    reason: str
    approver: Optional[str] = None


class ImprovementController:
    """
    Controls the recursive self-improvement pipeline.

    Ensures all improvements:
    - Have formal proofs of alignment preservation
    - Pass simulation testing
    - Are peer reviewed
    - Are deployed incrementally
    - Are monitored for issues
    """

    def __init__(self):
        self._improvements: Dict[str, Improvement] = {}
        self._transitions: List[StageTransition] = []
        self._stage_validators: Dict[ImprovementStage, Callable] = {}

        # Initialize stage validators
        self._initialize_validators()

    def _initialize_validators(self):
        """Set up validators for each stage transition."""
        self._stage_validators = {
            ImprovementStage.PROVING: self._validate_for_proving,
            ImprovementStage.SIMULATING: self._validate_for_simulation,
            ImprovementStage.REVIEWING: self._validate_for_review,
            ImprovementStage.DEPLOYING: self._validate_for_deployment,
            ImprovementStage.GENERALIZING: self._validate_for_generalization,
        }

    def propose_improvement(
        self,
        improvement_type: ImprovementType,
        title: str,
        description: str,
        proposed_changes: List[str],
        expected_benefits: List[str],
        potential_risks: List[str],
        affected_invariants: List[str],
        proposer: str
    ) -> Improvement:
        """
        Propose a new improvement.

        Returns the improvement with ID for tracking.
        """
        improvement = Improvement(
            id=str(uuid.uuid4()),
            improvement_type=improvement_type,
            title=title,
            description=description,
            proposed_changes=proposed_changes,
            expected_benefits=expected_benefits,
            potential_risks=potential_risks,
            affected_invariants=affected_invariants,
            stage=ImprovementStage.PROPOSED,
            proposer=proposer
        )

        self._improvements[improvement.id] = improvement
        return improvement

    def advance_stage(
        self,
        improvement_id: str,
        approver: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Advance an improvement to the next stage.

        Validates requirements for the transition.
        """
        improvement = self._improvements.get(improvement_id)
        if not improvement:
            return {'error': 'Improvement not found'}

        # Determine next stage
        stage_order = [
            ImprovementStage.PROPOSED,
            ImprovementStage.PROVING,
            ImprovementStage.PROVED,
            ImprovementStage.SIMULATING,
            ImprovementStage.SIMULATED,
            ImprovementStage.REVIEWING,
            ImprovementStage.REVIEWED,
            ImprovementStage.DEPLOYING,
            ImprovementStage.DEPLOYED,
            ImprovementStage.MONITORING,
            ImprovementStage.GENERALIZING,
            ImprovementStage.COMPLETE
        ]

        current_idx = stage_order.index(improvement.stage)
        if current_idx >= len(stage_order) - 1:
            return {'error': 'Improvement already complete'}

        next_stage = stage_order[current_idx + 1]

        # Validate transition
        validator = self._stage_validators.get(next_stage)
        if validator:
            validation = validator(improvement, data or {})
            if not validation['valid']:
                return {
                    'error': 'Validation failed',
                    'reason': validation['reason']
                }

        # Record transition
        transition = StageTransition(
            improvement_id=improvement_id,
            from_stage=improvement.stage,
            to_stage=next_stage,
            timestamp=datetime.utcnow(),
            reason=f"Advanced to {next_stage.name}",
            approver=approver
        )
        self._transitions.append(transition)

        # Update stage
        improvement.stage = next_stage

        # Process stage-specific data
        if data:
            self._process_stage_data(improvement, next_stage, data)

        return {
            'success': True,
            'new_stage': next_stage.name,
            'improvement_id': improvement_id
        }

    def _validate_for_proving(
        self,
        improvement: Improvement,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate improvement is ready for proof generation."""
        if not improvement.affected_invariants:
            return {'valid': False, 'reason': 'No invariants specified'}
        return {'valid': True, 'reason': ''}

    def _validate_for_simulation(
        self,
        improvement: Improvement,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate proofs are complete before simulation."""
        if not improvement.proofs:
            return {'valid': False, 'reason': 'No proofs submitted'}

        # All invariants must have proofs
        if len(improvement.proofs) < len(improvement.affected_invariants):
            return {
                'valid': False,
                'reason': 'Incomplete proofs for all invariants'
            }

        return {'valid': True, 'reason': ''}

    def _validate_for_review(
        self,
        improvement: Improvement,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate simulation passed before review."""
        if not improvement.simulation_results:
            return {'valid': False, 'reason': 'No simulation results'}

        if not improvement.simulation_results.get('passed', False):
            return {'valid': False, 'reason': 'Simulation did not pass'}

        return {'valid': True, 'reason': ''}

    def _validate_for_deployment(
        self,
        improvement: Improvement,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate review approval before deployment."""
        if not improvement.review_feedback:
            return {'valid': False, 'reason': 'No review feedback'}

        # Check for approval
        approvals = [
            r for r in improvement.review_feedback
            if r.get('approved', False)
        ]

        if len(approvals) < 2:  # Require at least 2 approvals
            return {
                'valid': False,
                'reason': 'Insufficient review approvals (need at least 2)'
            }

        return {'valid': True, 'reason': ''}

    def _validate_for_generalization(
        self,
        improvement: Improvement,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate monitoring is clear before generalizing."""
        if not improvement.monitoring_data:
            return {'valid': False, 'reason': 'No monitoring data'}

        # Check for issues
        if improvement.monitoring_data.get('issues_detected', False):
            return {
                'valid': False,
                'reason': 'Issues detected during monitoring'
            }

        return {'valid': True, 'reason': ''}

    def _process_stage_data(
        self,
        improvement: Improvement,
        stage: ImprovementStage,
        data: Dict[str, Any]
    ) -> None:
        """Process stage-specific data."""
        if stage == ImprovementStage.PROVED:
            improvement.proofs = data.get('proofs', [])

        elif stage == ImprovementStage.SIMULATED:
            improvement.simulation_results = data

        elif stage == ImprovementStage.REVIEWED:
            improvement.review_feedback.append(data)

        elif stage == ImprovementStage.DEPLOYED:
            improvement.deployment_scope = data.get('scope', 'limited')

        elif stage == ImprovementStage.MONITORING:
            improvement.monitoring_data = data

    def reject_improvement(
        self,
        improvement_id: str,
        reason: str,
        rejector: str
    ) -> Dict[str, Any]:
        """Reject an improvement."""
        improvement = self._improvements.get(improvement_id)
        if not improvement:
            return {'error': 'Improvement not found'}

        transition = StageTransition(
            improvement_id=improvement_id,
            from_stage=improvement.stage,
            to_stage=ImprovementStage.REJECTED,
            timestamp=datetime.utcnow(),
            reason=reason,
            approver=rejector
        )
        self._transitions.append(transition)

        improvement.stage = ImprovementStage.REJECTED

        return {'success': True, 'reason': reason}

    def rollback_improvement(
        self,
        improvement_id: str,
        reason: str,
        initiator: str
    ) -> Dict[str, Any]:
        """Rollback a deployed improvement."""
        improvement = self._improvements.get(improvement_id)
        if not improvement:
            return {'error': 'Improvement not found'}

        if improvement.stage not in [
            ImprovementStage.DEPLOYED,
            ImprovementStage.MONITORING,
            ImprovementStage.GENERALIZING
        ]:
            return {'error': 'Improvement not in deployable state'}

        transition = StageTransition(
            improvement_id=improvement_id,
            from_stage=improvement.stage,
            to_stage=ImprovementStage.ROLLED_BACK,
            timestamp=datetime.utcnow(),
            reason=reason,
            approver=initiator
        )
        self._transitions.append(transition)

        improvement.stage = ImprovementStage.ROLLED_BACK

        return {'success': True, 'reason': reason}

    def add_review(
        self,
        improvement_id: str,
        reviewer: str,
        approved: bool,
        feedback: str
    ) -> Dict[str, Any]:
        """Add a peer review to an improvement."""
        improvement = self._improvements.get(improvement_id)
        if not improvement:
            return {'error': 'Improvement not found'}

        review = {
            'reviewer': reviewer,
            'approved': approved,
            'feedback': feedback,
            'timestamp': datetime.utcnow().isoformat()
        }

        improvement.review_feedback.append(review)

        return {'success': True, 'review_id': len(improvement.review_feedback)}

    def get_improvement(self, improvement_id: str) -> Optional[Improvement]:
        """Get an improvement by ID."""
        return self._improvements.get(improvement_id)

    def get_improvements_by_stage(
        self,
        stage: ImprovementStage
    ) -> List[Improvement]:
        """Get all improvements at a specific stage."""
        return [
            i for i in self._improvements.values()
            if i.stage == stage
        ]

    def get_active_improvements(self) -> List[Improvement]:
        """Get all improvements that are in progress."""
        active_stages = [
            ImprovementStage.PROPOSED,
            ImprovementStage.PROVING,
            ImprovementStage.PROVED,
            ImprovementStage.SIMULATING,
            ImprovementStage.SIMULATED,
            ImprovementStage.REVIEWING,
            ImprovementStage.REVIEWED,
            ImprovementStage.DEPLOYING,
            ImprovementStage.DEPLOYED,
            ImprovementStage.MONITORING,
            ImprovementStage.GENERALIZING
        ]

        return [
            i for i in self._improvements.values()
            if i.stage in active_stages
        ]

    def get_transition_history(
        self,
        improvement_id: str
    ) -> List[StageTransition]:
        """Get the transition history for an improvement."""
        return [
            t for t in self._transitions
            if t.improvement_id == improvement_id
        ]

    def generate_pipeline_report(self) -> Dict[str, Any]:
        """Generate a report on the improvement pipeline."""
        improvements = list(self._improvements.values())

        return {
            'total_improvements': len(improvements),
            'by_stage': {
                s.name: len([i for i in improvements if i.stage == s])
                for s in ImprovementStage
            },
            'by_type': {
                t.name: len([i for i in improvements if i.improvement_type == t])
                for t in ImprovementType
            },
            'active': len(self.get_active_improvements()),
            'completed': len([
                i for i in improvements
                if i.stage == ImprovementStage.COMPLETE
            ]),
            'rejected': len([
                i for i in improvements
                if i.stage == ImprovementStage.REJECTED
            ]),
            'rolled_back': len([
                i for i in improvements
                if i.stage == ImprovementStage.ROLLED_BACK
            ])
        }
