"""
Dormant Disruption - Latent Pattern Activation System

Manage and activate dormant patterns when conditions are right.
"""

from .disruption import DormantDisruption
from .pattern import Pattern
from .trigger import Trigger, TriggerSet
from .activation import ActivationController

__all__ = [
    "DormantDisruption",
    "Pattern",
    "Trigger",
    "TriggerSet",
    "ActivationController",
]

__version__ = "0.1.0"
