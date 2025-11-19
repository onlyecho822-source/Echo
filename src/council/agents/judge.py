"""
Judge Agent - Final Arbitration

Makes final decisions based on all agent inputs.
"""

from typing import Any, Dict, List
from ..base_agent import BaseAgent, AgentResponse, AgentPriority


class JudgeAgent(BaseAgent):
    """
    Judge Agent for final arbitration and decision making.

    Responsibilities:
    - Synthesize inputs from all agents
    - Resolve conflicts between agents
    - Make final recommendations
    - Ensure balanced decision-making
    """

    def __init__(self):
        super().__init__(
            name="judge",
            description="Final arbitration and decision synthesis"
        )
        self._keywords = [
            'decide', 'choose', 'final', 'verdict', 'conclusion',
            'judgment', 'resolve', 'arbitrate', 'determine'
        ]

        # Agent weight for decision-making
        self._agent_weights = {
            'auditor': 1.5,    # Compliance is critical
            'devil': 1.3,      # Risk awareness important
            'navigator': 1.0,  # Strategic balance
            'scout': 0.8,      # Opportunities considered
            'builder': 0.8,    # Solutions valued
            'mapper': 0.7      # Patterns inform decisions
        }

    def can_handle(self, query: str) -> float:
        """Evaluate query relevance to arbitration."""
        query_lower = query.lower()
        matches = sum(1 for kw in self._keywords if kw in query_lower)
        return min(matches / 3, 1.0)

    def analyze(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Make final judgment based on agent inputs.

        Args:
            query: Question requiring judgment
            context: Should contain 'agent_responses' from other agents

        Returns:
            AgentResponse with final judgment
        """
        agent_responses = context.get('agent_responses', [])

        judgment = {
            'decision': 'proceed',  # proceed, caution, block
            'confidence': 0.0,
            'reasoning': [],
            'dissenting_views': [],
            'action_items': []
        }

        # No other agent input - make independent judgment
        if not agent_responses:
            judgment['decision'] = 'proceed'
            judgment['confidence'] = 0.5
            judgment['reasoning'].append(
                'No agent consensus available - defaulting to cautious proceed'
            )
            return AgentResponse(
                agent_name=self.name,
                success=True,
                message=f"Judgment: {judgment['decision']} (confidence: {judgment['confidence']:.0%})",
                data={'judgment': judgment},
                priority=AgentPriority.HIGH,
                confidence=judgment['confidence']
            )

        # Synthesize all agent responses
        judgment = self._synthesize_responses(agent_responses, judgment)

        # Generate action items
        judgment['action_items'] = self._generate_action_items(
            judgment, agent_responses
        )

        warnings = []
        if judgment['decision'] == 'block':
            warnings.append('Action blocked due to critical concerns')
        elif judgment['dissenting_views']:
            warnings.append(
                f"{len(judgment['dissenting_views'])} agent(s) raised concerns"
            )

        return AgentResponse(
            agent_name=self.name,
            success=judgment['decision'] != 'block',
            message=f"Judgment: {judgment['decision']} (confidence: {judgment['confidence']:.0%})",
            data={'judgment': judgment},
            priority=AgentPriority.HIGH,
            confidence=judgment['confidence'],
            warnings=warnings,
            recommendations=judgment['action_items']
        )

    def _synthesize_responses(self, responses: List[AgentResponse],
                               judgment: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize multiple agent responses into a judgment."""
        proceed_score = 0.0
        caution_score = 0.0
        block_score = 0.0

        for response in responses:
            agent_name = response.agent_name
            weight = self._agent_weights.get(agent_name, 1.0)

            # Interpret response
            if not response.success:
                block_score += weight * response.confidence
                judgment['dissenting_views'].append({
                    'agent': agent_name,
                    'concern': response.message
                })
            elif response.warnings:
                caution_score += weight * response.confidence * 0.5
                judgment['reasoning'].append(
                    f"{agent_name}: {response.message} (with warnings)"
                )
            else:
                proceed_score += weight * response.confidence
                judgment['reasoning'].append(
                    f"{agent_name}: {response.message}"
                )

        # Determine final decision
        total_score = proceed_score + caution_score + block_score
        if total_score == 0:
            total_score = 1  # Avoid division by zero

        if block_score / total_score > 0.4:
            judgment['decision'] = 'block'
            judgment['confidence'] = block_score / total_score
        elif caution_score / total_score > 0.3:
            judgment['decision'] = 'caution'
            judgment['confidence'] = 1 - (caution_score / total_score)
        else:
            judgment['decision'] = 'proceed'
            judgment['confidence'] = proceed_score / total_score

        return judgment

    def _generate_action_items(self, judgment: Dict[str, Any],
                                responses: List[AgentResponse]) -> List[str]:
        """Generate action items from judgment."""
        items = []

        if judgment['decision'] == 'block':
            items.append('Resolve blocking issues before proceeding')

        if judgment['decision'] == 'caution':
            items.append('Review warnings and confirm intent before proceeding')

        # Collect recommendations from all agents
        for response in responses:
            for rec in response.recommendations[:2]:  # Top 2 from each
                if rec not in items:
                    items.append(rec)

        return items[:5]  # Limit to 5 action items
