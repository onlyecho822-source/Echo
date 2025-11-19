"""
Echo Universe - Configuration Settings
Central configuration for all API integrations and dashboard settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
FOUNDATIONS_DIR = BASE_DIR / "foundations"

# API Keys (loaded from environment)
class APIKeys:
    """Centralized API key management for Echo Universe."""

    # OpenAI / ChatGPT
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Anthropic / Claude
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")

    # Zapier
    ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL", "")
    ZAPIER_API_KEY = os.getenv("ZAPIER_API_KEY", "")

    # Microsoft Power Automate
    AUTOMATE_CLIENT_ID = os.getenv("AUTOMATE_CLIENT_ID", "")
    AUTOMATE_CLIENT_SECRET = os.getenv("AUTOMATE_CLIENT_SECRET", "")
    AUTOMATE_TENANT_ID = os.getenv("AUTOMATE_TENANT_ID", "")


# Dashboard Configuration
class DashboardConfig:
    """Dashboard application settings."""

    HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    PORT = int(os.getenv("DASHBOARD_PORT", "5000"))
    DEBUG = os.getenv("DASHBOARD_DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "echo-universe-secret-key-change-in-production")


# API Endpoints
class APIEndpoints:
    """External API endpoint configurations."""

    # OpenAI
    OPENAI_BASE_URL = "https://api.openai.com/v1"
    OPENAI_CHAT_ENDPOINT = f"{OPENAI_BASE_URL}/chat/completions"

    # Anthropic
    ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"
    ANTHROPIC_MESSAGES_ENDPOINT = f"{ANTHROPIC_BASE_URL}/messages"

    # GitHub
    GITHUB_API_BASE = "https://api.github.com"

    # Microsoft Graph (Power Automate)
    MS_GRAPH_BASE = "https://graph.microsoft.com/v1.0"
    MS_AUTH_URL = "https://login.microsoftonline.com"


# Echo Universe Metadata
class EchoMetadata:
    """Echo Universe project metadata and versioning."""

    VERSION = "1.0.0"
    CODENAME = "Phoenix Phase"

    # Foundational layers
    FABRIC_OF_ZERO = "Multi-State Resonance Substrate"
    HARMONIC_DIRECTIVES = "Constitutional Governance Layer"

    # System components
    COMPONENTS = {
        "foundations": "DNA + Heartbeat",
        "nexus": "Mind/Constitution",
        "engines": "Organs",
        "relay": "Voice/Arms",
        "library": "Memory + Soul",
        "products": "Expression/Commerce",
        "services": "Operational Expressions",
        "ops": "Circulation/Immune System"
    }


# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG"
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO"
    }
}
