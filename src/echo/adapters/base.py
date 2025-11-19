"""
Base adapter interface for Echo Phoenix.

All protocol adapters inherit from BaseAdapter and implement
the transform method to convert source data to EchoMessage format.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from echo.models.schema import EchoMessage, TransformResult


@dataclass
class AdapterConfig:
    """Configuration for a protocol adapter."""

    # Request settings
    timeout_seconds: float = 30.0
    retry_count: int = 3
    retry_delay_seconds: float = 1.0

    # Transform settings
    field_mappings: dict[str, str] = field(default_factory=dict)
    default_values: dict[str, Any] = field(default_factory=dict)

    # Validation
    required_fields: list[str] = field(default_factory=list)
    schema_version: str = "1.0"


class BaseAdapter(ABC):
    """
    Abstract base class for protocol adapters.

    Each adapter knows how to:
    1. Fetch data from a source using its native protocol
    2. Transform the response into a normalized EchoMessage

    This is the "pre-compiled adapter" approach - no AI learning,
    just explicit field mappings.
    """

    def __init__(self, config: AdapterConfig | None = None):
        self.config = config or AdapterConfig()

    @property
    @abstractmethod
    def protocol(self) -> str:
        """Return the protocol this adapter handles."""
        pass

    @abstractmethod
    async def fetch(
        self,
        endpoint: str,
        **kwargs: Any
    ) -> tuple[dict[str, Any], int]:
        """
        Fetch data from the source.

        Args:
            endpoint: The source endpoint URL/address
            **kwargs: Protocol-specific options

        Returns:
            Tuple of (response_data, status_code)
        """
        pass

    @abstractmethod
    def transform(
        self,
        source_id: str,
        raw_data: dict[str, Any]
    ) -> TransformResult:
        """
        Transform raw source data into an EchoMessage.

        Args:
            source_id: Identifier of the data source
            raw_data: Raw data from the source

        Returns:
            TransformResult with the normalized message
        """
        pass

    async def fetch_and_transform(
        self,
        source_id: str,
        endpoint: str,
        **kwargs: Any
    ) -> TransformResult:
        """
        Convenience method to fetch and transform in one call.
        """
        import time

        start = time.perf_counter()

        try:
            raw_data, status = await self.fetch(endpoint, **kwargs)

            if status >= 400:
                return TransformResult(
                    success=False,
                    error=f"Fetch failed with status {status}"
                )

            result = self.transform(source_id, raw_data)
            result.transform_time_ms = (time.perf_counter() - start) * 1000

            return result

        except Exception as e:
            return TransformResult(
                success=False,
                error=str(e),
                transform_time_ms=(time.perf_counter() - start) * 1000
            )

    def apply_field_mappings(
        self,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Apply configured field mappings to transform data.

        Maps source field names to target field names based on config.
        """
        if not self.config.field_mappings:
            return data

        result = {}
        for target_field, source_field in self.config.field_mappings.items():
            if '.' in source_field:
                # Handle nested fields like "response.data.value"
                value = data
                for key in source_field.split('.'):
                    if isinstance(value, dict):
                        value = value.get(key)
                    else:
                        value = None
                        break
                result[target_field] = value
            else:
                result[target_field] = data.get(source_field)

        # Apply defaults for missing fields
        for field_name, default in self.config.default_values.items():
            if field_name not in result or result[field_name] is None:
                result[field_name] = default

        return result

    def validate_required_fields(self, data: dict[str, Any]) -> list[str]:
        """
        Check that all required fields are present.

        Returns list of missing field names.
        """
        missing = []
        for field_name in self.config.required_fields:
            if field_name not in data or data[field_name] is None:
                missing.append(field_name)
        return missing
