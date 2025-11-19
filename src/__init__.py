"""
Echo Life OS
============
Persistent, personal digital intelligence system.

A system-of-systems that lives across devices, cloud, local systems, and identity.
"""

__version__ = "0.1.0"
__author__ = "Nathan Poinsette"

from src.core.memory_kernel import MemoryKernel, Memory, MemoryType, MemoryPriority
from src.agents.council import EchoCouncil, EthicsMode
from src.security.defense_wall import DefenseWall
from src.financial.financial_os import FinancialOS

__all__ = [
    "MemoryKernel",
    "Memory",
    "MemoryType",
    "MemoryPriority",
    "EchoCouncil",
    "EthicsMode",
    "DefenseWall",
    "FinancialOS",
]
