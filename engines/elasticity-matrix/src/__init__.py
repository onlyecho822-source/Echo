"""
Elasticity Matrix - LLM Capability Mapping and Adaptation

Dynamic capability-context mapping for adaptive AI behavior.
"""

from .matrix import ElasticityMatrix
from .capability import Capability, CapabilityProfile
from .context import Context, ContextRequirements

__all__ = [
    "ElasticityMatrix",
    "Capability",
    "CapabilityProfile",
    "Context",
    "ContextRequirements",
]

__version__ = "0.1.0"
