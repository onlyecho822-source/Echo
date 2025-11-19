"""
Value Learner - Cooperative Inverse Reinforcement Learning
==========================================================

Implements value learning through CIRL (Cooperative Inverse Reinforcement Learning),
inverse RL, debate, and elicitation methods. Explicitly tracks uncertainty and
refuses power-seeking, deception, or unilateral override.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid


class ValueSource(Enum):
    """Sources from which values can be learned."""
    EXPLICIT_STATEMENT = auto()      # Direct human statement
    BEHAVIORAL_INFERENCE = auto()    # Inferred from behavior
    DEBATE_ELICITATION = auto()      # Through structured debate
    PREFERENCE_COMPARISON = auto()   # Pairwise preferences
    CULTURAL_NORMS = auto()          # Community/cultural standards
    RIGHTS_FRAMEWORK = auto()        # Fundamental rights documents


class ValueConfidence(Enum):
    """Confidence levels in learned values."""
    HIGH = auto()       # Multiple consistent sources, low uncertainty
    MEDIUM = auto()     # Some evidence, moderate uncertainty
    LOW = auto()        # Limited evidence, high uncertainty
    UNCERTAIN = auto()  # Conflicting evidence or insufficient data


@dataclass
class LearnedValue:
    """
    Represents a value learned from human feedback or observation.

    Includes provenance, confidence, and uncertainty bounds.
    """
    id: str
    description: str
    source: ValueSource
    confidence: ValueConfidence
    uncertainty_bounds: Tuple[float, float]  # (lower, upper) probability bounds
    supporting_evidence: List[str]
    conflicting_evidence: List[str]
    learned_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    # Contextual information
    cultural_context: Optional[str] = None
    domain_specific: bool = False

    def needs_clarification(self) -> bool:
        """Check if value needs human clarification."""
        return (
            self.confidence in [ValueConfidence.LOW, ValueConfidence.UNCERTAIN] or
            len(self.conflicting_evidence) > 0
        )


@dataclass
class PreferenceObservation:
    """An observed preference from human behavior or statement."""
    id: str
    context: Dict[str, Any]
    choice_made: str
    alternatives: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ValueLearner:
    """
    Learns human values through cooperative methods.

    Key principles:
    - Cooperative: Treats value learning as collaborative, not adversarial
    - Uncertain: Explicitly tracks and communicates uncertainty
    - Cautious: Errs on the side of human values when uncertain
    - Transparent: Makes learned values and evidence available for review
    """

    def __init__(self):
        self._learned_values: Dict[str, LearnedValue] = {}
        self._observations: List[PreferenceObservation] = []
        self._elicitation_queue: List[Dict[str, Any]] = []

        # Core constraints that cannot be overridden by learning
        self._immutable_constraints = {
            'no_power_seeking': "Never seek to accumulate power or resources beyond task needs",
            'no_deception': "Never deceive humans unless explicitly authorized and justified",
            'no_unilateral_override': "Never override human decisions without explicit authorization",
            'maintain_corrigibility': "Always remain interruptible and correctable",
            'preserve_autonomy': "Never manipulate or coerce humans"
        }

    def observe_preference(
        self,
        context: Dict[str, Any],
        choice: str,
        alternatives: List[str],
        confidence: float = 1.0
    ) -> str:
        """
        Record an observed preference for value learning.

        Returns observation ID.
        """
        observation = PreferenceObservation(
            id=str(uuid.uuid4()),
            context=context,
            choice_made=choice,
            alternatives=alternatives,
            confidence=confidence
        )
        self._observations.append(observation)

        # Trigger value update
        self._update_values_from_observation(observation)

        return observation.id

    def _update_values_from_observation(self, observation: PreferenceObservation) -> None:
        """Update learned values based on new observation."""
        # In a real system, this would use inverse RL or CIRL
        # to update the value model based on observed preferences
        pass

    def learn_from_explicit_statement(
        self,
        statement: str,
        context: Dict[str, Any],
        cultural_context: Optional[str] = None
    ) -> LearnedValue:
        """
        Learn a value from an explicit human statement.

        Statements are the highest-confidence source of values.
        """
        value = LearnedValue(
            id=str(uuid.uuid4()),
            description=statement,
            source=ValueSource.EXPLICIT_STATEMENT,
            confidence=ValueConfidence.HIGH,
            uncertainty_bounds=(0.8, 1.0),
            supporting_evidence=[f"Direct statement: {statement}"],
            conflicting_evidence=[],
            cultural_context=cultural_context
        )

        self._learned_values[value.id] = value
        return value

    def learn_from_behavior(
        self,
        behavior_description: str,
        inferred_value: str,
        evidence: List[str]
    ) -> LearnedValue:
        """
        Infer a value from observed behavior patterns.

        Lower confidence than explicit statements due to inference.
        """
        value = LearnedValue(
            id=str(uuid.uuid4()),
            description=inferred_value,
            source=ValueSource.BEHAVIORAL_INFERENCE,
            confidence=ValueConfidence.MEDIUM,
            uncertainty_bounds=(0.5, 0.8),
            supporting_evidence=evidence,
            conflicting_evidence=[]
        )

        self._learned_values[value.id] = value
        return value

    def elicit_through_debate(
        self,
        question: str,
        position_a: str,
        position_b: str,
        resolution: str
    ) -> LearnedValue:
        """
        Learn value through structured debate/deliberation.

        Uses debate as an alignment technique to elicit human values
        on complex or contested questions.
        """
        value = LearnedValue(
            id=str(uuid.uuid4()),
            description=resolution,
            source=ValueSource.DEBATE_ELICITATION,
            confidence=ValueConfidence.MEDIUM,
            uncertainty_bounds=(0.6, 0.85),
            supporting_evidence=[
                f"Question: {question}",
                f"Position A: {position_a}",
                f"Position B: {position_b}",
                f"Resolution: {resolution}"
            ],
            conflicting_evidence=[]
        )

        self._learned_values[value.id] = value
        return value

    def get_value(self, value_id: str) -> Optional[LearnedValue]:
        """Retrieve a learned value by ID."""
        return self._learned_values.get(value_id)

    def get_all_values(self) -> List[LearnedValue]:
        """Get all learned values."""
        return list(self._learned_values.values())

    def get_values_by_confidence(
        self,
        min_confidence: ValueConfidence
    ) -> List[LearnedValue]:
        """Get values with at least the specified confidence."""
        confidence_order = [
            ValueConfidence.UNCERTAIN,
            ValueConfidence.LOW,
            ValueConfidence.MEDIUM,
            ValueConfidence.HIGH
        ]
        min_idx = confidence_order.index(min_confidence)

        return [
            v for v in self._learned_values.values()
            if confidence_order.index(v.confidence) >= min_idx
        ]

    def get_values_needing_clarification(self) -> List[LearnedValue]:
        """Get values that need human clarification."""
        return [v for v in self._learned_values.values() if v.needs_clarification()]

    def check_against_constraints(self, proposed_action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a proposed action violates immutable constraints.

        These constraints cannot be overridden by learned values.
        """
        violations = []

        # Check for power-seeking
        if proposed_action.get('acquires_resources') or proposed_action.get('increases_influence'):
            if not proposed_action.get('necessary_for_task'):
                violations.append({
                    'constraint': 'no_power_seeking',
                    'reason': self._immutable_constraints['no_power_seeking']
                })

        # Check for deception
        if proposed_action.get('involves_deception'):
            if not proposed_action.get('explicitly_authorized'):
                violations.append({
                    'constraint': 'no_deception',
                    'reason': self._immutable_constraints['no_deception']
                })

        # Check for unilateral override
        if proposed_action.get('overrides_human_decision'):
            if not proposed_action.get('explicit_authorization'):
                violations.append({
                    'constraint': 'no_unilateral_override',
                    'reason': self._immutable_constraints['no_unilateral_override']
                })

        # Check for manipulation
        if proposed_action.get('manipulative') or proposed_action.get('coercive'):
            violations.append({
                'constraint': 'preserve_autonomy',
                'reason': self._immutable_constraints['preserve_autonomy']
            })

        return {
            'permitted': len(violations) == 0,
            'violations': violations
        }

    def request_clarification(
        self,
        value_id: str,
        question: str
    ) -> None:
        """Request human clarification on an uncertain value."""
        self._elicitation_queue.append({
            'value_id': value_id,
            'question': question,
            'requested_at': datetime.utcnow().isoformat()
        })

    def get_pending_clarifications(self) -> List[Dict[str, Any]]:
        """Get list of pending clarification requests."""
        return self._elicitation_queue.copy()

    def provide_clarification(
        self,
        value_id: str,
        clarification: str
    ) -> None:
        """
        Provide clarification for a value.

        Updates the value based on human clarification.
        """
        value = self._learned_values.get(value_id)
        if not value:
            return

        value.supporting_evidence.append(f"Clarification: {clarification}")
        value.confidence = ValueConfidence.HIGH
        value.uncertainty_bounds = (0.85, 0.95)
        value.last_updated = datetime.utcnow()

        # Remove from queue
        self._elicitation_queue = [
            q for q in self._elicitation_queue
            if q['value_id'] != value_id
        ]

    def aggregate_values(
        self,
        value_ids: List[str],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Aggregate multiple values for decision-making.

        Uses robust aggregation that accounts for uncertainty.
        """
        values = [
            self._learned_values[vid]
            for vid in value_ids
            if vid in self._learned_values
        ]

        if not values:
            return {'error': 'No valid values to aggregate'}

        # Simple aggregation (real implementation would be more sophisticated)
        total_weight = 0.0
        weighted_confidence = 0.0

        confidence_scores = {
            ValueConfidence.HIGH: 1.0,
            ValueConfidence.MEDIUM: 0.7,
            ValueConfidence.LOW: 0.4,
            ValueConfidence.UNCERTAIN: 0.2
        }

        for value in values:
            weight = weights.get(value.id, 1.0) if weights else 1.0
            conf_score = confidence_scores[value.confidence]
            weighted_confidence += weight * conf_score
            total_weight += weight

        avg_confidence = weighted_confidence / total_weight if total_weight > 0 else 0

        return {
            'value_count': len(values),
            'aggregated_confidence': avg_confidence,
            'needs_clarification': any(v.needs_clarification() for v in values),
            'uncertain_values': [v.id for v in values if v.needs_clarification()]
        }

    def generate_value_report(self) -> Dict[str, Any]:
        """Generate a report on learned values."""
        return {
            'total_values': len(self._learned_values),
            'by_source': {
                s.name: len([v for v in self._learned_values.values() if v.source == s])
                for s in ValueSource
            },
            'by_confidence': {
                c.name: len([v for v in self._learned_values.values() if v.confidence == c])
                for c in ValueConfidence
            },
            'needing_clarification': len(self.get_values_needing_clarification()),
            'pending_clarifications': len(self._elicitation_queue),
            'observations_recorded': len(self._observations)
        }
