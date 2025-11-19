"""
EchoLex Configuration

Application configuration and settings.
"""

from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "EchoLex"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Database
    database_url: str = "postgresql+asyncpg://localhost/echolex"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis (for caching and pub/sub)
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600  # 1 hour

    # ML Models
    model_path: str = "./models"
    prediction_cache_ttl: int = 1800  # 30 minutes

    # Security
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # CORS
    allowed_origins: List[str] = ["*"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Disclaimer
    disclaimer_text: str = (
        "FOR RESEARCH PURPOSES ONLY. This system does not constitute "
        "legal advice. Always consult a licensed attorney."
    )

    class Config:
        env_prefix = "ECHOLEX_"
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Feature flags
class FeatureFlags:
    """Feature flags for enabling/disabling features."""

    # Predictions
    enable_case_predictions: bool = True
    enable_sentence_predictions: bool = True
    enable_appeal_predictions: bool = True

    # Analytics
    enable_judge_analytics: bool = True
    enable_jurisdiction_analytics: bool = True

    # Real-time
    enable_websocket: bool = True
    enable_notifications: bool = True

    # Experimental
    enable_nlp_analysis: bool = False
    enable_advanced_ml: bool = False


features = FeatureFlags()
