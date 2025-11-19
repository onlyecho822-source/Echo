"""
Navigator Agent - Strategy and Planning

Provides strategic direction and long-term planning.
"""

from typing import Any, Dict, List
from ..base_agent import BaseAgent, AgentResponse, AgentPriority


class NavigatorAgent(BaseAgent):
    """
    Navigator Agent for strategic planning and direction.

    Responsibilities:
    - Long-term strategic planning
    - Goal alignment and prioritization
    - Resource allocation
    - Decision framework
    """

    def __init__(self):
        super().__init__(
            name="navigator",
            description="Strategic planning and direction"
        )
        self._keywords = [
            'strategy', 'plan', 'goal', 'objective', 'priority',
            'long-term', 'future', 'direction', 'roadmap', 'vision',
            'allocate', 'decide', 'choose', 'trade-off'
        ]

    def can_handle(self, query: str) -> float:
        """Evaluate query relevance to strategic planning."""
        query_lower = query.lower()
        matches = sum(1 for kw in self._keywords if kw in query_lower)
        return min(matches / 3, 1.0)

    def analyze(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Provide strategic analysis.

        Args:
            query: Strategic question or planning need
            context: Additional context including goals

        Returns:
            AgentResponse with strategic recommendation
        """
        strategy = {
            'query': query,
            'alignment_score': 0.0,
            'priorities': [],
            'trade_offs': [],
            'recommendation': ''
        }

        # Analyze goal alignment
        user_goals = context.get('goals', [])
        if user_goals:
            alignment = self._calculate_alignment(query, user_goals)
            strategy['alignment_score'] = alignment
        else:
            strategy['alignment_score'] = 0.5  # Neutral if no goals defined

        # Generate priorities
        strategy['priorities'] = self._generate_priorities(query, context)

        # Identify trade-offs
        strategy['trade_offs'] = self._identify_trade_offs(query, context)

        # Generate recommendation
        if strategy['alignment_score'] >= 0.7:
            strategy['recommendation'] = 'Strongly aligned with goals - proceed'
            priority = AgentPriority.HIGH
        elif strategy['alignment_score'] >= 0.4:
            strategy['recommendation'] = 'Partially aligned - consider trade-offs'
            priority = AgentPriority.MEDIUM
        else:
            strategy['recommendation'] = 'Low alignment - reconsider approach'
            priority = AgentPriority.LOW

        recommendations = []
        if strategy['trade_offs']:
            recommendations.append(
                f"Consider {len(strategy['trade_offs'])} identified trade-offs before proceeding"
            )

        return AgentResponse(
            agent_name=self.name,
            success=True,
            message=f"Strategic alignment: {strategy['alignment_score']:.0%}",
            data={'strategy': strategy},
            priority=priority,
            confidence=0.7,
            recommendations=recommendations
        )

    def _calculate_alignment(self, query: str, goals: List[str]) -> float:
        """Calculate alignment between query and user goals."""
        if not goals:
            return 0.5

        query_words = set(query.lower().split())
        total_alignment = 0

        for goal in goals:
            goal_words = set(goal.lower().split())
            overlap = len(query_words & goal_words)
            if overlap > 0:
                total_alignment += overlap / len(goal_words)

        return min(total_alignment / len(goals), 1.0)

    def _generate_priorities(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate priority list for the query."""
        priorities = []

        # Default priorities based on common patterns
        if 'urgent' in query.lower() or 'asap' in query.lower():
            priorities.append({
                'item': 'Time sensitivity',
                'level': 'high',
                'reason': 'Urgency indicated in request'
            })

        if context.get('financial_involved'):
            priorities.append({
                'item': 'Financial accuracy',
                'level': 'high',
                'reason': 'Financial decisions require precision'
            })

        priorities.append({
            'item': 'Goal alignment',
            'level': 'medium',
            'reason': 'Ensure actions support long-term objectives'
        })

        return priorities

    def _identify_trade_offs(self, query: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify potential trade-offs."""
        trade_offs = []

        # Common trade-offs
        if 'fast' in query.lower() or 'quick' in query.lower():
            trade_offs.append({
                'factor_a': 'Speed',
                'factor_b': 'Quality',
                'note': 'Faster execution may reduce thoroughness'
            })

        if 'cheap' in query.lower() or 'budget' in query.lower():
            trade_offs.append({
                'factor_a': 'Cost',
                'factor_b': 'Features',
                'note': 'Lower cost may limit capabilities'
            })

        return trade_offs
