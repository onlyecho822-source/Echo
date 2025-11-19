"""
Echo Council - Multi-Agent Cognitive Engine

The Council orchestrates multiple specialized agents:
- Scout: Opportunity detection
- Builder: Solution creation
- Auditor: Legal/ethics checking
- Navigator: Strategic planning
- Devil: Risk/anomaly detection
- Mapper: Pattern recognition
- Judge: Final arbitration
"""

from .orchestrator import EchoCouncil
from .base_agent import BaseAgent, AgentResponse

__all__ = ['EchoCouncil', 'BaseAgent', 'AgentResponse']
