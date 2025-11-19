"""
Dimensional Shield - Sandboxed Execution Environments

Secure, isolated execution environments with resource controls.
"""

from .shield import DimensionalShield
from .dimension import Dimension
from .resource import ResourceGovernor
from .capability import CapabilityEnforcer

__all__ = [
    "DimensionalShield",
    "Dimension",
    "ResourceGovernor",
    "CapabilityEnforcer",
]

__version__ = "0.1.0"
