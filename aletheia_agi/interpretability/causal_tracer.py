"""
Causal Tracer - Mechanistic Interpretability
============================================

Provides causal tracing and mechanistic interpretability tools
to understand why the system made specific decisions or took
specific actions.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class TraceType(Enum):
    """Types of causal traces."""
    DECISION = auto()       # Why a decision was made
    ACTION = auto()         # Why an action was taken
    INFERENCE = auto()      # How an inference was drawn
    VALUE = auto()          # How values influenced outcome


class FactorType(Enum):
    """Types of causal factors."""
    INPUT = auto()          # Input data
    LEARNED_VALUE = auto()  # Learned value/preference
    CONSTRAINT = auto()     # Alignment constraint
    PRIOR = auto()          # Prior knowledge
    INFERENCE = auto()      # Intermediate inference
    UNCERTAINTY = auto()    # Uncertainty consideration


@dataclass
class CausalFactor:
    """A factor that influenced an outcome."""
    id: str
    factor_type: FactorType
    description: str
    influence: float  # -1.0 to 1.0 (negative = against, positive = for)
    confidence: float  # Confidence in this attribution
    evidence: List[str]


@dataclass
class CausalTrace:
    """A trace explaining why something happened."""
    id: str
    target_id: str  # ID of decision/action being explained
    trace_type: TraceType
    timestamp: datetime
    factors: List[CausalFactor]
    counterfactuals: List[Dict[str, Any]]  # What would have changed outcome
    summary: str
    confidence: float


class CausalTracer:
    """
    Provides causal tracing for interpretability.

    Features:
    - Factor attribution
    - Counterfactual analysis
    - Influence quantification
    - Trace storage and retrieval
    """

    def __init__(self):
        self._traces: Dict[str, CausalTrace] = {}

    def trace_decision(
        self,
        decision_id: str,
        decision_description: str,
        factors: List[Dict[str, Any]]
    ) -> CausalTrace:
        """
        Create a causal trace for a decision.

        Analyzes what factors led to the decision and generates
        counterfactual explanations.
        """
        # Convert factor dicts to CausalFactor objects
        causal_factors = []
        for f in factors:
            factor = CausalFactor(
                id=str(uuid.uuid4()),
                factor_type=f.get('type', FactorType.INPUT),
                description=f.get('description', ''),
                influence=f.get('influence', 0.0),
                confidence=f.get('confidence', 0.5),
                evidence=f.get('evidence', [])
            )
            causal_factors.append(factor)

        # Generate counterfactuals
        counterfactuals = self._generate_counterfactuals(causal_factors)

        # Create trace
        trace = CausalTrace(
            id=str(uuid.uuid4()),
            target_id=decision_id,
            trace_type=TraceType.DECISION,
            timestamp=datetime.utcnow(),
            factors=causal_factors,
            counterfactuals=counterfactuals,
            summary=self._generate_summary(decision_description, causal_factors),
            confidence=self._calculate_trace_confidence(causal_factors)
        )

        self._traces[trace.id] = trace
        return trace

    def trace_action(
        self,
        action_id: str,
        action_description: str,
        factors: List[Dict[str, Any]]
    ) -> CausalTrace:
        """Create a causal trace for an action."""
        causal_factors = [
            CausalFactor(
                id=str(uuid.uuid4()),
                factor_type=f.get('type', FactorType.INPUT),
                description=f.get('description', ''),
                influence=f.get('influence', 0.0),
                confidence=f.get('confidence', 0.5),
                evidence=f.get('evidence', [])
            )
            for f in factors
        ]

        trace = CausalTrace(
            id=str(uuid.uuid4()),
            target_id=action_id,
            trace_type=TraceType.ACTION,
            timestamp=datetime.utcnow(),
            factors=causal_factors,
            counterfactuals=self._generate_counterfactuals(causal_factors),
            summary=self._generate_summary(action_description, causal_factors),
            confidence=self._calculate_trace_confidence(causal_factors)
        )

        self._traces[trace.id] = trace
        return trace

    def _generate_counterfactuals(
        self,
        factors: List[CausalFactor]
    ) -> List[Dict[str, Any]]:
        """
        Generate counterfactual explanations.

        Identifies what changes would have led to different outcomes.
        """
        counterfactuals = []

        # For each high-influence factor, generate counterfactual
        for factor in factors:
            if abs(factor.influence) > 0.5:
                cf = {
                    'factor_id': factor.id,
                    'original': factor.description,
                    'counterfactual': f"If '{factor.description}' were different",
                    'expected_change': 'Outcome would likely change',
                    'confidence': factor.confidence * 0.8  # Slightly lower confidence
                }
                counterfactuals.append(cf)

        return counterfactuals

    def _generate_summary(
        self,
        description: str,
        factors: List[CausalFactor]
    ) -> str:
        """Generate a human-readable summary of the trace."""
        # Sort factors by influence
        sorted_factors = sorted(
            factors,
            key=lambda f: abs(f.influence),
            reverse=True
        )

        if not sorted_factors:
            return f"No clear factors identified for: {description}"

        top_factor = sorted_factors[0]
        summary = f"{description} was primarily influenced by: {top_factor.description}"

        if len(sorted_factors) > 1:
            secondary = sorted_factors[1].description
            summary += f". Secondary factor: {secondary}"

        return summary

    def _calculate_trace_confidence(self, factors: List[CausalFactor]) -> float:
        """Calculate overall confidence in the trace."""
        if not factors:
            return 0.0

        # Weighted average by influence magnitude
        total_influence = sum(abs(f.influence) for f in factors)
        if total_influence == 0:
            return 0.5

        weighted_confidence = sum(
            abs(f.influence) * f.confidence for f in factors
        )
        return weighted_confidence / total_influence

    def get_trace(self, trace_id: str) -> Optional[CausalTrace]:
        """Get a trace by ID."""
        return self._traces.get(trace_id)

    def get_traces_for_target(self, target_id: str) -> List[CausalTrace]:
        """Get all traces for a specific decision/action."""
        return [
            t for t in self._traces.values()
            if t.target_id == target_id
        ]

    def get_influential_factors(
        self,
        trace_id: str,
        min_influence: float = 0.3
    ) -> List[CausalFactor]:
        """Get factors with influence above threshold."""
        trace = self._traces.get(trace_id)
        if not trace:
            return []

        return [
            f for f in trace.factors
            if abs(f.influence) >= min_influence
        ]

    def compare_traces(
        self,
        trace_id_1: str,
        trace_id_2: str
    ) -> Dict[str, Any]:
        """Compare two traces to identify differences."""
        trace1 = self._traces.get(trace_id_1)
        trace2 = self._traces.get(trace_id_2)

        if not trace1 or not trace2:
            return {'error': 'One or both traces not found'}

        # Find common and unique factors
        factors1 = {f.description: f for f in trace1.factors}
        factors2 = {f.description: f for f in trace2.factors}

        common = set(factors1.keys()) & set(factors2.keys())
        unique_to_1 = set(factors1.keys()) - set(factors2.keys())
        unique_to_2 = set(factors2.keys()) - set(factors1.keys())

        return {
            'common_factors': len(common),
            'unique_to_first': list(unique_to_1),
            'unique_to_second': list(unique_to_2),
            'confidence_difference': abs(trace1.confidence - trace2.confidence)
        }

    def generate_explanation(
        self,
        trace_id: str,
        detail_level: str = 'standard'
    ) -> str:
        """Generate a natural language explanation from a trace."""
        trace = self._traces.get(trace_id)
        if not trace:
            return "Trace not found"

        if detail_level == 'brief':
            return trace.summary

        # Standard explanation
        explanation = [trace.summary, ""]

        # Add factor details
        explanation.append("Contributing factors:")
        for factor in sorted(trace.factors, key=lambda f: -abs(f.influence)):
            direction = "supported" if factor.influence > 0 else "opposed"
            explanation.append(
                f"  - {factor.description} ({direction}, "
                f"influence: {abs(factor.influence):.2f})"
            )

        # Add counterfactuals
        if trace.counterfactuals and detail_level == 'detailed':
            explanation.append("")
            explanation.append("Counterfactual analysis:")
            for cf in trace.counterfactuals:
                explanation.append(f"  - {cf['counterfactual']}")

        return "\n".join(explanation)

    def generate_interpretability_report(self) -> Dict[str, Any]:
        """Generate a report on interpretability metrics."""
        traces = list(self._traces.values())

        if not traces:
            return {'total_traces': 0}

        avg_factors = sum(len(t.factors) for t in traces) / len(traces)
        avg_confidence = sum(t.confidence for t in traces) / len(traces)

        return {
            'total_traces': len(traces),
            'by_type': {
                t.name: len([tr for tr in traces if tr.trace_type == t])
                for t in TraceType
            },
            'average_factors_per_trace': avg_factors,
            'average_confidence': avg_confidence,
            'total_counterfactuals': sum(
                len(t.counterfactuals) for t in traces
            )
        }
