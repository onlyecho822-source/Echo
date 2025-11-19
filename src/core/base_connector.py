"""
Echo Universe - Base API Connector
Foundational class for all API integrations in the Echo ecosystem.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import httpx
import requests

logger = logging.getLogger(__name__)


class ConnectorStatus(Enum):
    """Status states for API connectors."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class APIResponse:
    """Standardized response object for all API calls."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert response to dictionary format."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "status_code": self.status_code,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class BaseAPIConnector(ABC):
    """
    Abstract base class for all Echo Universe API connectors.

    Implements the Fabric of Zero principle: connections as structural lattice,
    not mere data pipes. Each connector maintains harmonic resonance with its API.
    """

    def __init__(self, name: str, api_key: str = "", base_url: str = ""):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.status = ConnectorStatus.DISCONNECTED
        self._session: Optional[requests.Session] = None
        self._async_client: Optional[httpx.AsyncClient] = None
        self._last_request_time: Optional[datetime] = None
        self._request_count = 0

    @property
    def is_configured(self) -> bool:
        """Check if the connector has required configuration."""
        return bool(self.api_key)

    @property
    def headers(self) -> dict:
        """Default headers for API requests. Override in subclasses."""
        return {
            "Content-Type": "application/json",
            "User-Agent": "EchoUniverse/1.0"
        }

    def get_session(self) -> requests.Session:
        """Get or create a requests session."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(self.headers)
        return self._session

    async def get_async_client(self) -> httpx.AsyncClient:
        """Get or create an async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(headers=self.headers)
        return self._async_client

    @abstractmethod
    def test_connection(self) -> APIResponse:
        """Test the API connection. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_status(self) -> dict:
        """Get current connector status and metadata."""
        pass

    def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> APIResponse:
        """
        Make a synchronous HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL for the request
            **kwargs: Additional arguments for requests

        Returns:
            APIResponse with result or error
        """
        try:
            session = self.get_session()
            response = session.request(method, url, **kwargs)
            self._last_request_time = datetime.utcnow()
            self._request_count += 1

            if response.status_code == 429:
                self.status = ConnectorStatus.RATE_LIMITED
                return APIResponse(
                    success=False,
                    error="Rate limited",
                    status_code=429
                )

            response.raise_for_status()
            self.status = ConnectorStatus.CONNECTED

            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code
            )

        except requests.exceptions.RequestException as e:
            self.status = ConnectorStatus.ERROR
            logger.error(f"{self.name} request error: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                status_code=getattr(e.response, "status_code", None) if hasattr(e, "response") else None
            )

    async def _make_async_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> APIResponse:
        """
        Make an asynchronous HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL for the request
            **kwargs: Additional arguments for httpx

        Returns:
            APIResponse with result or error
        """
        try:
            client = await self.get_async_client()
            response = await client.request(method, url, **kwargs)
            self._last_request_time = datetime.utcnow()
            self._request_count += 1

            if response.status_code == 429:
                self.status = ConnectorStatus.RATE_LIMITED
                return APIResponse(
                    success=False,
                    error="Rate limited",
                    status_code=429
                )

            response.raise_for_status()
            self.status = ConnectorStatus.CONNECTED

            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code
            )

        except httpx.HTTPError as e:
            self.status = ConnectorStatus.ERROR
            logger.error(f"{self.name} async request error: {e}")
            return APIResponse(
                success=False,
                error=str(e)
            )

    def close(self):
        """Close any open connections."""
        if self._session:
            self._session.close()
            self._session = None

    async def aclose(self):
        """Close async connections."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, status={self.status.value})>"
