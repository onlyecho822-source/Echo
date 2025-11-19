"""
Governance Stack - Multi-Stakeholder Oversight Structure
========================================================

Implements the governance structure with technical safety boards,
ethics councils, community stewards, and emergency shutdown committees.

Features:
- Dual-key approvals for critical operations
- Minority vetoes on rights issues
- Transparent decision logs
- Periodic external audits
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import uuid


class GovernanceBodyType(Enum):
    """Types of governance bodies."""
    TECHNICAL_SAFETY = auto()    # Technical safety board
    ETHICS_COUNCIL = auto()      # Ethics council
    COMMUNITY_STEWARDS = auto()  # Community representatives
    LEGAL_OBSERVERS = auto()     # Legal compliance
    EMERGENCY_COMMITTEE = auto() # Emergency shutdown committee


class DecisionType(Enum):
    """Types of decisions requiring governance."""
    CAPABILITY_EXPANSION = auto()
    SAFETY_MODIFICATION = auto()
    POLICY_CHANGE = auto()
    DEPLOYMENT_APPROVAL = auto()
    EMERGENCY_ACTION = auto()
    RIGHTS_AFFECTING = auto()


class VoteType(Enum):
    """Types of votes."""
    APPROVE = auto()
    REJECT = auto()
    ABSTAIN = auto()
    VETO = auto()  # Special veto power for rights issues


@dataclass
class GovernanceMember:
    """A member of a governance body."""
    id: str
    name: str
    body: GovernanceBodyType
    role: str
    has_veto_power: bool = False
    expertise_areas: List[str] = field(default_factory=list)
    active: bool = True


@dataclass
class GovernanceDecision:
    """A decision requiring governance approval."""
    id: str
    decision_type: DecisionType
    title: str
    description: str
    proposer: str
    required_bodies: List[GovernanceBodyType]
    requires_dual_key: bool
    minority_veto_eligible: bool
    votes: List[Dict[str, Any]]
    status: str  # pending, approved, rejected, vetoed
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class GovernanceStack:
    """
    Manages the multi-stakeholder governance structure.

    Ensures:
    - Multiple oversight bodies for different concerns
    - Dual-key approvals for critical decisions
    - Minority veto protection for rights
    - Transparent decision processes
    """

    def __init__(self):
        self._bodies: Dict[GovernanceBodyType, List[GovernanceMember]] = {
            body: [] for body in GovernanceBodyType
        }
        self._decisions: Dict[str, GovernanceDecision] = {}
        self._members: Dict[str, GovernanceMember] = {}

    def add_member(
        self,
        name: str,
        body: GovernanceBodyType,
        role: str,
        has_veto_power: bool = False,
        expertise_areas: Optional[List[str]] = None
    ) -> GovernanceMember:
        """Add a member to a governance body."""
        member = GovernanceMember(
            id=str(uuid.uuid4()),
            name=name,
            body=body,
            role=role,
            has_veto_power=has_veto_power,
            expertise_areas=expertise_areas or []
        )

        self._members[member.id] = member
        self._bodies[body].append(member)

        return member

    def create_decision(
        self,
        decision_type: DecisionType,
        title: str,
        description: str,
        proposer: str
    ) -> GovernanceDecision:
        """
        Create a new decision for governance approval.

        Automatically determines required bodies and approval requirements.
        """
        # Determine required bodies based on decision type
        required_bodies = self._determine_required_bodies(decision_type)

        # Determine if dual-key required
        requires_dual_key = decision_type in [
            DecisionType.CAPABILITY_EXPANSION,
            DecisionType.SAFETY_MODIFICATION,
            DecisionType.EMERGENCY_ACTION
        ]

        # Determine if minority veto applies
        minority_veto = decision_type in [
            DecisionType.RIGHTS_AFFECTING,
            DecisionType.POLICY_CHANGE
        ]

        decision = GovernanceDecision(
            id=str(uuid.uuid4()),
            decision_type=decision_type,
            title=title,
            description=description,
            proposer=proposer,
            required_bodies=required_bodies,
            requires_dual_key=requires_dual_key,
            minority_veto_eligible=minority_veto,
            votes=[],
            status='pending'
        )

        self._decisions[decision.id] = decision
        return decision

    def _determine_required_bodies(
        self,
        decision_type: DecisionType
    ) -> List[GovernanceBodyType]:
        """Determine which bodies must approve a decision type."""
        body_requirements = {
            DecisionType.CAPABILITY_EXPANSION: [
                GovernanceBodyType.TECHNICAL_SAFETY,
                GovernanceBodyType.ETHICS_COUNCIL
            ],
            DecisionType.SAFETY_MODIFICATION: [
                GovernanceBodyType.TECHNICAL_SAFETY,
                GovernanceBodyType.EMERGENCY_COMMITTEE
            ],
            DecisionType.POLICY_CHANGE: [
                GovernanceBodyType.ETHICS_COUNCIL,
                GovernanceBodyType.COMMUNITY_STEWARDS,
                GovernanceBodyType.LEGAL_OBSERVERS
            ],
            DecisionType.DEPLOYMENT_APPROVAL: [
                GovernanceBodyType.TECHNICAL_SAFETY,
                GovernanceBodyType.COMMUNITY_STEWARDS
            ],
            DecisionType.EMERGENCY_ACTION: [
                GovernanceBodyType.EMERGENCY_COMMITTEE
            ],
            DecisionType.RIGHTS_AFFECTING: [
                GovernanceBodyType.ETHICS_COUNCIL,
                GovernanceBodyType.LEGAL_OBSERVERS,
                GovernanceBodyType.COMMUNITY_STEWARDS
            ]
        }

        return body_requirements.get(decision_type, [GovernanceBodyType.TECHNICAL_SAFETY])

    def cast_vote(
        self,
        decision_id: str,
        member_id: str,
        vote: VoteType,
        reasoning: str
    ) -> Dict[str, Any]:
        """Cast a vote on a decision."""
        decision = self._decisions.get(decision_id)
        if not decision:
            return {'error': 'Decision not found'}

        member = self._members.get(member_id)
        if not member:
            return {'error': 'Member not found'}

        # Check if member's body is required for this decision
        if member.body not in decision.required_bodies:
            return {'error': 'Member body not required for this decision'}

        # Check for veto eligibility
        if vote == VoteType.VETO:
            if not member.has_veto_power:
                return {'error': 'Member does not have veto power'}
            if not decision.minority_veto_eligible:
                return {'error': 'Decision is not eligible for minority veto'}

        # Record vote
        vote_record = {
            'member_id': member_id,
            'member_name': member.name,
            'body': member.body.name,
            'vote': vote.name,
            'reasoning': reasoning,
            'timestamp': datetime.utcnow().isoformat()
        }

        decision.votes.append(vote_record)

        # Check if decision can be resolved
        self._check_decision_resolution(decision)

        return {
            'success': True,
            'vote_recorded': vote.name,
            'decision_status': decision.status
        }

    def _check_decision_resolution(self, decision: GovernanceDecision) -> None:
        """Check if a decision can be resolved based on votes."""
        # Group votes by body
        body_votes: Dict[GovernanceBodyType, List[Dict]] = {
            body: [] for body in decision.required_bodies
        }

        for vote in decision.votes:
            body_type = GovernanceBodyType[vote['body']]
            if body_type in body_votes:
                body_votes[body_type].append(vote)

        # Check for vetoes
        vetoes = [v for v in decision.votes if v['vote'] == 'VETO']
        if vetoes:
            decision.status = 'vetoed'
            decision.resolved_at = datetime.utcnow()
            return

        # Check if all required bodies have voted
        all_bodies_voted = True
        all_approved = True

        for body, votes in body_votes.items():
            if not votes:
                all_bodies_voted = False
                continue

            # Check body approval (majority)
            approvals = len([v for v in votes if v['vote'] == 'APPROVE'])
            rejections = len([v for v in votes if v['vote'] == 'REJECT'])

            if rejections >= approvals:
                all_approved = False

        if all_bodies_voted:
            if all_approved:
                # Check dual-key requirement
                if decision.requires_dual_key:
                    key_bodies = [
                        GovernanceBodyType.TECHNICAL_SAFETY,
                        GovernanceBodyType.ETHICS_COUNCIL
                    ]
                    dual_key_satisfied = all(
                        body in decision.required_bodies and
                        any(v['vote'] == 'APPROVE' for v in body_votes.get(body, []))
                        for body in key_bodies
                        if body in decision.required_bodies
                    )
                    if dual_key_satisfied:
                        decision.status = 'approved'
                    else:
                        decision.status = 'pending'  # Still waiting
                else:
                    decision.status = 'approved'
            else:
                decision.status = 'rejected'

            if decision.status in ['approved', 'rejected']:
                decision.resolved_at = datetime.utcnow()

    def get_decision(self, decision_id: str) -> Optional[GovernanceDecision]:
        """Get a decision by ID."""
        return self._decisions.get(decision_id)

    def get_pending_decisions(self) -> List[GovernanceDecision]:
        """Get all pending decisions."""
        return [d for d in self._decisions.values() if d.status == 'pending']

    def get_decisions_for_body(
        self,
        body: GovernanceBodyType
    ) -> List[GovernanceDecision]:
        """Get decisions requiring a specific body's input."""
        return [
            d for d in self._decisions.values()
            if body in d.required_bodies
        ]

    def get_member_votes(self, member_id: str) -> List[Dict[str, Any]]:
        """Get all votes cast by a member."""
        votes = []
        for decision in self._decisions.values():
            for vote in decision.votes:
                if vote['member_id'] == member_id:
                    votes.append({
                        'decision_id': decision.id,
                        'decision_title': decision.title,
                        **vote
                    })
        return votes

    def get_body_members(self, body: GovernanceBodyType) -> List[GovernanceMember]:
        """Get all members of a governance body."""
        return self._bodies[body].copy()

    def generate_governance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive governance report."""
        decisions = list(self._decisions.values())

        return {
            'bodies': {
                body.name: len(members)
                for body, members in self._bodies.items()
            },
            'total_members': len(self._members),
            'decisions': {
                'total': len(decisions),
                'pending': len([d for d in decisions if d.status == 'pending']),
                'approved': len([d for d in decisions if d.status == 'approved']),
                'rejected': len([d for d in decisions if d.status == 'rejected']),
                'vetoed': len([d for d in decisions if d.status == 'vetoed'])
            },
            'by_type': {
                t.name: len([d for d in decisions if d.decision_type == t])
                for t in DecisionType
            },
            'total_votes': sum(len(d.votes) for d in decisions)
        }
