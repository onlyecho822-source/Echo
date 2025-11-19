"""
Aletheia Truth Verification Engine

Main orchestrator that integrates all analysis modules and engines
to perform comprehensive truth verification and narrative reconstruction.

Named after the Greek goddess of truth (Αλήθεια), this system
correlates multi-domain evidence to challenge false narratives
and reconstruct suppressed historical truths.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import sys
sys.path.insert(0, '/home/user/Echo')

from aletheia.core.models import (
    Evidence, EvidenceType, Artifact, Narrative, HistoricalEvent,
    CorrectiveDossier, TruthAssertion, CosmicQuery, TimePeriod, GeoLocation,
    NarrativeStatus, Symbol
)

from aletheia.analyzers.symbolic_decoder import SymbolicLinguisticDecoder
from aletheia.analyzers.material_analyzer import MaterialForensicAnalyzer
from aletheia.analyzers.genetic_tracker import GeneticTracker
from aletheia.analyzers.provenance_tracer import ProvenanceTracer

from aletheia.engines.correlation_engine import CorrelationEngine
from aletheia.engines.epistemic_engine import EpistemicReasoningEngine
from aletheia.engines.ontological_mapper import OntologicalMapper
from aletheia.engines.narrative_reconstructor import NarrativeReconstructor


@dataclass
class AletheiaResult:
    """Complete result from an Aletheia investigation."""
    investigation_id: str
    timestamp: datetime
    subject: str  # What was investigated
    investigation_type: str  # artifact, narrative, cosmic_question

    # Analysis results
    evidence_gathered: list[Evidence]
    correlations_found: list
    discrepancies_found: list
    patterns_detected: list

    # Truth assessment
    truth_assertion: Optional[TruthAssertion]
    corrective_dossier: Optional[CorrectiveDossier]
    cosmic_analysis: Optional[CosmicQuery]

    # Recommendations
    next_steps: list[str]
    questions_to_ask: list[str]
    instruments_to_build: list[str]

    # Confidence
    overall_confidence: float


class Aletheia:
    """
    The Aletheia Truth Verification Engine.

    A comprehensive system for:
    - Analyzing multi-domain evidence (genetic, material, linguistic, symbolic)
    - Correlating evidence across sources
    - Detecting narrative distortions and biases
    - Reconstructing suppressed historical truths
    - Answering cosmic questions about reality

    Usage:
        aletheia = Aletheia()
        result = aletheia.investigate_artifact(artifact, evidence)
        dossier = aletheia.generate_corrective_dossier(artifact, narrative, evidence)
        cosmic = aletheia.analyze_cosmic_question("What is consciousness?")
    """

    def __init__(self):
        # Initialize all analysis modules
        self.symbolic_decoder = SymbolicLinguisticDecoder()
        self.material_analyzer = MaterialForensicAnalyzer()
        self.genetic_tracker = GeneticTracker()
        self.provenance_tracer = ProvenanceTracer()

        # Initialize engines
        self.correlation_engine = CorrelationEngine()
        self.epistemic_engine = EpistemicReasoningEngine()
        self.ontological_mapper = OntologicalMapper()
        self.narrative_reconstructor = NarrativeReconstructor()

        # Track investigations
        self.investigation_count = 0

    def investigate_artifact(self, artifact: Artifact,
                            additional_evidence: list[Evidence] = None
                            ) -> AletheiaResult:
        """
        Perform comprehensive investigation of an artifact.

        This is the primary method for investigating physical artifacts,
        manuscripts, or other historical objects.

        Args:
            artifact: The artifact to investigate
            additional_evidence: Any additional evidence already gathered

        Returns:
            Complete investigation result
        """
        self.investigation_count += 1
        investigation_id = f"INV-{self.investigation_count:06d}"

        all_evidence = list(additional_evidence) if additional_evidence else []

        # Gather evidence from all domains

        # 1. Symbolic and linguistic analysis
        if artifact.inscriptions or artifact.symbols:
            linguistic_evidence = self.symbolic_decoder.generate_linguistic_evidence(
                artifact
            )
            all_evidence.extend(linguistic_evidence)

        # 2. Material analysis (if we had spectral data)
        # In production, this would analyze actual material data
        if artifact.material_composition:
            # Generate evidence from material data
            evidence = Evidence(
                evidence_type=EvidenceType.MATERIAL,
                description=f"Material composition of {artifact.name}",
                source="Material analysis",
                material_data=artifact.material_composition,
                confidence_score=artifact.material_composition.origin_confidence
            )
            all_evidence.append(evidence)

        # 3. Provenance analysis
        provenance_analysis = self.provenance_tracer.trace_provenance(artifact)
        provenance_evidence = self.provenance_tracer.generate_provenance_evidence(
            artifact, provenance_analysis
        )
        all_evidence.extend(provenance_evidence)

        # 4. Correlate all evidence
        correlations = self.correlation_engine.correlate_evidence(all_evidence)

        # 5. Find discrepancies
        discrepancies = self.correlation_engine.find_discrepancies(all_evidence)

        # 6. Detect patterns
        patterns = self.correlation_engine.find_patterns(all_evidence)

        # 7. Generate truth assertion
        claim = f"The artifact '{artifact.name}' has been correctly attributed"
        truth_assertion = self.correlation_engine.generate_truth_assertion(
            correlations, discrepancies, patterns, claim
        )

        # 8. Weight evidence and assess epistemically
        evidence_weights = self.epistemic_engine.weight_evidence(all_evidence)

        # Calculate overall confidence
        confidence = self._calculate_investigation_confidence(
            all_evidence, correlations, discrepancies, patterns
        )

        # Generate next steps and questions
        next_steps, questions, instruments = self._generate_recommendations(
            artifact, all_evidence, correlations, discrepancies
        )

        return AletheiaResult(
            investigation_id=investigation_id,
            timestamp=datetime.now(),
            subject=artifact.name,
            investigation_type="artifact",
            evidence_gathered=all_evidence,
            correlations_found=correlations,
            discrepancies_found=discrepancies,
            patterns_detected=patterns,
            truth_assertion=truth_assertion,
            corrective_dossier=None,
            cosmic_analysis=None,
            next_steps=next_steps,
            questions_to_ask=questions,
            instruments_to_build=instruments,
            overall_confidence=confidence
        )

    def investigate_narrative(self, narrative: Narrative,
                             evidence: list[Evidence]) -> AletheiaResult:
        """
        Investigate a historical narrative for truth and bias.

        Args:
            narrative: The narrative to investigate
            evidence: Available evidence

        Returns:
            Investigation result with narrative analysis
        """
        self.investigation_count += 1
        investigation_id = f"INV-{self.investigation_count:06d}"

        # Correlate evidence
        correlations = self.correlation_engine.correlate_evidence(evidence)

        # Analyze narrative consistency
        narrative_analysis = self.correlation_engine.analyze_narrative(
            narrative, evidence
        )

        # Find discrepancies
        discrepancies = self.correlation_engine.find_discrepancies(evidence)

        # Detect patterns
        patterns = self.correlation_engine.find_patterns(evidence)

        # Detect biases
        biases = self.epistemic_engine.detect_biases(evidence, narrative)

        # Generate truth assertion
        claim = f"The narrative '{narrative.title}' is historically accurate"
        truth_assertion = self.correlation_engine.generate_truth_assertion(
            correlations, discrepancies, patterns, claim
        )

        # Calculate confidence
        confidence = narrative_analysis.overall_consistency

        # Generate recommendations
        next_steps = [
            f"Investigate {len(narrative_analysis.contradicting_evidence)} contradicting sources",
            f"Address {len(biases)} identified biases"
        ]
        questions = narrative_analysis.alternative_interpretations
        instruments = []

        return AletheiaResult(
            investigation_id=investigation_id,
            timestamp=datetime.now(),
            subject=narrative.title,
            investigation_type="narrative",
            evidence_gathered=evidence,
            correlations_found=correlations,
            discrepancies_found=discrepancies,
            patterns_detected=patterns,
            truth_assertion=truth_assertion,
            corrective_dossier=None,
            cosmic_analysis=None,
            next_steps=next_steps,
            questions_to_ask=questions,
            instruments_to_build=instruments,
            overall_confidence=confidence
        )

    def generate_corrective_dossier(self, artifact: Artifact,
                                   narrative: Narrative,
                                   evidence: list[Evidence]) -> CorrectiveDossier:
        """
        Generate a comprehensive corrective dossier.

        This is the primary output for correcting historical records
        and supporting repatriation claims.

        Args:
            artifact: The artifact under investigation
            narrative: The official narrative to correct
            evidence: All gathered evidence

        Returns:
            Complete corrective dossier
        """
        return self.narrative_reconstructor.generate_corrective_dossier(
            artifact, narrative, evidence
        )

    def analyze_cosmic_question(self, question: str) -> CosmicQuery:
        """
        Analyze a cosmic/metaphysical question.

        This handles the big questions about reality, consciousness,
        existence, and the nature of the universe.

        Args:
            question: The cosmic question to analyze

        Returns:
            Comprehensive cosmic query analysis
        """
        return self.ontological_mapper.generate_cosmic_query(question)

    def trace_artifact_provenance(self, artifact: Artifact):
        """
        Trace the complete provenance of an artifact.

        Returns detailed ownership history, gaps, and theft indicators.
        """
        return self.provenance_tracer.trace_provenance(artifact)

    def analyze_genetic_evidence(self, sample_id: str, genetic_data: dict,
                                claimed_origin: Optional[GeoLocation] = None):
        """
        Analyze genetic evidence for ancestry and migration.

        Args:
            sample_id: Identifier for the sample
            genetic_data: Genetic data including haplogroups
            claimed_origin: The officially claimed origin

        Returns:
            Ancestry analysis result
        """
        return self.genetic_tracker.analyze_ancestry(
            sample_id, genetic_data, claimed_origin
        )

    def decode_text(self, text: str, language: str, context: dict):
        """
        Decode and analyze an ancient text.

        Args:
            text: The text content
            language: Source language
            context: Additional context

        Returns:
            Text analysis with symbols, themes, and potential mistranslations
        """
        return self.symbolic_decoder.analyze_text(text, language, context)

    def cross_reference_symbols(self, symbol_a: Symbol, symbol_b: Symbol):
        """
        Cross-reference two symbols for connections.

        Used to track symbol migration and meaning evolution.
        """
        return self.symbolic_decoder.cross_reference_symbols(symbol_a, symbol_b)

    def assess_truth_claim(self, claim: str, evidence: list[Evidence],
                          paradigm: str = "integrative"):
        """
        Assess the truth of a specific claim.

        Args:
            claim: The claim to assess
            evidence: Available evidence
            paradigm: The paradigm framework to use

        Returns:
            Epistemic assessment with confidence levels
        """
        return self.epistemic_engine.assess_claim(claim, evidence, paradigm)

    def compare_cosmologies(self, culture_a: str, culture_b: str):
        """
        Compare cosmological systems of two cultures.

        Useful for finding unexpected connections and shared concepts.
        """
        return self.ontological_mapper.compare_cosmologies(culture_a, culture_b)

    def _calculate_investigation_confidence(self, evidence: list[Evidence],
                                           correlations: list,
                                           discrepancies: list,
                                           patterns: list) -> float:
        """Calculate overall confidence in investigation results."""
        confidence = 0.5  # Base confidence

        # Evidence diversity increases confidence
        evidence_types = set(ev.evidence_type for ev in evidence)
        confidence += min(len(evidence_types) * 0.05, 0.2)

        # Strong correlations increase confidence
        if correlations:
            avg_strength = sum(c.strength for c in correlations) / len(correlations)
            confidence += avg_strength * 0.15

        # Discrepancies decrease confidence (they indicate uncertainty)
        if discrepancies:
            confidence -= min(len(discrepancies) * 0.05, 0.15)

        # Patterns increase confidence
        if patterns:
            confidence += min(len(patterns) * 0.05, 0.1)

        return max(0.1, min(0.95, confidence))

    def _generate_recommendations(self, artifact: Artifact,
                                 evidence: list[Evidence],
                                 correlations: list,
                                 discrepancies: list):
        """Generate investigation recommendations."""
        next_steps = []
        questions = []
        instruments = []

        # Based on evidence gaps
        evidence_types = set(ev.evidence_type for ev in evidence)

        if EvidenceType.GENETIC not in evidence_types:
            next_steps.append("Obtain genetic analysis if organic materials present")
            instruments.append("Ancient DNA extraction and sequencing")

        if EvidenceType.MATERIAL not in evidence_types:
            next_steps.append("Perform material composition analysis")
            instruments.append("XRF spectrometer for non-destructive analysis")

        # Based on discrepancies
        if discrepancies:
            next_steps.append(f"Resolve {len(discrepancies)} identified discrepancies")
            questions.append("Why does evidence conflict in these areas?")

        # Based on provenance
        if artifact.provenance_gaps:
            next_steps.append(f"Investigate {len(artifact.provenance_gaps)} provenance gaps")
            questions.append("What happened during undocumented periods?")

        # Standard questions
        questions.extend([
            "Who benefited from the official narrative?",
            "What indigenous sources have not been consulted?",
            "Are there related artifacts that could corroborate findings?"
        ])

        return next_steps, questions, instruments


# Convenience function for quick investigations
def investigate(artifact: Artifact = None,
               narrative: Narrative = None,
               evidence: list[Evidence] = None,
               cosmic_question: str = None) -> AletheiaResult:
    """
    Convenience function for quick Aletheia investigations.

    Args:
        artifact: Artifact to investigate
        narrative: Narrative to investigate
        evidence: Evidence to analyze
        cosmic_question: Cosmic question to analyze

    Returns:
        Investigation result
    """
    aletheia = Aletheia()

    if cosmic_question:
        cosmic_result = aletheia.analyze_cosmic_question(cosmic_question)
        return AletheiaResult(
            investigation_id="QUICK-001",
            timestamp=datetime.now(),
            subject=cosmic_question,
            investigation_type="cosmic_question",
            evidence_gathered=[],
            correlations_found=[],
            discrepancies_found=[],
            patterns_detected=[],
            truth_assertion=None,
            corrective_dossier=None,
            cosmic_analysis=cosmic_result,
            next_steps=cosmic_result.investigation_paths,
            questions_to_ask=[cosmic_result.reframed_question],
            instruments_to_build=[],
            overall_confidence=cosmic_result.confidence_in_synthesis
        )

    if artifact:
        return aletheia.investigate_artifact(artifact, evidence)

    if narrative and evidence:
        return aletheia.investigate_narrative(narrative, evidence)

    raise ValueError("Must provide artifact, narrative+evidence, or cosmic_question")
