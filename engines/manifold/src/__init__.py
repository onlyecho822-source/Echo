"""
Manifold Engine - H-Rule Behavioral Manifold

Implements differential geometry-based behavioral correction
using Ricci curvature and harmonic resonance.
"""

from .manifold import Manifold
from .point import Point
from .tensor import Tensor, MetricTensor
from .curvature import RicciCurvature

__all__ = [
    "Manifold",
    "Point",
    "Tensor",
    "MetricTensor",
    "RicciCurvature",
]

__version__ = "0.1.0"
