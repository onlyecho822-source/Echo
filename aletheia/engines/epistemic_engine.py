"""
Aletheia Truth Verification Engine - Epistemic Reasoning Engine

Handles the fundamental question: "How do we know what we know?"
Evaluates evidence reliability, identifies biases, and weighs competing claims.
"""

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict

import sys
sys.path.insert(0, '/home/user/Echo')

from aletheia.core.models import (
    Evidence, EvidenceType, Narrative, HistoricalEvent,
    TruthAssertion, ConfidenceLevel
)


@dataclass
class SourceAnalysis:
    """Analysis of a source's reliability."""
    source_id: str
    source_type: str
    reliability_score: float
    bias_factors: list[str]
    verification_status: str
    provenance_quality: float
    corroboration_level: float


@dataclass
class EpistemicAssessment:
    """Assessment of our knowledge about a claim."""
    claim: str
    certainty_level: ConfidenceLevel
    justification_chain: list[str]
    assumptions: list[str]
    potential_defeaters: list[str]
    falsifiability: float
    paradigm_dependencies: list[str]


@dataclass
class BiasReport:
    """Report on biases affecting evidence or narratives."""
    bias_type: str
    description: str
    affected_sources: list[str]
    correction_suggestions: list[str]
    impact_assessment: str


@dataclass
class EvidenceWeight:
    """Weighted assessment of evidence."""
    evidence_id: str
    raw_strength: float
    reliability_adjusted: float
    bias_adjusted: float
    final_weight: float
    reasoning: str


class EpistemicReasoningEngine:
    """
    Evaluates the epistemological status of claims and evidence.

    Capabilities:
    - Source reliability assessment
    - Bias detection and correction
    - Evidence weighing
    - Paradigm analysis
    - Falsifiability evaluation
    """

    def __init__(self):
        # Source type reliability baselines
        self.source_reliability = {
            "primary_document": 0.9,
            "archaeological_find": 0.85,
            "scientific_analysis": 0.9,
            "eyewitness_account": 0.7,
            "secondary_source": 0.6,
            "oral_tradition": 0.7,  # Often undervalued
            "institutional_record": 0.5,  # May have institutional bias
            "colonial_record": 0.4,  # High bias potential
            "religious_text": 0.6,  # Symbolic truths, not always literal
            "unknown": 0.3
        }

        # Known bias types
        self.bias_types = {
            "confirmation": "Seeking evidence that confirms pre-existing beliefs",
            "survivorship": "Only successful/surviving examples are visible",
            "eurocentric": "Interpreting all cultures through European lens",
            "presentism": "Judging past by present standards",
            "victors_history": "History written by conquerors",
            "institutional": "Protecting institutional interests",
            "funding": "Conclusions influenced by who funded the research",
            "publication": "Only significant results get published",
            "selection": "Cherry-picking favorable evidence"
        }

        # Paradigm frameworks
        self.paradigms = {
            "materialist": {
                "assumptions": [
                    "Only physical matter exists",
                    "Consciousness emerges from matter",
                    "Supernatural explanations are invalid"
                ],
                "blind_spots": [
                    "Dismisses consciousness studies",
                    "May ignore valid experiential data"
                ]
            },
            "colonial": {
                "assumptions": [
                    "European civilization is superior",
                    "Progress is linear from primitive to advanced",
                    "Indigenous knowledge is superstition"
                ],
                "blind_spots": [
                    "Ignores advanced indigenous knowledge",
                    "Dismisses non-written sources",
                    "Misinterprets symbols and concepts"
                ]
            },
            "religious_orthodox": {
                "assumptions": [
                    "Scripture is literally true",
                    "Divine revelation supersedes evidence",
                    "Certain questions are off-limits"
                ],
                "blind_spots": [
                    "Rejects contradicting scientific evidence",
                    "Suppresses heterodox interpretations"
                ]
            },
            "integrative": {
                "assumptions": [
                    "Multiple evidence types are valid",
                    "Indigenous and scientific knowledge can complement",
                    "Paradigms are tools, not truths"
                ],
                "blind_spots": [
                    "May lack rigor if not careful",
                    "Can be overwhelmed by competing frameworks"
                ]
            }
        }

    def analyze_source(self, evidence: Evidence) -> SourceAnalysis:
        """
        Analyze the reliability of an evidence source.

        Args:
            evidence: The evidence to analyze

        Returns:
            Detailed source analysis
        """
        # Determine source type
        source_type = self._classify_source(evidence)

        # Get baseline reliability
        base_reliability = self.source_reliability.get(source_type, 0.5)

        # Identify bias factors
        bias_factors = self._identify_source_biases(evidence, source_type)

        # Calculate reliability adjustments
        reliability = base_reliability
        for bias in bias_factors:
            reliability -= 0.1  # Each bias reduces reliability

        reliability = max(0.1, reliability)  # Minimum 10%

        # Check verification status
        verification = "verified" if evidence.verified else "unverified"
        if not evidence.verified:
            reliability -= 0.15

        # Check corroboration
        corroboration = self._assess_corroboration(evidence)

        # Calculate provenance quality
        provenance = self._assess_provenance(evidence)

        return SourceAnalysis(
            source_id=evidence.id,
            source_type=source_type,
            reliability_score=reliability,
            bias_factors=bias_factors,
            verification_status=verification,
            provenance_quality=provenance,
            corroboration_level=corroboration
        )

    def _classify_source(self, evidence: Evidence) -> str:
        """Classify the type of source."""
        # Map evidence types to source types
        type_mapping = {
            EvidenceType.GENETIC: "scientific_analysis",
            EvidenceType.MATERIAL: "scientific_analysis",
            EvidenceType.ARCHAEOLOGICAL: "archaeological_find",
            EvidenceType.DOCUMENTARY: "primary_document",
            EvidenceType.ORAL_TRADITION: "oral_tradition",
            EvidenceType.LINGUISTIC: "primary_document",
            EvidenceType.SYMBOLIC: "primary_document",
            EvidenceType.ASTRONOMICAL: "scientific_analysis",
            EvidenceType.GEOLOGICAL: "scientific_analysis",
            EvidenceType.ARTISTIC: "primary_document"
        }

        base_type = type_mapping.get(evidence.evidence_type, "unknown")

        # Check for colonial source indicators
        if evidence.source:
            source_lower = evidence.source.lower()
            if any(term in source_lower for term in
                   ["colonial", "expedition", "conquest", "missionary"]):
                return "colonial_record"

        return base_type

    def _identify_source_biases(self, evidence: Evidence,
                               source_type: str) -> list[str]:
        """Identify potential biases in a source."""
        biases = []

        # Check for known biases based on source type
        if source_type == "colonial_record":
            biases.append("eurocentric")
            biases.append("victors_history")

        if source_type == "institutional_record":
            biases.append("institutional")

        # Check evidence metadata for bias indicators
        if evidence.potential_biases:
            for bias_note in evidence.potential_biases:
                bias_note_lower = bias_note.lower()
                for bias_name in self.bias_types:
                    if bias_name in bias_note_lower:
                        if bias_name not in biases:
                            biases.append(bias_name)

        return biases

    def _assess_corroboration(self, evidence: Evidence) -> float:
        """Assess level of corroboration from other sources."""
        # Would check against other evidence in database
        # For now, return based on verification status
        return 0.7 if evidence.verified else 0.3

    def _assess_provenance(self, evidence: Evidence) -> float:
        """Assess the quality of evidence provenance."""
        score = 0.5

        if evidence.chain_of_custody:
            score += min(len(evidence.chain_of_custody) * 0.1, 0.3)

        if evidence.date_recorded:
            score += 0.1

        if evidence.location:
            score += 0.1

        return min(score, 1.0)

    def weight_evidence(self, evidence_list: list[Evidence]) -> list[EvidenceWeight]:
        """
        Calculate weighted importance of each evidence item.

        Args:
            evidence_list: List of evidence to weight

        Returns:
            List of weighted evidence assessments
        """
        weights = []

        for evidence in evidence_list:
            # Get source analysis
            source_analysis = self.analyze_source(evidence)

            # Raw strength based on evidence type
            raw = self._calculate_raw_strength(evidence)

            # Adjust for reliability
            reliability_adj = raw * source_analysis.reliability_score

            # Adjust for biases
            bias_penalty = len(source_analysis.bias_factors) * 0.05
            bias_adj = reliability_adj * (1 - bias_penalty)

            # Final weight includes corroboration
            final = bias_adj * (0.7 + 0.3 * source_analysis.corroboration_level)

            reasoning = (
                f"Raw strength: {raw:.2f}, "
                f"Reliability: {source_analysis.reliability_score:.2f}, "
                f"Biases: {len(source_analysis.bias_factors)}, "
                f"Corroboration: {source_analysis.corroboration_level:.2f}"
            )

            weights.append(EvidenceWeight(
                evidence_id=evidence.id,
                raw_strength=raw,
                reliability_adjusted=reliability_adj,
                bias_adjusted=bias_adj,
                final_weight=final,
                reasoning=reasoning
            ))

        return weights

    def _calculate_raw_strength(self, evidence: Evidence) -> float:
        """Calculate raw evidential strength."""
        # Physical evidence is generally stronger
        physical_types = {
            EvidenceType.GENETIC, EvidenceType.MATERIAL,
            EvidenceType.ARCHAEOLOGICAL, EvidenceType.GEOLOGICAL
        }

        if evidence.evidence_type in physical_types:
            return 0.85

        # Documentary evidence
        if evidence.evidence_type in {EvidenceType.DOCUMENTARY, EvidenceType.LINGUISTIC}:
            return 0.7

        # Oral and symbolic
        return 0.6

    def assess_claim(self, claim: str, evidence_list: list[Evidence],
                    paradigm: str = "integrative") -> EpistemicAssessment:
        """
        Perform full epistemic assessment of a claim.

        Args:
            claim: The claim to assess
            evidence_list: Available evidence
            paradigm: The paradigm framework to use

        Returns:
            Complete epistemic assessment
        """
        # Get paradigm info
        paradigm_info = self.paradigms.get(paradigm, self.paradigms["integrative"])

        # Build justification chain
        justification = self._build_justification(claim, evidence_list)

        # Identify assumptions
        assumptions = paradigm_info["assumptions"].copy()
        assumptions.extend(self._identify_claim_assumptions(claim))

        # Find potential defeaters
        defeaters = self._find_defeaters(claim, evidence_list)

        # Assess falsifiability
        falsifiability = self._assess_falsifiability(claim)

        # Determine certainty level
        certainty = self._determine_certainty(
            evidence_list, justification, defeaters
        )

        return EpistemicAssessment(
            claim=claim,
            certainty_level=certainty,
            justification_chain=justification,
            assumptions=assumptions,
            potential_defeaters=defeaters,
            falsifiability=falsifiability,
            paradigm_dependencies=paradigm_info["assumptions"]
        )

    def _build_justification(self, claim: str,
                            evidence_list: list[Evidence]) -> list[str]:
        """Build the chain of justification for a claim."""
        chain = []

        if not evidence_list:
            chain.append("NO DIRECT EVIDENCE: Claim requires evidential support")
            return chain

        # Weight evidence
        weights = self.weight_evidence(evidence_list)

        # Sort by weight
        weights.sort(key=lambda w: w.final_weight, reverse=True)

        # Build chain from strongest evidence
        for weight in weights[:5]:  # Top 5
            evidence = next(
                (e for e in evidence_list if e.id == weight.evidence_id), None
            )
            if evidence:
                chain.append(
                    f"EVIDENCE ({weight.final_weight:.2f}): {evidence.description} - "
                    f"{evidence.evidence_type.value}"
                )

        return chain

    def _identify_claim_assumptions(self, claim: str) -> list[str]:
        """Identify assumptions embedded in a claim."""
        assumptions = []

        claim_lower = claim.lower()

        # Check for assumption indicators
        if "always" in claim_lower or "never" in claim_lower:
            assumptions.append("Assumes universal applicability")

        if "proves" in claim_lower:
            assumptions.append("Assumes proof is possible (vs. support)")

        if "civilization" in claim_lower:
            assumptions.append("Assumes shared definition of 'civilization'")

        if "advanced" in claim_lower or "primitive" in claim_lower:
            assumptions.append("Assumes linear model of progress")

        return assumptions

    def _find_defeaters(self, claim: str,
                       evidence_list: list[Evidence]) -> list[str]:
        """Find potential defeaters for a claim."""
        defeaters = []

        # Check for contradicting evidence
        for evidence in evidence_list:
            if evidence.potential_biases:
                for bias in evidence.potential_biases:
                    if "contradict" in bias.lower() or "conflict" in bias.lower():
                        defeaters.append(f"Contradicting evidence: {evidence.description}")
                        break

        # Paradigm-based defeaters
        defeaters.append(
            "Alternative paradigm may interpret evidence differently"
        )

        return defeaters

    def _assess_falsifiability(self, claim: str) -> float:
        """Assess how falsifiable a claim is."""
        # Higher score = more falsifiable = more scientific
        score = 0.5

        claim_lower = claim.lower()

        # Specific claims are more falsifiable
        if any(word in claim_lower for word in ["specific", "exactly", "precisely"]):
            score += 0.2

        # Vague claims are less falsifiable
        if any(word in claim_lower for word in ["might", "could", "possibly"]):
            score -= 0.1

        # Metaphysical claims are hard to falsify
        if any(word in claim_lower for word in
               ["spirit", "soul", "consciousness", "divine"]):
            score -= 0.2

        return max(0.1, min(1.0, score))

    def _determine_certainty(self, evidence_list: list[Evidence],
                            justification: list[str],
                            defeaters: list[str]) -> ConfidenceLevel:
        """Determine the certainty level for a claim."""
        score = 0.5

        # More evidence increases certainty
        score += min(len(evidence_list) * 0.05, 0.2)

        # Strong justification increases certainty
        score += min(len(justification) * 0.05, 0.15)

        # Defeaters decrease certainty
        score -= min(len(defeaters) * 0.05, 0.2)

        # Map to confidence level
        if score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.6:
            return ConfidenceLevel.HIGH
        elif score >= 0.4:
            return ConfidenceLevel.MODERATE
        elif score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.SPECULATIVE

    def detect_biases(self, evidence_list: list[Evidence],
                     narrative: Optional[Narrative] = None) -> list[BiasReport]:
        """
        Detect biases in evidence and narratives.

        This is crucial for correcting historical distortions.
        """
        reports = []

        # Aggregate biases from evidence
        bias_counts = defaultdict(list)
        for evidence in evidence_list:
            analysis = self.analyze_source(evidence)
            for bias in analysis.bias_factors:
                bias_counts[bias].append(evidence.id)

        # Create reports for significant biases
        for bias_name, affected in bias_counts.items():
            if len(affected) >= 2:  # Multiple sources affected
                reports.append(BiasReport(
                    bias_type=bias_name,
                    description=self.bias_types.get(bias_name, "Unknown bias type"),
                    affected_sources=affected,
                    correction_suggestions=self._get_bias_corrections(bias_name),
                    impact_assessment=f"Affects {len(affected)} of {len(evidence_list)} sources"
                ))

        # Check narrative-level biases
        if narrative:
            if narrative.beneficiaries:
                reports.append(BiasReport(
                    bias_type="institutional",
                    description=f"Narrative benefits: {', '.join(narrative.beneficiaries)}",
                    affected_sources=["narrative"],
                    correction_suggestions=[
                        "Seek sources that don't benefit from this narrative",
                        "Look for suppressed counter-narratives"
                    ],
                    impact_assessment="Narrative structure may be shaped by beneficiary interests"
                ))

        return reports

    def _get_bias_corrections(self, bias_name: str) -> list[str]:
        """Get correction suggestions for a bias type."""
        corrections = {
            "eurocentric": [
                "Include sources from non-European perspectives",
                "Re-examine 'primitive' classifications",
                "Consult indigenous knowledge keepers"
            ],
            "victors_history": [
                "Seek accounts from defeated/colonized peoples",
                "Look for suppressed or destroyed records",
                "Examine oral traditions"
            ],
            "confirmation": [
                "Actively seek disconfirming evidence",
                "Apply same scrutiny to supporting evidence",
                "Consider alternative hypotheses equally"
            ],
            "institutional": [
                "Check who funds/controls the source",
                "Look for independent verification",
                "Consider whistleblower accounts"
            ],
            "survivorship": [
                "Research what didn't survive",
                "Consider selection effects",
                "Look for negative evidence"
            ]
        }

        return corrections.get(bias_name, [
            "Seek diverse sources",
            "Apply critical analysis",
            "Consider alternative interpretations"
        ])

    def evaluate_paradigm_impact(self, claim: str,
                                paradigms: list[str]) -> dict:
        """
        Evaluate how different paradigms interpret the same claim.

        This reveals how our framework for knowledge shapes what
        we can even consider as true.
        """
        results = {}

        for paradigm_name in paradigms:
            if paradigm_name not in self.paradigms:
                continue

            paradigm = self.paradigms[paradigm_name]

            # Assess claim under this paradigm
            results[paradigm_name] = {
                "interpretation": self._interpret_under_paradigm(claim, paradigm),
                "validity": self._assess_validity_under_paradigm(claim, paradigm),
                "blind_spots": paradigm["blind_spots"],
                "key_assumptions": paradigm["assumptions"]
            }

        return results

    def _interpret_under_paradigm(self, claim: str, paradigm: dict) -> str:
        """Interpret a claim under a specific paradigm."""
        # Simplified - would be more sophisticated in production
        if "supernatural" in str(paradigm["assumptions"]).lower():
            return "Claim may be interpreted symbolically or rejected"
        elif "indigenous" in str(paradigm["assumptions"]).lower():
            return "Claim should be evaluated alongside indigenous knowledge"
        else:
            return "Standard interpretation applies"

    def _assess_validity_under_paradigm(self, claim: str, paradigm: dict) -> str:
        """Assess validity of claim under paradigm."""
        # Check if claim conflicts with paradigm assumptions
        claim_lower = claim.lower()

        for assumption in paradigm["assumptions"]:
            assumption_lower = assumption.lower()
            # Check for conflicts
            if "supernatural" in assumption_lower and "spirit" in claim_lower:
                return "Invalid under this paradigm"

        return "Potentially valid under this paradigm"
