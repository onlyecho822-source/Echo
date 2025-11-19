"""
Echo Universe - OpenAI/ChatGPT API Connector
Integration with OpenAI for GPT model interactions.
"""

import logging
from typing import Optional

from openai import OpenAI, OpenAIError

import sys
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from src.core.base_connector import BaseAPIConnector, APIResponse, ConnectorStatus
from config.settings import APIKeys, APIEndpoints

logger = logging.getLogger(__name__)


class OpenAIConnector(BaseAPIConnector):
    """
    OpenAI API connector for Echo Universe.

    Provides access to GPT models for text generation, embeddings, and analysis.
    Part of the Echo Nexus intelligence layer.
    """

    def __init__(self, api_key: str = ""):
        super().__init__(
            name="OpenAI/ChatGPT",
            api_key=api_key or APIKeys.OPENAI_API_KEY,
            base_url=APIEndpoints.OPENAI_BASE_URL
        )
        self._client: Optional[OpenAI] = None
        self.default_model = "gpt-4-turbo-preview"

    @property
    def client(self) -> OpenAI:
        """Get or create OpenAI client."""
        if self._client is None and self.api_key:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def test_connection(self) -> APIResponse:
        """Test OpenAI API connection by listing models."""
        if not self.is_configured:
            return APIResponse(
                success=False,
                error="OpenAI API key not configured"
            )

        try:
            models = self.client.models.list()
            model_list = [m.id for m in models.data[:10]]
            self.status = ConnectorStatus.CONNECTED

            return APIResponse(
                success=True,
                data={
                    "available_models": model_list,
                    "total_models": len(models.data)
                }
            )

        except OpenAIError as e:
            self.status = ConnectorStatus.ERROR
            return APIResponse(
                success=False,
                error=str(e)
            )

    def get_status(self) -> dict:
        """Get current OpenAI connector status."""
        return {
            "name": self.name,
            "status": self.status.value,
            "configured": self.is_configured,
            "default_model": self.default_model,
            "request_count": self._request_count
        }

    def chat_completion(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> APIResponse:
        """
        Generate a chat completion using GPT models.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to gpt-4-turbo-preview)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response

        Returns:
            APIResponse with generated text
        """
        if not self.is_configured:
            return APIResponse(success=False, error="Not configured")

        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )

            self._request_count += 1
            self.status = ConnectorStatus.CONNECTED

            if stream:
                return APIResponse(
                    success=True,
                    data=response,
                    metadata={"streaming": True}
                )

            return APIResponse(
                success=True,
                data={
                    "content": response.choices[0].message.content,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "finish_reason": response.choices[0].finish_reason
                }
            )

        except OpenAIError as e:
            self.status = ConnectorStatus.ERROR
            return APIResponse(success=False, error=str(e))

    def simple_prompt(self, prompt: str, system_message: str = None) -> APIResponse:
        """
        Send a simple prompt to ChatGPT.

        Args:
            prompt: User prompt text
            system_message: Optional system message for context

        Returns:
            APIResponse with generated text
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        return self.chat_completion(messages)

    def create_embedding(self, text: str, model: str = "text-embedding-3-small") -> APIResponse:
        """
        Create text embeddings for semantic analysis.

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            APIResponse with embedding vector
        """
        if not self.is_configured:
            return APIResponse(success=False, error="Not configured")

        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )

            self._request_count += 1

            return APIResponse(
                success=True,
                data={
                    "embedding": response.data[0].embedding,
                    "model": model,
                    "dimensions": len(response.data[0].embedding),
                    "usage": response.usage.total_tokens
                }
            )

        except OpenAIError as e:
            return APIResponse(success=False, error=str(e))

    def analyze_code(self, code: str, language: str = "python") -> APIResponse:
        """
        Analyze code using GPT for insights and suggestions.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            APIResponse with analysis
        """
        system_message = f"""You are an expert {language} code analyzer.
        Analyze the provided code and give insights on:
        1. Code quality and best practices
        2. Potential bugs or issues
        3. Performance considerations
        4. Security concerns
        5. Suggested improvements"""

        return self.simple_prompt(
            f"Analyze this {language} code:\n\n```{language}\n{code}\n```",
            system_message
        )

    def close(self):
        """Close OpenAI client connections."""
        super().close()
        self._client = None
