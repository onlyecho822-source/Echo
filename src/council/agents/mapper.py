"""
Mapper Agent - Pattern Recognition and Resonance

Identifies patterns, connections, and human-integration points.
"""

from typing import Any, Dict, List
from ..base_agent import BaseAgent, AgentResponse, AgentPriority


class MapperAgent(BaseAgent):
    """
    Mapper Agent for pattern recognition and integration.

    Responsibilities:
    - Identify patterns in data and behavior
    - Find connections between concepts
    - Map user preferences and habits
    - Optimize for human integration
    """

    def __init__(self):
        super().__init__(
            name="mapper",
            description="Pattern recognition and human integration"
        )
        self._keywords = [
            'pattern', 'trend', 'habit', 'routine', 'connection',
            'similar', 'relate', 'link', 'correlate', 'behavior',
            'preference', 'style', 'like', 'dislike'
        ]

    def can_handle(self, query: str) -> float:
        """Evaluate query relevance to pattern mapping."""
        query_lower = query.lower()
        matches = sum(1 for kw in self._keywords if kw in query_lower)
        return min(matches / 3, 1.0)

    def analyze(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Analyze for patterns and connections.

        Args:
            query: Query to analyze
            context: Historical and preference data

        Returns:
            AgentResponse with pattern analysis
        """
        patterns = []
        connections = []
        recommendations = []

        # Analyze behavioral patterns
        if 'history' in context:
            patterns.extend(self._find_behavioral_patterns(context['history']))

        # Find preference patterns
        if 'preferences' in context:
            patterns.extend(self._find_preference_patterns(context['preferences']))

        # Identify connections
        connections = self._find_connections(query, context)

        # Generate personalization recommendations
        if patterns:
            recommendations.extend(
                self._generate_personalization_suggestions(patterns)
            )

        return AgentResponse(
            agent_name=self.name,
            success=True,
            message=f"Found {len(patterns)} patterns and {len(connections)} connections",
            data={
                'patterns': patterns,
                'connections': connections,
                'user_profile': self._build_user_profile(patterns)
            },
            priority=AgentPriority.MEDIUM,
            confidence=0.65,
            recommendations=recommendations
        )

    def _find_behavioral_patterns(self, history: List[Dict]) -> List[Dict[str, Any]]:
        """Identify patterns in user behavior history."""
        patterns = []

        if not history:
            return patterns

        # Time-based patterns
        time_counts = {}
        for event in history:
            if 'timestamp' in event:
                # Extract hour (simplified)
                hour = event.get('hour', 12)
                time_counts[hour] = time_counts.get(hour, 0) + 1

        if time_counts:
            peak_hour = max(time_counts, key=time_counts.get)
            patterns.append({
                'type': 'temporal',
                'description': f'Peak activity at hour {peak_hour}',
                'confidence': 0.7,
                'data': {'peak_hour': peak_hour}
            })

        # Action patterns
        action_counts = {}
        for event in history:
            action = event.get('action', 'unknown')
            action_counts[action] = action_counts.get(action, 0) + 1

        if action_counts:
            common_action = max(action_counts, key=action_counts.get)
            patterns.append({
                'type': 'behavioral',
                'description': f'Most common action: {common_action}',
                'confidence': 0.75,
                'data': {'action': common_action, 'count': action_counts[common_action]}
            })

        return patterns

    def _find_preference_patterns(self, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify patterns in user preferences."""
        patterns = []

        # Communication preference
        if preferences.get('notification_style'):
            patterns.append({
                'type': 'preference',
                'description': f"Communication style: {preferences['notification_style']}",
                'confidence': 0.9,
                'data': {'category': 'communication'}
            })

        return patterns

    def _find_connections(self, query: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Find connections between current query and existing data."""
        connections = []

        query_words = set(query.lower().split())

        # Check connections to goals
        for goal in context.get('goals', []):
            goal_words = set(goal.lower().split())
            overlap = query_words & goal_words
            if overlap:
                connections.append({
                    'type': 'goal_alignment',
                    'target': goal,
                    'matching_concepts': list(overlap)
                })

        # Check connections to past events
        for event in context.get('history', [])[-10:]:  # Last 10 events
            if any(word in str(event).lower() for word in query_words):
                connections.append({
                    'type': 'historical_relation',
                    'target': event.get('description', 'past event'),
                    'matching_concepts': []
                })

        return connections

    def _generate_personalization_suggestions(self, patterns: List[Dict]) -> List[str]:
        """Generate suggestions based on identified patterns."""
        suggestions = []

        for pattern in patterns:
            if pattern['type'] == 'temporal':
                hour = pattern['data'].get('peak_hour')
                suggestions.append(
                    f"Schedule important tasks around your peak hour ({hour}:00)"
                )
            elif pattern['type'] == 'behavioral':
                action = pattern['data'].get('action')
                suggestions.append(
                    f"Consider creating shortcuts for frequent action: {action}"
                )

        return suggestions

    def _build_user_profile(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Build a user profile from patterns."""
        profile = {
            'traits': [],
            'preferences': {},
            'habits': []
        }

        for pattern in patterns:
            if pattern['type'] == 'behavioral':
                profile['habits'].append(pattern['description'])
            elif pattern['type'] == 'preference':
                profile['preferences'][pattern['data'].get('category', 'general')] = \
                    pattern['description']

        return profile
