"""Main orchestration engine for reverse engineering investigations."""

from datetime import datetime
from typing import Optional
import json
import os

from echo_engine.core.models import (
    Source,
    Fact,
    Timeline,
    Connection,
    ProvenanceChain,
    ProvenanceNode,
    Investigation,
    SourceType,
    FactStatus,
    ConnectionType,
    ConfidenceLevel,
)
from echo_engine.core.exceptions import (
    EchoEngineError,
    SourceNotFoundError,
    AnalysisError,
)


class ReverseEngineeringEngine:
    """
    Main engine for conducting reverse engineering investigations.

    Traces information back to its origins by:
    - Collecting sources from multiple inputs
    - Extracting facts from sources
    - Validating facts through cross-referencing
    - Reconstructing timelines
    - Building provenance chains
    - Generating comprehensive reports
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize the engine with optional configuration."""
        self.config = config or {}
        self.investigations: dict[str, Investigation] = {}
        self._source_index: dict[str, Source] = {}
        self._fact_index: dict[str, Fact] = {}

    def create_investigation(
        self,
        name: str,
        query: str,
        description: str = ""
    ) -> Investigation:
        """
        Create a new investigation.

        Args:
            name: Name of the investigation
            query: The main question or claim to investigate
            description: Optional description

        Returns:
            The created Investigation object
        """
        investigation = Investigation(
            name=name,
            query=query,
            description=description,
        )
        self.investigations[investigation.id] = investigation
        return investigation

    def add_source(
        self,
        investigation_id: str,
        name: str,
        content: str,
        source_type: SourceType = SourceType.TEXT,
        url: Optional[str] = None,
        filepath: Optional[str] = None,
        author: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[dict] = None,
    ) -> Source:
        """
        Add a source to an investigation.

        Args:
            investigation_id: ID of the investigation
            name: Name/title of the source
            content: The source content
            source_type: Type of source
            url: Optional URL
            filepath: Optional file path
            author: Optional author
            timestamp: When the source was created
            metadata: Additional metadata

        Returns:
            The created Source object
        """
        investigation = self._get_investigation(investigation_id)

        source = Source(
            name=name,
            content=content,
            source_type=source_type,
            url=url,
            filepath=filepath,
            author=author,
            timestamp=timestamp,
            metadata=metadata or {},
        )

        investigation.add_source(source)
        self._source_index[source.id] = source

        return source

    def add_source_from_file(
        self,
        investigation_id: str,
        filepath: str,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Source:
        """
        Add a source from a file.

        Args:
            investigation_id: ID of the investigation
            filepath: Path to the file
            name: Optional name (defaults to filename)
            metadata: Additional metadata

        Returns:
            The created Source object
        """
        if not os.path.exists(filepath):
            raise SourceNotFoundError(f"File not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        file_stats = os.stat(filepath)
        file_timestamp = datetime.fromtimestamp(file_stats.st_mtime)

        return self.add_source(
            investigation_id=investigation_id,
            name=name or os.path.basename(filepath),
            content=content,
            source_type=SourceType.FILE,
            filepath=filepath,
            timestamp=file_timestamp,
            metadata=metadata,
        )

    def extract_facts(
        self,
        investigation_id: str,
        source_id: Optional[str] = None,
    ) -> list[Fact]:
        """
        Extract facts from sources in an investigation.

        Uses pattern matching and NLP techniques to identify
        factual statements within source content.

        Args:
            investigation_id: ID of the investigation
            source_id: Optional specific source to analyze

        Returns:
            List of extracted Facts
        """
        investigation = self._get_investigation(investigation_id)
        extracted_facts = []

        sources = [self._get_source(source_id)] if source_id else investigation.sources

        for source in sources:
            facts = self._extract_facts_from_source(source)
            for fact in facts:
                investigation.add_fact(fact)
                self._fact_index[fact.id] = fact
                extracted_facts.append(fact)

        return extracted_facts

    def _extract_facts_from_source(self, source: Source) -> list[Fact]:
        """
        Extract facts from a single source.

        This is a simplified extraction that identifies sentences
        containing factual patterns. In production, this would use
        more sophisticated NLP.
        """
        facts = []
        sentences = self._split_into_sentences(source.content)

        for sentence in sentences:
            # Skip very short sentences
            if len(sentence.split()) < 4:
                continue

            # Look for factual patterns
            factual_indicators = [
                " is ", " are ", " was ", " were ", " has ", " have ",
                " occurred ", " happened ", " stated ", " reported ",
                " according to ", " found that ", " showed that ",
                " confirmed ", " revealed ", " discovered ",
            ]

            is_factual = any(indicator in sentence.lower() for indicator in factual_indicators)

            if is_factual:
                # Extract entities (simplified - looks for capitalized words)
                words = sentence.split()
                entities = [
                    w.strip(".,!?;:'\"")
                    for w in words
                    if w[0].isupper() and len(w) > 1
                ]

                # Extract keywords (simplified)
                keywords = self._extract_keywords(sentence)

                fact = Fact(
                    statement=sentence.strip(),
                    source_ids=[source.id],
                    context=source.name,
                    entities=entities,
                    keywords=keywords,
                )
                facts.append(fact)

        return facts

    def validate_facts(
        self,
        investigation_id: str,
        fact_ids: Optional[list[str]] = None,
    ) -> dict[str, FactStatus]:
        """
        Validate facts by cross-referencing sources.

        Args:
            investigation_id: ID of the investigation
            fact_ids: Optional list of specific fact IDs to validate

        Returns:
            Dictionary mapping fact IDs to their validation status
        """
        investigation = self._get_investigation(investigation_id)
        results = {}

        facts_to_validate = (
            [self._get_fact(fid) for fid in fact_ids]
            if fact_ids
            else investigation.facts
        )

        for fact in facts_to_validate:
            status = self._validate_fact(fact, investigation)
            fact.status = status
            fact.verified_at = datetime.now()
            results[fact.id] = status

        return results

    def _validate_fact(self, fact: Fact, investigation: Investigation) -> FactStatus:
        """
        Validate a single fact against other sources.

        Checks for:
        - Corroboration from other sources
        - Contradictions from other sources
        - Consistency of claims
        """
        supporting_sources = []
        contradicting_sources = []

        # Get keywords and entities from the fact
        fact_keywords = set(kw.lower() for kw in fact.keywords)
        fact_entities = set(e.lower() for e in fact.entities)

        for source in investigation.sources:
            if source.id in fact.source_ids:
                continue  # Skip the original source

            source_content_lower = source.content.lower()

            # Check for keyword overlap
            keyword_matches = sum(
                1 for kw in fact_keywords
                if kw in source_content_lower
            )

            # Check for entity mentions
            entity_matches = sum(
                1 for e in fact_entities
                if e in source_content_lower
            )

            if keyword_matches >= 2 or entity_matches >= 1:
                # Check for negation patterns
                negation_patterns = [
                    "not true", "false", "incorrect", "wrong",
                    "denied", "refuted", "contradicted",
                ]
                has_negation = any(
                    neg in source_content_lower
                    for neg in negation_patterns
                )

                if has_negation:
                    contradicting_sources.append(source.id)
                    fact.contradicting_evidence.append(source.id)
                else:
                    supporting_sources.append(source.id)
                    fact.supporting_evidence.append(source.id)

        # Determine status based on evidence
        if contradicting_sources and supporting_sources:
            return FactStatus.DISPUTED
        elif contradicting_sources:
            return FactStatus.REFUTED
        elif len(supporting_sources) >= 2:
            fact.confidence = ConfidenceLevel.HIGH
            return FactStatus.VERIFIED
        elif supporting_sources:
            fact.confidence = ConfidenceLevel.MEDIUM
            return FactStatus.PARTIALLY_VERIFIED
        else:
            return FactStatus.UNVERIFIED

    def build_timeline(
        self,
        investigation_id: str,
        name: str,
        description: str = "",
    ) -> Timeline:
        """
        Build a timeline from events found in sources.

        Args:
            investigation_id: ID of the investigation
            name: Name of the timeline
            description: Description of the timeline

        Returns:
            The constructed Timeline
        """
        from echo_engine.core.models import TimelineEvent

        investigation = self._get_investigation(investigation_id)

        timeline = Timeline(
            name=name,
            description=description,
        )

        # Extract temporal information from facts
        for fact in investigation.facts:
            event_time = self._extract_temporal_info(fact.statement)
            if event_time:
                event = TimelineEvent(
                    description=fact.statement,
                    timestamp=event_time,
                    source_ids=fact.source_ids,
                    fact_ids=[fact.id],
                    entities=fact.entities,
                    confidence=fact.confidence,
                )
                timeline.add_event(event)

        investigation.timelines.append(timeline)
        return timeline

    def _extract_temporal_info(self, text: str) -> Optional[datetime]:
        """
        Extract temporal information from text.

        This is a simplified implementation that looks for common
        date patterns. Production would use more sophisticated parsing.
        """
        import re

        # Pattern for dates like "January 15, 2024" or "15 January 2024"
        months = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ]

        text_lower = text.lower()

        for i, month in enumerate(months, 1):
            if month in text_lower:
                # Try to find associated day and year
                day_pattern = r"(\d{1,2})"
                year_pattern = r"(20\d{2}|19\d{2})"

                day_match = re.search(day_pattern, text)
                year_match = re.search(year_pattern, text)

                if day_match and year_match:
                    try:
                        return datetime(
                            int(year_match.group(1)),
                            i,
                            int(day_match.group(1))
                        )
                    except ValueError:
                        pass

        return None

    def find_connections(
        self,
        investigation_id: str,
    ) -> list[Connection]:
        """
        Find connections between facts and sources.

        Analyzes the investigation to identify relationships
        between different pieces of information.

        Args:
            investigation_id: ID of the investigation

        Returns:
            List of discovered Connections
        """
        investigation = self._get_investigation(investigation_id)
        connections = []

        # Find connections between facts
        for i, fact1 in enumerate(investigation.facts):
            for fact2 in investigation.facts[i + 1:]:
                connection = self._analyze_fact_connection(fact1, fact2)
                if connection:
                    connections.append(connection)

        investigation.connections.extend(connections)
        return connections

    def _analyze_fact_connection(
        self,
        fact1: Fact,
        fact2: Fact
    ) -> Optional[Connection]:
        """Analyze connection between two facts."""
        # Check for shared entities
        shared_entities = set(e.lower() for e in fact1.entities) & set(e.lower() for e in fact2.entities)

        # Check for shared keywords
        shared_keywords = set(k.lower() for k in fact1.keywords) & set(k.lower() for k in fact2.keywords)

        if not shared_entities and len(shared_keywords) < 2:
            return None

        # Determine connection type based on validation status
        if fact1.status == FactStatus.VERIFIED and fact2.status == FactStatus.VERIFIED:
            connection_type = ConnectionType.CORROBORATES
            strength = 0.8
        elif fact1.status == FactStatus.REFUTED or fact2.status == FactStatus.REFUTED:
            connection_type = ConnectionType.CONTRADICTS
            strength = 0.7
        else:
            connection_type = ConnectionType.RELATED_TO
            strength = 0.5 + (len(shared_entities) * 0.1) + (len(shared_keywords) * 0.05)

        return Connection(
            source_entity_id=fact1.id,
            target_entity_id=fact2.id,
            connection_type=connection_type,
            strength=min(strength, 1.0),
            description=f"Shared entities: {shared_entities}, keywords: {shared_keywords}",
            evidence_ids=fact1.source_ids + fact2.source_ids,
        )

    def build_provenance_chain(
        self,
        investigation_id: str,
        fact_id: str,
        name: str = "",
    ) -> ProvenanceChain:
        """
        Build a provenance chain for a fact, tracing it back to origins.

        Args:
            investigation_id: ID of the investigation
            fact_id: ID of the fact to trace
            name: Optional name for the chain

        Returns:
            The constructed ProvenanceChain
        """
        investigation = self._get_investigation(investigation_id)
        fact = self._get_fact(fact_id)

        chain = ProvenanceChain(
            name=name or f"Provenance for: {fact.statement[:50]}...",
        )

        # Create node for the fact itself
        fact_node = ProvenanceNode(
            entity_id=fact.id,
            entity_type="fact",
            timestamp=fact.extracted_at,
            transformation="extracted",
            parent_ids=[],
        )

        # Create nodes for source documents
        for source_id in fact.source_ids:
            source = self._get_source(source_id)
            source_node = ProvenanceNode(
                entity_id=source.id,
                entity_type="source",
                timestamp=source.timestamp or source.collected_at,
                transformation="original",
            )
            chain.add_node(source_node)
            fact_node.parent_ids.append(source_node.id)

            if not chain.root_id:
                chain.root_id = source_node.id

        chain.add_node(fact_node)
        investigation.provenance_chains.append(chain)

        return chain

    def trace_to_origin(
        self,
        investigation_id: str,
        entity_id: str,
    ) -> list[dict]:
        """
        Trace an entity back to its original source(s).

        Args:
            investigation_id: ID of the investigation
            entity_id: ID of the entity to trace

        Returns:
            List of trace results with origin information
        """
        investigation = self._get_investigation(investigation_id)
        traces = []

        for chain in investigation.provenance_chains:
            if entity_id in [n.entity_id for n in chain.nodes.values()]:
                # Find the node
                for node in chain.nodes.values():
                    if node.entity_id == entity_id:
                        path = chain.trace_to_origin(node.id)
                        traces.append({
                            "chain_id": chain.id,
                            "chain_name": chain.name,
                            "path": [n.to_dict() for n in path],
                            "origin_id": chain.root_id,
                        })
                        break

        return traces

    def generate_report(
        self,
        investigation_id: str,
        format: str = "dict",
    ) -> dict | str:
        """
        Generate a comprehensive report for an investigation.

        Args:
            investigation_id: ID of the investigation
            format: Output format ('dict', 'json', 'markdown')

        Returns:
            The report in the specified format
        """
        investigation = self._get_investigation(investigation_id)

        report = {
            "investigation": investigation.to_dict(),
            "summary": {
                "total_sources": len(investigation.sources),
                "total_facts": len(investigation.facts),
                "verified_facts": len(investigation.get_verified_facts()),
                "disputed_facts": len(investigation.get_disputed_facts()),
                "total_connections": len(investigation.connections),
                "total_timelines": len(investigation.timelines),
                "provenance_chains": len(investigation.provenance_chains),
            },
            "confidence_assessment": self._assess_confidence(investigation),
            "generated_at": datetime.now().isoformat(),
        }

        if format == "json":
            return json.dumps(report, indent=2)
        elif format == "markdown":
            return self._report_to_markdown(report)
        else:
            return report

    def _assess_confidence(self, investigation: Investigation) -> dict:
        """Assess overall confidence in investigation findings."""
        if not investigation.facts:
            return {
                "level": "insufficient_data",
                "score": 0,
                "explanation": "No facts extracted yet",
            }

        verified = len(investigation.get_verified_facts())
        disputed = len(investigation.get_disputed_facts())
        total = len(investigation.facts)

        verification_rate = verified / total if total > 0 else 0
        dispute_rate = disputed / total if total > 0 else 0

        score = (verification_rate * 100) - (dispute_rate * 50)
        score = max(0, min(100, score))

        if score >= 80:
            level = "high"
            explanation = "Strong evidence with multiple verified facts"
        elif score >= 60:
            level = "medium"
            explanation = "Moderate evidence with some verification"
        elif score >= 40:
            level = "low"
            explanation = "Limited verification, some disputes"
        else:
            level = "very_low"
            explanation = "Insufficient verification or significant disputes"

        return {
            "level": level,
            "score": round(score, 2),
            "explanation": explanation,
            "verification_rate": round(verification_rate * 100, 2),
            "dispute_rate": round(dispute_rate * 100, 2),
        }

    def _report_to_markdown(self, report: dict) -> str:
        """Convert report to markdown format."""
        inv = report["investigation"]
        summary = report["summary"]
        confidence = report["confidence_assessment"]

        md = f"""# Investigation Report: {inv['name']}

## Overview
- **Query**: {inv['query']}
- **Description**: {inv['description']}
- **Status**: {inv['status']}
- **Created**: {inv['created_at']}

## Summary
- Total Sources: {summary['total_sources']}
- Total Facts Extracted: {summary['total_facts']}
- Verified Facts: {summary['verified_facts']}
- Disputed Facts: {summary['disputed_facts']}
- Connections Found: {summary['total_connections']}
- Timelines Built: {summary['total_timelines']}

## Confidence Assessment
- **Level**: {confidence['level'].upper()}
- **Score**: {confidence['score']}/100
- **Explanation**: {confidence['explanation']}

## Sources
"""
        for source in inv['sources']:
            md += f"\n### {source['name']}\n"
            md += f"- Type: {source['source_type']}\n"
            md += f"- Collected: {source['collected_at']}\n"
            if source['author']:
                md += f"- Author: {source['author']}\n"

        md += "\n## Verified Facts\n"
        for fact in inv['facts']:
            if fact['status'] == 'verified':
                md += f"\n- **{fact['statement']}**\n"
                md += f"  - Confidence: {fact['confidence']}/5\n"
                md += f"  - Entities: {', '.join(fact['entities'])}\n"

        if inv['conclusions']:
            md += "\n## Conclusions\n"
            for conclusion in inv['conclusions']:
                md += f"- {conclusion}\n"

        md += f"\n---\n*Report generated: {report['generated_at']}*\n"

        return md

    def save_investigation(self, investigation_id: str, filepath: str):
        """Save investigation to a JSON file."""
        investigation = self._get_investigation(investigation_id)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(investigation.to_dict(), f, indent=2)

    def load_investigation(self, filepath: str) -> Investigation:
        """Load investigation from a JSON file."""
        if not os.path.exists(filepath):
            raise SourceNotFoundError(f"File not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Reconstruct investigation (simplified - full implementation would
        # reconstruct all nested objects)
        investigation = Investigation(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            query=data.get("query", ""),
            status=data.get("status", "in_progress"),
            conclusions=data.get("conclusions", []),
        )

        self.investigations[investigation.id] = investigation
        return investigation

    def _get_investigation(self, investigation_id: str) -> Investigation:
        """Get investigation by ID or raise error."""
        if investigation_id not in self.investigations:
            raise AnalysisError(f"Investigation not found: {investigation_id}")
        return self.investigations[investigation_id]

    def _get_source(self, source_id: str) -> Source:
        """Get source by ID or raise error."""
        if source_id not in self._source_index:
            raise SourceNotFoundError(f"Source not found: {source_id}")
        return self._source_index[source_id]

    def _get_fact(self, fact_id: str) -> Fact:
        """Get fact by ID or raise error."""
        if fact_id not in self._fact_index:
            raise AnalysisError(f"Fact not found: {fact_id}")
        return self._fact_index[fact_id]

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        import re
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from text."""
        # Simple keyword extraction - filter common words
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "above",
            "below", "between", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all", "each",
            "few", "more", "most", "other", "some", "such", "no", "nor",
            "not", "only", "own", "same", "so", "than", "too", "very",
            "can", "just", "don", "now", "and", "but", "or", "if", "that",
            "this", "these", "those", "it", "its", "their", "they", "them",
        }

        words = text.lower().split()
        keywords = [
            w.strip(".,!?;:'\"")
            for w in words
            if w.strip(".,!?;:'\"") not in stop_words
            and len(w) > 2
        ]

        # Return unique keywords
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords[:10]  # Limit to top 10
