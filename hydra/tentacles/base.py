"""
Base Tentacle Class
===================

The foundation for all Hydra tentacles. Like an octopus tentacle,
each is semi-autonomous but coordinated by the brain.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

from ..config import TentacleMode, AIModelConfig


class TentacleCapability(Enum):
    """Capabilities that tentacles can have"""
    # Analysis
    CODE_ANALYSIS = "code_analysis"
    NETWORK_ANALYSIS = "network_analysis"
    LOG_ANALYSIS = "log_analysis"
    MALWARE_ANALYSIS = "malware_analysis"
    MEMORY_ANALYSIS = "memory_analysis"

    # Reconnaissance
    OSINT = "osint"
    PORT_SCAN = "port_scan"
    SERVICE_ENUM = "service_enum"
    DNS_ENUM = "dns_enum"
    WEB_RECON = "web_recon"

    # Vulnerability
    VULN_SCAN = "vuln_scan"
    CVE_LOOKUP = "cve_lookup"
    EXPLOIT_DEV = "exploit_dev"

    # Forensics
    DISK_FORENSICS = "disk_forensics"
    MEMORY_FORENSICS = "memory_forensics"
    NETWORK_FORENSICS = "network_forensics"
    TIMELINE_ANALYSIS = "timeline_analysis"

    # Audit
    CONFIG_AUDIT = "config_audit"
    COMPLIANCE_CHECK = "compliance_check"
    POLICY_ANALYSIS = "policy_analysis"

    # AI-specific
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    MULTIMODAL = "multimodal"

    # General
    REPORT_GENERATION = "report_generation"
    DATA_CORRELATION = "data_correlation"


@dataclass
class TentacleStats:
    """Runtime statistics for a tentacle"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_tokens: int = 0
    avg_response_time: float = 0.0
    last_active: Optional[datetime] = None
    error_log: List[str] = field(default_factory=list)


class Tentacle(ABC):
    """
    Abstract base class for all Hydra tentacles.

    Each tentacle:
    - Has specific capabilities
    - Can operate in different modes
    - Maintains its own statistics
    - Executes tasks autonomously
    """

    def __init__(
        self,
        tentacle_id: str,
        name: str,
        capabilities: Set[TentacleCapability],
        model_config: Optional[AIModelConfig] = None
    ):
        self.tentacle_id = tentacle_id
        self.name = name
        self.capabilities = capabilities
        self.model_config = model_config

        self.mode = TentacleMode.PASSIVE
        self.stats = TentacleStats()
        self.logger = logging.getLogger(f"hydra.tentacle.{tentacle_id}")

        # Internal state
        self._initialized = False
        self._client: Any = None
        self._lock = asyncio.Lock()

    @property
    def specialization(self) -> str:
        """Get the tentacle's primary specialization"""
        if self.model_config:
            return self.model_config.specialization
        # Return most common capability as specialization
        return list(self.capabilities)[0].value if self.capabilities else "general"

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.stats.tasks_completed + self.stats.tasks_failed
        if total == 0:
            return 1.0
        return self.stats.tasks_completed / total

    async def initialize(self) -> None:
        """Initialize the tentacle (e.g., connect to API)"""
        if self._initialized:
            return

        try:
            await self._setup_client()
            self._initialized = True
            self.logger.info(f"Tentacle {self.name} initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown the tentacle gracefully"""
        if not self._initialized:
            return

        try:
            await self._cleanup_client()
            self._initialized = False
            self.logger.info(f"Tentacle {self.name} shutdown")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    async def set_mode(self, mode: TentacleMode) -> None:
        """Set the operating mode"""
        old_mode = self.mode
        self.mode = mode
        self.logger.info(f"Mode changed: {old_mode} -> {mode}")

    async def execute(self, task: Any) -> Dict[str, Any]:
        """
        Execute a task.

        This is the main method called by the brain.
        """
        if not self._initialized:
            raise RuntimeError(f"Tentacle {self.name} not initialized")

        if self.mode == TentacleMode.DORMANT:
            raise RuntimeError(f"Tentacle {self.name} is dormant")

        async with self._lock:
            start_time = asyncio.get_event_loop().time()

            try:
                # Perform the actual work
                result = await self._process(task)

                # Update stats
                execution_time = asyncio.get_event_loop().time() - start_time
                self.stats.tasks_completed += 1
                self.stats.last_active = datetime.utcnow()

                # Update average response time
                total_tasks = self.stats.tasks_completed
                self.stats.avg_response_time = (
                    (self.stats.avg_response_time * (total_tasks - 1) + execution_time)
                    / total_tasks
                )

                if isinstance(result, dict) and "tokens_used" in result:
                    self.stats.total_tokens += result["tokens_used"]

                return result

            except Exception as e:
                self.stats.tasks_failed += 1
                self.stats.error_log.append(str(e))
                self.logger.error(f"Task execution failed: {e}")
                raise

    @abstractmethod
    async def _setup_client(self) -> None:
        """Setup the client/connection (implement in subclass)"""
        pass

    @abstractmethod
    async def _cleanup_client(self) -> None:
        """Cleanup the client/connection (implement in subclass)"""
        pass

    @abstractmethod
    async def _process(self, task: Any) -> Dict[str, Any]:
        """Process a task (implement in subclass)"""
        pass

    def can_handle(self, task_type: str) -> bool:
        """Check if this tentacle can handle a task type"""
        try:
            cap = TentacleCapability(task_type)
            return cap in self.capabilities
        except ValueError:
            return False

    def get_info(self) -> Dict[str, Any]:
        """Get tentacle information"""
        return {
            "id": self.tentacle_id,
            "name": self.name,
            "mode": self.mode.value,
            "capabilities": [c.value for c in self.capabilities],
            "specialization": self.specialization,
            "initialized": self._initialized,
            "stats": {
                "tasks_completed": self.stats.tasks_completed,
                "tasks_failed": self.stats.tasks_failed,
                "success_rate": self.success_rate,
                "avg_response_time": self.stats.avg_response_time,
                "total_tokens": self.stats.total_tokens,
            }
        }
