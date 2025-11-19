"""
REST/HTTP adapter for Echo Phoenix.

Handles fetching and transforming data from REST APIs.
"""

import json
import time
import uuid
from typing import Any

import httpx

from echo.adapters.base import BaseAdapter, AdapterConfig
from echo.models.schema import (
    EchoMessage,
    DataPayload,
    Metadata,
    TransformResult,
)


class RestAdapter(BaseAdapter):
    """
    Adapter for REST/HTTP APIs.

    Supports:
    - GET, POST, PUT, DELETE methods
    - JSON and form-encoded payloads
    - Custom headers and authentication
    - Field mapping transformations
    """

    def __init__(
        self,
        config: AdapterConfig | None = None,
        headers: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
    ):
        super().__init__(config)
        self._default_headers = headers or {}
        self._auth = auth

    @property
    def protocol(self) -> str:
        return "rest"

    async def fetch(
        self,
        endpoint: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        **kwargs: Any
    ) -> tuple[dict[str, Any], int]:
        """
        Fetch data from a REST endpoint.

        Args:
            endpoint: Full URL to fetch from
            method: HTTP method (GET, POST, etc.)
            headers: Additional headers to send
            params: Query parameters
            json_data: JSON body for POST/PUT
            **kwargs: Additional httpx options

        Returns:
            Tuple of (response_data, status_code)
        """
        merged_headers = {**self._default_headers, **(headers or {})}

        async with httpx.AsyncClient(
            timeout=self.config.timeout_seconds,
            auth=self._auth,
        ) as client:
            for attempt in range(self.config.retry_count):
                try:
                    response = await client.request(
                        method=method,
                        url=endpoint,
                        headers=merged_headers,
                        params=params,
                        json=json_data,
                        **kwargs
                    )

                    # Try to parse JSON, fall back to text
                    try:
                        data = response.json()
                    except json.JSONDecodeError:
                        data = {"_raw": response.text}

                    return data, response.status_code

                except httpx.RequestError as e:
                    if attempt < self.config.retry_count - 1:
                        await self._sleep(self.config.retry_delay_seconds * (attempt + 1))
                        continue
                    raise RuntimeError(f"Request failed after {self.config.retry_count} attempts: {e}")

        # Should not reach here, but satisfy type checker
        raise RuntimeError("Unexpected state in fetch")

    async def _sleep(self, seconds: float) -> None:
        """Async sleep for retries."""
        import asyncio
        await asyncio.sleep(seconds)

    def transform(
        self,
        source_id: str,
        raw_data: dict[str, Any]
    ) -> TransformResult:
        """
        Transform REST response data into an EchoMessage.

        Args:
            source_id: Identifier of the data source
            raw_data: Raw JSON response from the API

        Returns:
            TransformResult with normalized message
        """
        start = time.perf_counter()

        try:
            # Apply field mappings if configured
            if self.config.field_mappings:
                normalized_data = self.apply_field_mappings(raw_data)
            else:
                normalized_data = raw_data

            # Validate required fields
            missing = self.validate_required_fields(normalized_data)
            if missing:
                return TransformResult(
                    success=False,
                    error=f"Missing required fields: {missing}",
                    source_bytes=len(json.dumps(raw_data).encode()),
                    transform_time_ms=(time.perf_counter() - start) * 1000
                )

            # Build the EchoMessage
            metadata = Metadata(
                source_id=source_id,
                source_protocol="rest",
                original_format="json",
                transform_version=self.config.schema_version,
            )

            payload = DataPayload(
                data=normalized_data,
                schema_version=self.config.schema_version,
            )

            message = EchoMessage(
                id=str(uuid.uuid4()),
                metadata=metadata,
                payload=payload,
            )

            return TransformResult(
                success=True,
                message=message,
                source_bytes=len(json.dumps(raw_data).encode()),
                transform_time_ms=(time.perf_counter() - start) * 1000
            )

        except Exception as e:
            return TransformResult(
                success=False,
                error=f"Transform error: {e}",
                transform_time_ms=(time.perf_counter() - start) * 1000
            )


class RestAdapterBuilder:
    """Builder pattern for configuring REST adapters."""

    def __init__(self) -> None:
        self._config = AdapterConfig()
        self._headers: dict[str, str] = {}
        self._auth: tuple[str, str] | None = None

    def with_timeout(self, seconds: float) -> "RestAdapterBuilder":
        self._config.timeout_seconds = seconds
        return self

    def with_retries(self, count: int, delay: float = 1.0) -> "RestAdapterBuilder":
        self._config.retry_count = count
        self._config.retry_delay_seconds = delay
        return self

    def with_field_mapping(self, target: str, source: str) -> "RestAdapterBuilder":
        self._config.field_mappings[target] = source
        return self

    def with_default(self, field: str, value: Any) -> "RestAdapterBuilder":
        self._config.default_values[field] = value
        return self

    def with_required_field(self, field: str) -> "RestAdapterBuilder":
        self._config.required_fields.append(field)
        return self

    def with_header(self, name: str, value: str) -> "RestAdapterBuilder":
        self._headers[name] = value
        return self

    def with_bearer_token(self, token: str) -> "RestAdapterBuilder":
        self._headers["Authorization"] = f"Bearer {token}"
        return self

    def with_api_key(self, key: str, header: str = "X-API-Key") -> "RestAdapterBuilder":
        self._headers[header] = key
        return self

    def with_basic_auth(self, username: str, password: str) -> "RestAdapterBuilder":
        self._auth = (username, password)
        return self

    def build(self) -> RestAdapter:
        return RestAdapter(
            config=self._config,
            headers=self._headers,
            auth=self._auth,
        )
