"""
Hydra Configuration System
==========================

Centralized configuration for AI model connections, tentacle parameters,
and load balancing thresholds.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import os


class AIProvider(Enum):
    """Supported AI providers for tentacle fusion"""
    CLAUDE = "anthropic"
    GEMINI = "google"
    CHATGPT = "openai"
    OPUS = "anthropic_opus"
    SONNET = "anthropic_sonnet"
    LOCAL = "local_llm"


class TentacleMode(Enum):
    """Operating modes for tentacles"""
    PASSIVE = "passive"      # Observation only
    ACTIVE = "active"        # Full engagement
    DORMANT = "dormant"      # Sleeping, conserving resources
    LEARNING = "learning"    # Training/adaptation mode


@dataclass
class AIModelConfig:
    """Configuration for individual AI models"""
    provider: AIProvider
    model_id: str
    api_key_env: str  # Environment variable name for API key
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    specialization: str = "general"

    @property
    def api_key(self) -> Optional[str]:
        return os.getenv(self.api_key_env)


@dataclass
class LoadBalancerConfig:
    """Configuration to prevent tentacle overstimulation"""
    max_concurrent_tentacles: int = 4  # Like octopus - not all 8 at once
    cooldown_period: float = 2.0  # Seconds between intense operations
    memory_limit_mb: int = 2048
    token_budget_per_minute: int = 100000
    priority_queue_size: int = 50
    circuit_breaker_threshold: int = 5  # Failures before shutdown
    backoff_multiplier: float = 1.5


@dataclass
class DashboardConfig:
    """Dashboard server configuration"""
    host: str = "127.0.0.1"
    port: int = 8080
    debug: bool = False
    secret_key: str = field(default_factory=lambda: os.urandom(24).hex())
    session_timeout: int = 3600
    websocket_enabled: bool = True


@dataclass
class HydraConfig:
    """Master configuration for the Hydra system"""

    # AI Model Configurations
    models: Dict[str, AIModelConfig] = field(default_factory=lambda: {
        "claude_sonnet": AIModelConfig(
            provider=AIProvider.SONNET,
            model_id="claude-sonnet-4-5-20250929",
            api_key_env="ANTHROPIC_API_KEY",
            specialization="reasoning_analysis"
        ),
        "claude_opus": AIModelConfig(
            provider=AIProvider.OPUS,
            model_id="claude-opus-4-0-20250514",
            api_key_env="ANTHROPIC_API_KEY",
            specialization="complex_orchestration"
        ),
        "gemini": AIModelConfig(
            provider=AIProvider.GEMINI,
            model_id="gemini-2.0-flash",
            api_key_env="GOOGLE_API_KEY",
            specialization="multimodal_analysis"
        ),
        "chatgpt": AIModelConfig(
            provider=AIProvider.CHATGPT,
            model_id="gpt-4-turbo",
            api_key_env="OPENAI_API_KEY",
            specialization="code_generation"
        ),
    })

    # Load Balancer
    load_balancer: LoadBalancerConfig = field(default_factory=LoadBalancerConfig)

    # Dashboard
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)

    # Logging
    log_level: str = "INFO"
    log_file: str = "hydra.log"

    # Security
    require_authorization: bool = True
    audit_all_operations: bool = True
    ethical_constraints_enabled: bool = True

    # Tentacle defaults
    default_tentacle_mode: TentacleMode = TentacleMode.PASSIVE
    tentacle_timeout: int = 60

    @classmethod
    def from_env(cls) -> "HydraConfig":
        """Load configuration from environment variables"""
        config = cls()

        if os.getenv("HYDRA_DEBUG"):
            config.dashboard.debug = True
            config.log_level = "DEBUG"

        if os.getenv("HYDRA_PORT"):
            config.dashboard.port = int(os.getenv("HYDRA_PORT"))

        return config
