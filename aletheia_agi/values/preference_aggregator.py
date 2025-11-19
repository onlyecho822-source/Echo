"""
Preference Aggregator - Multi-Stakeholder Value Aggregation
==========================================================

Implements robust preference aggregation with explicit handling of
dissent, cultural variation, and minority protections.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import uuid


class AggregationMethod(Enum):
    """Methods for aggregating preferences."""
    MAJORITY = auto()           # Simple majority
    SUPERMAJORITY = auto()      # Requires >2/3 agreement
    CONSENSUS = auto()          # Requires near-unanimous agreement
    WEIGHTED = auto()           # Weighted by confidence/expertise
    PLURALITY = auto()          # Most votes wins
    RANKED_CHOICE = auto()      # Instant runoff voting


class DissentType(Enum):
    """Types of dissenting positions."""
    MINORITY_VIEW = auto()      # Minority position on general issue
    RIGHTS_CONCERN = auto()     # Dissent based on rights violation
    CULTURAL_DIFFERENCE = auto()  # Cultural/contextual disagreement
    ETHICAL_OBJECTION = auto()  # Fundamental ethical disagreement


@dataclass
class StakeholderPreference:
    """A preference from a stakeholder or community."""
    stakeholder_id: str
    preference: str
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    cultural_context: Optional[str] = None
    reasoning: Optional[str] = None


@dataclass
class Dissent:
    """Records a dissenting view in the aggregation."""
    id: str
    dissent_type: DissentType
    stakeholder_ids: List[str]
    position: str
    reasoning: str
    must_accommodate: bool  # True if this is a rights-based veto


@dataclass
class AggregationResult:
    """Result of preference aggregation."""
    decision: str
    method_used: AggregationMethod
    support_level: float
    dissents: List[Dissent]
    accommodations_made: List[str]
    confidence: float
    requires_review: bool


class PreferenceAggregator:
    """
    Aggregates preferences from multiple stakeholders.

    Features:
    - Multiple aggregation methods
    - Explicit dissent handling
    - Rights-based vetoes
    - Cultural context awareness
    - Minority protection
    """

    def __init__(self):
        self._preferences: Dict[str, List[StakeholderPreference]] = {}
        self._dissents: List[Dissent] = []
        self._rights_baseline: Set[str] = self._initialize_rights_baseline()

    def _initialize_rights_baseline(self) -> Set[str]:
        """Initialize the global rights baseline that cannot be violated."""
        return {
            'life',
            'liberty',
            'security',
            'privacy',
            'freedom_of_thought',
            'freedom_of_expression',
            'non_discrimination',
            'due_process',
            'education',
            'cultural_participation'
        }

    def submit_preference(
        self,
        issue_id: str,
        preference: StakeholderPreference
    ) -> None:
        """Submit a stakeholder preference on an issue."""
        if issue_id not in self._preferences:
            self._preferences[issue_id] = []
        self._preferences[issue_id].append(preference)

    def register_dissent(
        self,
        issue_id: str,
        dissent_type: DissentType,
        stakeholder_ids: List[str],
        position: str,
        reasoning: str
    ) -> Dissent:
        """
        Register a dissenting view.

        Rights-based dissents trigger mandatory review.
        """
        # Determine if this is a mandatory veto
        must_accommodate = dissent_type == DissentType.RIGHTS_CONCERN

        dissent = Dissent(
            id=str(uuid.uuid4()),
            dissent_type=dissent_type,
            stakeholder_ids=stakeholder_ids,
            position=position,
            reasoning=reasoning,
            must_accommodate=must_accommodate
        )

        self._dissents.append(dissent)
        return dissent

    def aggregate(
        self,
        issue_id: str,
        method: AggregationMethod = AggregationMethod.WEIGHTED
    ) -> AggregationResult:
        """
        Aggregate preferences on an issue.

        Accounts for dissent and rights protections.
        """
        preferences = self._preferences.get(issue_id, [])
        if not preferences:
            return AggregationResult(
                decision="No preferences submitted",
                method_used=method,
                support_level=0.0,
                dissents=[],
                accommodations_made=[],
                confidence=0.0,
                requires_review=True
            )

        # Group by preference
        pref_groups: Dict[str, List[StakeholderPreference]] = {}
        for pref in preferences:
            if pref.preference not in pref_groups:
                pref_groups[pref.preference] = []
            pref_groups[pref.preference].append(pref)

        # Apply aggregation method
        if method == AggregationMethod.WEIGHTED:
            result = self._weighted_aggregation(pref_groups)
        elif method == AggregationMethod.MAJORITY:
            result = self._majority_aggregation(pref_groups)
        elif method == AggregationMethod.CONSENSUS:
            result = self._consensus_aggregation(pref_groups)
        else:
            result = self._weighted_aggregation(pref_groups)

        # Check for rights violations
        accommodations = []
        requires_review = False

        relevant_dissents = [
            d for d in self._dissents
            if any(sid in [p.stakeholder_id for p in preferences]
                   for sid in d.stakeholder_ids)
        ]

        for dissent in relevant_dissents:
            if dissent.must_accommodate:
                accommodations.append(
                    f"Must accommodate: {dissent.position} ({dissent.reasoning})"
                )
                requires_review = True

        return AggregationResult(
            decision=result['decision'],
            method_used=method,
            support_level=result['support'],
            dissents=relevant_dissents,
            accommodations_made=accommodations,
            confidence=result['confidence'],
            requires_review=requires_review or result['confidence'] < 0.6
        )

    def _weighted_aggregation(
        self,
        pref_groups: Dict[str, List[StakeholderPreference]]
    ) -> Dict[str, Any]:
        """Weighted aggregation by strength and confidence."""
        scores: Dict[str, float] = {}

        for pref_text, prefs in pref_groups.items():
            score = sum(p.strength * p.confidence for p in prefs)
            scores[pref_text] = score

        if not scores:
            return {'decision': 'No decision', 'support': 0.0, 'confidence': 0.0}

        total_score = sum(scores.values())
        winner = max(scores, key=scores.get)
        support = scores[winner] / total_score if total_score > 0 else 0

        return {
            'decision': winner,
            'support': support,
            'confidence': min(support, 0.9)  # Cap confidence
        }

    def _majority_aggregation(
        self,
        pref_groups: Dict[str, List[StakeholderPreference]]
    ) -> Dict[str, Any]:
        """Simple majority aggregation."""
        counts = {pref: len(prefs) for pref, prefs in pref_groups.items()}
        total = sum(counts.values())

        if not counts:
            return {'decision': 'No decision', 'support': 0.0, 'confidence': 0.0}

        winner = max(counts, key=counts.get)
        support = counts[winner] / total

        return {
            'decision': winner,
            'support': support,
            'confidence': support if support > 0.5 else support * 0.5
        }

    def _consensus_aggregation(
        self,
        pref_groups: Dict[str, List[StakeholderPreference]]
    ) -> Dict[str, Any]:
        """Consensus-seeking aggregation (requires high agreement)."""
        counts = {pref: len(prefs) for pref, prefs in pref_groups.items()}
        total = sum(counts.values())

        if not counts:
            return {'decision': 'No decision', 'support': 0.0, 'confidence': 0.0}

        winner = max(counts, key=counts.get)
        support = counts[winner] / total

        # Consensus requires >90% agreement
        if support < 0.9:
            return {
                'decision': f"No consensus (leading: {winner})",
                'support': support,
                'confidence': 0.3
            }

        return {
            'decision': winner,
            'support': support,
            'confidence': 0.95
        }

    def check_rights_violation(self, decision: str) -> List[str]:
        """
        Check if a decision violates the rights baseline.

        Returns list of potentially violated rights.
        """
        # In a real system, this would use NLP/semantic analysis
        # to check for rights violations
        violations = []

        decision_lower = decision.lower()

        # Simple keyword checks (placeholder)
        if 'privacy' in decision_lower and 'violat' in decision_lower:
            violations.append('privacy')
        if 'discriminat' in decision_lower:
            violations.append('non_discrimination')
        if 'censor' in decision_lower:
            violations.append('freedom_of_expression')

        return violations

    def get_cultural_contexts(self, issue_id: str) -> Set[str]:
        """Get all cultural contexts represented in preferences."""
        preferences = self._preferences.get(issue_id, [])
        return {
            p.cultural_context for p in preferences
            if p.cultural_context
        }

    def generate_aggregation_report(self, issue_id: str) -> Dict[str, Any]:
        """Generate a report on preference aggregation for an issue."""
        preferences = self._preferences.get(issue_id, [])

        return {
            'issue_id': issue_id,
            'total_preferences': len(preferences),
            'stakeholders': len(set(p.stakeholder_id for p in preferences)),
            'cultural_contexts': list(self.get_cultural_contexts(issue_id)),
            'dissents': len([
                d for d in self._dissents
                if any(sid in [p.stakeholder_id for p in preferences]
                       for sid in d.stakeholder_ids)
            ]),
            'rights_concerns': len([
                d for d in self._dissents
                if d.dissent_type == DissentType.RIGHTS_CONCERN
            ])
        }
