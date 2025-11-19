"""
Auditor Agent - Legal, Safety, and Compliance

Checks actions for legal compliance and safety concerns.
"""

from typing import Any, Dict, List
from ..base_agent import BaseAgent, AgentResponse, AgentPriority


class AuditorAgent(BaseAgent):
    """
    Auditor Agent for legal and safety compliance.

    Responsibilities:
    - Check legal compliance
    - Identify safety concerns
    - Verify ethical boundaries
    - Flag regulatory issues
    """

    def __init__(self):
        super().__init__(
            name="auditor",
            description="Legal, safety, and compliance checking"
        )
        self._keywords = [
            'legal', 'law', 'compliance', 'safe', 'risk',
            'ethical', 'privacy', 'regulation', 'policy',
            'permission', 'consent', 'license'
        ]

        # Actions that require extra scrutiny
        self._sensitive_actions = [
            'delete', 'remove', 'transfer', 'send', 'share',
            'access', 'modify', 'financial', 'personal', 'private'
        ]

        # Prohibited actions
        self._prohibited = [
            'malware', 'hack', 'exploit', 'unauthorized',
            'impersonate', 'steal', 'fraud'
        ]

    def can_handle(self, query: str) -> float:
        """Evaluate query relevance to compliance checking."""
        query_lower = query.lower()

        # High relevance for prohibited terms
        if any(term in query_lower for term in self._prohibited):
            return 1.0

        # Medium relevance for sensitive actions
        if any(term in query_lower for term in self._sensitive_actions):
            return 0.8

        matches = sum(1 for kw in self._keywords if kw in query_lower)
        return min(matches / 3, 1.0)

    def analyze(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Audit query for compliance and safety.

        Args:
            query: Action or query to audit
            context: Additional context

        Returns:
            AgentResponse with compliance assessment
        """
        issues = []
        warnings = []
        recommendations = []

        query_lower = query.lower()

        # Check for prohibited actions
        for term in self._prohibited:
            if term in query_lower:
                issues.append({
                    'type': 'prohibited',
                    'severity': 'critical',
                    'description': f"Prohibited action detected: {term}",
                    'recommendation': 'This action cannot be performed'
                })

        # Check for sensitive actions requiring review
        for action in self._sensitive_actions:
            if action in query_lower:
                warnings.append(
                    f"Sensitive action '{action}' detected - requires explicit consent"
                )

        # Privacy check
        if 'personal' in query_lower or 'private' in query_lower:
            recommendations.append(
                'Ensure user has consented to personal data processing'
            )

        # Financial check
        if 'financial' in query_lower or 'money' in query_lower:
            recommendations.append(
                'Financial actions should be logged and reversible'
            )
            if context.get('amount', 0) > 1000:
                warnings.append(
                    'Large financial transaction - recommend additional verification'
                )

        # Determine overall compliance status
        if issues:
            compliance_status = 'blocked'
            priority = AgentPriority.CRITICAL
            confidence = 1.0
        elif warnings:
            compliance_status = 'review_required'
            priority = AgentPriority.HIGH
            confidence = 0.85
        else:
            compliance_status = 'approved'
            priority = AgentPriority.LOW
            confidence = 0.9

        return AgentResponse(
            agent_name=self.name,
            success=len(issues) == 0,
            message=f"Compliance status: {compliance_status}",
            data={
                'status': compliance_status,
                'issues': issues,
                'sensitive_actions_detected': [
                    a for a in self._sensitive_actions if a in query_lower
                ]
            },
            priority=priority,
            confidence=confidence,
            recommendations=recommendations,
            warnings=warnings
        )
