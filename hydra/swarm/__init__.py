"""
Hydra Swarm Module
==================

Create and manage swarms of specialized AI agents for coordinated operations.
"""

from .factory import SwarmFactory, SwarmConfig
from .agents import Agent, AgentRole
from .coordinator import SwarmCoordinator

__all__ = [
    "SwarmFactory",
    "SwarmConfig",
    "Agent",
    "AgentRole",
    "SwarmCoordinator"
]
