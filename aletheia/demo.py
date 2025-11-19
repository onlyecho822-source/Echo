#!/usr/bin/env python3
"""
Aletheia Truth Verification Engine - Demonstration

This script demonstrates the core capabilities of the Aletheia system:
1. Artifact investigation with multi-domain evidence
2. Narrative truth verification and correction
3. Provenance tracing and repatriation support
4. Cosmic question analysis

Run this script to see the system in action.
"""

import sys
sys.path.insert(0, '/home/user/Echo')

from datetime import datetime

from aletheia import Aletheia
from aletheia.core.models import (
    Artifact, Evidence, EvidenceType, Narrative, HistoricalEvent,
    TimePeriod, GeoLocation, MaterialComposition, Symbol, NarrativeStatus
)


def demo_artifact_investigation():
    """Demonstrate artifact investigation capabilities."""
    print("\n" + "="*70)
    print("DEMO 1: Artifact Investigation - Benin Bronze")
    print("="*70)

    # Create the Aletheia engine
    aletheia = Aletheia()

    # Create artifact: A Benin Bronze plaque
    artifact = Artifact(
        name="Benin Bronze Commemorative Plaque",
        description="Bronze plaque depicting royal court scene",
        artifact_type="bronze_sculpture",
        claimed_origin=GeoLocation(51.52, -0.13, "London", "UK", 1),
        true_origin=GeoLocation(6.34, 5.63, "Benin City", "Nigeria", 10),
        origin_confidence=0.95,
        claimed_date=TimePeriod(1500, 1700),
        true_date=TimePeriod(1550, 1650),
        date_confidence=0.9,
        current_location=GeoLocation(51.52, -0.13, "British Museum", "UK", 1),
        current_holder="British Museum",
        acquisition_method="Punitive expedition looting",
        material_composition=MaterialComposition(
            primary_material="Bronze",
            secondary_materials=["Iron", "Lead"],
            trace_elements={"zinc": 15.2, "tin": 8.5, "lead": 3.1},
            analysis_method="XRF",
            analysis_date=datetime.now()
        ),
        inscriptions=["Royal insignia depicting Oba"],
        languages_present=["Edo symbolism"],
        symbols=[
            Symbol(
                name="Coral beads",
                description="Symbol of royal authority and wealth",
                cultures=["Edo", "Benin"],
                meanings={"Edo": "Divine kingship, connection to Olokun"}
            )
        ],
        provenance_gaps=[
            TimePeriod(1897, 1900)  # Gap during and after expedition
        ]
    )

    # Create evidence
    evidence = [
        Evidence(
            evidence_type=EvidenceType.DOCUMENTARY,
            description="British expedition records documenting seizure",
            source="National Archives colonial records",
            source_reliability=0.7,
            time_period=TimePeriod(1897, 1897),
            content="Expedition records describe systematic looting of royal palace",
            confidence_score=0.85,
            potential_biases=["Colonial perspective", "Justification narrative"]
        ),
        Evidence(
            evidence_type=EvidenceType.ORAL_TRADITION,
            description="Benin oral history of the invasion",
            source="Benin royal court historians",
            source_reliability=0.85,
            time_period=TimePeriod(1897, 2020),
            content="Oral accounts describe unprovoked attack and mass theft of sacred objects",
            confidence_score=0.9
        ),
        Evidence(
            evidence_type=EvidenceType.MATERIAL,
            description="Metallurgical analysis",
            source="University laboratory",
            source_reliability=0.95,
            content="Bronze composition matches known Benin metallurgy",
            confidence_score=0.95,
            material_data=artifact.material_composition
        ),
        Evidence(
            evidence_type=EvidenceType.ARCHAEOLOGICAL,
            description="Site survey of original palace location",
            source="Nigerian archaeological survey",
            source_reliability=0.9,
            location=GeoLocation(6.34, 5.63, "Benin City", "Nigeria", 1),
            time_period=TimePeriod(2010, 2015),
            content="Archaeological survey confirms royal workshop locations",
            confidence_score=0.88
        )
    ]

    # Investigate the artifact
    result = aletheia.investigate_artifact(artifact, evidence)

    # Print results
    print(f"\nInvestigation ID: {result.investigation_id}")
    print(f"Subject: {result.subject}")
    print(f"Timestamp: {result.timestamp}")
    print(f"\nEvidence gathered: {len(result.evidence_gathered)} items")
    print(f"Correlations found: {len(result.correlations_found)}")
    print(f"Discrepancies found: {len(result.discrepancies_found)}")
    print(f"Patterns detected: {len(result.patterns_detected)}")
    print(f"\nOverall confidence: {result.overall_confidence:.1%}")

    if result.truth_assertion:
        print(f"\nTruth Assessment:")
        print(f"  Confidence: {result.truth_assertion.truth_confidence:.1%}")
        print(f"  Conclusion: {result.truth_assertion.conclusion}")

    print(f"\nNext Steps:")
    for step in result.next_steps[:3]:
        print(f"  - {step}")

    print(f"\nQuestions to Investigate:")
    for q in result.questions_to_ask[:3]:
        print(f"  - {q}")

    # Trace provenance specifically
    print("\n--- Provenance Analysis ---")
    provenance = aletheia.trace_artifact_provenance(artifact)
    print(f"Colonial connection: {provenance.colonial_connection}")
    print(f"Theft indicators: {len(provenance.theft_indicators)}")
    print(f"Repatriation strength: {provenance.repatriation_strength:.1%}")
    print(f"\nSummary: {provenance.summary}")


def demo_narrative_correction():
    """Demonstrate narrative correction capabilities."""
    print("\n" + "="*70)
    print("DEMO 2: Narrative Correction - Ancient Knowledge Attribution")
    print("="*70)

    aletheia = Aletheia()

    # Create official narrative
    official_narrative = Narrative(
        title="Origins of Mathematical Knowledge",
        description=(
            "Advanced mathematics originated in ancient Greece. "
            "Pythagoras discovered the theorem bearing his name. "
            "Greek civilization independently developed geometry and astronomy."
        ),
        status=NarrativeStatus.OFFICIAL,
        cultures=["Greek"],
        beneficiaries=["European academic institutions", "Western civilization narrative"],
        suppressed_voices=["Egyptian mathematicians", "Babylonian astronomers", "African scholars"]
    )

    # Create correcting evidence
    evidence = [
        Evidence(
            evidence_type=EvidenceType.DOCUMENTARY,
            description="Babylonian clay tablets with Pythagorean triples",
            source="Yale Babylonian Collection",
            source_reliability=0.95,
            time_period=TimePeriod(-1800, -1600),
            content="Plimpton 322 tablet shows understanding of Pythagorean theorem 1000 years before Pythagoras",
            confidence_score=0.95
        ),
        Evidence(
            evidence_type=EvidenceType.DOCUMENTARY,
            description="Egyptian mathematical papyri",
            source="British Museum",
            source_reliability=0.9,
            time_period=TimePeriod(-1650, -1550),
            content="Rhind Mathematical Papyrus contains geometry predating Greek mathematics",
            confidence_score=0.9
        ),
        Evidence(
            evidence_type=EvidenceType.DOCUMENTARY,
            description="Greek scholars' own attributions",
            source="Classical texts",
            source_reliability=0.85,
            time_period=TimePeriod(-500, -300),
            content="Pythagoras and Plato explicitly credit Egyptian priests with mathematical knowledge",
            confidence_score=0.88
        ),
        Evidence(
            evidence_type=EvidenceType.ARCHAEOLOGICAL,
            description="Alignment analysis of Egyptian monuments",
            source="Archaeoastronomy studies",
            source_reliability=0.9,
            time_period=TimePeriod(-2500, -2000),
            content="Pyramid alignments demonstrate sophisticated astronomical and geometric knowledge",
            confidence_score=0.85
        )
    ]

    # Create a sample artifact for the dossier
    artifact = Artifact(
        name="Rhind Mathematical Papyrus",
        description="Ancient Egyptian mathematical document",
        artifact_type="papyrus",
        true_origin=GeoLocation(25.7, 32.6, "Thebes", "Egypt", 50),
        true_date=TimePeriod(-1650, -1550),
        current_location=GeoLocation(51.52, -0.13, "British Museum", "UK", 1),
        current_holder="British Museum"
    )

    # Generate corrective dossier
    dossier = aletheia.generate_corrective_dossier(artifact, official_narrative, evidence)

    print(f"\nDossier: {dossier.title}")
    print(f"Created: {dossier.created_at}")

    print(f"\nOfficial Narrative:")
    print(f"  {dossier.official_narrative[:100]}...")

    print(f"\nReconstructed Truth:")
    print(f"  {dossier.reconstructed_truth[:200]}...")

    print(f"\nEvidence by Type:")
    for ev_type, items in dossier.evidence_by_type.items():
        print(f"  {ev_type}: {len(items)} items")

    print(f"\nMechanisms of Suppression:")
    for mech in dossier.mechanisms_of_suppression[:3]:
        print(f"  - {mech}")

    print(f"\nBroader Implications:")
    for impl in dossier.broader_implications:
        print(f"  - {impl}")

    print(f"\nQuestions to Investigate:")
    for q in dossier.questions_to_investigate[:3]:
        print(f"  - {q}")

    print(f"\nConfidence Scores:")
    print(f"  Overall: {dossier.overall_confidence:.1%}")
    print(f"  Evidence convergence: {dossier.evidence_convergence_score:.1%}")
    print(f"  Paradigm shift potential: {dossier.paradigm_shift_potential:.1%}")


def demo_cosmic_question():
    """Demonstrate cosmic question analysis capabilities."""
    print("\n" + "="*70)
    print("DEMO 3: Cosmic Question Analysis")
    print("="*70)

    aletheia = Aletheia()

    # Analyze a cosmic question
    question = "What is the nature of consciousness and reality?"

    cosmic_analysis = aletheia.analyze_cosmic_question(question)

    print(f"\nQuestion: {cosmic_analysis.question}")
    print(f"Domain: {cosmic_analysis.domain}")

    print(f"\nCultural Expressions ({len(cosmic_analysis.cultural_expressions)}):")
    for culture, description in list(cosmic_analysis.cultural_expressions.items())[:3]:
        print(f"  {culture}: {description[:80]}...")

    print(f"\nShared Concepts:")
    for concept in cosmic_analysis.shared_concepts[:4]:
        print(f"  - {concept}")

    print(f"\nConvergent Patterns:")
    for pattern in cosmic_analysis.convergent_patterns[:3]:
        print(f"  - {pattern}")

    print(f"\nPhysics Correlations:")
    for corr in cosmic_analysis.physics_correlations[:3]:
        print(f"  - {corr}")

    print(f"\nReframed Question:")
    print(f"  {cosmic_analysis.reframed_question[:200]}...")

    print(f"\nInvestigation Paths:")
    for path in cosmic_analysis.investigation_paths[:3]:
        print(f"  - {path}")

    print(f"\nSynthesis:")
    print(f"  {cosmic_analysis.synthesis[:300]}...")

    print(f"\nConfidence: {cosmic_analysis.confidence_in_synthesis:.1%}")


def demo_cosmology_comparison():
    """Demonstrate cosmology comparison capabilities."""
    print("\n" + "="*70)
    print("DEMO 4: Cosmology Comparison - Hindu and Aboriginal")
    print("="*70)

    aletheia = Aletheia()

    # Compare two distant cosmologies
    comparison = aletheia.compare_cosmologies("Hindu", "Aboriginal")

    print(f"\nComparing: {comparison['culture_a']} and {comparison['culture_b']}")

    print(f"\nStructural Parallels: {len(comparison['structural_parallels'])}")
    for parallel in comparison['structural_parallels'][:3]:
        print(f"  - {parallel['concept_a']} <-> {parallel['concept_b']}")
        print(f"    Shared science: {', '.join(parallel['shared_science'])}")
        print(f"    Implication: {parallel['implication']}")

    print(f"\nSynthesis:")
    print(f"  {comparison['synthesis']}")


def demo_genetic_analysis():
    """Demonstrate genetic analysis capabilities."""
    print("\n" + "="*70)
    print("DEMO 5: Genetic Evidence Analysis")
    print("="*70)

    aletheia = Aletheia()

    # Analyze genetic evidence that contradicts claimed origin
    genetic_data = {
        "mtdna_haplogroup": "L3",
        "y_haplogroup": "E1b1a"
    }

    claimed_origin = GeoLocation(52.0, 0.0, "Britain", "Europe", 100)

    result = aletheia.analyze_genetic_evidence(
        "SAMPLE-001",
        genetic_data,
        claimed_origin
    )

    print(f"\nSample ID: {result.sample_id}")
    print(f"Maternal haplogroup: {result.maternal_haplogroup}")
    print(f"Paternal haplogroup: {result.paternal_haplogroup}")
    print(f"\nGeographic origin: {result.geographic_origin.region}")
    print(f"Time depth: {result.time_depth_years} years")
    print(f"\nConflicts with claimed origin: {result.conflicts_with_claimed}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"\nAnalysis: {result.analysis}")


def demo_text_decoding():
    """Demonstrate text decoding capabilities."""
    print("\n" + "="*70)
    print("DEMO 6: Ancient Text Decoding")
    print("="*70)

    aletheia = Aletheia()

    # Analyze ancient text
    text = """
    In the beginning was the Word, and the Word was with God.
    The heavens declare the glory of the divine order.
    As above, so below - the cosmic law of correspondence.
    The serpent of wisdom guards the sacred knowledge.
    """

    context = {
        "text_id": "TEXT-001",
        "script": "Greek",
        "era": "Hellenistic",
        "document_type": "Religious/philosophical"
    }

    analysis = aletheia.decode_text(text, "greek", context)

    print(f"\nText ID: {analysis.text_id}")
    print(f"Language: {analysis.language}")
    print(f"Confidence: {analysis.confidence:.1%}")

    print(f"\nSymbols Identified: {len(analysis.symbols_identified)}")
    for symbol in analysis.symbols_identified[:3]:
        print(f"  - {symbol.name}")

    print(f"\nSemantic Themes: {', '.join(analysis.semantic_themes)}")
    print(f"Astronomical References: {', '.join(analysis.astronomical_references)}")
    print(f"Cosmological Concepts: {', '.join(analysis.cosmological_concepts)}")

    print(f"\nPotential Mistranslations: {len(analysis.potential_mistranslations)}")
    for mt in analysis.potential_mistranslations[:2]:
        print(f"  - Term: {mt['term']}")
        print(f"    Issue: {mt['issue']}")
        print(f"    Lost meaning: {mt['lost_meaning']}")

    print(f"\nSuppressed Meanings:")
    for sm in analysis.suppressed_meanings[:3]:
        print(f"  - {sm}")


def main():
    """Run all demonstrations."""
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  ALETHEIA TRUTH VERIFICATION ENGINE - DEMONSTRATION  ".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)

    print("\nAletheia (Αλήθεια) - Greek goddess of truth and disclosure")
    print("A system for verifying truth through multi-domain evidence correlation")

    # Run demonstrations
    demo_artifact_investigation()
    demo_narrative_correction()
    demo_cosmic_question()
    demo_cosmology_comparison()
    demo_genetic_analysis()
    demo_text_decoding()

    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)

    print("""
The Aletheia system provides tools for:

1. ARTIFACT INVESTIGATION
   - Multi-domain evidence correlation
   - Provenance tracing and theft detection
   - Repatriation claim support

2. NARRATIVE CORRECTION
   - Bias detection and analysis
   - Evidence-based reconstruction
   - Corrective dossier generation

3. COSMIC QUESTIONS
   - Cross-cultural cosmology analysis
   - Ancient-modern concept correlation
   - Question reframing and deepening

4. EPISTEMIC REASONING
   - Source reliability assessment
   - Paradigm impact analysis
   - Truth confidence scoring

Use these tools to break the monopoly on historical narrative,
restore suppressed knowledge, and ask better questions about
the nature of reality.
""")


if __name__ == "__main__":
    main()
