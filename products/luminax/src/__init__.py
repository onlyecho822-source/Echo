"""
Luminax - Illumination and Insight Generation

Discover patterns and generate actionable intelligence.
"""

from .luminax import Luminax
from .insight import Insight, InsightQuery
from .pattern import PatternDetector
from .connection import ConnectionMapper

__all__ = [
    "Luminax",
    "Insight",
    "InsightQuery",
    "PatternDetector",
    "ConnectionMapper",
]

__version__ = "0.1.0"
