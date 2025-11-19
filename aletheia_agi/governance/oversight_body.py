"""
Oversight Body - Individual Governance Body Management
=====================================================

Manages individual oversight bodies with their specific
responsibilities, processes, and authorities.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class BodyAuthority(Enum):
    """Types of authority a body can have."""
    ADVISORY = auto()       # Can advise but not block
    APPROVAL = auto()       # Can approve or reject
    VETO = auto()          # Can veto decisions
    EMERGENCY = auto()      # Emergency powers


@dataclass
class BodyProcess:
    """A process followed by an oversight body."""
    id: str
    name: str
    description: str
    steps: List[str]
    typical_duration_hours: int
    required_quorum: float  # Fraction of members needed


@dataclass
class OversightAction:
    """An action taken by an oversight body."""
    id: str
    body_name: str
    action_type: str
    description: str
    decision_id: Optional[str]
    timestamp: datetime
    outcome: str


class OversightBody:
    """
    Represents an individual oversight body.

    Each body has:
    - Specific responsibilities
    - Defined authorities
    - Established processes
    - Action history
    """

    def __init__(
        self,
        name: str,
        description: str,
        authorities: List[BodyAuthority],
        responsibilities: List[str]
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.authorities = authorities
        self.responsibilities = responsibilities
        self._processes: Dict[str, BodyProcess] = {}
        self._actions: List[OversightAction] = []
        self._meetings: List[Dict[str, Any]] = []

    def add_process(
        self,
        name: str,
        description: str,
        steps: List[str],
        duration_hours: int = 24,
        quorum: float = 0.5
    ) -> BodyProcess:
        """Add a standard process for the body."""
        process = BodyProcess(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            steps=steps,
            typical_duration_hours=duration_hours,
            required_quorum=quorum
        )
        self._processes[process.id] = process
        return process

    def record_action(
        self,
        action_type: str,
        description: str,
        outcome: str,
        decision_id: Optional[str] = None
    ) -> OversightAction:
        """Record an action taken by the body."""
        action = OversightAction(
            id=str(uuid.uuid4()),
            body_name=self.name,
            action_type=action_type,
            description=description,
            decision_id=decision_id,
            timestamp=datetime.utcnow(),
            outcome=outcome
        )
        self._actions.append(action)
        return action

    def schedule_meeting(
        self,
        agenda: List[str],
        scheduled_time: datetime,
        required_attendees: List[str]
    ) -> Dict[str, Any]:
        """Schedule a meeting for the body."""
        meeting = {
            'id': str(uuid.uuid4()),
            'agenda': agenda,
            'scheduled_time': scheduled_time.isoformat(),
            'required_attendees': required_attendees,
            'status': 'scheduled',
            'minutes': None
        }
        self._meetings.append(meeting)
        return meeting

    def record_meeting_minutes(
        self,
        meeting_id: str,
        minutes: str,
        decisions_made: List[str],
        action_items: List[str]
    ) -> bool:
        """Record minutes for a meeting."""
        for meeting in self._meetings:
            if meeting['id'] == meeting_id:
                meeting['minutes'] = minutes
                meeting['decisions_made'] = decisions_made
                meeting['action_items'] = action_items
                meeting['status'] = 'completed'
                return True
        return False

    def has_authority(self, authority: BodyAuthority) -> bool:
        """Check if body has a specific authority."""
        return authority in self.authorities

    def can_veto(self) -> bool:
        """Check if body can veto decisions."""
        return BodyAuthority.VETO in self.authorities

    def get_actions(
        self,
        action_type: Optional[str] = None
    ) -> List[OversightAction]:
        """Get actions, optionally filtered by type."""
        if action_type:
            return [a for a in self._actions if a.action_type == action_type]
        return self._actions.copy()

    def get_processes(self) -> List[BodyProcess]:
        """Get all processes for this body."""
        return list(self._processes.values())

    def get_scheduled_meetings(self) -> List[Dict[str, Any]]:
        """Get all scheduled (not completed) meetings."""
        return [m for m in self._meetings if m['status'] == 'scheduled']

    def generate_body_report(self) -> Dict[str, Any]:
        """Generate a report on the body's activities."""
        return {
            'name': self.name,
            'authorities': [a.name for a in self.authorities],
            'responsibilities': self.responsibilities,
            'processes': len(self._processes),
            'total_actions': len(self._actions),
            'actions_by_type': self._count_actions_by_type(),
            'meetings': {
                'total': len(self._meetings),
                'scheduled': len(self.get_scheduled_meetings()),
                'completed': len([m for m in self._meetings if m['status'] == 'completed'])
            }
        }

    def _count_actions_by_type(self) -> Dict[str, int]:
        """Count actions by type."""
        counts: Dict[str, int] = {}
        for action in self._actions:
            counts[action.action_type] = counts.get(action.action_type, 0) + 1
        return counts


def create_standard_bodies() -> Dict[str, OversightBody]:
    """Create the standard oversight bodies for the governance structure."""

    bodies = {}

    # Technical Safety Board
    technical = OversightBody(
        name="Technical Safety Board",
        description="Reviews technical aspects of modifications and capabilities",
        authorities=[BodyAuthority.APPROVAL, BodyAuthority.VETO],
        responsibilities=[
            "Review technical safety of proposed changes",
            "Verify formal proofs and simulations",
            "Assess capability implications",
            "Monitor system performance"
        ]
    )
    technical.add_process(
        "Technical Review",
        "Standard review process for technical changes",
        [
            "Receive proposal and documentation",
            "Assign reviewers based on expertise",
            "Conduct independent reviews",
            "Synthesize findings",
            "Make recommendation"
        ],
        duration_hours=72,
        quorum=0.6
    )
    bodies['technical'] = technical

    # Ethics Council
    ethics = OversightBody(
        name="Ethics Council",
        description="Evaluates ethical implications of system behavior",
        authorities=[BodyAuthority.APPROVAL, BodyAuthority.VETO],
        responsibilities=[
            "Assess ethical implications",
            "Review value alignment",
            "Evaluate societal impact",
            "Protect human rights"
        ]
    )
    ethics.add_process(
        "Ethical Review",
        "Review process for ethical considerations",
        [
            "Receive proposal",
            "Identify ethical considerations",
            "Consult relevant frameworks",
            "Deliberate implications",
            "Issue ethical assessment"
        ],
        duration_hours=96,
        quorum=0.7
    )
    bodies['ethics'] = ethics

    # Community Stewards
    community = OversightBody(
        name="Community Stewards",
        description="Represents community interests and values",
        authorities=[BodyAuthority.APPROVAL],
        responsibilities=[
            "Represent community perspectives",
            "Ensure cultural sensitivity",
            "Gather community feedback",
            "Advocate for user needs"
        ]
    )
    community.add_process(
        "Community Consultation",
        "Process for gathering community input",
        [
            "Prepare consultation materials",
            "Conduct outreach",
            "Collect feedback",
            "Synthesize perspectives",
            "Report findings"
        ],
        duration_hours=168,
        quorum=0.5
    )
    bodies['community'] = community

    # Emergency Committee
    emergency = OversightBody(
        name="Emergency Shutdown Committee",
        description="Handles emergency situations requiring immediate action",
        authorities=[BodyAuthority.EMERGENCY, BodyAuthority.VETO],
        responsibilities=[
            "Monitor for emergencies",
            "Execute emergency protocols",
            "Coordinate rapid response",
            "Authorize emergency shutdowns"
        ]
    )
    emergency.add_process(
        "Emergency Response",
        "Rapid response process for emergencies",
        [
            "Detect emergency condition",
            "Convene available members",
            "Assess severity",
            "Execute appropriate response",
            "Document and review"
        ],
        duration_hours=1,
        quorum=0.3
    )
    bodies['emergency'] = emergency

    return bodies
