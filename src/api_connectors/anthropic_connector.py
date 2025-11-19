"""
Echo Universe - Anthropic/Claude API Connector
Integration with Anthropic for Claude model interactions.
"""

import logging
from typing import Optional

from anthropic import Anthropic, APIError

import sys
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from src.core.base_connector import BaseAPIConnector, APIResponse, ConnectorStatus
from config.settings import APIKeys, APIEndpoints

logger = logging.getLogger(__name__)


class AnthropicConnector(BaseAPIConnector):
    """
    Anthropic/Claude API connector for Echo Universe.

    Provides access to Claude models for intelligent conversation and analysis.
    Part of the Echo Nexus intelligence layer - harmonic resonance with AI.
    """

    def __init__(self, api_key: str = ""):
        super().__init__(
            name="Anthropic/Claude",
            api_key=api_key or APIKeys.ANTHROPIC_API_KEY,
            base_url=APIEndpoints.ANTHROPIC_BASE_URL
        )
        self._client: Optional[Anthropic] = None
        self.default_model = "claude-sonnet-4-20250514"

    @property
    def client(self) -> Anthropic:
        """Get or create Anthropic client."""
        if self._client is None and self.api_key:
            self._client = Anthropic(api_key=self.api_key)
        return self._client

    def test_connection(self) -> APIResponse:
        """Test Anthropic API connection with a simple message."""
        if not self.is_configured:
            return APIResponse(
                success=False,
                error="Anthropic API key not configured"
            )

        try:
            # Test with a minimal message
            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )

            self.status = ConnectorStatus.CONNECTED

            return APIResponse(
                success=True,
                data={
                    "model": response.model,
                    "status": "connected"
                }
            )

        except APIError as e:
            self.status = ConnectorStatus.ERROR
            return APIResponse(
                success=False,
                error=str(e)
            )

    def get_status(self) -> dict:
        """Get current Anthropic connector status."""
        return {
            "name": self.name,
            "status": self.status.value,
            "configured": self.is_configured,
            "default_model": self.default_model,
            "request_count": self._request_count
        }

    def create_message(
        self,
        messages: list,
        model: str = None,
        system: str = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False
    ) -> APIResponse:
        """
        Create a message using Claude models.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to claude-sonnet-4-20250514)
            system: System prompt for context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            stream: Whether to stream the response

        Returns:
            APIResponse with generated message
        """
        if not self.is_configured:
            return APIResponse(success=False, error="Not configured")

        try:
            kwargs = {
                "model": model or self.default_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            if system:
                kwargs["system"] = system

            if stream:
                response = self.client.messages.stream(**kwargs)
                return APIResponse(
                    success=True,
                    data=response,
                    metadata={"streaming": True}
                )

            response = self.client.messages.create(**kwargs)

            self._request_count += 1
            self.status = ConnectorStatus.CONNECTED

            return APIResponse(
                success=True,
                data={
                    "content": response.content[0].text,
                    "model": response.model,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    },
                    "stop_reason": response.stop_reason
                }
            )

        except APIError as e:
            self.status = ConnectorStatus.ERROR
            return APIResponse(success=False, error=str(e))

    def simple_prompt(self, prompt: str, system_message: str = None) -> APIResponse:
        """
        Send a simple prompt to Claude.

        Args:
            prompt: User prompt text
            system_message: Optional system message for context

        Returns:
            APIResponse with generated text
        """
        messages = [{"role": "user", "content": prompt}]
        return self.create_message(messages, system=system_message)

    def analyze_with_thinking(
        self,
        prompt: str,
        system: str = None
    ) -> APIResponse:
        """
        Analyze a complex problem with extended thinking.

        Uses Claude's capability for deeper reasoning on complex tasks.

        Args:
            prompt: Analysis prompt
            system: System context

        Returns:
            APIResponse with detailed analysis
        """
        enhanced_system = system or ""
        enhanced_system += """

        Please think through this step-by-step:
        1. Understand the core question/problem
        2. Break down the components
        3. Analyze each component
        4. Synthesize insights
        5. Provide actionable conclusions
        """

        return self.simple_prompt(prompt, enhanced_system)

    def code_review(self, code: str, language: str = "python") -> APIResponse:
        """
        Review code using Claude's analysis capabilities.

        Args:
            code: Source code to review
            language: Programming language

        Returns:
            APIResponse with code review
        """
        system_message = f"""You are an expert {language} code reviewer.
        Provide a thorough code review covering:
        - Code quality and readability
        - Best practices adherence
        - Potential bugs or edge cases
        - Security considerations
        - Performance optimizations
        - Suggested improvements with examples"""

        return self.simple_prompt(
            f"Please review this {language} code:\n\n```{language}\n{code}\n```",
            system_message
        )

    def harmonic_analysis(self, content: str) -> APIResponse:
        """
        Perform harmonic analysis using Echo Universe principles.

        Analyzes content through the lens of resonance and multi-state fabric.

        Args:
            content: Content to analyze

        Returns:
            APIResponse with harmonic analysis
        """
        system_message = """You are analyzing content through the Echo Universe
        harmonic framework. Consider:
        - Resonance patterns and coherence
        - Multi-state potential interpretations
        - Harmonic alignment and dissonance
        - Structural integrity of ideas
        - Potential for amplification or attenuation

        Provide insights that reveal the harmonic nature of the content."""

        return self.simple_prompt(
            f"Perform a harmonic analysis of:\n\n{content}",
            system_message
        )

    def close(self):
        """Close Anthropic client connections."""
        super().close()
        self._client = None
