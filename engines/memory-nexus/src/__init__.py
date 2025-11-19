"""
Memory Nexus - Distributed Resonant Memory Fabric

This module provides the core memory management system for Echo Nexus,
enabling distributed, cryptographically-verified storage with resonant indexing.
"""

from .nexus import MemoryNexus
from .capsule import Capsule
from .shard import Shard
from .index import ResonanceIndex

__all__ = [
    "MemoryNexus",
    "Capsule",
    "Shard",
    "ResonanceIndex",
]

__version__ = "0.1.0"
