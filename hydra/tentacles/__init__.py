"""
Hydra Tentacles
===============

Specialized AI tentacles for different tasks. Each tentacle operates
semi-autonomously but coordinates through the brain.
"""

from .base import Tentacle, TentacleCapability
from .ai_models import (
    ClaudeTentacle,
    GeminiTentacle,
    ChatGPTTentacle,
    LocalLLMTentacle
)
from .security import (
    ReconTentacle,
    VulnScanTentacle,
    ForensicsTentacle,
    AuditTentacle,
    ExploitTentacle,
    ThreatIntelTentacle
)

__all__ = [
    # Base
    "Tentacle",
    "TentacleCapability",
    # AI Models
    "ClaudeTentacle",
    "GeminiTentacle",
    "ChatGPTTentacle",
    "LocalLLMTentacle",
    # Security
    "ReconTentacle",
    "VulnScanTentacle",
    "ForensicsTentacle",
    "AuditTentacle",
    "ExploitTentacle",
    "ThreatIntelTentacle"
]
