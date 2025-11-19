"""
Configuration settings for Echo Fact-Check App.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_factcheck_api_key: Optional[str] = None
    claimbuster_api_key: Optional[str] = None

    # File Upload
    max_upload_size_mb: int = 100
    upload_dir: str = "./uploads"

    # Processing
    whisper_model: str = "base"
    max_audio_duration_seconds: int = 300
    max_video_duration_seconds: int = 300

    # WebSocket
    ws_heartbeat_interval: int = 30

    # Paths
    base_dir: Path = Path(__file__).parent.parent

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def upload_path(self) -> Path:
        """Get the upload directory path."""
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def has_ai_api_key(self) -> bool:
        """Check if at least one AI API key is configured."""
        return bool(self.openai_api_key or self.anthropic_api_key)


# Global settings instance
settings = Settings()
