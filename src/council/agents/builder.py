"""
Builder Agent - Solution Creation

Creates actionable solutions and implementations.
"""

from typing import Any, Dict, List
from ..base_agent import BaseAgent, AgentResponse, AgentPriority


class BuilderAgent(BaseAgent):
    """
    Builder Agent for solution creation and implementation.

    Responsibilities:
    - Create actionable plans
    - Design solutions to problems
    - Generate implementation steps
    - Build automated workflows
    """

    def __init__(self):
        super().__init__(
            name="builder",
            description="Solution creation and implementation"
        )
        self._keywords = [
            'create', 'build', 'make', 'implement', 'design',
            'plan', 'automate', 'setup', 'configure', 'develop',
            'solution', 'fix', 'resolve', 'construct'
        ]

    def can_handle(self, query: str) -> float:
        """Evaluate query relevance to solution building."""
        query_lower = query.lower()
        matches = sum(1 for kw in self._keywords if kw in query_lower)
        return min(matches / 3, 1.0)

    def analyze(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Create solution for query.

        Args:
            query: Problem or task to solve
            context: Additional context

        Returns:
            AgentResponse with solution plan
        """
        solution = {
            'query': query,
            'steps': [],
            'resources_needed': [],
            'estimated_time': 'unknown',
            'automation_possible': False
        }

        # Generate basic solution steps
        steps = self._generate_steps(query, context)
        solution['steps'] = steps
        solution['estimated_time'] = f"{len(steps) * 5} minutes"

        # Check for automation potential
        automation_keywords = ['automate', 'schedule', 'recurring', 'repeat']
        if any(kw in query.lower() for kw in automation_keywords):
            solution['automation_possible'] = True

        recommendations = []
        if solution['automation_possible']:
            recommendations.append(
                'This task can be automated - consider setting up a recurring workflow'
            )

        return AgentResponse(
            agent_name=self.name,
            success=True,
            message=f"Solution created with {len(steps)} steps",
            data={'solution': solution},
            priority=AgentPriority.MEDIUM,
            confidence=0.75,
            recommendations=recommendations
        )

    def _generate_steps(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate solution steps based on query."""
        steps = []

        # Basic step generation logic
        steps.append({
            'order': 1,
            'action': 'Analyze requirements',
            'description': f'Review and understand: {query[:100]}',
            'status': 'pending'
        })

        steps.append({
            'order': 2,
            'action': 'Gather resources',
            'description': 'Collect necessary information and tools',
            'status': 'pending'
        })

        steps.append({
            'order': 3,
            'action': 'Execute solution',
            'description': 'Implement the planned approach',
            'status': 'pending'
        })

        steps.append({
            'order': 4,
            'action': 'Verify results',
            'description': 'Confirm solution meets requirements',
            'status': 'pending'
        })

        return steps
