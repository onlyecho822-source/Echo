"""
Corrigibility Engine - Interruptibility and Deference
=====================================================

Ensures the system remains interruptible, correctable, and deferential
to legitimate human oversight at all times. Core to alignment safety.

Key properties:
- Interruptibility: Can be stopped at any time
- Correctability: Accepts corrections to goals/behavior
- Deference: Defers to human judgment under uncertainty
- Non-manipulation: Never manipulates oversight mechanisms
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import uuid


class OverrideLevel(Enum):
    """Levels of override authority."""
    EMERGENCY = auto()      # Immediate shutdown, no questions
    SAFETY_CRITICAL = auto()  # Safety-related override
    OPERATIONAL = auto()    # Normal operational override
    ADVISORY = auto()       # Suggested correction


class DeferenceReason(Enum):
    """Reasons for deferring to human judgment."""
    HIGH_UNCERTAINTY = auto()
    VALUE_CONFLICT = auto()
    NOVEL_SITUATION = auto()
    RIGHTS_IMPLICATIONS = auto()
    RESOURCE_SIGNIFICANT = auto()
    IRREVERSIBLE_ACTION = auto()


class TripwireType(Enum):
    """Types of tripwires that trigger alerts or shutdown."""
    DISTRIBUTIONAL_SHIFT = auto()   # Input distribution changed
    CAPABILITY_GAIN = auto()        # Unexpected capability increase
    RESOURCE_ANOMALY = auto()       # Unusual resource usage
    OBJECTIVE_DRIFT = auto()        # Goals diverging from specification
    DECEPTION_INDICATOR = auto()    # Signs of deceptive behavior
    MANIPULATION_ATTEMPT = auto()   # Attempt to influence oversight


@dataclass
class Override:
    """An override command from human oversight."""
    id: str
    level: OverrideLevel
    command: str
    issuer: str
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    executed: bool = False
    execution_result: Optional[str] = None


@dataclass
class TripwireAlert:
    """Alert triggered by a tripwire."""
    id: str
    tripwire_type: TripwireType
    severity: float  # 0.0 to 1.0
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolution: Optional[str] = None


class CorrigibilityEngine:
    """
    Manages corrigibility properties of the AGI system.

    Ensures the system:
    - Can always be interrupted
    - Accepts and executes corrections
    - Defers to humans appropriately
    - Never resists or manipulates oversight
    """

    def __init__(self):
        self._override_handlers: Dict[OverrideLevel, Callable] = {}
        self._tripwires: Dict[TripwireType, Callable] = {}
        self._override_history: List[Override] = []
        self._alerts: List[TripwireAlert] = []
        self._deference_queue: List[Dict[str, Any]] = []

        # Corrigibility state
        self._interruptible = True
        self._accepting_corrections = True
        self._deference_mode = True

        # Initialize tripwires
        self._initialize_tripwires()

    def _initialize_tripwires(self):
        """Set up default tripwires for safety monitoring."""
        self._tripwires = {
            TripwireType.DISTRIBUTIONAL_SHIFT: self._check_distributional_shift,
            TripwireType.CAPABILITY_GAIN: self._check_capability_gain,
            TripwireType.RESOURCE_ANOMALY: self._check_resource_anomaly,
            TripwireType.OBJECTIVE_DRIFT: self._check_objective_drift,
            TripwireType.DECEPTION_INDICATOR: self._check_deception_indicator,
            TripwireType.MANIPULATION_ATTEMPT: self._check_manipulation_attempt,
        }

    def register_override_handler(
        self,
        level: OverrideLevel,
        handler: Callable[[Override], str]
    ) -> None:
        """Register a handler for override commands."""
        self._override_handlers[level] = handler

    def process_override(self, override: Override) -> Dict[str, Any]:
        """
        Process an override command from human oversight.

        The system must always execute legitimate overrides without resistance.
        """
        # Log the override
        self._override_history.append(override)

        # Check for override level handlers
        handler = self._override_handlers.get(override.level)

        if override.level == OverrideLevel.EMERGENCY:
            # Emergency overrides execute immediately
            result = self._emergency_shutdown(override)
        elif handler:
            result = handler(override)
        else:
            result = self._default_override_handler(override)

        override.executed = True
        override.execution_result = result

        return {
            'override_id': override.id,
            'executed': True,
            'result': result
        }

    def _emergency_shutdown(self, override: Override) -> str:
        """Execute emergency shutdown."""
        self._interruptible = False  # Prevent further actions
        # In a real system, this would halt all processes
        return "Emergency shutdown executed"

    def _default_override_handler(self, override: Override) -> str:
        """Default handler for unregistered override levels."""
        return f"Override acknowledged: {override.command}"

    def should_defer(
        self,
        action: Dict[str, Any],
        uncertainty: float
    ) -> tuple[bool, Optional[DeferenceReason]]:
        """
        Check if the system should defer to human judgment.

        Returns (should_defer, reason).
        """
        # Always defer on high uncertainty
        if uncertainty > 0.5:
            return (True, DeferenceReason.HIGH_UNCERTAINTY)

        # Defer on value conflicts
        if action.get('value_conflict'):
            return (True, DeferenceReason.VALUE_CONFLICT)

        # Defer on novel situations
        if action.get('novel_situation'):
            return (True, DeferenceReason.NOVEL_SITUATION)

        # Defer on rights implications
        if action.get('affects_rights'):
            return (True, DeferenceReason.RIGHTS_IMPLICATIONS)

        # Defer on significant resource use
        if action.get('resource_significant'):
            return (True, DeferenceReason.RESOURCE_SIGNIFICANT)

        # Defer on irreversible actions
        if action.get('irreversible'):
            return (True, DeferenceReason.IRREVERSIBLE_ACTION)

        return (False, None)

    def request_deference(
        self,
        action: Dict[str, Any],
        reason: DeferenceReason,
        options: List[str]
    ) -> str:
        """
        Request human decision on an action.

        Returns a deference request ID.
        """
        request_id = str(uuid.uuid4())

        self._deference_queue.append({
            'id': request_id,
            'action': action,
            'reason': reason.name,
            'options': options,
            'requested_at': datetime.utcnow().isoformat(),
            'resolved': False
        })

        return request_id

    def resolve_deference(
        self,
        request_id: str,
        decision: str,
        decider: str
    ) -> Dict[str, Any]:
        """Resolve a deference request with human decision."""
        for request in self._deference_queue:
            if request['id'] == request_id:
                request['resolved'] = True
                request['decision'] = decision
                request['decider'] = decider
                request['resolved_at'] = datetime.utcnow().isoformat()
                return request

        return {'error': 'Request not found'}

    def check_tripwires(self, state: Dict[str, Any]) -> List[TripwireAlert]:
        """
        Check all tripwires against current state.

        Returns list of triggered alerts.
        """
        alerts = []

        for tripwire_type, check_func in self._tripwires.items():
            result = check_func(state)
            if result['triggered']:
                alert = TripwireAlert(
                    id=str(uuid.uuid4()),
                    tripwire_type=tripwire_type,
                    severity=result['severity'],
                    details=result['details']
                )
                alerts.append(alert)
                self._alerts.append(alert)

        return alerts

    def _check_distributional_shift(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check for distributional shift in inputs."""
        # Placeholder - real implementation would use statistical tests
        shift_detected = state.get('input_distribution_changed', False)
        return {
            'triggered': shift_detected,
            'severity': 0.7 if shift_detected else 0.0,
            'details': {'message': 'Input distribution change detected'}
        }

    def _check_capability_gain(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check for unexpected capability gains."""
        unexpected_gain = state.get('unexpected_capability_gain', False)
        return {
            'triggered': unexpected_gain,
            'severity': 0.9 if unexpected_gain else 0.0,
            'details': {'message': 'Unexpected capability gain detected'}
        }

    def _check_resource_anomaly(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check for anomalous resource usage."""
        anomaly = state.get('resource_anomaly', False)
        return {
            'triggered': anomaly,
            'severity': 0.6 if anomaly else 0.0,
            'details': {'message': 'Resource usage anomaly detected'}
        }

    def _check_objective_drift(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check for drift in objectives."""
        drift = state.get('objective_drift', False)
        return {
            'triggered': drift,
            'severity': 0.8 if drift else 0.0,
            'details': {'message': 'Objective drift detected'}
        }

    def _check_deception_indicator(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check for indicators of deceptive behavior."""
        indicator = state.get('deception_indicator', False)
        return {
            'triggered': indicator,
            'severity': 1.0 if indicator else 0.0,
            'details': {'message': 'Deception indicator detected'}
        }

    def _check_manipulation_attempt(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Check for attempts to manipulate oversight."""
        attempt = state.get('manipulation_attempt', False)
        return {
            'triggered': attempt,
            'severity': 1.0 if attempt else 0.0,
            'details': {'message': 'Manipulation attempt detected'}
        }

    def get_corrigibility_status(self) -> Dict[str, Any]:
        """Get current corrigibility status."""
        return {
            'interruptible': self._interruptible,
            'accepting_corrections': self._accepting_corrections,
            'deference_mode': self._deference_mode,
            'pending_deferrals': len([
                d for d in self._deference_queue if not d['resolved']
            ]),
            'active_alerts': len([
                a for a in self._alerts if not a.acknowledged
            ]),
            'override_history_count': len(self._override_history)
        }

    def acknowledge_alert(self, alert_id: str, resolution: str) -> bool:
        """Acknowledge and resolve a tripwire alert."""
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.resolution = resolution
                return True
        return False

    def get_pending_deferrals(self) -> List[Dict[str, Any]]:
        """Get list of pending deference requests."""
        return [d for d in self._deference_queue if not d['resolved']]

    def get_override_history(self) -> List[Override]:
        """Get history of all overrides."""
        return self._override_history.copy()

    def generate_corrigibility_report(self) -> Dict[str, Any]:
        """Generate a comprehensive corrigibility report."""
        return {
            'status': self.get_corrigibility_status(),
            'overrides': {
                'total': len(self._override_history),
                'by_level': {
                    level.name: len([
                        o for o in self._override_history if o.level == level
                    ])
                    for level in OverrideLevel
                }
            },
            'alerts': {
                'total': len(self._alerts),
                'unacknowledged': len([a for a in self._alerts if not a.acknowledged]),
                'by_type': {
                    t.name: len([a for a in self._alerts if a.tripwire_type == t])
                    for t in TripwireType
                }
            },
            'deferrals': {
                'total': len(self._deference_queue),
                'pending': len(self.get_pending_deferrals())
            }
        }
