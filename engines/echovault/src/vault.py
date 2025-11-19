"""
EchoVault Core Implementation

Secure identity and state management with cryptographic verification.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import hashlib
import secrets
import hmac


@dataclass
class VaultConfig:
    """Configuration for EchoVault."""
    master_key: str = ""
    derivation_path: str = "m/44'/0'/0'"
    lock_timeout: int = 30
    audit_level: str = "full"


class Identity:
    """
    Cryptographic Identity.

    Represents an entity with signing and verification capabilities.
    """

    def __init__(self, name: str, public_key: bytes, private_key: Optional[bytes] = None):
        self.id = f"id_{secrets.token_hex(8)}"
        self.name = name
        self.public_key = public_key
        self._private_key = private_key
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.metadata: Dict[str, Any] = {}

    def can_sign(self) -> bool:
        """Check if identity has signing capability."""
        return self._private_key is not None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding private key)."""
        return {
            "id": self.id,
            "name": self.name,
            "public_key": self.public_key.hex(),
            "created_at": self.created_at,
            "metadata": self.metadata
        }


class EchoVault:
    """
    Secure Identity and State Management System.

    Provides cryptographic identity operations, secure state
    management, and audit logging.

    Attributes:
        config: Vault configuration
        identities: Registered identities
        states: Managed states

    Example:
        >>> vault = EchoVault(VaultConfig(master_key="secret"))
        >>> identity = vault.create_identity("agent-1")
        >>> signature = vault.sign(identity, b"data")
        >>> valid = vault.verify(identity, b"data", signature)
    """

    def __init__(self, config: Optional[VaultConfig] = None):
        """Initialize EchoVault with configuration."""
        self.config = config or VaultConfig()
        self._identities: Dict[str, Identity] = {}
        self._states: Dict[str, Any] = {}
        self._locks: Dict[str, 'StateLock'] = {}
        self._audit_log: List[Dict[str, Any]] = []
        self._master_key = self._derive_master_key()

    def _derive_master_key(self) -> bytes:
        """Derive master key from configuration."""
        if self.config.master_key:
            return hashlib.sha3_256(self.config.master_key.encode()).digest()
        return secrets.token_bytes(32)

    def create_identity(self, name: str) -> Identity:
        """
        Create a new cryptographic identity.

        Args:
            name: Human-readable name for the identity

        Returns:
            Created identity with key pair
        """
        # Generate key pair (simplified - real impl would use Ed25519)
        private_key = secrets.token_bytes(32)
        public_key = hashlib.sha3_256(private_key).digest()

        identity = Identity(name, public_key, private_key)
        self._identities[identity.id] = identity

        self._audit("identity_created", {"identity_id": identity.id, "name": name})

        return identity

    def sign(self, identity: Identity, data: bytes) -> bytes:
        """
        Sign data with an identity.

        Args:
            identity: Identity to sign with
            data: Data to sign

        Returns:
            Signature bytes

        Raises:
            ValueError: If identity cannot sign
        """
        if not identity.can_sign():
            raise ValueError("Identity does not have signing capability")

        # HMAC-based signature (simplified - real impl would use Ed25519)
        signature = hmac.new(
            identity._private_key,
            data,
            hashlib.sha3_256
        ).digest()

        self._audit("data_signed", {
            "identity_id": identity.id,
            "data_hash": hashlib.sha3_256(data).hexdigest()[:16]
        })

        return signature

    def verify(self, identity: Identity, data: bytes, signature: bytes) -> bool:
        """
        Verify a signature.

        Args:
            identity: Identity that signed
            data: Original data
            signature: Signature to verify

        Returns:
            True if valid, False otherwise
        """
        if identity._private_key is None:
            # Cannot verify without private key in this simplified impl
            return False

        expected = hmac.new(
            identity._private_key,
            data,
            hashlib.sha3_256
        ).digest()

        valid = hmac.compare_digest(signature, expected)

        self._audit("signature_verified", {
            "identity_id": identity.id,
            "valid": valid
        })

        return valid

    def derive(self, identity: Identity, path: str) -> Identity:
        """
        Derive a child identity.

        Args:
            identity: Parent identity
            path: Derivation path (e.g., "0/1")

        Returns:
            Derived child identity
        """
        if not identity.can_sign():
            raise ValueError("Cannot derive from identity without private key")

        # Derive child key
        derivation_data = f"{identity._private_key.hex()}:{path}".encode()
        child_private = hashlib.sha3_256(derivation_data).digest()
        child_public = hashlib.sha3_256(child_private).digest()

        child = Identity(
            f"{identity.name}/{path}",
            child_public,
            child_private
        )
        self._identities[child.id] = child

        return child

    def lock(self, key: str) -> 'StateLock':
        """
        Acquire a state lock.

        Args:
            key: State key to lock

        Returns:
            StateLock context manager
        """
        if key in self._locks:
            raise ValueError(f"State '{key}' is already locked")

        lock = StateLock(self, key)
        self._locks[key] = lock
        return lock

    def read(self, key: str) -> Any:
        """
        Read a state value.

        Args:
            key: State key

        Returns:
            State value or None
        """
        return self._states.get(key)

    def transition(self, key: str, old_value: Any, new_value: Any) -> bool:
        """
        Atomic state transition.

        Args:
            key: State key
            old_value: Expected current value
            new_value: New value to set

        Returns:
            True if transition succeeded, False otherwise
        """
        current = self._states.get(key)
        if current != old_value:
            return False

        self._states[key] = new_value
        self._audit("state_transition", {
            "key": key,
            "old_hash": hashlib.sha3_256(str(old_value).encode()).hexdigest()[:16],
            "new_hash": hashlib.sha3_256(str(new_value).encode()).hexdigest()[:16]
        })

        return True

    def _audit(self, event: str, details: Dict[str, Any]):
        """Record an audit log entry."""
        if self.config.audit_level == "none":
            return

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": event,
            "details": details
        }
        self._audit_log.append(entry)

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get the audit log."""
        return self._audit_log.copy()


class StateLock:
    """
    Context manager for state locking.

    Provides atomic state modifications with automatic unlock.
    """

    def __init__(self, vault: EchoVault, key: str):
        self._vault = vault
        self._key = key
        self.value = vault._states.get(key)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._key in self._vault._locks:
            del self._vault._locks[self._key]
        return False

    def commit(self):
        """Commit the state change."""
        self._vault._states[self._key] = self.value
        self._vault._audit("state_committed", {"key": self._key})
