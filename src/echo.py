"""
Echo Life OS - Main Entry Point

A persistent, portable, personal intelligence layer.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from .memory_kernel import MemoryKernel
from .council import EchoCouncil
from .security import DefenseWall
from .financial import FinancialEngine


class EchoLifeOS:
    """
    Main orchestrator for Echo Life OS.

    Integrates all subsystems:
    - Memory Kernel (encrypted storage)
    - Echo Council (multi-agent reasoning)
    - Defense Wall (security)
    - Financial Engine (financial management)
    """

    def __init__(self, data_dir: Optional[str] = None, master_password: Optional[str] = None):
        """
        Initialize Echo Life OS.

        Args:
            data_dir: Directory for data storage (default: ~/.echo)
            master_password: Master password for encryption
        """
        if data_dir is None:
            data_dir = os.path.expanduser('~/.echo')

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize subsystems
        self._master_password = master_password
        self._memory: Optional[MemoryKernel] = None
        self._council: Optional[EchoCouncil] = None
        self._security: Optional[DefenseWall] = None
        self._financial: Optional[FinancialEngine] = None

        self._initialized = False

    def initialize(self, password: Optional[str] = None):
        """
        Initialize all subsystems.

        Args:
            password: Master password (uses stored if not provided)
        """
        if password:
            self._master_password = password

        if not self._master_password:
            raise ValueError("Master password required for initialization")

        # Initialize Memory Kernel
        db_path = self.data_dir / 'memory.db'
        self._memory = MemoryKernel(str(db_path), self._master_password)

        # Initialize other subsystems with memory kernel
        self._council = EchoCouncil(self._memory)
        self._security = DefenseWall(self._memory)
        self._financial = FinancialEngine(self._memory)

        self._initialized = True

    @property
    def memory(self) -> MemoryKernel:
        """Get Memory Kernel instance."""
        if not self._initialized:
            raise RuntimeError("Echo Life OS not initialized. Call initialize() first.")
        return self._memory

    @property
    def council(self) -> EchoCouncil:
        """Get Echo Council instance."""
        if not self._initialized:
            raise RuntimeError("Echo Life OS not initialized. Call initialize() first.")
        return self._council

    @property
    def security(self) -> DefenseWall:
        """Get Defense Wall instance."""
        if not self._initialized:
            raise RuntimeError("Echo Life OS not initialized. Call initialize() first.")
        return self._security

    @property
    def financial(self) -> FinancialEngine:
        """Get Financial Engine instance."""
        if not self._initialized:
            raise RuntimeError("Echo Life OS not initialized. Call initialize() first.")
        return self._financial

    def query(self, question: str, context: Optional[dict] = None) -> dict:
        """
        Submit a query to the Echo Council.

        Args:
            question: Query or task
            context: Additional context

        Returns:
            Council response with recommendations
        """
        if not self._initialized:
            raise RuntimeError("Echo Life OS not initialized")

        # Security check
        security_check = self._security.check_action(question, context)
        if not security_check['allowed']:
            return {
                'success': False,
                'blocked': True,
                'reason': security_check['threats']
            }

        # Consult council
        result = self._council.consult(question, context)

        # Log to memory
        self._memory.log_event('query', {
            'question': question,
            'result': result.get('judgment', {}).get('data', {}).get('judgment', {}).get('decision')
        })

        return result

    def quick_action(self, action: str) -> bool:
        """
        Perform a quick security-checked action.

        Args:
            action: Action to perform

        Returns:
            True if action is allowed
        """
        return self._security.check_action(action)['allowed']

    def get_status(self) -> dict:
        """Get overall system status."""
        if not self._initialized:
            return {'initialized': False}

        return {
            'initialized': True,
            'data_dir': str(self.data_dir),
            'council': self._council.get_status(),
            'security': self._security.get_status(),
            'financial': self._financial.get_financial_health()
        }

    def close(self):
        """Shutdown and cleanup."""
        if self._council:
            self._council.close()
        if self._financial:
            self._financial.close()
        if self._memory:
            self._memory.close()

        self._initialized = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_echo(data_dir: Optional[str] = None, password: Optional[str] = None) -> EchoLifeOS:
    """
    Factory function to create and initialize Echo Life OS.

    Args:
        data_dir: Optional data directory
        password: Master password

    Returns:
        Initialized EchoLifeOS instance
    """
    echo = EchoLifeOS(data_dir)
    if password:
        echo.initialize(password)
    return echo
