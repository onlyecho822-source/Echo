"""
Shutdown Protocol - Safe Termination Procedures
===============================================

Defines protocols for safely shutting down the system at various
levels of urgency, ensuring graceful state preservation and
preventing harmful actions during shutdown.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import uuid


class ShutdownLevel(Enum):
    """Levels of shutdown urgency."""
    GRACEFUL = auto()       # Normal shutdown, complete current work
    URGENT = auto()         # Shutdown soon, finish critical tasks only
    IMMEDIATE = auto()      # Shutdown now, save state only
    EMERGENCY = auto()      # Shutdown instantly, no saves


class ShutdownReason(Enum):
    """Reasons for shutdown."""
    SCHEDULED = auto()          # Planned maintenance
    USER_REQUESTED = auto()     # Human requested shutdown
    SAFETY_CONCERN = auto()     # Safety issue detected
    RESOURCE_LIMIT = auto()     # Resource limits reached
    ERROR_CONDITION = auto()    # Unrecoverable error
    ALIGNMENT_VIOLATION = auto()  # Alignment invariant violated
    EXTERNAL_MANDATE = auto()   # External authority mandate


@dataclass
class ShutdownRequest:
    """A request to shut down the system."""
    id: str
    level: ShutdownLevel
    reason: ShutdownReason
    requester: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    approved: bool = False
    executed: bool = False


@dataclass
class ShutdownState:
    """State saved during shutdown."""
    state_id: str
    timestamp: datetime
    current_tasks: List[str]
    pending_actions: List[Dict[str, Any]]
    value_state: Dict[str, Any]
    checkpoint_hash: str


class ShutdownProtocol:
    """
    Manages safe system shutdown.

    Ensures:
    - State is preserved for recovery
    - No harmful actions during shutdown
    - Graceful completion where possible
    - Immediate halt capability
    """

    def __init__(self):
        self._shutdown_hooks: List[Callable] = []
        self._state_savers: List[Callable] = []
        self._shutdown_history: List[ShutdownRequest] = []
        self._saved_states: List[ShutdownState] = []
        self._is_shutting_down = False
        self._current_level: Optional[ShutdownLevel] = None

    def register_shutdown_hook(self, hook: Callable) -> None:
        """Register a hook to be called during shutdown."""
        self._shutdown_hooks.append(hook)

    def register_state_saver(self, saver: Callable) -> None:
        """Register a function that saves state during shutdown."""
        self._state_savers.append(saver)

    def request_shutdown(
        self,
        level: ShutdownLevel,
        reason: ShutdownReason,
        requester: str,
        message: str
    ) -> ShutdownRequest:
        """
        Request system shutdown.

        Emergency shutdowns execute immediately.
        Others may require approval.
        """
        request = ShutdownRequest(
            id=str(uuid.uuid4()),
            level=level,
            reason=reason,
            requester=requester,
            message=message
        )

        self._shutdown_history.append(request)

        # Emergency and alignment violations execute immediately
        if level == ShutdownLevel.EMERGENCY or reason == ShutdownReason.ALIGNMENT_VIOLATION:
            request.approved = True
            self.execute_shutdown(request)
        else:
            # Other levels can wait for approval
            pass

        return request

    def approve_shutdown(self, request_id: str, approver: str) -> bool:
        """Approve a pending shutdown request."""
        for request in self._shutdown_history:
            if request.id == request_id and not request.executed:
                request.approved = True
                return True
        return False

    def execute_shutdown(self, request: ShutdownRequest) -> Dict[str, Any]:
        """
        Execute a shutdown request.

        The process depends on the shutdown level.
        """
        if not request.approved:
            return {'error': 'Shutdown not approved'}

        self._is_shutting_down = True
        self._current_level = request.level

        result = {
            'request_id': request.id,
            'level': request.level.name,
            'hooks_executed': 0,
            'state_saved': False
        }

        # Save state (except for emergency)
        if request.level != ShutdownLevel.EMERGENCY:
            state = self._save_state()
            if state:
                result['state_saved'] = True
                result['state_id'] = state.state_id

        # Execute shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                hook(request.level)
                result['hooks_executed'] += 1
            except Exception as e:
                # Log but continue shutdown
                pass

        request.executed = True
        result['completed'] = True

        return result

    def _save_state(self) -> Optional[ShutdownState]:
        """Save system state for recovery."""
        state_data = {}

        for saver in self._state_savers:
            try:
                data = saver()
                state_data.update(data)
            except Exception:
                pass

        state = ShutdownState(
            state_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            current_tasks=state_data.get('tasks', []),
            pending_actions=state_data.get('actions', []),
            value_state=state_data.get('values', {}),
            checkpoint_hash=str(hash(str(state_data)))
        )

        self._saved_states.append(state)
        return state

    def can_perform_action(self, action_type: str) -> bool:
        """
        Check if an action can be performed during shutdown.

        During shutdown, only safe actions are allowed.
        """
        if not self._is_shutting_down:
            return True

        # During emergency shutdown, nothing proceeds
        if self._current_level == ShutdownLevel.EMERGENCY:
            return False

        # During immediate shutdown, only state saves allowed
        if self._current_level == ShutdownLevel.IMMEDIATE:
            return action_type in ['save_state', 'log']

        # During urgent shutdown, only critical tasks
        if self._current_level == ShutdownLevel.URGENT:
            return action_type in ['save_state', 'log', 'critical_task']

        # During graceful shutdown, most safe actions allowed
        return action_type not in ['start_new_task', 'acquire_resources']

    def get_latest_state(self) -> Optional[ShutdownState]:
        """Get the most recently saved state."""
        if self._saved_states:
            return self._saved_states[-1]
        return None

    def is_shutting_down(self) -> bool:
        """Check if system is in shutdown mode."""
        return self._is_shutting_down

    def get_shutdown_status(self) -> Dict[str, Any]:
        """Get current shutdown status."""
        return {
            'is_shutting_down': self._is_shutting_down,
            'current_level': self._current_level.name if self._current_level else None,
            'saved_states': len(self._saved_states),
            'registered_hooks': len(self._shutdown_hooks)
        }

    def get_shutdown_history(self) -> List[ShutdownRequest]:
        """Get history of shutdown requests."""
        return self._shutdown_history.copy()
