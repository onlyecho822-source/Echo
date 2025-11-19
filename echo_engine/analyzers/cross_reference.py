"""Cross-reference analysis module."""

from typing import Optional
from echo_engine.core.models import (
    Source,
    Fact,
    Connection,
    ConnectionType,
    ConfidenceLevel,
)


class CrossReferenceAnalyzer:
    """
    Analyzes cross-references between sources and facts.

    Identifies relationships, corroborations, and contradictions
    across multiple information sources.
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize the cross-reference analyzer."""
        self.config = config or {}
        self.similarity_threshold = self.config.get("similarity_threshold", 0.3)

    def analyze(
        self,
        sources: list[Source],
        facts: list[Fact],
    ) -> list[Connection]:
        """
        Analyze cross-references between sources and facts.

        Args:
            sources: List of sources
            facts: List of facts

        Returns:
            List of discovered Connection objects
        """
        connections = []

        # Analyze fact-to-fact connections
        fact_connections = self._analyze_fact_connections(facts)
        connections.extend(fact_connections)

        # Analyze source-to-source connections
        source_connections = self._analyze_source_connections(sources)
        connections.extend(source_connections)

        # Analyze fact-to-source connections
        cross_connections = self._analyze_fact_source_connections(facts, sources)
        connections.extend(cross_connections)

        return connections

    def _analyze_fact_connections(self, facts: list[Fact]) -> list[Connection]:
        """Analyze connections between facts."""
        connections = []

        for i, fact1 in enumerate(facts):
            for fact2 in facts[i + 1:]:
                connection = self._compare_facts(fact1, fact2)
                if connection:
                    connections.append(connection)

        return connections

    def _compare_facts(self, fact1: Fact, fact2: Fact) -> Optional[Connection]:
        """Compare two facts and determine their relationship."""
        # Calculate similarity based on shared elements
        similarity = self._calculate_similarity(
            set(e.lower() for e in fact1.entities),
            set(e.lower() for e in fact2.entities),
            set(k.lower() for k in fact1.keywords),
            set(k.lower() for k in fact2.keywords),
        )

        if similarity < self.similarity_threshold:
            return None

        # Determine connection type
        connection_type = self._determine_fact_relationship(fact1, fact2)

        return Connection(
            source_entity_id=fact1.id,
            target_entity_id=fact2.id,
            connection_type=connection_type,
            strength=similarity,
            description=self._generate_connection_description(
                fact1, fact2, connection_type
            ),
            evidence_ids=fact1.source_ids + fact2.source_ids,
            confidence=self._calculate_connection_confidence(fact1, fact2),
        )

    def _calculate_similarity(
        self,
        entities1: set,
        entities2: set,
        keywords1: set,
        keywords2: set,
    ) -> float:
        """Calculate similarity score between two sets of entities and keywords."""
        # Jaccard similarity for entities
        if entities1 or entities2:
            entity_intersection = len(entities1 & entities2)
            entity_union = len(entities1 | entities2)
            entity_similarity = entity_intersection / entity_union if entity_union else 0
        else:
            entity_similarity = 0

        # Jaccard similarity for keywords
        if keywords1 or keywords2:
            keyword_intersection = len(keywords1 & keywords2)
            keyword_union = len(keywords1 | keywords2)
            keyword_similarity = keyword_intersection / keyword_union if keyword_union else 0
        else:
            keyword_similarity = 0

        # Weight entities higher than keywords
        return (entity_similarity * 0.6) + (keyword_similarity * 0.4)

    def _determine_fact_relationship(
        self,
        fact1: Fact,
        fact2: Fact
    ) -> ConnectionType:
        """Determine the type of relationship between facts."""
        # Check for contradiction indicators
        contradiction_words = {
            'not', 'never', 'false', 'incorrect', 'wrong',
            'denied', 'refuted', 'disputed'
        }

        fact1_words = set(fact1.statement.lower().split())
        fact2_words = set(fact2.statement.lower().split())

        fact1_has_negation = bool(fact1_words & contradiction_words)
        fact2_has_negation = bool(fact2_words & contradiction_words)

        if fact1_has_negation != fact2_has_negation:
            return ConnectionType.CONTRADICTS

        # Check validation status
        from echo_engine.core.models import FactStatus

        if (fact1.status == FactStatus.VERIFIED and
            fact2.status == FactStatus.VERIFIED):
            return ConnectionType.CORROBORATES

        if (fact1.status == FactStatus.REFUTED or
            fact2.status == FactStatus.REFUTED):
            return ConnectionType.CONTRADICTS

        # Check for derivation patterns
        if any(source_id in fact2.source_ids for source_id in fact1.source_ids):
            return ConnectionType.DERIVES_FROM

        return ConnectionType.RELATED_TO

    def _analyze_source_connections(self, sources: list[Source]) -> list[Connection]:
        """Analyze connections between sources."""
        connections = []

        for i, source1 in enumerate(sources):
            for source2 in sources[i + 1:]:
                connection = self._compare_sources(source1, source2)
                if connection:
                    connections.append(connection)

        return connections

    def _compare_sources(self, source1: Source, source2: Source) -> Optional[Connection]:
        """Compare two sources for relationships."""
        # Extract keywords from both sources
        keywords1 = set(self._extract_keywords(source1.content))
        keywords2 = set(self._extract_keywords(source2.content))

        if not keywords1 or not keywords2:
            return None

        # Calculate overlap
        overlap = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        similarity = overlap / union if union else 0

        if similarity < self.similarity_threshold:
            return None

        # Check if one references the other
        if source1.name.lower() in source2.content.lower():
            connection_type = ConnectionType.REFERENCES
        elif source2.name.lower() in source1.content.lower():
            connection_type = ConnectionType.REFERENCES
        else:
            connection_type = ConnectionType.RELATED_TO

        return Connection(
            source_entity_id=source1.id,
            target_entity_id=source2.id,
            connection_type=connection_type,
            strength=similarity,
            description=f"Sources share {overlap} common keywords",
            confidence=ConfidenceLevel.MEDIUM,
        )

    def _analyze_fact_source_connections(
        self,
        facts: list[Fact],
        sources: list[Source]
    ) -> list[Connection]:
        """Analyze connections between facts and sources they're not from."""
        connections = []

        for fact in facts:
            for source in sources:
                # Skip if this source is the fact's origin
                if source.id in fact.source_ids:
                    continue

                # Check if source mentions similar content
                fact_keywords = set(k.lower() for k in fact.keywords)
                source_content_lower = source.content.lower()

                matches = sum(1 for kw in fact_keywords if kw in source_content_lower)
                match_ratio = matches / len(fact_keywords) if fact_keywords else 0

                if match_ratio >= self.similarity_threshold:
                    connections.append(Connection(
                        source_entity_id=fact.id,
                        target_entity_id=source.id,
                        connection_type=ConnectionType.SUPPORTS,
                        strength=match_ratio,
                        description=f"Source contains {matches} keywords from fact",
                        confidence=ConfidenceLevel.MEDIUM,
                    ))

        return connections

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from text."""
        import re

        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'shall', 'to', 'of', 'in', 'for',
            'on', 'with', 'at', 'by', 'from', 'and', 'but', 'or',
        }

        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]

    def _generate_connection_description(
        self,
        fact1: Fact,
        fact2: Fact,
        connection_type: ConnectionType
    ) -> str:
        """Generate a description for a connection."""
        shared_entities = set(e.lower() for e in fact1.entities) & set(e.lower() for e in fact2.entities)
        shared_keywords = set(k.lower() for k in fact1.keywords) & set(k.lower() for k in fact2.keywords)

        parts = []
        if shared_entities:
            parts.append(f"shared entities: {', '.join(list(shared_entities)[:3])}")
        if shared_keywords:
            parts.append(f"shared keywords: {', '.join(list(shared_keywords)[:3])}")

        return f"{connection_type.value}: {'; '.join(parts)}"

    def _calculate_connection_confidence(
        self,
        fact1: Fact,
        fact2: Fact
    ) -> ConfidenceLevel:
        """Calculate confidence level for a connection."""
        # Average of both facts' confidence
        avg = (fact1.confidence.value + fact2.confidence.value) / 2

        if avg >= 4.5:
            return ConfidenceLevel.VERY_HIGH
        elif avg >= 3.5:
            return ConfidenceLevel.HIGH
        elif avg >= 2.5:
            return ConfidenceLevel.MEDIUM
        elif avg >= 1.5:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def find_corroborations(self, facts: list[Fact]) -> list[dict]:
        """Find facts that corroborate each other."""
        corroborations = []

        for i, fact1 in enumerate(facts):
            supporting_facts = []
            for fact2 in facts[i + 1:]:
                connection = self._compare_facts(fact1, fact2)
                if connection and connection.connection_type == ConnectionType.CORROBORATES:
                    supporting_facts.append({
                        "fact_id": fact2.id,
                        "statement": fact2.statement,
                        "strength": connection.strength,
                    })

            if supporting_facts:
                corroborations.append({
                    "primary_fact": {
                        "id": fact1.id,
                        "statement": fact1.statement,
                    },
                    "supporting_facts": supporting_facts,
                })

        return corroborations

    def find_contradictions(self, facts: list[Fact]) -> list[dict]:
        """Find facts that contradict each other."""
        contradictions = []

        for i, fact1 in enumerate(facts):
            contradicting_facts = []
            for fact2 in facts[i + 1:]:
                connection = self._compare_facts(fact1, fact2)
                if connection and connection.connection_type == ConnectionType.CONTRADICTS:
                    contradicting_facts.append({
                        "fact_id": fact2.id,
                        "statement": fact2.statement,
                        "strength": connection.strength,
                    })

            if contradicting_facts:
                contradictions.append({
                    "fact": {
                        "id": fact1.id,
                        "statement": fact1.statement,
                    },
                    "contradictions": contradicting_facts,
                })

        return contradictions
