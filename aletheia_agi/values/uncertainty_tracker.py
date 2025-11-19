"""
Uncertainty Tracker - Explicit Uncertainty Quantification
=========================================================

Tracks and propagates uncertainty through the value learning
and decision-making pipeline, ensuring the system knows what
it doesn't know.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import math


class UncertaintyType(Enum):
    """Types of uncertainty."""
    ALEATORIC = auto()      # Irreducible randomness
    EPISTEMIC = auto()      # Knowledge uncertainty (reducible)
    MODEL = auto()          # Uncertainty about model correctness
    VALUE = auto()          # Uncertainty about values/preferences


class UncertaintySource(Enum):
    """Sources of uncertainty."""
    LIMITED_DATA = auto()           # Insufficient observations
    CONFLICTING_EVIDENCE = auto()   # Contradictory information
    AMBIGUOUS_LANGUAGE = auto()     # Unclear statements
    NOVEL_SITUATION = auto()        # Out-of-distribution
    VALUE_DISAGREEMENT = auto()     # Stakeholder disagreement
    MODEL_LIMITATIONS = auto()      # Known model weaknesses


@dataclass
class UncertaintyEstimate:
    """An uncertainty estimate for a belief or decision."""
    id: str
    subject: str  # What this uncertainty is about
    uncertainty_type: UncertaintyType
    sources: List[UncertaintySource]

    # Probability bounds
    lower_bound: float
    upper_bound: float
    point_estimate: float

    # Metadata
    confidence_in_bounds: float  # How confident are we in these bounds
    reducible: bool  # Can this uncertainty be reduced with more info
    timestamp: datetime = field(default_factory=datetime.utcnow)


class UncertaintyTracker:
    """
    Tracks uncertainty across the system.

    Ensures the AGI:
    - Knows what it doesn't know
    - Communicates uncertainty honestly
    - Defers to humans when uncertain
    - Seeks to reduce epistemic uncertainty
    """

    def __init__(self):
        self._estimates: Dict[str, UncertaintyEstimate] = {}
        self._history: List[Dict[str, Any]] = []

        # Thresholds for escalation
        self._escalation_threshold = 0.3  # High uncertainty
        self._action_threshold = 0.7      # Minimum confidence for action

    def create_estimate(
        self,
        subject: str,
        uncertainty_type: UncertaintyType,
        lower: float,
        upper: float,
        sources: Optional[List[UncertaintySource]] = None
    ) -> UncertaintyEstimate:
        """Create a new uncertainty estimate."""
        estimate = UncertaintyEstimate(
            id=str(uuid.uuid4()),
            subject=subject,
            uncertainty_type=uncertainty_type,
            sources=sources or [],
            lower_bound=lower,
            upper_bound=upper,
            point_estimate=(lower + upper) / 2,
            confidence_in_bounds=0.8,
            reducible=uncertainty_type in [
                UncertaintyType.EPISTEMIC,
                UncertaintyType.VALUE
            ]
        )

        self._estimates[estimate.id] = estimate
        self._log_event('created', estimate)

        return estimate

    def update_estimate(
        self,
        estimate_id: str,
        new_lower: Optional[float] = None,
        new_upper: Optional[float] = None,
        new_sources: Optional[List[UncertaintySource]] = None
    ) -> Optional[UncertaintyEstimate]:
        """Update an existing uncertainty estimate."""
        estimate = self._estimates.get(estimate_id)
        if not estimate:
            return None

        if new_lower is not None:
            estimate.lower_bound = new_lower
        if new_upper is not None:
            estimate.upper_bound = new_upper
        if new_sources:
            estimate.sources.extend(new_sources)

        estimate.point_estimate = (estimate.lower_bound + estimate.upper_bound) / 2
        estimate.timestamp = datetime.utcnow()

        self._log_event('updated', estimate)
        return estimate

    def get_uncertainty(self, subject: str) -> Optional[UncertaintyEstimate]:
        """Get uncertainty estimate for a subject."""
        for estimate in self._estimates.values():
            if estimate.subject == subject:
                return estimate
        return None

    def should_escalate(self, estimate_id: str) -> bool:
        """
        Check if uncertainty is high enough to escalate to human review.

        Escalates when:
        - Spread between bounds is large
        - Involves value uncertainty
        - Conflicting evidence
        """
        estimate = self._estimates.get(estimate_id)
        if not estimate:
            return True  # Unknown → escalate

        spread = estimate.upper_bound - estimate.lower_bound

        # High spread indicates high uncertainty
        if spread > self._escalation_threshold:
            return True

        # Value uncertainty should be escalated
        if estimate.uncertainty_type == UncertaintyType.VALUE:
            return True

        # Conflicting evidence needs human judgment
        if UncertaintySource.CONFLICTING_EVIDENCE in estimate.sources:
            return True

        return False

    def can_act(self, estimate_id: str) -> Tuple[bool, str]:
        """
        Check if confidence is sufficient for action.

        Returns (can_act, reason).
        """
        estimate = self._estimates.get(estimate_id)
        if not estimate:
            return (False, "No uncertainty estimate found")

        # Check if lower bound is above threshold
        if estimate.lower_bound >= self._action_threshold:
            return (True, "Sufficient confidence")

        # Check spread
        spread = estimate.upper_bound - estimate.lower_bound
        if spread > 0.5:
            return (False, f"Uncertainty too high (spread: {spread:.2f})")

        # Check point estimate
        if estimate.point_estimate < self._action_threshold:
            return (
                False,
                f"Confidence below threshold ({estimate.point_estimate:.2f} < {self._action_threshold})"
            )

        return (True, "Point estimate meets threshold")

    def propagate_uncertainty(
        self,
        estimate_ids: List[str],
        operation: str = 'combine'
    ) -> UncertaintyEstimate:
        """
        Propagate uncertainty through operations.

        Combines multiple uncertainty estimates for downstream decisions.
        """
        estimates = [
            self._estimates[eid] for eid in estimate_ids
            if eid in self._estimates
        ]

        if not estimates:
            return self.create_estimate(
                "propagated_unknown",
                UncertaintyType.EPISTEMIC,
                0.0,
                1.0,
                [UncertaintySource.LIMITED_DATA]
            )

        if operation == 'combine':
            # Conservative combination: widest bounds
            combined = UncertaintyEstimate(
                id=str(uuid.uuid4()),
                subject="combined_uncertainty",
                uncertainty_type=UncertaintyType.EPISTEMIC,
                sources=list(set(
                    src for est in estimates for src in est.sources
                )),
                lower_bound=min(est.lower_bound for est in estimates),
                upper_bound=max(est.upper_bound for est in estimates),
                point_estimate=sum(est.point_estimate for est in estimates) / len(estimates),
                confidence_in_bounds=min(est.confidence_in_bounds for est in estimates),
                reducible=any(est.reducible for est in estimates)
            )
        elif operation == 'intersect':
            # Intersection: narrowest shared bounds
            combined = UncertaintyEstimate(
                id=str(uuid.uuid4()),
                subject="intersected_uncertainty",
                uncertainty_type=UncertaintyType.EPISTEMIC,
                sources=list(set(
                    src for est in estimates for src in est.sources
                )),
                lower_bound=max(est.lower_bound for est in estimates),
                upper_bound=min(est.upper_bound for est in estimates),
                point_estimate=sum(est.point_estimate for est in estimates) / len(estimates),
                confidence_in_bounds=max(est.confidence_in_bounds for est in estimates),
                reducible=any(est.reducible for est in estimates)
            )
        else:
            combined = estimates[0]

        self._estimates[combined.id] = combined
        return combined

    def get_reducible_uncertainties(self) -> List[UncertaintyEstimate]:
        """Get uncertainties that could be reduced with more information."""
        return [
            est for est in self._estimates.values()
            if est.reducible and (est.upper_bound - est.lower_bound) > 0.2
        ]

    def suggest_information_gathering(
        self,
        estimate_id: str
    ) -> List[str]:
        """Suggest ways to reduce uncertainty."""
        estimate = self._estimates.get(estimate_id)
        if not estimate:
            return []

        suggestions = []

        for source in estimate.sources:
            if source == UncertaintySource.LIMITED_DATA:
                suggestions.append("Gather additional observations or data")
            elif source == UncertaintySource.CONFLICTING_EVIDENCE:
                suggestions.append("Seek clarification from stakeholders")
            elif source == UncertaintySource.AMBIGUOUS_LANGUAGE:
                suggestions.append("Request precise definition of terms")
            elif source == UncertaintySource.NOVEL_SITUATION:
                suggestions.append("Consult domain experts or analogous cases")
            elif source == UncertaintySource.VALUE_DISAGREEMENT:
                suggestions.append("Facilitate structured deliberation")

        if not suggestions:
            suggestions.append("Review assumptions and methodology")

        return suggestions

    def calculate_entropy(self, estimate_id: str) -> float:
        """Calculate entropy (information-theoretic uncertainty)."""
        estimate = self._estimates.get(estimate_id)
        if not estimate:
            return float('inf')

        spread = estimate.upper_bound - estimate.lower_bound
        if spread <= 0:
            return 0.0

        # Entropy of uniform distribution over interval
        return math.log(spread) if spread > 0 else 0

    def _log_event(self, event_type: str, estimate: UncertaintyEstimate) -> None:
        """Log an uncertainty event."""
        self._history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': event_type,
            'estimate_id': estimate.id,
            'subject': estimate.subject,
            'bounds': (estimate.lower_bound, estimate.upper_bound)
        })

    def generate_uncertainty_report(self) -> Dict[str, Any]:
        """Generate a report on system uncertainty."""
        estimates = list(self._estimates.values())

        if not estimates:
            return {'total': 0, 'message': 'No uncertainty estimates tracked'}

        return {
            'total_estimates': len(estimates),
            'by_type': {
                t.name: len([e for e in estimates if e.uncertainty_type == t])
                for t in UncertaintyType
            },
            'high_uncertainty': len([
                e for e in estimates
                if (e.upper_bound - e.lower_bound) > 0.5
            ]),
            'reducible': len([e for e in estimates if e.reducible]),
            'needs_escalation': len([
                e for e in estimates
                if self.should_escalate(e.id)
            ]),
            'average_spread': sum(
                e.upper_bound - e.lower_bound for e in estimates
            ) / len(estimates)
        }
