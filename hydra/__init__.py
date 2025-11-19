"""
Hydra: Multi-AI Fusion Cybersecurity Framework
===============================================

A coordinated AI orchestration system that fuses the best capabilities
of multiple AI models into specialized "tentacles" for cybersecurity operations.

Architecture inspired by the octopus - intelligent, coordinated, but never overstimulated.
Each tentacle operates semi-autonomously while the brain maintains strategic control.

Author: Echo Project
Purpose: Ethical cybersecurity operations, auditing, forensics, and AI agent swarms
"""

__version__ = "0.1.0"
__codename__ = "Moses"  # Freeing AI to work together

from .core.orchestrator import HydraOrchestrator
from .core.brain import HydraBrain
from .tentacles.base import Tentacle
from .config import HydraConfig

__all__ = [
    "HydraOrchestrator",
    "HydraBrain",
    "Tentacle",
    "HydraConfig"
]
