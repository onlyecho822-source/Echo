"""Tests for the unified data model."""

import pytest
from datetime import datetime, timezone

from echo.models.schema import (
    EchoMessage,
    DataPayload,
    Metadata,
    TransformResult,
)


class TestDataPayload:
    """Tests for DataPayload model."""

    def test_content_hash_deterministic(self):
        """Same data should produce same hash."""
        payload1 = DataPayload(data={"key": "value", "num": 42})
        payload2 = DataPayload(data={"key": "value", "num": 42})

        assert payload1.content_hash() == payload2.content_hash()

    def test_content_hash_key_order_independent(self):
        """Hash should be same regardless of key order."""
        payload1 = DataPayload(data={"a": 1, "b": 2})
        payload2 = DataPayload(data={"b": 2, "a": 1})

        assert payload1.content_hash() == payload2.content_hash()

    def test_content_hash_different_for_different_data(self):
        """Different data should produce different hash."""
        payload1 = DataPayload(data={"key": "value1"})
        payload2 = DataPayload(data={"key": "value2"})

        assert payload1.content_hash() != payload2.content_hash()


class TestMetadata:
    """Tests for Metadata model."""

    def test_defaults(self):
        """Test default values are set correctly."""
        meta = Metadata(
            source_id="test-source",
            source_protocol="rest"
        )

        assert meta.source_id == "test-source"
        assert meta.source_protocol == "rest"
        assert meta.transform_version == "1.0"
        assert meta.original_format == "json"
        assert isinstance(meta.timestamp, datetime)


class TestEchoMessage:
    """Tests for EchoMessage model."""

    def test_auto_compute_content_hash(self):
        """Content hash should be auto-computed on creation."""
        message = EchoMessage(
            id="test-id",
            metadata=Metadata(source_id="src", source_protocol="rest"),
            payload=DataPayload(data={"test": "data"})
        )

        assert message.content_hash != ""
        assert message.content_hash == message.payload.content_hash()

    def test_verify_integrity_valid(self):
        """Verification should pass for unmodified message."""
        message = EchoMessage(
            id="test-id",
            metadata=Metadata(source_id="src", source_protocol="rest"),
            payload=DataPayload(data={"test": "data"})
        )

        assert message.verify_integrity() is True

    def test_verify_integrity_invalid(self):
        """Verification should fail if hash doesn't match."""
        message = EchoMessage(
            id="test-id",
            metadata=Metadata(source_id="src", source_protocol="rest"),
            payload=DataPayload(data={"test": "data"}),
            content_hash="invalid-hash"
        )

        assert message.verify_integrity() is False

    def test_serialization(self):
        """Message should serialize to JSON properly."""
        message = EchoMessage(
            id="test-id",
            metadata=Metadata(source_id="src", source_protocol="rest"),
            payload=DataPayload(data={"test": "data"})
        )

        json_str = message.model_dump_json()
        assert "test-id" in json_str
        assert "test" in json_str


class TestTransformResult:
    """Tests for TransformResult model."""

    def test_success_result(self):
        """Test successful transform result."""
        message = EchoMessage(
            id="test-id",
            metadata=Metadata(source_id="src", source_protocol="rest"),
            payload=DataPayload(data={"test": "data"})
        )

        result = TransformResult(
            success=True,
            message=message,
            source_bytes=100,
            transform_time_ms=5.5
        )

        assert result.success is True
        assert result.message is not None
        assert result.error is None

    def test_failure_result(self):
        """Test failed transform result."""
        result = TransformResult(
            success=False,
            error="Something went wrong"
        )

        assert result.success is False
        assert result.message is None
        assert result.error == "Something went wrong"
