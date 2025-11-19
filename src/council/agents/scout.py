"""
Scout Agent - Opportunity Detection

Identifies opportunities, trends, and potential benefits.
"""

from typing import Any, Dict
from ..base_agent import BaseAgent, AgentResponse, AgentPriority


class ScoutAgent(BaseAgent):
    """
    Scout Agent for opportunity detection and trend analysis.

    Responsibilities:
    - Identify opportunities in data
    - Detect emerging trends
    - Find potential benefits and advantages
    - Monitor for favorable conditions
    """

    def __init__(self):
        super().__init__(
            name="scout",
            description="Opportunity detection and trend analysis"
        )
        self._keywords = [
            'opportunity', 'find', 'search', 'discover', 'trend',
            'potential', 'benefit', 'advantage', 'growth', 'improve',
            'optimize', 'best', 'recommend', 'suggest'
        ]

    def can_handle(self, query: str) -> float:
        """Evaluate query relevance to opportunity detection."""
        query_lower = query.lower()
        matches = sum(1 for kw in self._keywords if kw in query_lower)
        return min(matches / 3, 1.0)

    def analyze(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Analyze query for opportunities.

        Args:
            query: Query to analyze
            context: Additional context

        Returns:
            AgentResponse with identified opportunities
        """
        opportunities = []
        recommendations = []

        # Analyze context for opportunities
        if 'financial' in context:
            financial = context['financial']
            if financial.get('savings_rate', 0) < 0.2:
                opportunities.append({
                    'type': 'financial',
                    'description': 'Savings rate below 20% - optimization potential',
                    'potential_impact': 'medium'
                })
                recommendations.append(
                    'Consider automating transfers to savings account'
                )

        if 'schedule' in context:
            schedule = context['schedule']
            if schedule.get('free_blocks', 0) > 5:
                opportunities.append({
                    'type': 'time',
                    'description': f"{schedule['free_blocks']} free time blocks available",
                    'potential_impact': 'low'
                })

        # Default opportunity analysis
        if not opportunities:
            opportunities.append({
                'type': 'general',
                'description': 'Baseline analysis complete - monitoring for opportunities',
                'potential_impact': 'info'
            })

        return AgentResponse(
            agent_name=self.name,
            success=True,
            message=f"Identified {len(opportunities)} potential opportunity/opportunities",
            data={'opportunities': opportunities},
            priority=AgentPriority.MEDIUM,
            confidence=0.7,
            recommendations=recommendations
        )
