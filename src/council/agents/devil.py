"""
Devil Agent - Risk and Anomaly Detection

Identifies risks, failures, and anomalies.
"""

from typing import Any, Dict, List
from ..base_agent import BaseAgent, AgentResponse, AgentPriority


class DevilAgent(BaseAgent):
    """
    Devil Agent for risk and anomaly detection.

    Responsibilities:
    - Identify potential risks
    - Detect anomalies and outliers
    - Predict failure modes
    - Challenge assumptions
    """

    def __init__(self):
        super().__init__(
            name="devil",
            description="Risk analysis and anomaly detection"
        )
        self._keywords = [
            'risk', 'danger', 'problem', 'issue', 'fail',
            'anomaly', 'unusual', 'wrong', 'error', 'threat',
            'vulnerability', 'weakness', 'concern'
        ]

        # Common risk categories
        self._risk_categories = [
            'financial', 'security', 'privacy', 'reliability',
            'compliance', 'reputation', 'operational'
        ]

    def can_handle(self, query: str) -> float:
        """Evaluate query relevance to risk detection."""
        query_lower = query.lower()
        matches = sum(1 for kw in self._keywords if kw in query_lower)
        return min(matches / 3, 1.0)

    def analyze(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Analyze query for risks and anomalies.

        Args:
            query: Action or situation to analyze
            context: Additional context

        Returns:
            AgentResponse with risk assessment
        """
        risks = []
        anomalies = []
        warnings = []

        query_lower = query.lower()

        # Analyze for common risk patterns
        risks.extend(self._detect_financial_risks(query_lower, context))
        risks.extend(self._detect_security_risks(query_lower, context))
        risks.extend(self._detect_operational_risks(query_lower, context))

        # Check for anomalies in context
        anomalies.extend(self._detect_anomalies(context))

        # Calculate overall risk score
        risk_score = self._calculate_risk_score(risks, anomalies)

        # Generate warnings based on findings
        if risk_score > 0.7:
            warnings.append('High risk detected - recommend careful review')
            priority = AgentPriority.CRITICAL
        elif risk_score > 0.4:
            warnings.append('Moderate risk - consider mitigations')
            priority = AgentPriority.HIGH
        else:
            priority = AgentPriority.MEDIUM

        recommendations = []
        for risk in risks:
            if risk.get('mitigation'):
                recommendations.append(risk['mitigation'])

        return AgentResponse(
            agent_name=self.name,
            success=True,
            message=f"Risk score: {risk_score:.0%} ({len(risks)} risks, {len(anomalies)} anomalies)",
            data={
                'risk_score': risk_score,
                'risks': risks,
                'anomalies': anomalies
            },
            priority=priority,
            confidence=0.8,
            recommendations=recommendations,
            warnings=warnings
        )

    def _detect_financial_risks(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect financial risks."""
        risks = []

        if 'transfer' in query or 'send money' in query:
            risks.append({
                'category': 'financial',
                'severity': 'high',
                'description': 'Financial transfer detected',
                'mitigation': 'Verify recipient and amount before executing'
            })

        if context.get('amount', 0) > context.get('balance', float('inf')) * 0.5:
            risks.append({
                'category': 'financial',
                'severity': 'medium',
                'description': 'Transaction exceeds 50% of balance',
                'mitigation': 'Confirm this large transaction is intentional'
            })

        return risks

    def _detect_security_risks(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect security risks."""
        risks = []

        sensitive_terms = ['password', 'key', 'secret', 'credential', 'token']
        if any(term in query for term in sensitive_terms):
            risks.append({
                'category': 'security',
                'severity': 'high',
                'description': 'Sensitive credential handling detected',
                'mitigation': 'Ensure secure storage and transmission'
            })

        if 'share' in query or 'public' in query:
            risks.append({
                'category': 'privacy',
                'severity': 'medium',
                'description': 'Data sharing/publication detected',
                'mitigation': 'Review what data will be exposed'
            })

        return risks

    def _detect_operational_risks(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect operational risks."""
        risks = []

        if 'delete' in query or 'remove' in query:
            risks.append({
                'category': 'operational',
                'severity': 'high',
                'description': 'Destructive operation detected',
                'mitigation': 'Ensure backup exists before deletion'
            })

        if 'all' in query and ('delete' in query or 'update' in query):
            risks.append({
                'category': 'operational',
                'severity': 'critical',
                'description': 'Bulk operation on all items',
                'mitigation': 'Consider processing in batches with verification'
            })

        return risks

    def _detect_anomalies(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in context data."""
        anomalies = []

        # Check for unusual patterns
        if 'history' in context:
            history = context['history']
            if len(history) > 0:
                # Check for sudden changes in patterns
                # (simplified - would use statistical analysis)
                pass

        return anomalies

    def _calculate_risk_score(self, risks: List[Dict], anomalies: List[Dict]) -> float:
        """Calculate overall risk score."""
        if not risks and not anomalies:
            return 0.1  # Baseline risk

        score = 0.0
        severity_weights = {
            'critical': 0.4,
            'high': 0.25,
            'medium': 0.15,
            'low': 0.05
        }

        for risk in risks:
            severity = risk.get('severity', 'medium')
            score += severity_weights.get(severity, 0.1)

        score += len(anomalies) * 0.1

        return min(score, 1.0)
