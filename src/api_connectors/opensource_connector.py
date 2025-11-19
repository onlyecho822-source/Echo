"""
Echo Universe - Open Source API Connector
Framework for integrating with various open-source APIs and services.
"""

import logging
from typing import Any, Optional
from dataclasses import dataclass

import sys
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from src.core.base_connector import BaseAPIConnector, APIResponse, ConnectorStatus

logger = logging.getLogger(__name__)


@dataclass
class OpenSourceAPI:
    """Definition for an open-source API endpoint."""
    name: str
    base_url: str
    auth_type: str = "none"  # none, bearer, api_key, basic
    auth_header: str = "Authorization"
    api_key: str = ""
    description: str = ""


class OpenSourceConnector(BaseAPIConnector):
    """
    Generic open-source API connector for Echo Universe.

    Provides a flexible framework for integrating with any open-source API.
    Part of the Echo Relay system for community-driven integrations.
    """

    def __init__(self):
        super().__init__(
            name="Open Source APIs",
            api_key="",
            base_url=""
        )
        self._apis: dict[str, OpenSourceAPI] = {}
        self._register_default_apis()

    def _register_default_apis(self):
        """Register commonly used open-source APIs."""

        # Ollama - Local LLM
        self.register_api(OpenSourceAPI(
            name="ollama",
            base_url="http://localhost:11434",
            auth_type="none",
            description="Local LLM inference with Ollama"
        ))

        # LocalAI - OpenAI-compatible local AI
        self.register_api(OpenSourceAPI(
            name="localai",
            base_url="http://localhost:8080",
            auth_type="none",
            description="OpenAI-compatible local AI backend"
        ))

        # Hugging Face Inference
        self.register_api(OpenSourceAPI(
            name="huggingface",
            base_url="https://api-inference.huggingface.co",
            auth_type="bearer",
            description="Hugging Face model inference API"
        ))

        # JSONPlaceholder - Testing API
        self.register_api(OpenSourceAPI(
            name="jsonplaceholder",
            base_url="https://jsonplaceholder.typicode.com",
            auth_type="none",
            description="Free fake API for testing"
        ))

        # OpenWeatherMap
        self.register_api(OpenSourceAPI(
            name="openweather",
            base_url="https://api.openweathermap.org/data/2.5",
            auth_type="api_key",
            auth_header="appid",
            description="Weather data API"
        ))

        # NewsAPI
        self.register_api(OpenSourceAPI(
            name="newsapi",
            base_url="https://newsapi.org/v2",
            auth_type="api_key",
            auth_header="X-Api-Key",
            description="News aggregation API"
        ))

    @property
    def is_configured(self) -> bool:
        """Always returns True as this is a framework connector."""
        return True

    def test_connection(self) -> APIResponse:
        """Test the connector by listing registered APIs."""
        self.status = ConnectorStatus.CONNECTED
        return APIResponse(
            success=True,
            data={
                "registered_apis": list(self._apis.keys()),
                "count": len(self._apis)
            }
        )

    def get_status(self) -> dict:
        """Get current connector status."""
        return {
            "name": self.name,
            "status": self.status.value,
            "configured": self.is_configured,
            "registered_apis": len(self._apis),
            "api_names": list(self._apis.keys()),
            "request_count": self._request_count
        }

    def register_api(self, api: OpenSourceAPI) -> APIResponse:
        """
        Register a new open-source API.

        Args:
            api: OpenSourceAPI configuration

        Returns:
            APIResponse confirming registration
        """
        self._apis[api.name] = api
        logger.info(f"Registered API: {api.name} ({api.base_url})")

        return APIResponse(
            success=True,
            data={
                "name": api.name,
                "base_url": api.base_url,
                "registered": True
            }
        )

    def set_api_key(self, api_name: str, api_key: str) -> APIResponse:
        """
        Set the API key for a registered API.

        Args:
            api_name: Name of the registered API
            api_key: API key to set

        Returns:
            APIResponse confirming update
        """
        if api_name not in self._apis:
            return APIResponse(
                success=False,
                error=f"API '{api_name}' not registered"
            )

        self._apis[api_name].api_key = api_key
        return APIResponse(
            success=True,
            data={"api": api_name, "key_set": True}
        )

    def _get_auth_headers(self, api: OpenSourceAPI) -> dict:
        """Get authentication headers for an API."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "EchoUniverse/1.0"
        }

        if api.auth_type == "bearer" and api.api_key:
            headers["Authorization"] = f"Bearer {api.api_key}"
        elif api.auth_type == "api_key" and api.api_key:
            headers[api.auth_header] = api.api_key

        return headers

    def call_api(
        self,
        api_name: str,
        endpoint: str,
        method: str = "GET",
        data: dict = None,
        params: dict = None
    ) -> APIResponse:
        """
        Make a request to a registered open-source API.

        Args:
            api_name: Name of the registered API
            endpoint: API endpoint path
            method: HTTP method
            data: Request body data
            params: Query parameters

        Returns:
            APIResponse with API result
        """
        if api_name not in self._apis:
            return APIResponse(
                success=False,
                error=f"API '{api_name}' not registered"
            )

        api = self._apis[api_name]
        url = f"{api.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_auth_headers(api)

        kwargs = {"headers": headers}
        if data:
            kwargs["json"] = data
        if params:
            kwargs["params"] = params

        return self._make_request(method, url, **kwargs)

    # Convenience methods for common open-source APIs

    def ollama_generate(
        self,
        prompt: str,
        model: str = "llama2",
        stream: bool = False
    ) -> APIResponse:
        """
        Generate text using Ollama local LLM.

        Args:
            prompt: Text prompt
            model: Model name
            stream: Whether to stream response

        Returns:
            APIResponse with generated text
        """
        return self.call_api(
            "ollama",
            "api/generate",
            method="POST",
            data={
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
        )

    def ollama_chat(
        self,
        messages: list,
        model: str = "llama2"
    ) -> APIResponse:
        """
        Chat with Ollama local LLM.

        Args:
            messages: List of message dicts
            model: Model name

        Returns:
            APIResponse with chat response
        """
        return self.call_api(
            "ollama",
            "api/chat",
            method="POST",
            data={
                "model": model,
                "messages": messages,
                "stream": False
            }
        )

    def huggingface_inference(
        self,
        model_id: str,
        inputs: Any,
        api_key: str = None
    ) -> APIResponse:
        """
        Run inference on a Hugging Face model.

        Args:
            model_id: Model identifier (e.g., 'bert-base-uncased')
            inputs: Model inputs
            api_key: Optional API key override

        Returns:
            APIResponse with inference results
        """
        if api_key:
            self.set_api_key("huggingface", api_key)

        return self.call_api(
            "huggingface",
            f"models/{model_id}",
            method="POST",
            data={"inputs": inputs}
        )

    def localai_chat(
        self,
        messages: list,
        model: str = "gpt-3.5-turbo"
    ) -> APIResponse:
        """
        Chat using LocalAI (OpenAI-compatible).

        Args:
            messages: Chat messages
            model: Model name

        Returns:
            APIResponse with chat response
        """
        return self.call_api(
            "localai",
            "v1/chat/completions",
            method="POST",
            data={
                "model": model,
                "messages": messages
            }
        )

    def list_registered_apis(self) -> APIResponse:
        """
        List all registered APIs with their details.

        Returns:
            APIResponse with API list
        """
        apis_info = []
        for name, api in self._apis.items():
            apis_info.append({
                "name": name,
                "base_url": api.base_url,
                "auth_type": api.auth_type,
                "description": api.description,
                "has_key": bool(api.api_key)
            })

        return APIResponse(success=True, data=apis_info)
