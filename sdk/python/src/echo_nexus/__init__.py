"""
Echo Nexus - Distributed Intelligence Platform

A distributed, self-reinforcing, multi-engine intelligence platform.
"""

__version__ = "0.1.0"

# Core exports
from echo_nexus.core import Orchestrator

# Re-export main components for convenience
__all__ = [
    "Orchestrator",
    "__version__",
]
