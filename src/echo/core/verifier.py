"""
Content verification and cryptographic provenance for Echo Phoenix.

Implements content addressing (hashing) and optional signature verification.
This is the "zero-trust" layer - verify everything, trust nothing.
"""

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any

from echo.models.schema import EchoMessage


@dataclass
class ContentHash:
    """Represents a content-addressed hash."""

    algorithm: str
    digest: str

    def __str__(self) -> str:
        return f"{self.algorithm}:{self.digest}"

    @classmethod
    def from_string(cls, hash_string: str) -> "ContentHash":
        """Parse a hash string like 'sha256:abc123...'"""
        if ':' not in hash_string:
            # Assume SHA-256 if no algorithm specified
            return cls(algorithm="sha256", digest=hash_string)
        algorithm, digest = hash_string.split(':', 1)
        return cls(algorithm=algorithm, digest=digest)

    def verify(self, data: bytes) -> bool:
        """Verify that data matches this hash."""
        if self.algorithm == "sha256":
            computed = hashlib.sha256(data).hexdigest()
        elif self.algorithm == "sha384":
            computed = hashlib.sha384(data).hexdigest()
        elif self.algorithm == "sha512":
            computed = hashlib.sha512(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {self.algorithm}")
        return hmac.compare_digest(computed, self.digest)


class Verifier:
    """
    Verifies data integrity and provenance.

    Core responsibilities:
    - Content hash verification (data hasn't been tampered with)
    - Signature verification (data came from claimed source)
    - Provenance chain tracking
    """

    def __init__(self, signing_key: bytes | None = None):
        """
        Initialize the verifier.

        Args:
            signing_key: Optional HMAC key for signature verification.
                        In production, use asymmetric keys (RSA/Ed25519).
        """
        self._signing_key = signing_key

    def compute_hash(
        self,
        data: dict[str, Any],
        algorithm: str = "sha256"
    ) -> ContentHash:
        """
        Compute content hash for data.

        Uses canonical JSON serialization for consistent hashing
        regardless of key order or whitespace.
        """
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':')).encode()

        if algorithm == "sha256":
            digest = hashlib.sha256(canonical).hexdigest()
        elif algorithm == "sha384":
            digest = hashlib.sha384(canonical).hexdigest()
        elif algorithm == "sha512":
            digest = hashlib.sha512(canonical).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        return ContentHash(algorithm=algorithm, digest=digest)

    def verify_message(self, message: EchoMessage) -> tuple[bool, str]:
        """
        Verify an EchoMessage's integrity.

        Returns:
            Tuple of (is_valid, reason)
        """
        # Check content hash
        if not message.verify_integrity():
            expected = message.payload.content_hash()
            return False, f"Content hash mismatch: expected {expected}, got {message.content_hash}"

        # Check signature if present and we have a key
        if message.signature and self._signing_key:
            if not self._verify_signature(message):
                return False, "Signature verification failed"

        return True, "Verification successful"

    def sign_message(self, message: EchoMessage) -> str:
        """
        Generate HMAC signature for a message.

        In production, replace with asymmetric signatures (RSA/Ed25519).
        """
        if not self._signing_key:
            raise ValueError("No signing key configured")

        # Sign the content hash
        signature = hmac.new(
            self._signing_key,
            message.content_hash.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def _verify_signature(self, message: EchoMessage) -> bool:
        """Verify HMAC signature on a message."""
        if not self._signing_key or not message.signature:
            return False

        expected = hmac.new(
            self._signing_key,
            message.content_hash.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, message.signature)

    def create_provenance_record(
        self,
        message: EchoMessage,
        operation: str
    ) -> dict[str, Any]:
        """
        Create a provenance record for audit trail.

        This tracks the data's journey through the system.
        """
        return {
            "message_id": message.id,
            "content_hash": message.content_hash,
            "source_id": message.metadata.source_id,
            "timestamp": message.metadata.timestamp.isoformat(),
            "operation": operation,
            "verified": message.verify_integrity(),
        }
