"""
Echo Council Orchestrator

Coordinates multiple specialized agents to process queries and make decisions.
"""

import asyncio
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from .base_agent import BaseAgent, AgentResponse, AgentPriority
from .agents import (
    ScoutAgent, BuilderAgent, AuditorAgent, NavigatorAgent,
    DevilAgent, MapperAgent, JudgeAgent
)


class EchoCouncil:
    """
    Multi-agent orchestrator for the Echo Life OS.

    The Council coordinates specialized agents to:
    - Analyze queries from multiple perspectives
    - Synthesize recommendations
    - Make balanced decisions
    - Learn from outcomes
    """

    def __init__(self, memory_kernel=None):
        """
        Initialize the Echo Council.

        Args:
            memory_kernel: Optional MemoryKernel for persistent context
        """
        self.memory_kernel = memory_kernel
        self._agents: Dict[str, BaseAgent] = {}
        self._executor = ThreadPoolExecutor(max_workers=7)

        # Initialize all agents
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all council agents."""
        agents = [
            ScoutAgent(),
            BuilderAgent(),
            AuditorAgent(),
            NavigatorAgent(),
            DevilAgent(),
            MapperAgent(),
            JudgeAgent()
        ]

        for agent in agents:
            self._agents[agent.name] = agent

        # Load saved context if memory kernel available
        if self.memory_kernel:
            for name, agent in self._agents.items():
                context = self.memory_kernel.load_agent_context(name)
                if context:
                    agent.set_context(context)

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """List all available agents."""
        return list(self._agents.keys())

    def consult(self, query: str, context: Optional[Dict[str, Any]] = None,
                agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Consult the council on a query.

        Args:
            query: The query or task to analyze
            context: Additional context for analysis
            agents: Specific agents to consult (None = auto-select)

        Returns:
            Dictionary with all agent responses and final judgment
        """
        if context is None:
            context = {}

        # Select agents to consult
        if agents:
            selected_agents = [
                self._agents[name] for name in agents
                if name in self._agents and self._agents[name].is_enabled
            ]
        else:
            selected_agents = self._select_agents(query)

        # Collect responses from all selected agents (except judge)
        responses = []
        for agent in selected_agents:
            if agent.name != 'judge':
                response = agent.analyze(query, context)
                responses.append(response)

        # Get final judgment
        judge = self._agents.get('judge')
        judgment_context = context.copy()
        judgment_context['agent_responses'] = responses

        if judge and judge.is_enabled:
            judgment = judge.analyze(query, judgment_context)
        else:
            judgment = self._default_judgment(responses)

        # Log to memory kernel if available
        if self.memory_kernel:
            self.memory_kernel.log_event(
                'council_consultation',
                {
                    'query': query,
                    'agents_consulted': [r.agent_name for r in responses],
                    'decision': judgment.data.get('judgment', {}).get('decision')
                },
                agent='council'
            )

        return {
            'query': query,
            'responses': [r.to_dict() for r in responses],
            'judgment': judgment.to_dict(),
            'success': judgment.success
        }

    def _select_agents(self, query: str) -> List[BaseAgent]:
        """
        Auto-select relevant agents based on query.

        Args:
            query: The query to analyze

        Returns:
            List of selected agents
        """
        scored_agents = []

        for agent in self._agents.values():
            if agent.is_enabled and agent.name != 'judge':
                score = agent.can_handle(query)
                scored_agents.append((agent, score))

        # Sort by score and select top agents
        scored_agents.sort(key=lambda x: x[1], reverse=True)

        # Always include auditor and devil for safety
        selected = []
        must_include = {'auditor', 'devil'}

        for agent, score in scored_agents:
            if agent.name in must_include:
                selected.append(agent)
                must_include.discard(agent.name)
            elif score > 0.3:  # Threshold for relevance
                selected.append(agent)

        # Add any remaining must-include agents
        for name in must_include:
            if name in self._agents:
                selected.append(self._agents[name])

        # Always add judge at the end
        if 'judge' in self._agents:
            selected.append(self._agents['judge'])

        return selected

    def _default_judgment(self, responses: List[AgentResponse]) -> AgentResponse:
        """Create default judgment when judge is disabled."""
        has_failures = any(not r.success for r in responses)
        has_warnings = any(r.warnings for r in responses)

        if has_failures:
            decision = 'block'
            confidence = 0.9
        elif has_warnings:
            decision = 'caution'
            confidence = 0.7
        else:
            decision = 'proceed'
            confidence = 0.8

        return AgentResponse(
            agent_name='default_judge',
            success=decision != 'block',
            message=f"Default judgment: {decision}",
            data={
                'judgment': {
                    'decision': decision,
                    'confidence': confidence,
                    'reasoning': ['Automated judgment based on agent responses']
                }
            },
            priority=AgentPriority.HIGH,
            confidence=confidence
        )

    def quick_check(self, action: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Quick safety check for an action.

        Args:
            action: Action to check
            context: Additional context

        Returns:
            True if action is safe to proceed
        """
        if context is None:
            context = {}

        # Quick check with just auditor and devil
        auditor = self._agents.get('auditor')
        devil = self._agents.get('devil')

        if auditor:
            audit_result = auditor.analyze(action, context)
            if not audit_result.success:
                return False

        if devil:
            risk_result = devil.analyze(action, context)
            risk_score = risk_result.data.get('risk_score', 0)
            if risk_score > 0.7:
                return False

        return True

    def get_recommendations(self, query: str,
                            context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Get aggregated recommendations for a query.

        Args:
            query: Query to analyze
            context: Additional context

        Returns:
            List of recommendations
        """
        result = self.consult(query, context)
        recommendations = []

        for response in result['responses']:
            recommendations.extend(response.get('recommendations', []))

        # Add judgment recommendations
        judgment = result.get('judgment', {})
        judgment_data = judgment.get('data', {}).get('judgment', {})
        recommendations.extend(judgment_data.get('action_items', []))

        # Deduplicate while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)

        return unique_recommendations

    def save_contexts(self):
        """Save all agent contexts to memory kernel."""
        if not self.memory_kernel:
            return

        for name, agent in self._agents.items():
            context = agent.get_context()
            if context:
                self.memory_kernel.save_agent_context(name, context)

    def enable_agent(self, name: str):
        """Enable an agent."""
        if name in self._agents:
            self._agents[name].enable()

    def disable_agent(self, name: str):
        """Disable an agent."""
        if name in self._agents:
            self._agents[name].disable()

    def get_status(self) -> Dict[str, Any]:
        """Get council status."""
        return {
            'agents': {
                name: {
                    'enabled': agent.is_enabled,
                    'description': agent.description
                }
                for name, agent in self._agents.items()
            },
            'total_agents': len(self._agents),
            'enabled_agents': sum(1 for a in self._agents.values() if a.is_enabled)
        }

    def close(self):
        """Clean up resources."""
        self.save_contexts()
        self._executor.shutdown(wait=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
