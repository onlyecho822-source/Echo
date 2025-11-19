"""
Echo Capsules - Dual-Hash Provenance Truth Units

Atomic units of verified truth with cryptographic provenance.
"""

from .capsule import Capsule
from .chain import CapsuleChain
from .store import CapsuleStore
from .verification import Verifier

__all__ = [
    "Capsule",
    "CapsuleChain",
    "CapsuleStore",
    "Verifier",
]

__version__ = "0.1.0"
