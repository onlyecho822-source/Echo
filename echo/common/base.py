"""Base agent class for all Echo agents."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from echo.common.logger import get_logger


class BaseAgent(ABC):
    """Abstract base class for Echo agents."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.agent_id = str(uuid.uuid4())
        self.config = config or {}
        self.logger = get_logger(name)
        self.state = {
            "status": "initialized",
            "last_run": None,
            "run_count": 0,
            "errors": [],
            "metrics": {}
        }
        self.created_at = datetime.utcnow()

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """Execute the agent's primary function."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Return current agent status and metrics."""
        pass

    def update_state(self, key: str, value: Any) -> None:
        """Update agent state."""
        self.state[key] = value
        self.state["last_modified"] = datetime.utcnow().isoformat()

    def log_error(self, error: str) -> None:
        """Log an error to agent state."""
        self.state["errors"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": error
        })
        self.logger.error(error)

    def record_metric(self, metric_name: str, value: Any) -> None:
        """Record a metric value."""
        if metric_name not in self.state["metrics"]:
            self.state["metrics"][metric_name] = []
        self.state["metrics"][metric_name].append({
            "timestamp": datetime.utcnow().isoformat(),
            "value": value
        })

    def prepare_run(self) -> None:
        """Prepare agent for execution."""
        self.state["status"] = "running"
        self.state["last_run"] = datetime.utcnow().isoformat()
        self.state["run_count"] += 1

    def complete_run(self, success: bool = True) -> None:
        """Mark run as complete."""
        self.state["status"] = "completed" if success else "failed"
