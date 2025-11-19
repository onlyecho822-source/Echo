"""Tests for source registry."""

import pytest

from echo.core.registry import SourceRegistry, Source, Protocol


class TestSource:
    """Tests for Source dataclass."""

    def test_create_source(self):
        """Test basic source creation."""
        source = Source(
            id="test-api",
            name="Test API",
            protocol=Protocol.REST,
            endpoint="https://api.example.com/data"
        )

        assert source.id == "test-api"
        assert source.protocol == Protocol.REST
        assert source.enabled is True

    def test_protocol_string_conversion(self):
        """Protocol should convert from string."""
        source = Source(
            id="test",
            name="Test",
            protocol="rest",  # type: ignore
            endpoint="http://test"
        )

        assert source.protocol == Protocol.REST


class TestSourceRegistry:
    """Tests for SourceRegistry class."""

    def test_register_source(self):
        """Test registering a new source."""
        registry = SourceRegistry()
        source = Source(
            id="test-api",
            name="Test API",
            protocol=Protocol.REST,
            endpoint="https://api.example.com"
        )

        registry.register(source)

        assert registry.get("test-api") == source

    def test_register_duplicate_raises(self):
        """Registering duplicate ID should raise."""
        registry = SourceRegistry()
        source = Source(
            id="test-api",
            name="Test API",
            protocol=Protocol.REST,
            endpoint="https://api.example.com"
        )

        registry.register(source)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(source)

    def test_unregister_source(self):
        """Test unregistering a source."""
        registry = SourceRegistry()
        source = Source(
            id="test-api",
            name="Test API",
            protocol=Protocol.REST,
            endpoint="https://api.example.com"
        )

        registry.register(source)
        registry.unregister("test-api")

        assert registry.get("test-api") is None

    def test_get_by_protocol(self):
        """Test filtering sources by protocol."""
        registry = SourceRegistry()

        rest_source = Source(
            id="rest-api",
            name="REST API",
            protocol=Protocol.REST,
            endpoint="https://rest.example.com"
        )
        mqtt_source = Source(
            id="mqtt-broker",
            name="MQTT Broker",
            protocol=Protocol.MQTT,
            endpoint="mqtt://broker.example.com"
        )

        registry.register(rest_source)
        registry.register(mqtt_source)

        rest_sources = registry.get_by_protocol(Protocol.REST)

        assert len(rest_sources) == 1
        assert rest_sources[0].id == "rest-api"

    def test_get_by_tag(self):
        """Test filtering sources by tag."""
        registry = SourceRegistry()

        source1 = Source(
            id="api-1",
            name="API 1",
            protocol=Protocol.REST,
            endpoint="https://api1.example.com",
            tags=["production", "metrics"]
        )
        source2 = Source(
            id="api-2",
            name="API 2",
            protocol=Protocol.REST,
            endpoint="https://api2.example.com",
            tags=["staging"]
        )

        registry.register(source1)
        registry.register(source2)

        production = registry.get_by_tag("production")

        assert len(production) == 1
        assert production[0].id == "api-1"

    def test_enable_disable(self):
        """Test enabling and disabling sources."""
        registry = SourceRegistry()
        source = Source(
            id="test-api",
            name="Test API",
            protocol=Protocol.REST,
            endpoint="https://api.example.com"
        )

        registry.register(source)

        # Disable
        registry.disable("test-api")
        assert registry.get("test-api").enabled is False  # type: ignore

        # Should not appear in list_all by default
        all_sources = registry.list_all()
        assert len(all_sources) == 0

        # But should appear with include_disabled
        all_sources = registry.list_all(include_disabled=True)
        assert len(all_sources) == 1

        # Re-enable
        registry.enable("test-api")
        assert registry.get("test-api").enabled is True  # type: ignore

    def test_export_and_import_config(self):
        """Test config export and import."""
        registry = SourceRegistry()
        source = Source(
            id="test-api",
            name="Test API",
            protocol=Protocol.REST,
            endpoint="https://api.example.com",
            tags=["test"],
            description="A test API"
        )

        registry.register(source)

        # Export
        config = registry.export_config()

        # Import to new registry
        new_registry = SourceRegistry.from_config(config)

        # Verify
        imported = new_registry.get("test-api")
        assert imported is not None
        assert imported.name == "Test API"
        assert imported.protocol == Protocol.REST
        assert "test" in imported.tags
