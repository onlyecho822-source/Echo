"""
Aletheia Truth Verification Engine - Correlation Engine (Panopticon)

The central analytical brain that connects evidence across domains,
identifies patterns, and detects narrative discrepancies.
"""

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict

import sys
sys.path.insert(0, '/home/user/Echo')

from aletheia.core.models import (
    Evidence, EvidenceType, Artifact, Narrative, HistoricalEvent,
    TimePeriod, GeoLocation, TruthAssertion
)


@dataclass
class CorrelationResult:
    """Result of correlating multiple evidence items."""
    evidence_ids: list[str]
    correlation_type: str
    strength: float
    description: str
    implications: list[str]
    discrepancies: list[str]
    confidence: float


@dataclass
class DiscrepancyReport:
    """Report on discrepancies found in evidence or narratives."""
    discrepancy_type: str
    description: str
    evidence_a: Evidence
    evidence_b: Evidence
    severity: str  # minor, moderate, severe, critical
    implications: list[str]
    resolution_suggestions: list[str]


@dataclass
class PatternMatch:
    """A pattern found across multiple data points."""
    pattern_type: str
    description: str
    occurrences: list[dict]
    cultures: list[str]
    time_span: Optional[TimePeriod]
    significance: str
    confidence: float


@dataclass
class NarrativeAnalysis:
    """Analysis of a narrative's consistency with evidence."""
    narrative_id: str
    overall_consistency: float
    supporting_evidence: list[Evidence]
    contradicting_evidence: list[Evidence]
    unexplained_elements: list[str]
    bias_indicators: list[str]
    alternative_interpretations: list[str]


class CorrelationEngine:
    """
    The Panopticon - correlates evidence across all domains.

    Capabilities:
    - Cross-domain evidence correlation
    - Temporal and spatial pattern detection
    - Narrative consistency checking
    - Discrepancy identification
    - Network analysis of connections
    """

    def __init__(self):
        self.evidence_store: dict[str, Evidence] = {}
        self.correlations: list[CorrelationResult] = []
        self.patterns: list[PatternMatch] = []

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the correlation store."""
        self.evidence_store[evidence.id] = evidence

    def correlate_evidence(self, evidence_list: list[Evidence]) -> list[CorrelationResult]:
        """
        Find correlations between pieces of evidence.

        Args:
            evidence_list: List of evidence items to correlate

        Returns:
            List of found correlations
        """
        results = []

        # Add all evidence to store
        for ev in evidence_list:
            self.add_evidence(ev)

        # Check temporal correlations
        temporal = self._find_temporal_correlations(evidence_list)
        results.extend(temporal)

        # Check spatial correlations
        spatial = self._find_spatial_correlations(evidence_list)
        results.extend(spatial)

        # Check thematic correlations
        thematic = self._find_thematic_correlations(evidence_list)
        results.extend(thematic)

        # Check cross-domain correlations
        cross_domain = self._find_cross_domain_correlations(evidence_list)
        results.extend(cross_domain)

        self.correlations.extend(results)
        return results

    def _find_temporal_correlations(self, evidence_list: list[Evidence]) -> list[CorrelationResult]:
        """Find evidence that correlates temporally."""
        results = []

        # Group by overlapping time periods
        temporal_groups = defaultdict(list)

        for ev in evidence_list:
            if ev.time_period:
                # Create bins for centuries
                start_century = ev.time_period.start_year // 100
                end_century = ev.time_period.end_year // 100
                for century in range(start_century, end_century + 1):
                    temporal_groups[century].append(ev)

        # Find groups with multiple evidence types
        for century, group in temporal_groups.items():
            if len(group) > 1:
                types = set(ev.evidence_type for ev in group)
                if len(types) > 1:
                    results.append(CorrelationResult(
                        evidence_ids=[ev.id for ev in group],
                        correlation_type="temporal",
                        strength=min(len(group) / 5, 1.0),
                        description=f"Multiple evidence types ({', '.join(t.value for t in types)}) "
                                   f"from {century * 100}s",
                        implications=[
                            f"Evidence convergence in {century * 100}s suggests significant historical moment"
                        ],
                        discrepancies=[],
                        confidence=0.7
                    ))

        return results

    def _find_spatial_correlations(self, evidence_list: list[Evidence]) -> list[CorrelationResult]:
        """Find evidence that correlates spatially."""
        results = []

        # Group by location
        spatial_groups = defaultdict(list)

        for ev in evidence_list:
            if ev.location:
                # Use region as grouping key
                spatial_groups[ev.location.region].append(ev)

        # Find groups with multiple evidence types
        for region, group in spatial_groups.items():
            if len(group) > 1:
                types = set(ev.evidence_type for ev in group)
                if len(types) > 1:
                    results.append(CorrelationResult(
                        evidence_ids=[ev.id for ev in group],
                        correlation_type="spatial",
                        strength=min(len(group) / 5, 1.0),
                        description=f"Multiple evidence types from {region}",
                        implications=[
                            f"Regional evidence cluster in {region} may indicate cultural hub or significant site"
                        ],
                        discrepancies=[],
                        confidence=0.65
                    ))

        return results

    def _find_thematic_correlations(self, evidence_list: list[Evidence]) -> list[CorrelationResult]:
        """Find evidence that shares thematic elements."""
        results = []

        # Extract themes from evidence content
        theme_groups = defaultdict(list)
        themes = [
            "astronomical", "mathematical", "cosmological", "religious",
            "technological", "migration", "conquest", "trade"
        ]

        for ev in evidence_list:
            content_lower = ev.content.lower() if ev.content else ""
            desc_lower = ev.description.lower() if ev.description else ""
            combined = content_lower + " " + desc_lower

            for theme in themes:
                if theme in combined:
                    theme_groups[theme].append(ev)

        # Report significant thematic clusters
        for theme, group in theme_groups.items():
            if len(group) > 1:
                types = set(ev.evidence_type for ev in group)
                results.append(CorrelationResult(
                    evidence_ids=[ev.id for ev in group],
                    correlation_type="thematic",
                    strength=min(len(group) / 4, 1.0),
                    description=f"Thematic cluster around '{theme}' across {len(types)} evidence types",
                    implications=[
                        f"Multiple independent sources reference '{theme}' theme - "
                        f"may indicate historical reality"
                    ],
                    discrepancies=[],
                    confidence=0.6
                ))

        return results

    def _find_cross_domain_correlations(self, evidence_list: list[Evidence]) -> list[CorrelationResult]:
        """Find correlations that span different evidence domains."""
        results = []

        # Group by evidence type
        type_groups = defaultdict(list)
        for ev in evidence_list:
            type_groups[ev.evidence_type].append(ev)

        # Look for cross-domain support
        # e.g., genetic + archaeological + linguistic all pointing to same conclusion
        if (EvidenceType.GENETIC in type_groups and
            EvidenceType.ARCHAEOLOGICAL in type_groups):

            genetic = type_groups[EvidenceType.GENETIC]
            archaeological = type_groups[EvidenceType.ARCHAEOLOGICAL]

            # Check for geographic overlap
            for g_ev in genetic:
                for a_ev in archaeological:
                    if g_ev.location and a_ev.location:
                        distance = g_ev.location.distance_to(a_ev.location)
                        if distance < 500:  # Within 500km
                            results.append(CorrelationResult(
                                evidence_ids=[g_ev.id, a_ev.id],
                                correlation_type="cross_domain_genetic_archaeological",
                                strength=0.85,
                                description=f"Genetic and archaeological evidence converge "
                                           f"in {g_ev.location.region}",
                                implications=[
                                    "Strong multi-domain support for population presence",
                                    "Physical and biological evidence align"
                                ],
                                discrepancies=[],
                                confidence=0.8
                            ))

        if (EvidenceType.LINGUISTIC in type_groups and
            EvidenceType.SYMBOLIC in type_groups):

            results.append(CorrelationResult(
                evidence_ids=[ev.id for ev in type_groups[EvidenceType.LINGUISTIC] +
                             type_groups[EvidenceType.SYMBOLIC]],
                correlation_type="cross_domain_linguistic_symbolic",
                strength=0.75,
                description="Linguistic and symbolic evidence correlate",
                implications=[
                    "Language and symbolism support each other",
                    "Cultural continuity indicated"
                ],
                discrepancies=[],
                confidence=0.7
            ))

        return results

    def find_discrepancies(self, evidence_list: list[Evidence]) -> list[DiscrepancyReport]:
        """
        Find discrepancies between pieces of evidence.

        These are crucial for identifying where narratives may be false.
        """
        reports = []

        # Compare evidence pairs for inconsistencies
        for i, ev_a in enumerate(evidence_list):
            for ev_b in evidence_list[i+1:]:
                # Check temporal discrepancy
                if ev_a.time_period and ev_b.time_period:
                    if not ev_a.time_period.overlaps(ev_b.time_period):
                        # Check if they should overlap (same topic)
                        if self._same_topic(ev_a, ev_b):
                            reports.append(DiscrepancyReport(
                                discrepancy_type="temporal",
                                description=f"Evidence items about same topic have non-overlapping dates",
                                evidence_a=ev_a,
                                evidence_b=ev_b,
                                severity="moderate",
                                implications=[
                                    "One source may have incorrect dating",
                                    "May indicate different events conflated into one narrative"
                                ],
                                resolution_suggestions=[
                                    "Independent dating analysis",
                                    "Review original sources for dating methodology"
                                ]
                            ))

                # Check spatial discrepancy
                if ev_a.location and ev_b.location:
                    distance = ev_a.location.distance_to(ev_b.location)
                    if distance > 1000 and self._same_topic(ev_a, ev_b):
                        reports.append(DiscrepancyReport(
                            discrepancy_type="spatial",
                            description=f"Evidence about same topic from locations {distance:.0f}km apart",
                            evidence_a=ev_a,
                            evidence_b=ev_b,
                            severity="moderate",
                            implications=[
                                "May indicate trade or cultural transmission",
                                "One source may have wrong origin attribution"
                            ],
                            resolution_suggestions=[
                                "Investigate potential trade routes",
                                "Verify claimed origins of artifacts"
                            ]
                        ))

                # Check material discrepancy (for material evidence)
                if (ev_a.evidence_type == EvidenceType.MATERIAL and
                    ev_b.evidence_type == EvidenceType.MATERIAL):
                    if ev_a.material_data and ev_b.material_data:
                        # Compare claimed origins with material origins
                        pass  # Would implement detailed material comparison

        return reports

    def _same_topic(self, ev_a: Evidence, ev_b: Evidence) -> bool:
        """Check if two evidence items are about the same topic."""
        # Simple keyword overlap check
        if not ev_a.content or not ev_b.content:
            return False

        words_a = set(ev_a.content.lower().split())
        words_b = set(ev_b.content.lower().split())

        overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)
        return overlap > 0.3

    def analyze_narrative(self, narrative: Narrative,
                         evidence_list: list[Evidence]) -> NarrativeAnalysis:
        """
        Analyze how well a narrative is supported by evidence.

        This is the core function for truth verification.
        """
        supporting = []
        contradicting = []
        unexplained = []
        biases = []

        # Check each piece of evidence against narrative
        for evidence in evidence_list:
            support_score = self._calculate_support(narrative, evidence)

            if support_score > 0.6:
                supporting.append(evidence)
            elif support_score < 0.3:
                contradicting.append(evidence)

        # Check for bias indicators
        biases = self._identify_biases(narrative, evidence_list)

        # Find unexplained elements
        unexplained = self._find_unexplained(narrative, evidence_list)

        # Calculate overall consistency
        if supporting or contradicting:
            total = len(supporting) + len(contradicting)
            consistency = len(supporting) / total
        else:
            consistency = 0.5  # No strong evidence either way

        # Generate alternative interpretations
        alternatives = self._generate_alternatives(
            narrative, supporting, contradicting
        )

        return NarrativeAnalysis(
            narrative_id=narrative.id,
            overall_consistency=consistency,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            unexplained_elements=unexplained,
            bias_indicators=biases,
            alternative_interpretations=alternatives
        )

    def _calculate_support(self, narrative: Narrative, evidence: Evidence) -> float:
        """Calculate how much evidence supports a narrative."""
        score = 0.5  # Neutral baseline

        # Check temporal consistency
        if evidence.time_period and narrative.events:
            for event in narrative.events:
                if event.time_period and evidence.time_period.overlaps(event.time_period):
                    score += 0.1

        # Check if evidence source is in narrative
        if evidence.source and narrative.description:
            if evidence.source.lower() in narrative.description.lower():
                score += 0.2

        # Check for contradicting elements
        if evidence.potential_biases:
            for bias in evidence.potential_biases:
                if "contradicts" in bias.lower() or "conflict" in bias.lower():
                    score -= 0.3

        return max(0, min(1, score))

    def _identify_biases(self, narrative: Narrative,
                        evidence_list: list[Evidence]) -> list[str]:
        """Identify potential biases in a narrative."""
        biases = []

        # Check beneficiaries
        if narrative.beneficiaries:
            biases.append(
                f"Narrative benefits: {', '.join(narrative.beneficiaries)}. "
                f"Check for motivated reasoning."
            )

        # Check suppressed voices
        if narrative.suppressed_voices:
            biases.append(
                f"Narrative marginalizes: {', '.join(narrative.suppressed_voices)}. "
                f"Seek alternative sources from these perspectives."
            )

        # Check evidence source distribution
        source_types = defaultdict(int)
        for ev in evidence_list:
            source_types[ev.evidence_type] += 1

        if len(source_types) < 3:
            biases.append(
                f"Limited evidence diversity ({len(source_types)} types). "
                f"Seek additional evidence domains."
            )

        return biases

    def _find_unexplained(self, narrative: Narrative,
                         evidence_list: list[Evidence]) -> list[str]:
        """Find elements not explained by available evidence."""
        unexplained = []

        # Check narrative events
        for event in narrative.events:
            has_support = False
            for evidence in evidence_list:
                if evidence.time_period and event.time_period:
                    if evidence.time_period.overlaps(event.time_period):
                        has_support = True
                        break

            if not has_support:
                unexplained.append(f"Event '{event.name}' lacks supporting evidence")

        return unexplained

    def _generate_alternatives(self, narrative: Narrative,
                              supporting: list[Evidence],
                              contradicting: list[Evidence]) -> list[str]:
        """Generate alternative interpretations based on evidence."""
        alternatives = []

        # If significant contradicting evidence
        if len(contradicting) > len(supporting):
            alternatives.append(
                "ALTERNATIVE: The contradicting evidence suggests the narrative "
                "may be fundamentally incorrect. Consider reversing core assumptions."
            )

        # If evidence from different regions
        regions = set()
        for ev in supporting + contradicting:
            if ev.location:
                regions.add(ev.location.region)

        if len(regions) > 2:
            alternatives.append(
                f"ALTERNATIVE: Evidence from {len(regions)} regions suggests "
                f"the narrative may conflate multiple distinct events or cultures."
            )

        return alternatives

    def find_patterns(self, evidence_list: list[Evidence]) -> list[PatternMatch]:
        """
        Find recurring patterns across evidence.

        Patterns that appear across isolated cultures are strong
        indicators of either shared origin or universal truth.
        """
        patterns = []

        # Check for recurring symbols
        symbol_occurrences = defaultdict(list)
        for ev in evidence_list:
            for symbol in ev.symbols:
                symbol_occurrences[symbol.name].append({
                    "evidence_id": ev.id,
                    "culture": ev.location.region if ev.location else "Unknown",
                    "time_period": ev.time_period
                })

        # Report significant symbol patterns
        for symbol_name, occurrences in symbol_occurrences.items():
            if len(occurrences) > 2:
                cultures = list(set(o["culture"] for o in occurrences))
                patterns.append(PatternMatch(
                    pattern_type="symbol_recurrence",
                    description=f"Symbol '{symbol_name}' appears in {len(cultures)} cultures",
                    occurrences=occurrences,
                    cultures=cultures,
                    time_span=self._calculate_time_span(occurrences),
                    significance=f"Cross-cultural presence of '{symbol_name}' suggests "
                                f"shared origin or universal concept",
                    confidence=min(len(occurrences) / 5, 1.0)
                ))

        self.patterns.extend(patterns)
        return patterns

    def _calculate_time_span(self, occurrences: list[dict]) -> Optional[TimePeriod]:
        """Calculate the total time span covered by occurrences."""
        starts = []
        ends = []

        for occ in occurrences:
            if occ.get("time_period"):
                period = occ["time_period"]
                starts.append(period.start_year)
                ends.append(period.end_year)

        if starts and ends:
            return TimePeriod(min(starts), max(ends))
        return None

    def generate_truth_assertion(self, correlations: list[CorrelationResult],
                                discrepancies: list[DiscrepancyReport],
                                patterns: list[PatternMatch],
                                claim: str) -> TruthAssertion:
        """
        Generate a truth assertion based on correlation analysis.

        This is the output that tells us what we can reasonably assert as true.
        """
        # Gather all supporting and contradicting evidence
        supporting = []
        contradicting = []

        for corr in correlations:
            if corr.strength > 0.6:
                for ev_id in corr.evidence_ids:
                    if ev_id in self.evidence_store:
                        supporting.append(self.evidence_store[ev_id])

        for disc in discrepancies:
            if disc.severity in ["severe", "critical"]:
                contradicting.append(disc.evidence_a)
                contradicting.append(disc.evidence_b)

        # Calculate confidence scores
        evidence_strength = len(supporting) / max(len(supporting) + len(contradicting), 1)

        correlation_strength = sum(c.strength for c in correlations) / max(len(correlations), 1)

        pattern_confidence = sum(p.confidence for p in patterns) / max(len(patterns), 1)

        # Overall truth confidence
        truth_confidence = (
            evidence_strength * 0.4 +
            correlation_strength * 0.3 +
            pattern_confidence * 0.3
        )

        # Generate conclusions and questions
        conclusions = []
        questions = []
        recommendations = []

        if truth_confidence > 0.7:
            conclusions.append(
                f"SUPPORTED: The claim '{claim}' is supported by converging evidence "
                f"across {len(correlations)} correlations."
            )
        elif truth_confidence > 0.4:
            conclusions.append(
                f"PARTIALLY SUPPORTED: The claim '{claim}' has mixed evidence. "
                f"Further investigation needed."
            )
        else:
            conclusions.append(
                f"CONTESTED: The claim '{claim}' is contradicted by available evidence."
            )

        # Generate questions
        if discrepancies:
            questions.append(
                "Why do certain evidence items contradict each other? "
                "Is there a resolution that accounts for both?"
            )

        if patterns:
            questions.append(
                f"What explains the recurring pattern across {len(patterns)} cultures? "
                f"Common origin, universal human experience, or historical transmission?"
            )

        # Generate recommendations
        if evidence_strength < 0.5:
            recommendations.append("Seek additional independent evidence sources")

        if len(set(ev.evidence_type for ev in supporting)) < 3:
            recommendations.append("Diversify evidence types for stronger corroboration")

        return TruthAssertion(
            assertion=claim,
            domain="historical",
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            truth_confidence=truth_confidence,
            evidence_strength=evidence_strength,
            source_reliability=0.7,  # Would be calculated from source analysis
            cross_domain_correlation=correlation_strength,
            conclusion="; ".join(conclusions),
            next_questions=questions,
            recommended_investigations=recommendations
        )
