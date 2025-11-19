"""
Memory Kernel - Encrypted Persistent Personal History

The Memory Kernel provides:
- Encrypted, persistent personal history and preferences
- Local + cloud storage options
- Ownable, portable, upgradable data
"""

from .kernel import MemoryKernel
from .encryption import EncryptionEngine

__all__ = ['MemoryKernel', 'EncryptionEngine']
