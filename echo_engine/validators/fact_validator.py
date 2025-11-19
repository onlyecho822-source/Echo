"""Fact validation module."""

from datetime import datetime
from typing import Optional
from echo_engine.core.models import (
    Source,
    Fact,
    FactStatus,
    ConfidenceLevel,
)
from echo_engine.core.exceptions import ValidationError


class FactValidator:
    """
    Validates facts by cross-referencing with sources and other facts.

    Uses multiple validation strategies to determine the truthfulness
    and reliability of extracted facts.
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize the fact validator."""
        self.config = config or {}
        self.min_corroboration = self.config.get("min_corroboration", 2)
        self.keyword_threshold = self.config.get("keyword_threshold", 0.3)

    def validate(
        self,
        fact: Fact,
        sources: list[Source],
        other_facts: list[Fact],
    ) -> FactStatus:
        """
        Validate a fact against sources and other facts.

        Args:
            fact: The fact to validate
            sources: Available sources
            other_facts: Other facts for cross-validation

        Returns:
            The determined FactStatus
        """
        supporting = []
        contradicting = []

        # Check against sources
        for source in sources:
            if source.id in fact.source_ids:
                continue  # Skip original source

            result = self._check_source_support(fact, source)
            if result == "support":
                supporting.append(source.id)
                fact.supporting_evidence.append(source.id)
            elif result == "contradict":
                contradicting.append(source.id)
                fact.contradicting_evidence.append(source.id)

        # Check against other facts
        for other in other_facts:
            if other.id == fact.id:
                continue

            result = self._check_fact_alignment(fact, other)
            if result == "support":
                supporting.append(other.id)
            elif result == "contradict":
                contradicting.append(other.id)

        # Determine status
        status = self._determine_status(len(supporting), len(contradicting))
        fact.status = status
        fact.verified_at = datetime.now()

        # Update confidence
        fact.confidence = self._calculate_confidence(
            len(supporting),
            len(contradicting),
            len(sources)
        )

        return status

    def validate_batch(
        self,
        facts: list[Fact],
        sources: list[Source],
    ) -> dict[str, FactStatus]:
        """
        Validate multiple facts.

        Args:
            facts: Facts to validate
            sources: Available sources

        Returns:
            Dictionary mapping fact IDs to statuses
        """
        results = {}

        for fact in facts:
            other_facts = [f for f in facts if f.id != fact.id]
            status = self.validate(fact, sources, other_facts)
            results[fact.id] = status

        return results

    def _check_source_support(self, fact: Fact, source: Source) -> str:
        """Check if a source supports or contradicts a fact."""
        source_lower = source.content.lower()
        fact_keywords = set(k.lower() for k in fact.keywords)

        # Count keyword matches
        matches = sum(1 for kw in fact_keywords if kw in source_lower)
        match_ratio = matches / len(fact_keywords) if fact_keywords else 0

        if match_ratio < self.keyword_threshold:
            return "neutral"

        # Check for contradiction indicators
        negation_indicators = [
            "not true", "false", "incorrect", "inaccurate",
            "wrong", "mistaken", "erroneous", "unfounded",
            "denied", "refuted", "disputed", "contradicted",
            "debunked", "disproven", "discredited",
        ]

        # Check if negation appears near fact keywords
        for indicator in negation_indicators:
            if indicator in source_lower:
                # Check proximity to fact keywords
                for keyword in fact_keywords:
                    if self._check_proximity(source_lower, indicator, keyword):
                        return "contradict"

        # If keywords match without negation, it's support
        return "support" if match_ratio >= self.keyword_threshold else "neutral"

    def _check_proximity(
        self,
        text: str,
        term1: str,
        term2: str,
        window: int = 50
    ) -> bool:
        """Check if two terms appear within a certain word window."""
        pos1 = text.find(term1)
        pos2 = text.find(term2)

        if pos1 == -1 or pos2 == -1:
            return False

        # Count words between positions
        between = text[min(pos1, pos2):max(pos1, pos2)]
        word_distance = len(between.split())

        return word_distance <= window

    def _check_fact_alignment(self, fact1: Fact, fact2: Fact) -> str:
        """Check if two facts align or contradict."""
        # Check entity overlap
        entities1 = set(e.lower() for e in fact1.entities)
        entities2 = set(e.lower() for e in fact2.entities)
        entity_overlap = entities1 & entities2

        if not entity_overlap:
            return "neutral"

        # Check keyword overlap
        keywords1 = set(k.lower() for k in fact1.keywords)
        keywords2 = set(k.lower() for k in fact2.keywords)
        keyword_overlap = keywords1 & keywords2

        # Look for negation differences
        negation_words = {'not', 'never', "n't", 'no', 'none', 'neither'}

        fact1_has_negation = bool(
            negation_words & set(fact1.statement.lower().split())
        )
        fact2_has_negation = bool(
            negation_words & set(fact2.statement.lower().split())
        )

        # If they share entities/keywords but differ in negation
        if entity_overlap and keyword_overlap:
            if fact1_has_negation != fact2_has_negation:
                return "contradict"
            return "support"

        return "neutral"

    def _determine_status(self, support_count: int, contradict_count: int) -> FactStatus:
        """Determine fact status based on support and contradiction counts."""
        if contradict_count > 0 and support_count > 0:
            return FactStatus.DISPUTED

        if contradict_count >= self.min_corroboration:
            return FactStatus.REFUTED

        if support_count >= self.min_corroboration:
            return FactStatus.VERIFIED

        if support_count > 0:
            return FactStatus.PARTIALLY_VERIFIED

        return FactStatus.UNVERIFIED

    def _calculate_confidence(
        self,
        support_count: int,
        contradict_count: int,
        total_sources: int
    ) -> ConfidenceLevel:
        """Calculate confidence level based on evidence."""
        if total_sources == 0:
            return ConfidenceLevel.VERY_LOW

        # Calculate evidence ratio
        evidence_ratio = support_count / total_sources

        # Penalize for contradictions
        if contradict_count > 0:
            penalty = (contradict_count / total_sources) * 0.5
            evidence_ratio = max(0, evidence_ratio - penalty)

        if evidence_ratio >= 0.6:
            return ConfidenceLevel.VERY_HIGH
        elif evidence_ratio >= 0.4:
            return ConfidenceLevel.HIGH
        elif evidence_ratio >= 0.2:
            return ConfidenceLevel.MEDIUM
        elif evidence_ratio >= 0.1:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def get_validation_report(
        self,
        facts: list[Fact],
    ) -> dict:
        """
        Generate a validation report for a set of facts.

        Args:
            facts: Facts to report on

        Returns:
            Report dictionary
        """
        status_counts = {}
        confidence_counts = {}

        for fact in facts:
            status = fact.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

            confidence = fact.confidence.name.lower()
            confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1

        verified = [f for f in facts if f.status == FactStatus.VERIFIED]
        disputed = [f for f in facts if f.status == FactStatus.DISPUTED]
        refuted = [f for f in facts if f.status == FactStatus.REFUTED]

        return {
            "total_facts": len(facts),
            "status_breakdown": status_counts,
            "confidence_breakdown": confidence_counts,
            "verification_rate": len(verified) / len(facts) if facts else 0,
            "dispute_rate": len(disputed) / len(facts) if facts else 0,
            "refutation_rate": len(refuted) / len(facts) if facts else 0,
            "high_confidence_facts": [
                {
                    "id": f.id,
                    "statement": f.statement,
                    "status": f.status.value,
                }
                for f in facts
                if f.confidence.value >= 4
            ],
            "low_confidence_facts": [
                {
                    "id": f.id,
                    "statement": f.statement,
                    "status": f.status.value,
                }
                for f in facts
                if f.confidence.value <= 2
            ],
        }
