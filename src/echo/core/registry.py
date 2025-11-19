"""
Source registry for Echo Phoenix.

Manages curated data sources - no autonomous discovery,
just explicit registration of trusted sources.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Protocol(str, Enum):
    """Supported protocols in Phoenix."""
    REST = "rest"
    GRPC = "grpc"
    MQTT = "mqtt"


@dataclass
class Source:
    """
    A registered data source.

    Sources are explicitly registered, not discovered.
    This is the "curated over autonomous" design choice.
    """

    id: str
    name: str
    protocol: Protocol
    endpoint: str
    adapter_config: dict[str, Any] = field(default_factory=dict)

    # Authentication
    auth_type: str = "none"  # none, api_key, oauth2, mtls
    auth_config: dict[str, Any] = field(default_factory=dict)

    # Metadata
    description: str = ""
    tags: list[str] = field(default_factory=list)
    enabled: bool = True

    # Rate limiting
    rate_limit_rps: int = 100  # requests per second

    def __post_init__(self) -> None:
        if isinstance(self.protocol, str):
            self.protocol = Protocol(self.protocol)


class SourceRegistry:
    """
    Registry of curated data sources.

    This replaces autonomous discovery with explicit registration.
    Trade-off: Less "magic", more control and reliability.
    """

    def __init__(self) -> None:
        self._sources: dict[str, Source] = {}
        self._by_protocol: dict[Protocol, list[str]] = {
            Protocol.REST: [],
            Protocol.GRPC: [],
            Protocol.MQTT: [],
        }
        self._by_tag: dict[str, list[str]] = {}

    def register(self, source: Source) -> None:
        """
        Register a data source.

        Raises:
            ValueError: If source ID already exists
        """
        if source.id in self._sources:
            raise ValueError(f"Source already registered: {source.id}")

        self._sources[source.id] = source
        self._by_protocol[source.protocol].append(source.id)

        for tag in source.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(source.id)

    def unregister(self, source_id: str) -> None:
        """Remove a source from the registry."""
        if source_id not in self._sources:
            return

        source = self._sources[source_id]

        # Clean up indexes
        self._by_protocol[source.protocol].remove(source_id)
        for tag in source.tags:
            if tag in self._by_tag:
                self._by_tag[tag].remove(source_id)

        del self._sources[source_id]

    def get(self, source_id: str) -> Source | None:
        """Get a source by ID."""
        return self._sources.get(source_id)

    def get_by_protocol(self, protocol: Protocol) -> list[Source]:
        """Get all sources using a specific protocol."""
        return [
            self._sources[sid]
            for sid in self._by_protocol.get(protocol, [])
            if self._sources[sid].enabled
        ]

    def get_by_tag(self, tag: str) -> list[Source]:
        """Get all sources with a specific tag."""
        return [
            self._sources[sid]
            for sid in self._by_tag.get(tag, [])
            if self._sources[sid].enabled
        ]

    def list_all(self, include_disabled: bool = False) -> list[Source]:
        """List all registered sources."""
        if include_disabled:
            return list(self._sources.values())
        return [s for s in self._sources.values() if s.enabled]

    def enable(self, source_id: str) -> None:
        """Enable a source."""
        if source := self._sources.get(source_id):
            source.enabled = True

    def disable(self, source_id: str) -> None:
        """Disable a source without removing it."""
        if source := self._sources.get(source_id):
            source.enabled = False

    def export_config(self) -> dict[str, Any]:
        """Export registry configuration for persistence."""
        return {
            "version": "1.0",
            "sources": [
                {
                    "id": s.id,
                    "name": s.name,
                    "protocol": s.protocol.value,
                    "endpoint": s.endpoint,
                    "adapter_config": s.adapter_config,
                    "auth_type": s.auth_type,
                    "auth_config": s.auth_config,
                    "description": s.description,
                    "tags": s.tags,
                    "enabled": s.enabled,
                    "rate_limit_rps": s.rate_limit_rps,
                }
                for s in self._sources.values()
            ]
        }

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "SourceRegistry":
        """Load registry from configuration."""
        registry = cls()
        for source_data in config.get("sources", []):
            source = Source(
                id=source_data["id"],
                name=source_data["name"],
                protocol=Protocol(source_data["protocol"]),
                endpoint=source_data["endpoint"],
                adapter_config=source_data.get("adapter_config", {}),
                auth_type=source_data.get("auth_type", "none"),
                auth_config=source_data.get("auth_config", {}),
                description=source_data.get("description", ""),
                tags=source_data.get("tags", []),
                enabled=source_data.get("enabled", True),
                rate_limit_rps=source_data.get("rate_limit_rps", 100),
            )
            registry.register(source)
        return registry
