"""
Defense Wall - Core security system

Digital immune system for identity protection and risk management.
"""

import hashlib
import secrets
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ThreatLevel(Enum):
    """Threat severity levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5


class SecurityAction(Enum):
    """Actions that can be taken in response to threats."""
    BLOCK = 'block'
    ALERT = 'alert'
    LOG = 'log'
    QUARANTINE = 'quarantine'
    ALLOW = 'allow'


@dataclass
class SecurityEvent:
    """Record of a security event."""
    event_type: str
    threat_level: ThreatLevel
    description: str
    action_taken: SecurityAction
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    details: Dict[str, Any] = field(default_factory=dict)


class DefenseWall:
    """
    Core security system for Echo Life OS.

    Provides:
    - Identity firewall
    - Credential management
    - Breach detection
    - Behavior monitoring
    - Emergency controls
    """

    def __init__(self, memory_kernel=None):
        """
        Initialize Defense Wall.

        Args:
            memory_kernel: Optional MemoryKernel for persistent storage
        """
        self.memory_kernel = memory_kernel
        self._events: List[SecurityEvent] = []
        self._blocked_actions: set = set()
        self._alert_callbacks: List[callable] = []
        self._locked = False
        self._emergency_mode = False

        # Security configuration
        self._config = {
            'max_failed_attempts': 5,
            'lockout_duration': 300,  # seconds
            'auto_log_level': ThreatLevel.LOW,
            'sensitive_patterns': [
                'password', 'secret', 'key', 'token', 'credential',
                'ssn', 'social security', 'credit card', 'cvv'
            ],
            'prohibited_actions': [
                'delete_all', 'wipe_system', 'share_credentials',
                'disable_security', 'export_passwords'
            ]
        }

        self._failed_attempts: Dict[str, int] = {}
        self._lockout_until: Dict[str, float] = {}

    def check_action(self, action: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Check if an action is allowed.

        Args:
            action: Action to check
            context: Additional context

        Returns:
            Dictionary with allowed status and details
        """
        if context is None:
            context = {}

        result = {
            'allowed': True,
            'action': action,
            'threats': [],
            'warnings': [],
            'requires_confirmation': False
        }

        # Check emergency mode
        if self._emergency_mode:
            result['allowed'] = False
            result['threats'].append({
                'level': ThreatLevel.CRITICAL.name,
                'description': 'System in emergency lockdown mode'
            })
            return result

        # Check if system is locked
        if self._locked:
            result['allowed'] = False
            result['threats'].append({
                'level': ThreatLevel.HIGH.name,
                'description': 'System is locked'
            })
            return result

        action_lower = action.lower()

        # Check prohibited actions
        for prohibited in self._config['prohibited_actions']:
            if prohibited in action_lower:
                result['allowed'] = False
                result['threats'].append({
                    'level': ThreatLevel.CRITICAL.name,
                    'description': f'Prohibited action: {prohibited}'
                })
                self._log_event(SecurityEvent(
                    event_type='prohibited_action',
                    threat_level=ThreatLevel.CRITICAL,
                    description=f'Attempted prohibited action: {action}',
                    action_taken=SecurityAction.BLOCK
                ))

        # Check for sensitive data exposure
        for pattern in self._config['sensitive_patterns']:
            if pattern in action_lower:
                result['warnings'].append(
                    f'Action involves sensitive data: {pattern}'
                )
                result['requires_confirmation'] = True

        # Check user/source lockout
        source = context.get('source', 'default')
        if source in self._lockout_until:
            if time.time() < self._lockout_until[source]:
                result['allowed'] = False
                result['threats'].append({
                    'level': ThreatLevel.HIGH.name,
                    'description': f'Source {source} is locked out'
                })

        return result

    def validate_credential(self, credential_type: str, value: str) -> Dict[str, Any]:
        """
        Validate a credential value.

        Args:
            credential_type: Type of credential (password, token, etc.)
            value: Credential value to validate

        Returns:
            Validation result with strength assessment
        """
        result = {
            'valid': True,
            'strength': 'unknown',
            'issues': [],
            'recommendations': []
        }

        if credential_type == 'password':
            # Password strength check
            if len(value) < 8:
                result['issues'].append('Password too short (min 8 characters)')
                result['valid'] = False
            if len(value) < 12:
                result['recommendations'].append('Consider using 12+ characters')

            has_upper = any(c.isupper() for c in value)
            has_lower = any(c.islower() for c in value)
            has_digit = any(c.isdigit() for c in value)
            has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in value)

            complexity = sum([has_upper, has_lower, has_digit, has_special])

            if complexity < 2:
                result['issues'].append('Password lacks complexity')
                result['valid'] = False
            elif complexity == 2:
                result['strength'] = 'weak'
            elif complexity == 3:
                result['strength'] = 'medium'
            else:
                result['strength'] = 'strong'

            # Check for common patterns
            common_patterns = ['123', 'abc', 'password', 'qwerty']
            if any(p in value.lower() for p in common_patterns):
                result['issues'].append('Contains common pattern')
                result['strength'] = 'weak'

        return result

    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate a cryptographically secure token.

        Args:
            length: Token length in bytes

        Returns:
            Hex-encoded secure token
        """
        return secrets.token_hex(length)

    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> Dict[str, str]:
        """
        Hash sensitive data for storage.

        Args:
            data: Data to hash
            salt: Optional salt (generated if not provided)

        Returns:
            Dictionary with hash and salt
        """
        if salt is None:
            salt = secrets.token_hex(16)

        salted = salt + data
        hashed = hashlib.sha256(salted.encode()).hexdigest()

        return {
            'hash': hashed,
            'salt': salt
        }

    def verify_hash(self, data: str, stored_hash: str, salt: str) -> bool:
        """
        Verify data against stored hash.

        Args:
            data: Data to verify
            stored_hash: Stored hash value
            salt: Salt used in hashing

        Returns:
            True if data matches hash
        """
        salted = salt + data
        computed = hashlib.sha256(salted.encode()).hexdigest()
        return secrets.compare_digest(computed, stored_hash)

    def record_failed_attempt(self, source: str):
        """
        Record a failed authentication attempt.

        Args:
            source: Source of the failed attempt
        """
        self._failed_attempts[source] = self._failed_attempts.get(source, 0) + 1

        if self._failed_attempts[source] >= self._config['max_failed_attempts']:
            self._lockout_until[source] = time.time() + self._config['lockout_duration']
            self._log_event(SecurityEvent(
                event_type='lockout',
                threat_level=ThreatLevel.HIGH,
                description=f'Source {source} locked out after {self._failed_attempts[source]} failed attempts',
                action_taken=SecurityAction.BLOCK,
                details={'source': source}
            ))

    def clear_failed_attempts(self, source: str):
        """Clear failed attempts for a source after successful auth."""
        if source in self._failed_attempts:
            del self._failed_attempts[source]
        if source in self._lockout_until:
            del self._lockout_until[source]

    def lock(self):
        """Lock the system."""
        self._locked = True
        self._log_event(SecurityEvent(
            event_type='system_lock',
            threat_level=ThreatLevel.INFO,
            description='System locked',
            action_taken=SecurityAction.LOG
        ))

    def unlock(self):
        """Unlock the system."""
        self._locked = False
        self._log_event(SecurityEvent(
            event_type='system_unlock',
            threat_level=ThreatLevel.INFO,
            description='System unlocked',
            action_taken=SecurityAction.LOG
        ))

    def emergency_lockdown(self):
        """
        Activate emergency lockdown mode.

        Blocks all actions until manually reset.
        """
        self._emergency_mode = True
        self._locked = True
        self._log_event(SecurityEvent(
            event_type='emergency_lockdown',
            threat_level=ThreatLevel.CRITICAL,
            description='Emergency lockdown activated',
            action_taken=SecurityAction.BLOCK
        ))
        self._trigger_alerts('Emergency lockdown activated')

    def reset_emergency(self, confirmation_code: str) -> bool:
        """
        Reset emergency mode with confirmation.

        Args:
            confirmation_code: Required confirmation code

        Returns:
            True if reset successful
        """
        # In production, this would verify against a stored code
        if len(confirmation_code) >= 8:
            self._emergency_mode = False
            self._locked = False
            self._log_event(SecurityEvent(
                event_type='emergency_reset',
                threat_level=ThreatLevel.HIGH,
                description='Emergency mode reset',
                action_taken=SecurityAction.LOG
            ))
            return True
        return False

    def add_alert_callback(self, callback: callable):
        """Add a callback for security alerts."""
        self._alert_callbacks.append(callback)

    def _trigger_alerts(self, message: str):
        """Trigger all alert callbacks."""
        for callback in self._alert_callbacks:
            try:
                callback(message)
            except Exception:
                pass  # Don't let callback errors break security

    def _log_event(self, event: SecurityEvent):
        """Log a security event."""
        self._events.append(event)

        # Store in memory kernel if available
        if self.memory_kernel:
            self.memory_kernel.log_event(
                event.event_type,
                {
                    'threat_level': event.threat_level.name,
                    'description': event.description,
                    'action': event.action_taken.value,
                    'details': event.details
                },
                agent='defense_wall'
            )

        # Auto-alert for high severity
        if event.threat_level.value <= ThreatLevel.HIGH.value:
            self._trigger_alerts(f"[{event.threat_level.name}] {event.description}")

    def get_events(self, limit: int = 100,
                   min_level: ThreatLevel = ThreatLevel.INFO) -> List[Dict[str, Any]]:
        """
        Get recent security events.

        Args:
            limit: Maximum events to return
            min_level: Minimum threat level to include

        Returns:
            List of event dictionaries
        """
        filtered = [
            e for e in self._events
            if e.threat_level.value <= min_level.value
        ]

        return [
            {
                'type': e.event_type,
                'level': e.threat_level.name,
                'description': e.description,
                'action': e.action_taken.value,
                'timestamp': e.timestamp,
                'details': e.details
            }
            for e in filtered[-limit:]
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get security system status."""
        recent_threats = [
            e for e in self._events[-50:]
            if e.threat_level.value <= ThreatLevel.MEDIUM.value
        ]

        return {
            'locked': self._locked,
            'emergency_mode': self._emergency_mode,
            'active_lockouts': len(self._lockout_until),
            'recent_threats': len(recent_threats),
            'total_events': len(self._events)
        }
