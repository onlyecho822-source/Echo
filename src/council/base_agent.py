"""
Base Agent - Foundation for all Council agents

Defines the interface and common functionality for specialized agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime


class AgentPriority(Enum):
    """Priority levels for agent responses."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5


class AgentConfidence(Enum):
    """Confidence levels for agent assessments."""
    CERTAIN = 1.0
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4
    UNCERTAIN = 0.2


@dataclass
class AgentResponse:
    """Standardized response from an agent."""
    agent_name: str
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    priority: AgentPriority = AgentPriority.MEDIUM
    confidence: float = 0.8
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'agent_name': self.agent_name,
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'priority': self.priority.name,
            'confidence': self.confidence,
            'recommendations': self.recommendations,
            'warnings': self.warnings,
            'timestamp': self.timestamp
        }


class BaseAgent(ABC):
    """
    Base class for all Echo Council agents.

    Each agent specializes in a particular domain and provides
    analysis, recommendations, and actions within that domain.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize base agent.

        Args:
            name: Agent identifier
            description: Human-readable description of agent's role
        """
        self.name = name
        self.description = description
        self._context: Dict[str, Any] = {}
        self._enabled = True

    @abstractmethod
    def analyze(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Analyze a query within the agent's domain.

        Args:
            query: The query or task to analyze
            context: Additional context for analysis

        Returns:
            AgentResponse with analysis results
        """
        pass

    @abstractmethod
    def can_handle(self, query: str) -> float:
        """
        Determine how well this agent can handle a query.

        Args:
            query: The query to evaluate

        Returns:
            Score from 0.0 to 1.0 indicating capability match
        """
        pass

    def set_context(self, context: Dict[str, Any]):
        """Update agent's persistent context."""
        self._context.update(context)

    def get_context(self) -> Dict[str, Any]:
        """Get agent's current context."""
        return self._context.copy()

    def enable(self):
        """Enable the agent."""
        self._enabled = True

    def disable(self):
        """Disable the agent."""
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        """Check if agent is enabled."""
        return self._enabled

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', enabled={self._enabled})"
