"""
AI Model Tentacles
==================

Tentacles that wrap different AI providers (Claude, Gemini, ChatGPT, etc.)
Each has specialized strengths that contribute to the fusion.
"""

from typing import Any, Dict, Optional, Set
import asyncio
import json
import logging

from .base import Tentacle, TentacleCapability
from ..config import AIModelConfig, AIProvider


class ClaudeTentacle(Tentacle):
    """
    Claude AI Tentacle (Sonnet/Opus)

    Strengths:
    - Complex reasoning and analysis
    - Code understanding and generation
    - Safety and ethical considerations
    - Long context handling
    """

    def __init__(
        self,
        tentacle_id: str = "claude_primary",
        model_config: Optional[AIModelConfig] = None
    ):
        capabilities = {
            TentacleCapability.REASONING,
            TentacleCapability.CODE_ANALYSIS,
            TentacleCapability.CODE_GENERATION,
            TentacleCapability.TEXT_GENERATION,
            TentacleCapability.REPORT_GENERATION,
            TentacleCapability.DATA_CORRELATION,
            TentacleCapability.POLICY_ANALYSIS,
        }

        if model_config is None:
            model_config = AIModelConfig(
                provider=AIProvider.SONNET,
                model_id="claude-sonnet-4-5-20250929",
                api_key_env="ANTHROPIC_API_KEY",
                specialization="reasoning_analysis"
            )

        super().__init__(
            tentacle_id=tentacle_id,
            name="Claude AI",
            capabilities=capabilities,
            model_config=model_config
        )

    async def _setup_client(self) -> None:
        """Setup Anthropic client"""
        try:
            # Import here to avoid dependency issues
            import anthropic
            api_key = self.model_config.api_key
            if api_key:
                self._client = anthropic.AsyncAnthropic(api_key=api_key)
            else:
                self.logger.warning("No API key found, running in mock mode")
                self._client = None
        except ImportError:
            self.logger.warning("anthropic package not installed, running in mock mode")
            self._client = None

    async def _cleanup_client(self) -> None:
        """Cleanup client"""
        self._client = None

    async def _process(self, task: Any) -> Dict[str, Any]:
        """Process task using Claude"""
        payload = task.payload if hasattr(task, 'payload') else task

        prompt = payload.get("prompt", "")
        system_prompt = payload.get("system", "You are a cybersecurity expert assistant.")

        if self._client is None:
            # Mock response for demo/testing
            return {
                "response": f"[MOCK] Claude analysis of: {prompt[:100]}...",
                "tokens_used": 100,
                "model": self.model_config.model_id
            }

        try:
            response = await self._client.messages.create(
                model=self.model_config.model_id,
                max_tokens=self.model_config.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )

            return {
                "response": response.content[0].text,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "model": self.model_config.model_id
            }

        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            raise


class GeminiTentacle(Tentacle):
    """
    Google Gemini Tentacle

    Strengths:
    - Multimodal analysis (images, video)
    - Web/search integration
    - Fast responses
    - Large context window
    """

    def __init__(
        self,
        tentacle_id: str = "gemini_primary",
        model_config: Optional[AIModelConfig] = None
    ):
        capabilities = {
            TentacleCapability.MULTIMODAL,
            TentacleCapability.TEXT_GENERATION,
            TentacleCapability.CODE_GENERATION,
            TentacleCapability.WEB_RECON,
            TentacleCapability.OSINT,
            TentacleCapability.LOG_ANALYSIS,
        }

        if model_config is None:
            model_config = AIModelConfig(
                provider=AIProvider.GEMINI,
                model_id="gemini-2.0-flash",
                api_key_env="GOOGLE_API_KEY",
                specialization="multimodal_analysis"
            )

        super().__init__(
            tentacle_id=tentacle_id,
            name="Gemini AI",
            capabilities=capabilities,
            model_config=model_config
        )

    async def _setup_client(self) -> None:
        """Setup Google Gemini client"""
        try:
            import google.generativeai as genai
            api_key = self.model_config.api_key
            if api_key:
                genai.configure(api_key=api_key)
                self._client = genai.GenerativeModel(self.model_config.model_id)
            else:
                self.logger.warning("No API key found, running in mock mode")
                self._client = None
        except ImportError:
            self.logger.warning("google-generativeai package not installed, running in mock mode")
            self._client = None

    async def _cleanup_client(self) -> None:
        """Cleanup client"""
        self._client = None

    async def _process(self, task: Any) -> Dict[str, Any]:
        """Process task using Gemini"""
        payload = task.payload if hasattr(task, 'payload') else task
        prompt = payload.get("prompt", "")

        if self._client is None:
            return {
                "response": f"[MOCK] Gemini analysis of: {prompt[:100]}...",
                "tokens_used": 100,
                "model": self.model_config.model_id
            }

        try:
            response = await asyncio.to_thread(
                self._client.generate_content,
                prompt
            )

            return {
                "response": response.text,
                "tokens_used": 150,  # Gemini doesn't always provide token count
                "model": self.model_config.model_id
            }

        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            raise


class ChatGPTTentacle(Tentacle):
    """
    OpenAI ChatGPT Tentacle

    Strengths:
    - Code generation and completion
    - Broad knowledge base
    - Function calling
    - JSON mode
    """

    def __init__(
        self,
        tentacle_id: str = "chatgpt_primary",
        model_config: Optional[AIModelConfig] = None
    ):
        capabilities = {
            TentacleCapability.CODE_GENERATION,
            TentacleCapability.TEXT_GENERATION,
            TentacleCapability.CODE_ANALYSIS,
            TentacleCapability.EXPLOIT_DEV,
            TentacleCapability.REPORT_GENERATION,
        }

        if model_config is None:
            model_config = AIModelConfig(
                provider=AIProvider.CHATGPT,
                model_id="gpt-4-turbo",
                api_key_env="OPENAI_API_KEY",
                specialization="code_generation"
            )

        super().__init__(
            tentacle_id=tentacle_id,
            name="ChatGPT",
            capabilities=capabilities,
            model_config=model_config
        )

    async def _setup_client(self) -> None:
        """Setup OpenAI client"""
        try:
            from openai import AsyncOpenAI
            api_key = self.model_config.api_key
            if api_key:
                self._client = AsyncOpenAI(api_key=api_key)
            else:
                self.logger.warning("No API key found, running in mock mode")
                self._client = None
        except ImportError:
            self.logger.warning("openai package not installed, running in mock mode")
            self._client = None

    async def _cleanup_client(self) -> None:
        """Cleanup client"""
        self._client = None

    async def _process(self, task: Any) -> Dict[str, Any]:
        """Process task using ChatGPT"""
        payload = task.payload if hasattr(task, 'payload') else task

        prompt = payload.get("prompt", "")
        system_prompt = payload.get("system", "You are a cybersecurity expert.")

        if self._client is None:
            return {
                "response": f"[MOCK] ChatGPT analysis of: {prompt[:100]}...",
                "tokens_used": 100,
                "model": self.model_config.model_id
            }

        try:
            response = await self._client.chat.completions.create(
                model=self.model_config.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.model_config.max_tokens
            )

            return {
                "response": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": self.model_config.model_id
            }

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise


class LocalLLMTentacle(Tentacle):
    """
    Local LLM Tentacle (Ollama, llama.cpp, etc.)

    Strengths:
    - Privacy (no data leaves machine)
    - No API costs
    - Customizable models
    - Offline operation
    """

    def __init__(
        self,
        tentacle_id: str = "local_llm",
        model_config: Optional[AIModelConfig] = None,
        ollama_host: str = "http://localhost:11434"
    ):
        capabilities = {
            TentacleCapability.TEXT_GENERATION,
            TentacleCapability.CODE_GENERATION,
            TentacleCapability.CODE_ANALYSIS,
        }

        if model_config is None:
            model_config = AIModelConfig(
                provider=AIProvider.LOCAL,
                model_id="llama3.2",
                api_key_env="",  # No API key needed
                specialization="local_processing"
            )

        super().__init__(
            tentacle_id=tentacle_id,
            name="Local LLM",
            capabilities=capabilities,
            model_config=model_config
        )

        self.ollama_host = ollama_host

    async def _setup_client(self) -> None:
        """Setup Ollama client"""
        try:
            import httpx
            self._client = httpx.AsyncClient(
                base_url=self.ollama_host,
                timeout=120.0
            )
            # Test connection
            response = await self._client.get("/api/tags")
            if response.status_code != 200:
                self.logger.warning("Ollama not available, running in mock mode")
                self._client = None
        except Exception as e:
            self.logger.warning(f"Could not connect to Ollama: {e}")
            self._client = None

    async def _cleanup_client(self) -> None:
        """Cleanup client"""
        if self._client:
            await self._client.aclose()
        self._client = None

    async def _process(self, task: Any) -> Dict[str, Any]:
        """Process task using local LLM"""
        payload = task.payload if hasattr(task, 'payload') else task
        prompt = payload.get("prompt", "")

        if self._client is None:
            return {
                "response": f"[MOCK] Local LLM analysis of: {prompt[:100]}...",
                "tokens_used": 100,
                "model": self.model_config.model_id
            }

        try:
            response = await self._client.post(
                "/api/generate",
                json={
                    "model": self.model_config.model_id,
                    "prompt": prompt,
                    "stream": False
                }
            )

            data = response.json()

            return {
                "response": data.get("response", ""),
                "tokens_used": data.get("eval_count", 0),
                "model": self.model_config.model_id
            }

        except Exception as e:
            self.logger.error(f"Local LLM error: {e}")
            raise
