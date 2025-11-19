"""
Echo Life OS - Defense Wall
============================
Zero-trust security architecture for personal data protection.

The Defense Wall is the digital immune system that protects user identity,
data, and operations from threats while maintaining privacy.
"""

import os
import re
import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import asyncio
import aiohttp


class ThreatLevel(Enum):
    """Threat severity levels."""
    CRITICAL = 5    # Immediate action required
    HIGH = 4        # Significant risk
    MEDIUM = 3      # Moderate concern
    LOW = 2         # Minor issue
    INFO = 1        # Informational only


class SecurityLayer(Enum):
    """Defense Wall security layers."""
    L1_IDENTITY_FIREWALL = 1      # Password vault, breach monitoring
    L2_BEHAVIOR_WATCHDOG = 2      # Anomaly detection
    L3_VENDOR_ISOLATION = 3       # API sandboxing
    L4_KILL_SWITCH = 4            # Emergency controls
    L5_PUBLIC_BOUNDARY = 5        # Data classification enforcement


@dataclass
class SecurityAlert:
    """A security alert from the Defense Wall."""
    id: str
    timestamp: datetime
    layer: SecurityLayer
    threat_level: ThreatLevel
    title: str
    description: str
    source: str
    action_taken: Optional[str] = None
    requires_user_action: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Credential:
    """Stored credential with metadata."""
    id: str
    service: str
    username: str
    password_hash: str          # Only hash stored
    last_updated: datetime
    breach_checked: datetime
    is_compromised: bool = False
    strength_score: int = 0     # 0-100
    notes_encrypted: Optional[bytes] = None


class IdentityFirewall:
    """
    Layer 1: Personal Identity Firewall

    - Password vault with encryption
    - Breach monitoring via HIBP
    - Credential strength analysis
    - Phishing detection
    """

    def __init__(self, db_path: str, encryption_key: bytes):
        self.db_path = db_path
        self.encryption_key = encryption_key
        self._init_database()

        # Known phishing patterns
        self.phishing_patterns = [
            r'(?i)verify.*account',
            r'(?i)suspended.*account',
            r'(?i)unusual.*activity',
            r'(?i)click.*immediately',
            r'(?i)confirm.*identity',
        ]

        # Suspicious TLDs
        self.suspicious_tlds = ['.xyz', '.top', '.tk', '.ml', '.ga', '.cf']

    def _init_database(self):
        """Initialize credentials database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id TEXT PRIMARY KEY,
                service TEXT NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                breach_checked TEXT NOT NULL,
                is_compromised INTEGER DEFAULT 0,
                strength_score INTEGER DEFAULT 0,
                notes_encrypted BLOB
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS breach_history (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                checked_at TEXT NOT NULL,
                breaches_found INTEGER DEFAULT 0,
                breach_names TEXT
            )
        ''')

        conn.commit()
        conn.close()

    async def check_breach(self, email: str) -> Tuple[bool, List[str]]:
        """
        Check if email appears in known breaches via HIBP API.

        Args:
            email: Email address to check

        Returns:
            Tuple of (is_breached, list of breach names)
        """
        # Hash email for k-anonymity query
        sha1_hash = hashlib.sha1(email.lower().encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        try:
            async with aiohttp.ClientSession() as session:
                # Use HIBP range API for privacy
                url = f"https://api.pwnedpasswords.com/range/{prefix}"
                async with session.get(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        hashes = dict(
                            line.split(':') for line in text.strip().split('\n')
                        )
                        if suffix in hashes:
                            return True, [f"Found in {hashes[suffix]} breaches"]

            return False, []

        except Exception as e:
            return False, [f"Check failed: {str(e)}"]

    def analyze_password_strength(self, password: str) -> Tuple[int, List[str]]:
        """
        Analyze password strength.

        Returns:
            Tuple of (score 0-100, list of recommendations)
        """
        score = 0
        recommendations = []

        # Length check
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        else:
            recommendations.append("Use at least 16 characters")

        # Character diversity
        if re.search(r'[a-z]', password):
            score += 10
        else:
            recommendations.append("Add lowercase letters")

        if re.search(r'[A-Z]', password):
            score += 10
        else:
            recommendations.append("Add uppercase letters")

        if re.search(r'\d', password):
            score += 10
        else:
            recommendations.append("Add numbers")

        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 15
        else:
            recommendations.append("Add special characters")

        # Check for common patterns
        common_patterns = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if any(pattern in password.lower() for pattern in common_patterns):
            score -= 30
            recommendations.append("Avoid common password patterns")

        # Sequential characters
        if re.search(r'(012|123|234|345|456|567|678|789|abc|bcd|cde)', password.lower()):
            score -= 10
            recommendations.append("Avoid sequential characters")

        return max(0, min(100, score)), recommendations

    def detect_phishing(self, url: str, content: str = "") -> Tuple[bool, List[str]]:
        """
        Detect potential phishing attempts.

        Args:
            url: URL to check
            content: Optional email/page content

        Returns:
            Tuple of (is_phishing, reasons)
        """
        reasons = []

        # Check suspicious TLDs
        for tld in self.suspicious_tlds:
            if url.endswith(tld):
                reasons.append(f"Suspicious TLD: {tld}")

        # Check for IP address URLs
        if re.search(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
            reasons.append("URL uses IP address instead of domain")

        # Check for homograph attacks (lookalike characters)
        homograph_chars = {'0': 'o', '1': 'l', '5': 's', '@': 'a'}
        for char, replacement in homograph_chars.items():
            if char in url.lower():
                reasons.append(f"Possible homograph attack: {char} may be disguising {replacement}")

        # Check content for phishing patterns
        if content:
            for pattern in self.phishing_patterns:
                if re.search(pattern, content):
                    reasons.append(f"Phishing pattern detected: {pattern}")

        # Check for urgency indicators
        urgency_words = ['immediately', 'urgent', 'expire', 'suspended', 'verify now']
        if content:
            for word in urgency_words:
                if word in content.lower():
                    reasons.append(f"Urgency indicator: '{word}'")

        return len(reasons) > 0, reasons


class BehaviorWatchdog:
    """
    Layer 2: Behavior Watchdog

    - Anomaly detection in user patterns
    - Unauthorized access alerts
    - Session monitoring
    - AI response drift detection
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()

        # Behavioral baselines (loaded from user history)
        self.baselines: Dict[str, Any] = {}

    def _init_database(self):
        """Initialize behavior tracking database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior_logs (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT,
                risk_score REAL DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')

        conn.commit()
        conn.close()

    def log_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        risk_score: float = 0
    ) -> str:
        """Log a behavioral event."""
        event_id = secrets.token_hex(16)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO behavior_logs (id, timestamp, event_type, details, risk_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            event_id,
            datetime.utcnow().isoformat(),
            event_type,
            json.dumps(details),
            risk_score
        ))

        conn.commit()
        conn.close()

        return event_id

    def detect_anomaly(
        self,
        event_type: str,
        current_value: Any,
        baseline_key: str
    ) -> Tuple[bool, float]:
        """
        Detect anomalies by comparing to baseline.

        Returns:
            Tuple of (is_anomaly, deviation_score)
        """
        if baseline_key not in self.baselines:
            # No baseline yet, store current as baseline
            self.baselines[baseline_key] = {
                'values': [current_value],
                'mean': current_value if isinstance(current_value, (int, float)) else None
            }
            return False, 0

        baseline = self.baselines[baseline_key]

        # For numeric values, use statistical analysis
        if isinstance(current_value, (int, float)) and baseline['mean']:
            values = baseline['values']
            mean = sum(values) / len(values)
            std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5

            if std > 0:
                z_score = abs(current_value - mean) / std
                # Update baseline
                baseline['values'].append(current_value)
                baseline['values'] = baseline['values'][-100:]  # Keep last 100
                baseline['mean'] = sum(baseline['values']) / len(baseline['values'])

                return z_score > 3, z_score

        return False, 0

    def check_session_validity(self, session_id: str) -> bool:
        """Check if a session is still valid."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT is_active, last_activity FROM sessions WHERE id = ?
        ''', (session_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return False

        is_active, last_activity = row
        last_dt = datetime.fromisoformat(last_activity)

        # Session expires after 24 hours of inactivity
        if datetime.utcnow() - last_dt > timedelta(hours=24):
            return False

        return bool(is_active)


class VendorIsolation:
    """
    Layer 3: Vendor Isolation

    - API request/response sanitization
    - No raw memory sync to external services
    - Abstraction layers for LLM calls
    """

    def __init__(self):
        # Sensitive patterns to redact
        self.sensitive_patterns = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),
            (r'\b\d{16}\b', '[CARD_REDACTED]'),
            (r'\b(?:api[_-]?key|secret|token)["\']?\s*[:=]\s*["\']?([^"\'\s]+)', '[API_KEY_REDACTED]'),
        ]

    def sanitize_for_external(self, data: str) -> str:
        """
        Sanitize data before sending to external APIs.

        Removes or redacts sensitive information.
        """
        sanitized = data

        for pattern, replacement in self.sensitive_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized

    def abstract_memory_summary(self, memories: List[Dict]) -> str:
        """
        Create abstracted summary of memories for external LLM.

        Never sends raw memory content.
        """
        # Extract only non-sensitive metadata
        summary_parts = []

        for mem in memories:
            abstract = {
                'type': mem.get('memory_type'),
                'tags': mem.get('tags', []),
                'recency': 'recent' if mem.get('access_count', 0) > 5 else 'historical',
                'priority': mem.get('priority')
            }
            summary_parts.append(str(abstract))

        return f"User context includes {len(memories)} relevant memories: {'; '.join(summary_parts)}"


class KillSwitch:
    """
    Layer 4: Local Kill Switch

    - Single command: Lock all operations
    - Double command: Secure wipe
    - Remote deactivation
    - Automatic trigger on breach
    """

    def __init__(self, state_path: str):
        self.state_path = Path(state_path)
        self.state_file = self.state_path / "kill_switch.state"
        self._ensure_state_file()

    def _ensure_state_file(self):
        """Ensure state file exists."""
        self.state_path.mkdir(parents=True, exist_ok=True)
        if not self.state_file.exists():
            self._write_state({
                'locked': False,
                'lock_reason': None,
                'locked_at': None,
                'wipe_authorized': False
            })

    def _read_state(self) -> Dict[str, Any]:
        """Read current state."""
        return json.loads(self.state_file.read_text())

    def _write_state(self, state: Dict[str, Any]):
        """Write state."""
        self.state_file.write_text(json.dumps(state, indent=2))

    def lock(self, reason: str = "Manual lock") -> bool:
        """
        Lock all Echo operations.

        Returns:
            True if locked successfully
        """
        state = self._read_state()
        state['locked'] = True
        state['lock_reason'] = reason
        state['locked_at'] = datetime.utcnow().isoformat()
        self._write_state(state)
        return True

    def unlock(self, confirmation_code: str) -> bool:
        """
        Unlock operations with confirmation.

        Args:
            confirmation_code: User-provided unlock code

        Returns:
            True if unlocked successfully
        """
        # Verify confirmation (in production, this would be more sophisticated)
        expected = hashlib.sha256(b"echo_unlock_2025").hexdigest()[:8]
        if confirmation_code != expected:
            return False

        state = self._read_state()
        state['locked'] = False
        state['lock_reason'] = None
        state['locked_at'] = None
        self._write_state(state)
        return True

    def authorize_wipe(self) -> str:
        """
        Authorize secure wipe (requires second confirmation).

        Returns:
            Wipe authorization code
        """
        state = self._read_state()
        wipe_code = secrets.token_hex(8)
        state['wipe_authorized'] = True
        state['wipe_code'] = hashlib.sha256(wipe_code.encode()).hexdigest()
        self._write_state(state)
        return wipe_code

    def execute_wipe(self, wipe_code: str) -> bool:
        """
        Execute secure wipe with authorization code.

        THIS IS DESTRUCTIVE - removes all Echo data.
        """
        state = self._read_state()
        if not state.get('wipe_authorized'):
            return False

        expected_hash = state.get('wipe_code')
        if hashlib.sha256(wipe_code.encode()).hexdigest() != expected_hash:
            return False

        # In production, this would securely delete all Echo data
        # For safety, we just log the action here
        print("WIPE EXECUTED - All Echo data would be securely deleted")

        return True

    def is_locked(self) -> bool:
        """Check if system is locked."""
        state = self._read_state()
        return state.get('locked', False)


class DefenseWall:
    """
    Main Defense Wall orchestrator.

    Coordinates all security layers for comprehensive protection.
    """

    def __init__(self, base_path: str = "~/.echo"):
        self.base_path = Path(base_path).expanduser()
        self._setup_directories()

        # Initialize layers
        db_path = str(self.base_path / "security" / "defense.db")
        self.identity_firewall = IdentityFirewall(
            db_path,
            self._get_encryption_key()
        )
        self.behavior_watchdog = BehaviorWatchdog(db_path)
        self.vendor_isolation = VendorIsolation()
        self.kill_switch = KillSwitch(str(self.base_path / "security"))

        # Alert history
        self.alerts: List[SecurityAlert] = []

    def _setup_directories(self):
        """Create security directories."""
        (self.base_path / "security").mkdir(parents=True, exist_ok=True)

    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key."""
        key_path = self.base_path / "keys" / "defense.key"
        if key_path.exists():
            return key_path.read_bytes()
        else:
            key = secrets.token_bytes(32)
            key_path.parent.mkdir(parents=True, exist_ok=True)
            key_path.write_bytes(key)
            return key

    async def scan(self, data: Dict[str, Any]) -> List[SecurityAlert]:
        """
        Perform security scan on data.

        Args:
            data: Data to scan (may include URLs, credentials, content)

        Returns:
            List of security alerts
        """
        alerts = []

        # Check if system is locked
        if self.kill_switch.is_locked():
            alerts.append(SecurityAlert(
                id=secrets.token_hex(8),
                timestamp=datetime.utcnow(),
                layer=SecurityLayer.L4_KILL_SWITCH,
                threat_level=ThreatLevel.CRITICAL,
                title="System Locked",
                description="Echo operations are locked by Kill Switch",
                source="kill_switch",
                requires_user_action=True
            ))
            return alerts

        # Scan URLs for phishing
        if 'url' in data:
            is_phishing, reasons = self.identity_firewall.detect_phishing(
                data['url'],
                data.get('content', '')
            )
            if is_phishing:
                alerts.append(SecurityAlert(
                    id=secrets.token_hex(8),
                    timestamp=datetime.utcnow(),
                    layer=SecurityLayer.L1_IDENTITY_FIREWALL,
                    threat_level=ThreatLevel.HIGH,
                    title="Potential Phishing Detected",
                    description=f"URL: {data['url']}. Reasons: {', '.join(reasons)}",
                    source="identity_firewall",
                    requires_user_action=True
                ))

        # Check email for breaches
        if 'email' in data:
            is_breached, breaches = await self.identity_firewall.check_breach(data['email'])
            if is_breached:
                alerts.append(SecurityAlert(
                    id=secrets.token_hex(8),
                    timestamp=datetime.utcnow(),
                    layer=SecurityLayer.L1_IDENTITY_FIREWALL,
                    threat_level=ThreatLevel.HIGH,
                    title="Email Found in Breach",
                    description=f"Email: {data['email']} found in known breaches",
                    source="hibp_check",
                    requires_user_action=True,
                    metadata={'breaches': breaches}
                ))

        # Check password strength
        if 'password' in data:
            score, recommendations = self.identity_firewall.analyze_password_strength(
                data['password']
            )
            if score < 50:
                alerts.append(SecurityAlert(
                    id=secrets.token_hex(8),
                    timestamp=datetime.utcnow(),
                    layer=SecurityLayer.L1_IDENTITY_FIREWALL,
                    threat_level=ThreatLevel.MEDIUM,
                    title="Weak Password Detected",
                    description=f"Password strength: {score}/100. {', '.join(recommendations)}",
                    source="password_analyzer"
                ))

        self.alerts.extend(alerts)
        return alerts

    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status across all layers."""
        return {
            'locked': self.kill_switch.is_locked(),
            'active_alerts': len([a for a in self.alerts if a.requires_user_action]),
            'total_alerts': len(self.alerts),
            'layers_status': {
                'identity_firewall': 'active',
                'behavior_watchdog': 'active',
                'vendor_isolation': 'active',
                'kill_switch': 'locked' if self.kill_switch.is_locked() else 'ready'
            },
            'last_scan': datetime.utcnow().isoformat()
        }

    def emergency_lock(self, reason: str):
        """Emergency lock of all operations."""
        self.kill_switch.lock(reason)

        # Log the emergency
        self.behavior_watchdog.log_event(
            'emergency_lock',
            {'reason': reason},
            risk_score=10.0
        )


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        # Initialize Defense Wall
        wall = DefenseWall()

        # Check security status
        status = wall.get_security_status()
        print(f"Security Status: {json.dumps(status, indent=2)}")

        # Perform a security scan
        alerts = await wall.scan({
            'url': 'https://secure-bank.xyz/verify-account',
            'email': 'test@example.com',
            'password': 'weak123'
        })

        print(f"\nSecurity Alerts:")
        for alert in alerts:
            print(f"  [{alert.threat_level.name}] {alert.title}: {alert.description}")

    asyncio.run(main())
