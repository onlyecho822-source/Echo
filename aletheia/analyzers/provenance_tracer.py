"""
Aletheia Truth Verification Engine - Provenance Tracer

Tracks the ownership history of artifacts, identifies gaps,
documents theft and colonial plunder, and builds repatriation cases.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import sys
sys.path.insert(0, '/home/user/Echo')

from aletheia.core.models import (
    Artifact, Evidence, EvidenceType, TimePeriod, GeoLocation,
    HistoricalEvent
)


@dataclass
class ProvenanceRecord:
    """A single record in an artifact's ownership history."""
    period: TimePeriod
    holder: str
    holder_type: str  # individual, institution, state, unknown
    location: GeoLocation
    acquisition_method: str  # purchase, gift, inheritance, conquest, theft, unknown
    documentation: list[str]
    suspicious_flags: list[str]
    confidence: float


@dataclass
class ProvenanceGap:
    """An unexplained gap in provenance records."""
    gap_period: TimePeriod
    last_known_holder: str
    next_known_holder: str
    possible_explanations: list[str]
    historical_context: str  # wars, colonial expeditions, etc.
    theft_probability: float


@dataclass
class ProvenanceAnalysis:
    """Complete provenance analysis for an artifact."""
    artifact_id: str
    complete_chain: list[ProvenanceRecord]
    gaps: list[ProvenanceGap]
    theft_indicators: list[str]
    colonial_connection: bool
    legitimate_acquisition: bool
    repatriation_strength: float
    summary: str


class ProvenanceTracer:
    """
    Traces artifact provenance and ownership history.

    Capabilities:
    - Building complete ownership chains
    - Identifying gaps and suspicious transfers
    - Documenting colonial-era acquisitions
    - Assessing repatriation claims
    - Cross-referencing with historical events
    """

    def __init__(self):
        # Known colonial expeditions and their artifact acquisitions
        self.colonial_expeditions = {
            "napoleon_egypt": {
                "period": TimePeriod(1798, 1801),
                "region": GeoLocation(30.0, 31.0, "Egypt", "North Africa", 500),
                "artifacts_types": ["egyptian", "coptic", "greco_roman"],
                "current_holders": ["Louvre", "British Museum"]
            },
            "benin_punitive": {
                "period": TimePeriod(1897, 1897),
                "region": GeoLocation(6.3, 5.6, "Benin City", "Nigeria", 50),
                "artifacts_types": ["bronze", "ivory", "coral"],
                "current_holders": ["British Museum", "Ethnological Museum Berlin", "Various"]
            },
            "maqdala_expedition": {
                "period": TimePeriod(1868, 1868),
                "region": GeoLocation(11.4, 39.0, "Maqdala", "Ethiopia", 50),
                "artifacts_types": ["manuscripts", "religious", "royal"],
                "current_holders": ["British Museum", "V&A", "Royal Collection"]
            },
            "boxer_rebellion_looting": {
                "period": TimePeriod(1900, 1901),
                "region": GeoLocation(39.9, 116.4, "Beijing", "China", 100),
                "artifacts_types": ["imperial", "jade", "porcelain", "manuscripts"],
                "current_holders": ["Various European museums", "Private collections"]
            },
            "parthenon_removal": {
                "period": TimePeriod(1801, 1812),
                "region": GeoLocation(37.97, 23.73, "Athens", "Greece", 10),
                "artifacts_types": ["marble", "architectural", "sculptural"],
                "current_holders": ["British Museum"]
            }
        }

        # Acquisition methods and their legitimacy scores
        self.acquisition_legitimacy = {
            "direct_commission": 1.0,
            "purchase_market": 0.8,
            "gift_documented": 0.9,
            "inheritance": 0.85,
            "archaeological_legal": 0.75,
            "purchase_private": 0.6,
            "gift_undocumented": 0.5,
            "conquest_treaty": 0.3,
            "unknown": 0.2,
            "looting_documented": 0.0,
            "theft": 0.0
        }

        # Museums with significant contested collections
        self.museums_of_interest = {
            "british_museum": {
                "location": GeoLocation(51.52, -0.13, "London", "UK", 1),
                "contested_collections": ["Parthenon Marbles", "Benin Bronzes", "Rosetta Stone"],
                "acquisition_periods": [TimePeriod(1750, 1920)]
            },
            "louvre": {
                "location": GeoLocation(48.86, 2.34, "Paris", "France", 1),
                "contested_collections": ["Egyptian collection", "African art"],
                "acquisition_periods": [TimePeriod(1798, 1900)]
            },
            "neues_museum": {
                "location": GeoLocation(52.52, 13.40, "Berlin", "Germany", 1),
                "contested_collections": ["Nefertiti Bust", "Ishtar Gate"],
                "acquisition_periods": [TimePeriod(1840, 1920)]
            },
            "vatican_museums": {
                "location": GeoLocation(41.91, 12.45, "Vatican City", "Vatican", 1),
                "contested_collections": ["Egyptian obelisks", "Codices", "Classical sculpture"],
                "acquisition_periods": [TimePeriod(100, 1900)]
            },
            "metropolitan_museum": {
                "location": GeoLocation(40.78, -73.96, "New York", "USA", 1),
                "contested_collections": ["Various antiquities"],
                "acquisition_periods": [TimePeriod(1870, 1970)]
            }
        }

    def trace_provenance(self, artifact: Artifact) -> ProvenanceAnalysis:
        """
        Build complete provenance analysis for an artifact.

        Args:
            artifact: The artifact to trace

        Returns:
            Comprehensive provenance analysis
        """
        # Build ownership chain from artifact data
        chain = self._build_ownership_chain(artifact)

        # Identify gaps
        gaps = self._identify_gaps(chain, artifact)

        # Check for theft indicators
        theft_indicators = self._check_theft_indicators(artifact, chain, gaps)

        # Check colonial connections
        colonial = self._check_colonial_connection(artifact, chain)

        # Assess legitimacy
        legitimate = self._assess_legitimacy(chain, gaps, theft_indicators)

        # Calculate repatriation strength
        repatriation = self._calculate_repatriation_strength(
            artifact, chain, gaps, theft_indicators, colonial
        )

        # Generate summary
        summary = self._generate_summary(
            artifact, chain, gaps, theft_indicators, colonial, repatriation
        )

        return ProvenanceAnalysis(
            artifact_id=artifact.id,
            complete_chain=chain,
            gaps=gaps,
            theft_indicators=theft_indicators,
            colonial_connection=colonial,
            legitimate_acquisition=legitimate,
            repatriation_strength=repatriation,
            summary=summary
        )

    def _build_ownership_chain(self, artifact: Artifact) -> list[ProvenanceRecord]:
        """Build the ownership chain from artifact evidence."""
        chain = []

        # Extract from chain_of_custody in evidence
        for evidence in artifact.evidence:
            for custody in evidence.chain_of_custody:
                record = ProvenanceRecord(
                    period=custody.get("period", TimePeriod(0, 0)),
                    holder=custody.get("holder", "Unknown"),
                    holder_type=custody.get("holder_type", "unknown"),
                    location=custody.get("location", GeoLocation(0, 0, "Unknown", "Unknown", 0)),
                    acquisition_method=custody.get("method", "unknown"),
                    documentation=custody.get("documents", []),
                    suspicious_flags=[],
                    confidence=0.7 if custody.get("documents") else 0.3
                )

                # Flag suspicious patterns
                if record.acquisition_method in ["unknown", "conquest_treaty"]:
                    record.suspicious_flags.append(
                        f"Acquisition method '{record.acquisition_method}' requires investigation"
                    )

                chain.append(record)

        # Sort by time period
        chain.sort(key=lambda x: x.period.start_year if x.period else 0)

        return chain

    def _identify_gaps(self, chain: list[ProvenanceRecord],
                      artifact: Artifact) -> list[ProvenanceGap]:
        """Identify gaps in the provenance chain."""
        gaps = []

        for i in range(len(chain) - 1):
            current = chain[i]
            next_record = chain[i + 1]

            # Check for time gap
            gap_years = next_record.period.start_year - current.period.end_year
            if gap_years > 10:  # More than 10 years unaccounted
                # Determine historical context
                context = self._get_historical_context(
                    TimePeriod(current.period.end_year, next_record.period.start_year),
                    current.location
                )

                # Estimate theft probability
                theft_prob = self._estimate_theft_probability(
                    gap_years, context, current.location, next_record.location
                )

                gap = ProvenanceGap(
                    gap_period=TimePeriod(current.period.end_year, next_record.period.start_year),
                    last_known_holder=current.holder,
                    next_known_holder=next_record.holder,
                    possible_explanations=self._generate_explanations(context, gap_years),
                    historical_context=context,
                    theft_probability=theft_prob
                )
                gaps.append(gap)

        # Check for gap between origin and first record
        if chain and artifact.claimed_date:
            first_record_start = chain[0].period.start_year
            origin_end = artifact.claimed_date.end_year
            if first_record_start - origin_end > 50:
                gaps.insert(0, ProvenanceGap(
                    gap_period=TimePeriod(origin_end, first_record_start),
                    last_known_holder="Creator/Original owner",
                    next_known_holder=chain[0].holder,
                    possible_explanations=["Unknown early history", "Documentation lost"],
                    historical_context="Early provenance unknown",
                    theft_probability=0.3
                ))

        return gaps

    def _get_historical_context(self, period: TimePeriod,
                               location: GeoLocation) -> str:
        """Get historical context for a time period and location."""
        # Check against known colonial expeditions
        for name, expedition in self.colonial_expeditions.items():
            if period.overlaps(expedition["period"]):
                if location.distance_to(expedition["region"]) < 500:
                    return f"Colonial expedition: {name.replace('_', ' ').title()}"

        # Generic historical contexts
        if period.start_year >= 1939 and period.end_year <= 1945:
            return "World War II - significant art looting period"
        elif period.start_year >= 1789 and period.end_year <= 1815:
            return "Napoleonic Wars - major redistribution of art"
        elif period.start_year >= 1850 and period.end_year <= 1920:
            return "Height of European colonialism"

        return "No specific context identified"

    def _estimate_theft_probability(self, gap_years: int, context: str,
                                   from_loc: GeoLocation, to_loc: GeoLocation) -> float:
        """Estimate probability that gap represents theft."""
        prob = 0.1  # Base probability

        # Longer gaps are more suspicious
        if gap_years > 50:
            prob += 0.2
        elif gap_years > 20:
            prob += 0.1

        # Colonial context is highly suspicious
        if "colonial" in context.lower():
            prob += 0.4

        # War context is suspicious
        if "war" in context.lower():
            prob += 0.3

        # Movement from colonized to colonizer nation is suspicious
        colonized_regions = ["Africa", "Asia", "Americas", "Middle East"]
        colonizer_regions = ["Europe", "UK", "France", "Germany", "USA"]

        if from_loc.region in colonized_regions and to_loc.region in colonizer_regions:
            prob += 0.3

        return min(prob, 1.0)

    def _generate_explanations(self, context: str, gap_years: int) -> list[str]:
        """Generate possible explanations for a provenance gap."""
        explanations = []

        if "colonial" in context.lower():
            explanations.append("Acquisition during colonial expedition")
            explanations.append("Seizure by colonial authorities")

        if "war" in context.lower():
            explanations.append("Displacement during conflict")
            explanations.append("Wartime looting")
            explanations.append("Protective relocation")

        if gap_years > 100:
            explanations.append("Documentation lost over time")
            explanations.append("Private collection with no public records")

        explanations.append("Undocumented sale or transfer")

        return explanations

    def _check_theft_indicators(self, artifact: Artifact,
                                chain: list[ProvenanceRecord],
                                gaps: list[ProvenanceGap]) -> list[str]:
        """Check for indicators of theft or illegitimate acquisition."""
        indicators = []

        # Check each record
        for record in chain:
            if record.acquisition_method in ["looting_documented", "theft", "conquest_treaty"]:
                indicators.append(
                    f"Record shows acquisition by '{record.acquisition_method}' "
                    f"during {record.period.start_year}-{record.period.end_year}"
                )

            if not record.documentation:
                indicators.append(
                    f"No documentation for acquisition by {record.holder}"
                )

        # Check gaps
        for gap in gaps:
            if gap.theft_probability > 0.5:
                indicators.append(
                    f"High probability ({gap.theft_probability:.0%}) of theft during "
                    f"{gap.gap_period.start_year}-{gap.gap_period.end_year}: "
                    f"{gap.historical_context}"
                )

        # Check if artifact is in museum of interest
        if artifact.current_holder:
            holder_lower = artifact.current_holder.lower().replace(" ", "_")
            if holder_lower in self.museums_of_interest:
                museum_info = self.museums_of_interest[holder_lower]
                indicators.append(
                    f"Current holder ({artifact.current_holder}) has known contested collections"
                )

        return indicators

    def _check_colonial_connection(self, artifact: Artifact,
                                  chain: list[ProvenanceRecord]) -> bool:
        """Check if artifact has colonial-era acquisition."""
        if artifact.true_origin:
            for name, expedition in self.colonial_expeditions.items():
                # Check if artifact origin matches expedition region
                if artifact.true_origin.distance_to(expedition["region"]) < 500:
                    # Check if acquisition timing matches
                    for record in chain:
                        if record.period and expedition["period"].overlaps(record.period):
                            return True

        # Also check if any acquisition occurred during colonial period
        colonial_period = TimePeriod(1800, 1960)
        for record in chain:
            if record.period and colonial_period.overlaps(record.period):
                if record.acquisition_method in ["conquest_treaty", "unknown", "looting_documented"]:
                    return True

        return False

    def _assess_legitimacy(self, chain: list[ProvenanceRecord],
                          gaps: list[ProvenanceGap],
                          indicators: list[str]) -> bool:
        """Assess overall legitimacy of current possession."""
        # Calculate legitimacy score
        score = 1.0

        # Reduce for gaps
        for gap in gaps:
            score -= gap.theft_probability * 0.2

        # Reduce for theft indicators
        score -= len(indicators) * 0.1

        # Check acquisition methods
        for record in chain:
            method = record.acquisition_method
            if method in self.acquisition_legitimacy:
                method_score = self.acquisition_legitimacy[method]
                if method_score < 0.5:
                    score -= 0.2

        return score > 0.5

    def _calculate_repatriation_strength(self, artifact: Artifact,
                                        chain: list[ProvenanceRecord],
                                        gaps: list[ProvenanceGap],
                                        indicators: list[str],
                                        colonial: bool) -> float:
        """Calculate the strength of a repatriation claim."""
        strength = 0.0

        # Strong indicators
        if colonial:
            strength += 0.3

        if indicators:
            strength += min(len(indicators) * 0.1, 0.3)

        for gap in gaps:
            if gap.theft_probability > 0.7:
                strength += 0.2
                break

        # Check if origin culture is known and different from current holder
        if artifact.true_origin and artifact.current_location:
            if artifact.true_origin.region != artifact.current_location.region:
                strength += 0.2

        return min(strength, 1.0)

    def _generate_summary(self, artifact: Artifact, chain: list[ProvenanceRecord],
                         gaps: list[ProvenanceGap], indicators: list[str],
                         colonial: bool, repatriation: float) -> str:
        """Generate human-readable summary of provenance analysis."""
        summary_parts = []

        # Overview
        summary_parts.append(
            f"Provenance analysis for '{artifact.name}' reveals "
            f"{len(chain)} ownership records with {len(gaps)} unexplained gaps."
        )

        # Colonial connection
        if colonial:
            summary_parts.append(
                "SIGNIFICANT: Artifact shows colonial-era acquisition patterns."
            )

        # Theft indicators
        if indicators:
            summary_parts.append(
                f"ALERT: {len(indicators)} theft or illegitimate acquisition "
                f"indicators identified."
            )

        # Repatriation assessment
        if repatriation > 0.7:
            summary_parts.append(
                f"STRONG repatriation case (strength: {repatriation:.0%}). "
                f"Recommend formal claim proceedings."
            )
        elif repatriation > 0.4:
            summary_parts.append(
                f"MODERATE repatriation case (strength: {repatriation:.0%}). "
                f"Further investigation recommended."
            )
        else:
            summary_parts.append(
                f"WEAK repatriation case (strength: {repatriation:.0%}). "
                f"Current possession appears legitimate."
            )

        return " ".join(summary_parts)

    def generate_repatriation_dossier(self, artifact: Artifact,
                                     analysis: ProvenanceAnalysis) -> dict:
        """
        Generate a formal repatriation dossier.

        This is a legal-quality document for repatriation claims.
        """
        return {
            "dossier_id": f"REP-{artifact.id[:8]}",
            "artifact_name": artifact.name,
            "artifact_type": artifact.artifact_type,
            "claimed_origin": {
                "location": artifact.claimed_origin.name if artifact.claimed_origin else "Unknown",
                "region": artifact.claimed_origin.region if artifact.claimed_origin else "Unknown"
            },
            "true_origin": {
                "location": artifact.true_origin.name if artifact.true_origin else "Unknown",
                "region": artifact.true_origin.region if artifact.true_origin else "Unknown",
                "confidence": artifact.origin_confidence
            },
            "current_holder": artifact.current_holder,
            "current_location": artifact.current_location.name if artifact.current_location else "Unknown",
            "provenance_chain_length": len(analysis.complete_chain),
            "provenance_gaps": len(analysis.gaps),
            "theft_indicators": analysis.theft_indicators,
            "colonial_connection": analysis.colonial_connection,
            "repatriation_strength": analysis.repatriation_strength,
            "summary": analysis.summary,
            "recommendation": self._generate_recommendation(analysis),
            "evidence_package": [
                {"type": "Ownership chain", "items": len(analysis.complete_chain)},
                {"type": "Gap analysis", "items": len(analysis.gaps)},
                {"type": "Theft indicators", "items": len(analysis.theft_indicators)}
            ]
        }

    def _generate_recommendation(self, analysis: ProvenanceAnalysis) -> str:
        """Generate action recommendation based on analysis."""
        if analysis.repatriation_strength > 0.7:
            return (
                "IMMEDIATE ACTION: Initiate formal repatriation proceedings. "
                "Evidence strongly supports illegitimate acquisition."
            )
        elif analysis.repatriation_strength > 0.4:
            return (
                "INVESTIGATION: Conduct deeper historical research to fill "
                "provenance gaps. Consider diplomatic discussions with current holder."
            )
        else:
            return (
                "MONITOR: Current possession appears legitimate. "
                "Continue monitoring for new evidence."
            )

    def generate_provenance_evidence(self, artifact: Artifact,
                                    analysis: ProvenanceAnalysis) -> list[Evidence]:
        """Generate evidence items from provenance analysis."""
        evidence_items = []

        # Main provenance evidence
        evidence = Evidence(
            evidence_type=EvidenceType.DOCUMENTARY,
            description=f"Provenance analysis for {artifact.name}",
            source="Provenance investigation",
            content=analysis.summary,
            confidence_score=1.0 - (len(analysis.gaps) * 0.1)
        )

        if analysis.theft_indicators:
            evidence.potential_biases = analysis.theft_indicators

        evidence.chain_of_custody = [
            {
                "period": record.period,
                "holder": record.holder,
                "method": record.acquisition_method,
                "location": record.location
            }
            for record in analysis.complete_chain
        ]

        evidence_items.append(evidence)

        return evidence_items
