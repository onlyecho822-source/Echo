"""
Core Module - Formal Verification and Alignment Invariants
==========================================================

This module contains the foundational components for ensuring provable safety:
- Alignment invariants that encode non-negotiable constraints
- Formal verification interfaces for proof-carrying code
- Sandboxed execution environments for self-modification
"""

from .alignment_invariants import AlignmentInvariants
from .formal_verifier import FormalVerifier
from .sandbox import SandboxEnvironment

__all__ = ['AlignmentInvariants', 'FormalVerifier', 'SandboxEnvironment']
