"""
Core translation engine for Echo Phoenix.

This is the main orchestrator that coordinates:
- Source registry lookups
- Adapter selection and invocation
- Verification of results
- Provenance tracking
"""

import asyncio
from typing import Any

from echo.adapters.base import BaseAdapter
from echo.adapters.rest import RestAdapter
from echo.core.registry import SourceRegistry, Source, Protocol
from echo.core.verifier import Verifier
from echo.models.schema import EchoMessage, TransformResult


class Translator:
    """
    Main translation engine for Echo Phoenix.

    Coordinates the flow:
    1. Look up source in registry
    2. Select appropriate adapter
    3. Fetch and transform data
    4. Verify and sign result
    5. Return normalized EchoMessage
    """

    def __init__(
        self,
        registry: SourceRegistry | None = None,
        verifier: Verifier | None = None,
        sign_messages: bool = False,
    ):
        self.registry = registry or SourceRegistry()
        self.verifier = verifier or Verifier()
        self.sign_messages = sign_messages

        # Adapter cache by source ID
        self._adapters: dict[str, BaseAdapter] = {}

        # Provenance log
        self._provenance: list[dict[str, Any]] = []

    def register_adapter(self, source_id: str, adapter: BaseAdapter) -> None:
        """
        Register a custom adapter for a specific source.

        Use this when you need custom field mappings or behavior.
        """
        self._adapters[source_id] = adapter

    def get_adapter(self, source: Source) -> BaseAdapter:
        """
        Get the adapter for a source.

        Returns cached custom adapter or creates default based on protocol.
        """
        if source.id in self._adapters:
            return self._adapters[source.id]

        # Create default adapter based on protocol
        if source.protocol == Protocol.REST:
            adapter = RestAdapter()
        elif source.protocol == Protocol.GRPC:
            raise NotImplementedError("gRPC adapter not yet implemented")
        elif source.protocol == Protocol.MQTT:
            raise NotImplementedError("MQTT adapter not yet implemented")
        else:
            raise ValueError(f"Unknown protocol: {source.protocol}")

        return adapter

    async def translate(
        self,
        source_id: str,
        **fetch_kwargs: Any
    ) -> TransformResult:
        """
        Fetch and translate data from a registered source.

        Args:
            source_id: ID of the registered source
            **fetch_kwargs: Protocol-specific fetch options

        Returns:
            TransformResult with verified EchoMessage
        """
        # Look up source
        source = self.registry.get(source_id)
        if not source:
            return TransformResult(
                success=False,
                error=f"Source not found: {source_id}"
            )

        if not source.enabled:
            return TransformResult(
                success=False,
                error=f"Source is disabled: {source_id}"
            )

        # Get adapter
        try:
            adapter = self.get_adapter(source)
        except NotImplementedError as e:
            return TransformResult(
                success=False,
                error=str(e)
            )

        # Fetch and transform
        result = await adapter.fetch_and_transform(
            source_id=source_id,
            endpoint=source.endpoint,
            **fetch_kwargs
        )

        if not result.success or not result.message:
            return result

        # Verify integrity
        is_valid, reason = self.verifier.verify_message(result.message)
        if not is_valid:
            return TransformResult(
                success=False,
                error=f"Verification failed: {reason}",
                transform_time_ms=result.transform_time_ms
            )

        # Sign if configured
        if self.sign_messages:
            try:
                signature = self.verifier.sign_message(result.message)
                # Create new message with signature (immutable)
                result.message = EchoMessage(
                    id=result.message.id,
                    metadata=result.message.metadata,
                    payload=result.message.payload,
                    content_hash=result.message.content_hash,
                    signature=signature,
                )
            except ValueError:
                pass  # No signing key configured, skip

        # Record provenance
        provenance = self.verifier.create_provenance_record(
            result.message,
            operation="translate"
        )
        self._provenance.append(provenance)

        return result

    async def translate_many(
        self,
        source_ids: list[str],
        **fetch_kwargs: Any
    ) -> list[TransformResult]:
        """
        Translate from multiple sources concurrently.

        Args:
            source_ids: List of source IDs to fetch from
            **fetch_kwargs: Shared fetch options for all sources

        Returns:
            List of TransformResults in same order as source_ids
        """
        tasks = [
            self.translate(source_id, **fetch_kwargs)
            for source_id in source_ids
        ]
        return await asyncio.gather(*tasks)

    async def translate_by_tag(
        self,
        tag: str,
        **fetch_kwargs: Any
    ) -> list[TransformResult]:
        """
        Translate from all sources with a given tag.

        Useful for fetching from all sources in a category.
        """
        sources = self.registry.get_by_tag(tag)
        source_ids = [s.id for s in sources]
        return await self.translate_many(source_ids, **fetch_kwargs)

    def get_provenance(
        self,
        message_id: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get provenance records.

        Args:
            message_id: Optional filter by message ID

        Returns:
            List of provenance records
        """
        if message_id:
            return [p for p in self._provenance if p["message_id"] == message_id]
        return self._provenance.copy()

    def clear_provenance(self) -> None:
        """Clear the provenance log."""
        self._provenance.clear()


async def quick_fetch(
    endpoint: str,
    source_id: str = "anonymous",
    **kwargs: Any
) -> TransformResult:
    """
    Quick one-shot fetch without setting up registry.

    Convenience function for simple use cases.

    Example:
        result = await quick_fetch("https://api.example.com/data")
        if result.success:
            print(result.message.payload.data)
    """
    adapter = RestAdapter()
    return await adapter.fetch_and_transform(
        source_id=source_id,
        endpoint=endpoint,
        **kwargs
    )
