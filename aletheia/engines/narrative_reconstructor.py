"""
Aletheia Truth Verification Engine - Narrative Reconstructor

Synthesizes evidence from all sources to reconstruct corrected historical
narratives and generate comprehensive corrective dossiers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import sys
sys.path.insert(0, '/home/user/Echo')

from aletheia.core.models import (
    Evidence, EvidenceType, Artifact, Narrative, HistoricalEvent,
    CorrectiveDossier, TimePeriod, NarrativeStatus
)


@dataclass
class NarrativeCorrection:
    """A specific correction to a historical narrative."""
    original_claim: str
    corrected_claim: str
    evidence_basis: list[Evidence]
    confidence: float
    implications: list[str]


@dataclass
class ErasureEvent:
    """An event where knowledge was erased or suppressed."""
    name: str
    time_period: TimePeriod
    perpetrator: str
    method: str  # burning, confiscation, translation_distortion, etc.
    knowledge_lost: list[str]
    recoverable: bool
    recovery_methods: list[str]


@dataclass
class ReconstructedTimeline:
    """A corrected timeline of events."""
    title: str
    events: list[HistoricalEvent]
    corrections_made: int
    confidence: float
    gaps_remaining: list[TimePeriod]


class NarrativeReconstructor:
    """
    Reconstructs corrected narratives from multi-domain evidence.

    Capabilities:
    - Narrative correction generation
    - Erasure event tracking
    - Timeline reconstruction
    - Corrective dossier generation
    """

    def __init__(self):
        # Known historical erasure events
        self.erasure_events = {
            "library_alexandria": ErasureEvent(
                name="Destruction of Library of Alexandria",
                time_period=TimePeriod(-48, 642),
                perpetrator="Multiple (Caesar, Christians, Muslims)",
                method="burning, dispersal",
                knowledge_lost=[
                    "Ancient Egyptian scientific texts",
                    "Greek philosophical works",
                    "Medical and astronomical knowledge"
                ],
                recoverable=True,
                recovery_methods=[
                    "Fragments preserved in Arabic translations",
                    "Quotations in surviving texts",
                    "Archaeological evidence"
                ]
            ),
            "codex_burning": ErasureEvent(
                name="Maya Codex Burning",
                time_period=TimePeriod(1562, 1562),
                perpetrator="Diego de Landa",
                method="burning",
                knowledge_lost=[
                    "Maya astronomical calculations",
                    "Historical records",
                    "Religious and philosophical texts"
                ],
                recoverable=True,
                recovery_methods=[
                    "Four surviving codices",
                    "Inscriptions on monuments",
                    "Oral traditions"
                ]
            ),
            "benin_looting": ErasureEvent(
                name="Benin Punitive Expedition",
                time_period=TimePeriod(1897, 1897),
                perpetrator="British Empire",
                method="looting, destruction",
                knowledge_lost=[
                    "Historical records in bronze",
                    "Cultural continuity",
                    "Artistic techniques"
                ],
                recoverable=True,
                recovery_methods=[
                    "Bronzes in museums can be studied",
                    "Oral histories from Benin",
                    "Archaeological investigation"
                ]
            ),
            "timbuktu_manuscripts": ErasureEvent(
                name="Timbuktu Manuscript Threats",
                time_period=TimePeriod(1800, 2012),
                perpetrator="Colonial powers, extremists",
                method="neglect, deliberate destruction",
                knowledge_lost=[
                    "African intellectual history",
                    "Scientific achievements",
                    "Trade and diplomatic records"
                ],
                recoverable=True,
                recovery_methods=[
                    "Many manuscripts hidden and preserved",
                    "Digitization projects ongoing",
                    "Family collections"
                ]
            )
        }

    def reconstruct_narrative(self, official_narrative: Narrative,
                             evidence: list[Evidence],
                             artifacts: list[Artifact]) -> Narrative:
        """
        Reconstruct a corrected narrative from evidence.

        Args:
            official_narrative: The official/establishment narrative
            evidence: All available evidence
            artifacts: Related artifacts

        Returns:
            A corrected narrative
        """
        # Generate corrections
        corrections = self._generate_corrections(official_narrative, evidence)

        # Build corrected narrative
        corrected = Narrative(
            title=f"Corrected: {official_narrative.title}",
            description=self._build_corrected_description(
                official_narrative, corrections
            ),
            status=NarrativeStatus.RECONSTRUCTED,
            primary_sources=[e for e in evidence if e.source_reliability > 0.7],
            secondary_sources=[e for e in evidence if e.source_reliability <= 0.7],
            artifacts=artifacts,
            events=self._correct_events(official_narrative.events, evidence),
            cultures=official_narrative.cultures,
            truth_score=self._calculate_truth_score(corrections),
            confidence_score=sum(c.confidence for c in corrections) / max(len(corrections), 1),
            discrepancies=[c.original_claim for c in corrections],
            beneficiaries=official_narrative.beneficiaries,
            suppressed_voices=self._identify_suppressed_voices(evidence),
            control_mechanisms=self._identify_control_mechanisms(official_narrative),
            corrected_narrative=self._synthesize_corrected_text(corrections),
            correction_evidence=evidence,
            questions_raised=self._generate_questions(corrections)
        )

        return corrected

    def _generate_corrections(self, narrative: Narrative,
                             evidence: list[Evidence]) -> list[NarrativeCorrection]:
        """Generate specific corrections based on evidence."""
        corrections = []

        # Extract claims from narrative
        claims = self._extract_claims(narrative)

        for claim in claims:
            # Find contradicting evidence
            contradicting = []
            supporting = []

            for ev in evidence:
                relevance = self._check_relevance(claim, ev)
                if relevance < 0:
                    contradicting.append(ev)
                elif relevance > 0:
                    supporting.append(ev)

            # Generate correction if contradicting evidence is strong
            if contradicting and len(contradicting) >= len(supporting):
                corrected_claim = self._formulate_correction(claim, contradicting)
                corrections.append(NarrativeCorrection(
                    original_claim=claim,
                    corrected_claim=corrected_claim,
                    evidence_basis=contradicting,
                    confidence=self._calculate_correction_confidence(contradicting),
                    implications=self._derive_implications(claim, corrected_claim)
                ))

        return corrections

    def _extract_claims(self, narrative: Narrative) -> list[str]:
        """Extract testable claims from a narrative."""
        claims = []

        # Extract from description
        if narrative.description:
            sentences = narrative.description.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 20:
                    claims.append(sentence)

        # Extract from events
        for event in narrative.events:
            if event.official_narrative:
                claims.append(event.official_narrative)

        return claims

    def _check_relevance(self, claim: str, evidence: Evidence) -> float:
        """
        Check if evidence is relevant to a claim.

        Returns:
            Positive if supporting, negative if contradicting, 0 if irrelevant
        """
        if not evidence.content:
            return 0.0

        claim_words = set(claim.lower().split())
        evidence_words = set(evidence.content.lower().split())

        # Calculate word overlap
        overlap = len(claim_words & evidence_words) / max(len(claim_words), 1)

        if overlap < 0.1:
            return 0.0  # Not relevant

        # Check for contradiction indicators
        if evidence.potential_biases:
            for bias in evidence.potential_biases:
                if "contradict" in bias.lower() or "conflict" in bias.lower():
                    return -overlap

        return overlap

    def _formulate_correction(self, original: str,
                             evidence: list[Evidence]) -> str:
        """Formulate a corrected claim based on evidence."""
        # Extract key information from evidence
        evidence_points = []
        for ev in evidence:
            if ev.content:
                evidence_points.append(ev.content[:100])

        return f"CORRECTION: Evidence suggests alternative interpretation. {evidence_points[0] if evidence_points else 'See evidence.'}"

    def _calculate_correction_confidence(self, evidence: list[Evidence]) -> float:
        """Calculate confidence in a correction."""
        if not evidence:
            return 0.0

        # Average confidence of supporting evidence
        confidences = [ev.confidence_score for ev in evidence if ev.confidence_score > 0]
        if confidences:
            return sum(confidences) / len(confidences)

        return 0.5

    def _derive_implications(self, original: str, corrected: str) -> list[str]:
        """Derive implications of a correction."""
        return [
            f"Original claim may have been shaped by bias",
            f"Requires revision of related historical interpretations",
            f"Suggests need for broader reassessment of source reliability"
        ]

    def _build_corrected_description(self, original: Narrative,
                                    corrections: list[NarrativeCorrection]) -> str:
        """Build the description for corrected narrative."""
        return (
            f"This narrative corrects {len(corrections)} claims from the original "
            f"'{original.title}'. The corrections are based on multi-domain evidence "
            f"including genetic, material, linguistic, and documentary sources."
        )

    def _correct_events(self, events: list[HistoricalEvent],
                       evidence: list[Evidence]) -> list[HistoricalEvent]:
        """Generate corrected versions of historical events."""
        corrected_events = []

        for event in events:
            corrected_event = HistoricalEvent(
                id=event.id,
                name=event.name,
                description=event.description,
                time_period=event.time_period,
                location=event.location,
                participants=event.participants,
                cultures_affected=event.cultures_affected,
                official_narrative=event.official_narrative,
                narrative_status=NarrativeStatus.CONTESTED
            )

            # Find relevant evidence
            relevant_evidence = [
                ev for ev in evidence
                if ev.time_period and event.time_period and
                ev.time_period.overlaps(event.time_period)
            ]

            if relevant_evidence:
                corrected_event.supporting_evidence = [
                    ev for ev in relevant_evidence
                    if not ev.potential_biases
                ]
                corrected_event.contradicting_evidence = [
                    ev for ev in relevant_evidence
                    if ev.potential_biases
                ]

                # Generate reconstructed narrative
                if corrected_event.contradicting_evidence:
                    corrected_event.reconstructed_narrative = (
                        f"Evidence suggests revisions to official account of {event.name}. "
                        f"See {len(corrected_event.contradicting_evidence)} contradicting sources."
                    )
                    corrected_event.narrative_status = NarrativeStatus.RECONSTRUCTED

            corrected_events.append(corrected_event)

        return corrected_events

    def _calculate_truth_score(self, corrections: list[NarrativeCorrection]) -> float:
        """Calculate overall truth score for reconstructed narrative."""
        if not corrections:
            return 0.5

        return sum(c.confidence for c in corrections) / len(corrections)

    def _identify_suppressed_voices(self, evidence: list[Evidence]) -> list[str]:
        """Identify voices that were suppressed in the original narrative."""
        suppressed = set()

        for ev in evidence:
            if ev.evidence_type == EvidenceType.ORAL_TRADITION:
                if ev.location:
                    suppressed.add(f"Indigenous voices from {ev.location.region}")

            if "suppressed" in str(ev.potential_biases).lower():
                suppressed.add("Accounts deliberately marginalized")

        return list(suppressed)

    def _identify_control_mechanisms(self, narrative: Narrative) -> list[str]:
        """Identify mechanisms used to control the narrative."""
        mechanisms = []

        if narrative.beneficiaries:
            mechanisms.append(
                f"Narrative benefits {', '.join(narrative.beneficiaries)}"
            )

        if narrative.suppressed_voices:
            mechanisms.append(
                f"Deliberately excludes {', '.join(narrative.suppressed_voices)}"
            )

        mechanisms.append("Institutional repetition creates appearance of truth")
        mechanisms.append("Exclusion from academic curriculum")

        return mechanisms

    def _synthesize_corrected_text(self,
                                   corrections: list[NarrativeCorrection]) -> str:
        """Synthesize corrected narrative text."""
        if not corrections:
            return "No corrections identified."

        parts = []
        for i, correction in enumerate(corrections, 1):
            parts.append(
                f"{i}. {correction.corrected_claim} "
                f"(Confidence: {correction.confidence:.0%})"
            )

        return " | ".join(parts)

    def _generate_questions(self,
                           corrections: list[NarrativeCorrection]) -> list[str]:
        """Generate questions raised by the corrections."""
        questions = [
            "What other narratives are based on the same flawed assumptions?",
            "Who benefited from the original false narrative?",
            "What knowledge was lost or suppressed as a result?"
        ]

        if corrections:
            questions.append(
                f"Given these {len(corrections)} corrections, "
                f"what is the true sequence of events?"
            )

        return questions

    def generate_corrective_dossier(self, artifact: Artifact,
                                   narrative: Narrative,
                                   evidence: list[Evidence]) -> CorrectiveDossier:
        """
        Generate a comprehensive corrective dossier.

        This is the primary output for correcting historical records.
        """
        # Reconstruct the narrative
        corrected = self.reconstruct_narrative(narrative, evidence, [artifact])

        # Organize evidence by type
        evidence_by_type = {}
        for ev in evidence:
            type_name = ev.evidence_type.value
            if type_name not in evidence_by_type:
                evidence_by_type[type_name] = []
            evidence_by_type[type_name].append(ev)

        # Build erasure timeline
        erasure_timeline = self._build_erasure_timeline(artifact, evidence)

        # Identify key actors
        key_actors = self._identify_key_actors(evidence, narrative)

        # Derive implications
        immediate = self._derive_immediate_implications(corrected)
        broader = self._derive_broader_implications(corrected)
        cosmic = self._derive_cosmic_implications(corrected)

        # Generate action items
        questions = corrected.questions_raised
        instruments = self._suggest_instruments(evidence)

        # Calculate scores
        confidence = corrected.confidence_score
        convergence = self._calculate_convergence(evidence_by_type)
        paradigm_shift = self._assess_paradigm_shift(corrected)

        return CorrectiveDossier(
            title=f"Corrective Dossier: {artifact.name}",
            created_at=datetime.now(),
            official_narrative=narrative.description,
            reconstructed_truth=corrected.corrected_narrative,
            primary_evidence=corrected.primary_sources,
            evidence_by_type=evidence_by_type,
            erasure_timeline=erasure_timeline,
            key_actors=key_actors,
            mechanisms_of_suppression=corrected.control_mechanisms,
            immediate_implications=immediate,
            broader_implications=broader,
            cosmic_implications=cosmic,
            artifacts_to_repatriate=[artifact] if artifact.true_origin else [],
            questions_to_investigate=questions,
            instruments_to_build=instruments,
            overall_confidence=confidence,
            evidence_convergence_score=convergence,
            paradigm_shift_potential=paradigm_shift
        )

    def _build_erasure_timeline(self, artifact: Artifact,
                               evidence: list[Evidence]) -> list[HistoricalEvent]:
        """Build timeline of erasure events affecting the artifact."""
        timeline = []

        # Check artifact provenance gaps
        for gap in artifact.provenance_gaps:
            event = HistoricalEvent(
                name=f"Provenance gap: {gap.start_year}-{gap.end_year}",
                time_period=gap,
                narrative_status=NarrativeStatus.SUPPRESSED
            )
            timeline.append(event)

        return timeline

    def _identify_key_actors(self, evidence: list[Evidence],
                            narrative: Narrative) -> list[str]:
        """Identify key actors in the narrative distortion."""
        actors = []

        # Beneficiaries are potential actors
        if narrative.beneficiaries:
            actors.extend(narrative.beneficiaries)

        # Check evidence sources
        for ev in evidence:
            if "colonial" in ev.source.lower():
                actors.append(f"Colonial authority: {ev.source}")
            if "expedition" in ev.source.lower():
                actors.append(f"Expedition: {ev.source}")

        return list(set(actors))

    def _derive_immediate_implications(self, narrative: Narrative) -> list[str]:
        """Derive immediate implications of the correction."""
        return [
            "Historical record requires revision",
            f"Repatriation claims strengthened",
            f"Academic literature needs updating"
        ]

    def _derive_broader_implications(self, narrative: Narrative) -> list[str]:
        """Derive broader implications."""
        return [
            "Questions reliability of similar narratives from same period",
            "Highlights need for multi-domain evidence in historical claims",
            "Demonstrates importance of indigenous knowledge sources"
        ]

    def _derive_cosmic_implications(self, narrative: Narrative) -> list[str]:
        """Derive cosmic/paradigm-level implications."""
        return [
            "Challenges assumptions about what ancient cultures knew",
            "Suggests need to re-evaluate 'primitive' classifications",
            "May indicate lost advanced knowledge requiring investigation"
        ]

    def _suggest_instruments(self, evidence: list[Evidence]) -> list[str]:
        """Suggest instruments or tools to build for further investigation."""
        instruments = []

        evidence_types = set(ev.evidence_type for ev in evidence)

        if EvidenceType.MATERIAL not in evidence_types:
            instruments.append(
                "Material analysis: XRF spectrometer, Carbon dating equipment"
            )

        if EvidenceType.GENETIC not in evidence_types:
            instruments.append(
                "Genetic analysis: Ancient DNA extraction and sequencing"
            )

        if EvidenceType.ASTRONOMICAL in evidence_types:
            instruments.append(
                "Archaeoastronomy tools: Sky simulation software for ancient dates"
            )

        instruments.append(
            "AI tools: Symbol recognition trained on non-Western corpora"
        )

        return instruments

    def _calculate_convergence(self, evidence_by_type: dict) -> float:
        """Calculate evidence convergence score."""
        # More evidence types = higher convergence
        return min(len(evidence_by_type) / 5, 1.0)

    def _assess_paradigm_shift(self, narrative: Narrative) -> float:
        """Assess the paradigm shift potential of the correction."""
        score = 0.3  # Base potential

        # Major corrections increase potential
        if len(narrative.discrepancies) > 3:
            score += 0.2

        # Suppressed voices increase potential
        if narrative.suppressed_voices:
            score += 0.2

        # Control mechanisms increase potential
        if len(narrative.control_mechanisms) > 2:
            score += 0.2

        return min(score, 1.0)
