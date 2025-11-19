"""Tests for the core translator."""

import pytest

from echo.core.translator import Translator, quick_fetch
from echo.core.registry import SourceRegistry, Source, Protocol
from echo.core.verifier import Verifier
from echo.adapters.rest import RestAdapter, RestAdapterBuilder
from echo.adapters.base import AdapterConfig
from echo.models.schema import DataPayload, Metadata, EchoMessage


class TestTranslator:
    """Tests for Translator class."""

    def test_source_not_found(self):
        """Should return error for unknown source."""
        translator = Translator()

        async def run():
            result = await translator.translate("nonexistent")
            assert result.success is False
            assert "not found" in result.error.lower()

        import asyncio
        asyncio.run(run())

    def test_disabled_source(self):
        """Should return error for disabled source."""
        registry = SourceRegistry()
        source = Source(
            id="test-api",
            name="Test API",
            protocol=Protocol.REST,
            endpoint="https://api.example.com",
            enabled=False
        )
        registry.register(source)

        translator = Translator(registry=registry)

        async def run():
            result = await translator.translate("test-api")
            assert result.success is False
            assert "disabled" in result.error.lower()

        import asyncio
        asyncio.run(run())

    def test_register_custom_adapter(self):
        """Should use custom adapter when registered."""
        registry = SourceRegistry()
        source = Source(
            id="test-api",
            name="Test API",
            protocol=Protocol.REST,
            endpoint="https://api.example.com"
        )
        registry.register(source)

        # Custom adapter with field mapping
        custom_adapter = RestAdapterBuilder() \
            .with_field_mapping("name", "response.user.name") \
            .build()

        translator = Translator(registry=registry)
        translator.register_adapter("test-api", custom_adapter)

        # Verify custom adapter is returned
        adapter = translator.get_adapter(source)
        assert adapter is custom_adapter

    def test_provenance_tracking(self):
        """Translator should track provenance records."""
        translator = Translator()

        # Initially empty
        assert len(translator.get_provenance()) == 0

        # After clearing, still empty
        translator.clear_provenance()
        assert len(translator.get_provenance()) == 0


class TestRestAdapter:
    """Tests for REST adapter specifically."""

    def test_transform_basic(self):
        """Test basic transformation."""
        adapter = RestAdapter()

        result = adapter.transform(
            source_id="test-source",
            raw_data={"key": "value", "count": 42}
        )

        assert result.success is True
        assert result.message is not None
        assert result.message.payload.data == {"key": "value", "count": 42}
        assert result.message.metadata.source_protocol == "rest"

    def test_transform_with_field_mapping(self):
        """Test transformation with field mapping."""
        config = AdapterConfig(
            field_mappings={
                "name": "user.name",
                "email": "user.email"
            }
        )
        adapter = RestAdapter(config=config)

        result = adapter.transform(
            source_id="test-source",
            raw_data={
                "user": {
                    "name": "John",
                    "email": "john@example.com"
                }
            }
        )

        assert result.success is True
        assert result.message.payload.data == {
            "name": "John",
            "email": "john@example.com"
        }

    def test_transform_with_required_fields(self):
        """Test validation of required fields."""
        config = AdapterConfig(
            required_fields=["name", "email"]
        )
        adapter = RestAdapter(config=config)

        # Missing email
        result = adapter.transform(
            source_id="test-source",
            raw_data={"name": "John"}
        )

        assert result.success is False
        assert "email" in result.error

    def test_transform_with_defaults(self):
        """Test default values for missing fields."""
        config = AdapterConfig(
            field_mappings={"name": "name", "status": "status"},
            default_values={"status": "active"}
        )
        adapter = RestAdapter(config=config)

        result = adapter.transform(
            source_id="test-source",
            raw_data={"name": "John"}
        )

        assert result.success is True
        assert result.message.payload.data["status"] == "active"


class TestRestAdapterBuilder:
    """Tests for RestAdapterBuilder."""

    def test_builder_pattern(self):
        """Test building adapter with builder pattern."""
        adapter = RestAdapterBuilder() \
            .with_timeout(60.0) \
            .with_retries(5, delay=2.0) \
            .with_field_mapping("id", "response.id") \
            .with_required_field("id") \
            .with_api_key("secret-key") \
            .build()

        assert adapter.config.timeout_seconds == 60.0
        assert adapter.config.retry_count == 5
        assert adapter.config.retry_delay_seconds == 2.0
        assert "id" in adapter.config.field_mappings
        assert "id" in adapter.config.required_fields
        assert "X-API-Key" in adapter._default_headers

    def test_builder_bearer_token(self):
        """Test bearer token configuration."""
        adapter = RestAdapterBuilder() \
            .with_bearer_token("my-token") \
            .build()

        assert adapter._default_headers["Authorization"] == "Bearer my-token"


class TestIntegration:
    """Integration tests for the full translation pipeline."""

    def test_message_integrity(self):
        """Verify end-to-end message integrity."""
        verifier = Verifier()

        # Create message manually (simulating adapter output)
        message = EchoMessage(
            id="test-123",
            metadata=Metadata(source_id="api", source_protocol="rest"),
            payload=DataPayload(data={"temperature": 72.5, "unit": "F"})
        )

        # Verify integrity
        is_valid, reason = verifier.verify_message(message)
        assert is_valid is True

        # Tamper with data
        tampered = EchoMessage(
            id=message.id,
            metadata=message.metadata,
            payload=DataPayload(data={"temperature": 100.0, "unit": "F"}),
            content_hash=message.content_hash  # Old hash, new data
        )

        # Should fail verification
        is_valid, reason = verifier.verify_message(tampered)
        assert is_valid is False
