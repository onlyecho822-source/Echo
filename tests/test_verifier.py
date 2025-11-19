"""Tests for content verification."""

import pytest

from echo.core.verifier import Verifier, ContentHash
from echo.models.schema import (
    EchoMessage,
    DataPayload,
    Metadata,
)


class TestContentHash:
    """Tests for ContentHash dataclass."""

    def test_from_string_with_algorithm(self):
        """Parse hash string with algorithm prefix."""
        hash_obj = ContentHash.from_string("sha256:abc123")

        assert hash_obj.algorithm == "sha256"
        assert hash_obj.digest == "abc123"

    def test_from_string_without_algorithm(self):
        """Default to sha256 when no algorithm specified."""
        hash_obj = ContentHash.from_string("abc123")

        assert hash_obj.algorithm == "sha256"
        assert hash_obj.digest == "abc123"

    def test_str_representation(self):
        """Test string representation."""
        hash_obj = ContentHash(algorithm="sha256", digest="abc123")
        assert str(hash_obj) == "sha256:abc123"

    def test_verify_valid_data(self):
        """Verify should pass for matching data."""
        import hashlib
        data = b"test data"
        digest = hashlib.sha256(data).hexdigest()

        hash_obj = ContentHash(algorithm="sha256", digest=digest)
        assert hash_obj.verify(data) is True

    def test_verify_invalid_data(self):
        """Verify should fail for non-matching data."""
        hash_obj = ContentHash(algorithm="sha256", digest="invalid")
        assert hash_obj.verify(b"test data") is False


class TestVerifier:
    """Tests for Verifier class."""

    def test_compute_hash(self):
        """Test hash computation."""
        verifier = Verifier()

        hash1 = verifier.compute_hash({"key": "value"})
        hash2 = verifier.compute_hash({"key": "value"})

        assert hash1.digest == hash2.digest
        assert hash1.algorithm == "sha256"

    def test_compute_hash_key_order_independent(self):
        """Hash should be same regardless of key order."""
        verifier = Verifier()

        hash1 = verifier.compute_hash({"a": 1, "b": 2})
        hash2 = verifier.compute_hash({"b": 2, "a": 1})

        assert hash1.digest == hash2.digest

    def test_verify_message_valid(self):
        """Verify should pass for valid message."""
        verifier = Verifier()
        message = EchoMessage(
            id="test-id",
            metadata=Metadata(source_id="src", source_protocol="rest"),
            payload=DataPayload(data={"test": "data"})
        )

        is_valid, reason = verifier.verify_message(message)

        assert is_valid is True
        assert "successful" in reason.lower()

    def test_verify_message_invalid_hash(self):
        """Verify should fail for tampered message."""
        verifier = Verifier()
        message = EchoMessage(
            id="test-id",
            metadata=Metadata(source_id="src", source_protocol="rest"),
            payload=DataPayload(data={"test": "data"}),
            content_hash="tampered-hash"
        )

        is_valid, reason = verifier.verify_message(message)

        assert is_valid is False
        assert "mismatch" in reason.lower()

    def test_sign_and_verify(self):
        """Test signing and verification with key."""
        signing_key = b"secret-key-for-testing"
        verifier = Verifier(signing_key=signing_key)

        message = EchoMessage(
            id="test-id",
            metadata=Metadata(source_id="src", source_protocol="rest"),
            payload=DataPayload(data={"test": "data"})
        )

        # Sign the message
        signature = verifier.sign_message(message)
        assert signature is not None
        assert len(signature) == 64  # SHA-256 hex digest

        # Create signed message
        signed_message = EchoMessage(
            id=message.id,
            metadata=message.metadata,
            payload=message.payload,
            content_hash=message.content_hash,
            signature=signature
        )

        # Verify
        is_valid, reason = verifier.verify_message(signed_message)
        assert is_valid is True

    def test_sign_without_key_raises(self):
        """Signing without key should raise error."""
        verifier = Verifier()  # No signing key
        message = EchoMessage(
            id="test-id",
            metadata=Metadata(source_id="src", source_protocol="rest"),
            payload=DataPayload(data={"test": "data"})
        )

        with pytest.raises(ValueError, match="No signing key"):
            verifier.sign_message(message)

    def test_create_provenance_record(self):
        """Test provenance record creation."""
        verifier = Verifier()
        message = EchoMessage(
            id="test-id",
            metadata=Metadata(source_id="src", source_protocol="rest"),
            payload=DataPayload(data={"test": "data"})
        )

        record = verifier.create_provenance_record(message, "translate")

        assert record["message_id"] == "test-id"
        assert record["source_id"] == "src"
        assert record["operation"] == "translate"
        assert record["verified"] is True
        assert "content_hash" in record
        assert "timestamp" in record
