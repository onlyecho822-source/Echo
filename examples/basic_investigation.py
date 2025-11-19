#!/usr/bin/env python3
"""
Example: Basic Investigation with Echo Reverse Engineering Engine

This example demonstrates how to:
1. Create an investigation
2. Add sources
3. Extract and validate facts
4. Build timelines
5. Find connections
6. Generate reports
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo_engine import ReverseEngineeringEngine
from echo_engine.core.models import SourceType
from echo_engine.reporters import MarkdownReporter


def main():
    # Initialize the engine
    engine = ReverseEngineeringEngine()

    # Create a new investigation
    investigation = engine.create_investigation(
        name="Historical Event Analysis",
        query="What were the key events and their sequence?",
        description="Analyzing multiple sources to reconstruct a timeline of events",
    )

    print(f"Created investigation: {investigation.name}")
    print(f"ID: {investigation.id}\n")

    # Add some sample sources
    source1_content = """
    The project was announced on January 15, 2024 by the lead developer.
    Initial development began in February 2024. The team consisted of five
    engineers who worked on the core architecture. According to the project
    manager, the goal was to create a transparent and verifiable system.

    By March 2024, the first prototype was completed. Testing revealed
    several issues that needed to be addressed. The team reported that
    performance was 50% better than expected.
    """

    source2_content = """
    Development of the system started in early 2024. The announcement
    was made in mid-January by the project lead. Five team members
    contributed to the initial architecture design.

    The prototype phase occurred in March 2024. Some sources disputed
    the performance claims, stating that improvements were closer to 30%.
    However, the core functionality was confirmed to be working as intended.
    """

    source3_content = """
    The system launch was confirmed for Q2 2024. According to internal
    documents, the January 15, 2024 announcement marked the official
    start date. The development team of five engineers completed the
    prototype by March 2024.

    Performance testing showed improvements between 30-50% depending
    on the specific use case. The project manager stated that all
    primary objectives were met ahead of schedule.
    """

    # Add sources to investigation
    engine.add_source(
        investigation.id,
        name="Source A - Project Documentation",
        content=source1_content,
        source_type=SourceType.DOCUMENT,
        author="Project Team",
    )

    engine.add_source(
        investigation.id,
        name="Source B - External Report",
        content=source2_content,
        source_type=SourceType.DOCUMENT,
        author="External Analyst",
    )

    engine.add_source(
        investigation.id,
        name="Source C - Internal Memo",
        content=source3_content,
        source_type=SourceType.DOCUMENT,
        author="Project Manager",
    )

    print(f"Added {len(investigation.sources)} sources\n")

    # Extract facts from sources
    print("Extracting facts...")
    facts = engine.extract_facts(investigation.id)
    print(f"Extracted {len(facts)} facts\n")

    # Validate facts
    print("Validating facts...")
    validation_results = engine.validate_facts(investigation.id)

    verified = sum(1 for s in validation_results.values() if s.value == "verified")
    disputed = sum(1 for s in validation_results.values() if s.value == "disputed")
    print(f"Verified: {verified}, Disputed: {disputed}\n")

    # Build timeline
    print("Building timeline...")
    timeline = engine.build_timeline(
        investigation.id,
        name="Project Development Timeline",
        description="Key events in the project development",
    )
    print(f"Timeline created with {len(timeline.events)} events\n")

    # Find connections
    print("Finding connections...")
    connections = engine.find_connections(investigation.id)
    print(f"Found {len(connections)} connections\n")

    # Build provenance chain for a fact
    if investigation.facts:
        fact = investigation.facts[0]
        print(f"Building provenance chain for: {fact.statement[:50]}...")
        chain = engine.build_provenance_chain(
            investigation.id,
            fact.id,
            name="Sample Provenance Chain",
        )
        print(f"Provenance chain created with {len(chain.nodes)} nodes\n")

    # Generate report
    print("Generating report...")
    report = engine.generate_report(investigation.id, format="markdown")

    # Print report
    print("\n" + "=" * 60)
    print("INVESTIGATION REPORT")
    print("=" * 60 + "\n")
    print(report)

    # Save investigation
    save_path = f".echo_data/{investigation.id}.json"
    os.makedirs(".echo_data", exist_ok=True)
    engine.save_investigation(investigation.id, save_path)
    print(f"\nInvestigation saved to: {save_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Sources analyzed: {len(investigation.sources)}")
    print(f"Facts extracted: {len(investigation.facts)}")
    print(f"  - Verified: {len(investigation.get_verified_facts())}")
    print(f"  - Disputed: {len(investigation.get_disputed_facts())}")
    print(f"Timeline events: {len(timeline.events)}")
    print(f"Connections found: {len(connections)}")


if __name__ == "__main__":
    main()
