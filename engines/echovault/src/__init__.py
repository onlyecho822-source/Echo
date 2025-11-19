"""
EchoVault - Secure Identity and State Management

Provides cryptographic identity verification, secure key management,
and trusted state transitions for Echo Nexus.
"""

from .vault import EchoVault
from .identity import Identity
from .state import StateManager, StateLock

__all__ = [
    "EchoVault",
    "Identity",
    "StateManager",
    "StateLock",
]

__version__ = "0.1.0"
