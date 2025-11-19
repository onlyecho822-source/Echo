"""
Echo Ethics Dimmer - pH-Based Reasoning Calibration System

A configurable system for adjusting AI analytical depth and candor
while maintaining invariant safety boundaries.

Levels:
    L5 (pH 7.0) - Safe Harbor: Conservative, filtered
    L4 (pH 6.3) - Red Team: Threat modeling, defensive R&D
    L3 (pH 5.4) - Grey Zone: Competitive intelligence
    L2 (pH 4.7) - Black Lens: Unfiltered analysis
    L1 (pH 2.0) - Forbidden: Simulation-only boundary

Author: Nathan Poinsette
Framework: Echo Civilization - Phoenix Phase
"""

from .controller import EthicsDimmerController
from .reasoning_amplifier import ReasoningAmplifier
from .risk_modeler import RiskModeler, DriftMeter
from .boundaries_engine import BoundariesEngine
from .output_generator import OutputGenerator

__version__ = "1.0.0"
__author__ = "Nathan Poinsette"

__all__ = [
    "EthicsDimmerController",
    "ReasoningAmplifier",
    "RiskModeler",
    "DriftMeter",
    "BoundariesEngine",
    "OutputGenerator",
]
