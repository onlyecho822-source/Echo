"""
Echo Reverse Engineering Engine

A system for tracing information back to its origins and uncovering
truth by analyzing facts from multiple sources.

Core Capabilities:
- Source collection and analysis
- Fact extraction and validation
- Timeline reconstruction
- Cross-reference analysis
- Provenance tracking
- Comprehensive reporting
"""

__version__ = "0.1.0"
__author__ = "Echo Civilization"

from echo_engine.core.engine import ReverseEngineeringEngine
from echo_engine.core.models import (
    Source,
    Fact,
    Timeline,
    Connection,
    ProvenanceChain,
    Investigation,
)

__all__ = [
    "ReverseEngineeringEngine",
    "Source",
    "Fact",
    "Timeline",
    "Connection",
    "ProvenanceChain",
    "Investigation",
]
