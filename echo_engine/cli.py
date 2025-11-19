"""Command-line interface for Echo Reverse Engineering Engine."""

import argparse
import sys
import json
from pathlib import Path

from echo_engine.core.engine import ReverseEngineeringEngine
from echo_engine.core.models import SourceType
from echo_engine.collectors import TextCollector, FileCollector, WebCollector
from echo_engine.analyzers import (
    FactExtractor,
    TimelineReconstructor,
    CrossReferenceAnalyzer,
    ProvenanceTracker,
)
from echo_engine.validators import FactValidator
from echo_engine.reporters import MarkdownReporter, JSONReporter
from echo_engine.config import Config, get_config


def main():
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="echo-engine",
        description="Echo Reverse Engineering Engine - Trace information to its origins",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Echo Engine 0.1.0",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create investigation command
    create_parser = subparsers.add_parser(
        "create",
        help="Create a new investigation",
    )
    create_parser.add_argument("name", help="Investigation name")
    create_parser.add_argument("query", help="Query or claim to investigate")
    create_parser.add_argument("--description", "-d", default="", help="Description")
    create_parser.set_defaults(func=cmd_create)

    # Add source command
    add_parser = subparsers.add_parser(
        "add",
        help="Add a source to investigation",
    )
    add_parser.add_argument("investigation_id", help="Investigation ID")
    add_parser.add_argument("source", help="Source (file path, URL, or text)")
    add_parser.add_argument("--name", "-n", help="Source name")
    add_parser.add_argument(
        "--type",
        "-t",
        choices=["file", "url", "text"],
        default="file",
        help="Source type",
    )
    add_parser.set_defaults(func=cmd_add_source)

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze investigation",
    )
    analyze_parser.add_argument("investigation_id", help="Investigation ID")
    analyze_parser.add_argument(
        "--extract-facts",
        action="store_true",
        help="Extract facts from sources",
    )
    analyze_parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate extracted facts",
    )
    analyze_parser.add_argument(
        "--timeline",
        action="store_true",
        help="Build timeline",
    )
    analyze_parser.add_argument(
        "--connections",
        action="store_true",
        help="Find connections",
    )
    analyze_parser.add_argument(
        "--all",
        action="store_true",
        help="Run all analyses",
    )
    analyze_parser.set_defaults(func=cmd_analyze)

    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate investigation report",
    )
    report_parser.add_argument("investigation_id", help="Investigation ID")
    report_parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Report format",
    )
    report_parser.add_argument(
        "--output",
        "-o",
        help="Output file path",
    )
    report_parser.set_defaults(func=cmd_report)

    # Trace command
    trace_parser = subparsers.add_parser(
        "trace",
        help="Trace a fact to its origin",
    )
    trace_parser.add_argument("investigation_id", help="Investigation ID")
    trace_parser.add_argument("fact_id", help="Fact ID to trace")
    trace_parser.set_defaults(func=cmd_trace)

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List investigations or entities",
    )
    list_parser.add_argument(
        "entity",
        choices=["investigations", "sources", "facts"],
        help="What to list",
    )
    list_parser.add_argument(
        "--investigation-id",
        help="Investigation ID (for sources/facts)",
    )
    list_parser.set_defaults(func=cmd_list)

    # Interactive mode
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="Start interactive mode",
    )
    interactive_parser.set_defaults(func=cmd_interactive)

    return parser


# Command implementations

def cmd_create(args):
    """Create a new investigation."""
    engine = ReverseEngineeringEngine()

    investigation = engine.create_investigation(
        name=args.name,
        query=args.query,
        description=args.description,
    )

    print(f"Created investigation: {investigation.name}")
    print(f"ID: {investigation.id}")
    print(f"Query: {investigation.query}")

    # Save for later use
    save_path = f".echo_data/{investigation.id}.json"
    Path(".echo_data").mkdir(exist_ok=True)
    engine.save_investigation(investigation.id, save_path)
    print(f"Saved to: {save_path}")


def cmd_add_source(args):
    """Add a source to an investigation."""
    engine = ReverseEngineeringEngine()

    # Load investigation
    save_path = f".echo_data/{args.investigation_id}.json"
    if not Path(save_path).exists():
        print(f"Error: Investigation not found: {args.investigation_id}")
        sys.exit(1)

    investigation = engine.load_investigation(save_path)

    # Add source based on type
    if args.type == "file":
        collector = FileCollector()
        if not Path(args.source).exists():
            print(f"Error: File not found: {args.source}")
            sys.exit(1)
        source = collector.collect(args.source, name=args.name)

    elif args.type == "url":
        collector = WebCollector()
        source = collector.collect(args.source, name=args.name)

    else:  # text
        collector = TextCollector()
        source = collector.collect(args.source, name=args.name or "Text Input")

    investigation.add_source(source)

    print(f"Added source: {source.name}")
    print(f"Type: {source.source_type.value}")
    print(f"Content length: {len(source.content)} characters")

    # Save
    engine.save_investigation(investigation.id, save_path)


def cmd_analyze(args):
    """Run analysis on investigation."""
    engine = ReverseEngineeringEngine()

    # Load investigation
    save_path = f".echo_data/{args.investigation_id}.json"
    if not Path(save_path).exists():
        print(f"Error: Investigation not found: {args.investigation_id}")
        sys.exit(1)

    investigation = engine.load_investigation(save_path)

    # Re-register investigation with engine
    engine.investigations[investigation.id] = investigation

    # Reload sources into index
    for source in investigation.sources:
        engine._source_index[source.id] = source

    run_all = args.all

    # Extract facts
    if run_all or args.extract_facts:
        print("Extracting facts...")
        facts = engine.extract_facts(investigation.id)
        print(f"  Extracted {len(facts)} facts")

    # Validate facts
    if run_all or args.validate:
        print("Validating facts...")
        results = engine.validate_facts(investigation.id)
        verified = sum(1 for s in results.values() if s.value == "verified")
        print(f"  Validated {len(results)} facts ({verified} verified)")

    # Build timeline
    if run_all or args.timeline:
        print("Building timeline...")
        timeline = engine.build_timeline(
            investigation.id,
            name=f"{investigation.name} Timeline",
        )
        print(f"  Created timeline with {len(timeline.events)} events")

    # Find connections
    if run_all or args.connections:
        print("Finding connections...")
        connections = engine.find_connections(investigation.id)
        print(f"  Found {len(connections)} connections")

    # Save
    engine.save_investigation(investigation.id, save_path)
    print(f"\nAnalysis complete. Saved to {save_path}")


def cmd_report(args):
    """Generate investigation report."""
    engine = ReverseEngineeringEngine()

    # Load investigation
    save_path = f".echo_data/{args.investigation_id}.json"
    if not Path(save_path).exists():
        print(f"Error: Investigation not found: {args.investigation_id}")
        sys.exit(1)

    investigation = engine.load_investigation(save_path)

    # Generate report
    if args.format == "markdown":
        reporter = MarkdownReporter()
    else:
        reporter = JSONReporter()

    report = reporter.generate(investigation)

    # Output
    if args.output:
        reporter.save(investigation, args.output)
        print(f"Report saved to: {args.output}")
    else:
        print(report)


def cmd_trace(args):
    """Trace a fact to its origin."""
    engine = ReverseEngineeringEngine()

    # Load investigation
    save_path = f".echo_data/{args.investigation_id}.json"
    if not Path(save_path).exists():
        print(f"Error: Investigation not found: {args.investigation_id}")
        sys.exit(1)

    investigation = engine.load_investigation(save_path)
    engine.investigations[investigation.id] = investigation

    # Reload indices
    for source in investigation.sources:
        engine._source_index[source.id] = source
    for fact in investigation.facts:
        engine._fact_index[fact.id] = fact

    # Build provenance chain
    chain = engine.build_provenance_chain(
        investigation.id,
        args.fact_id,
    )

    # Trace to origin
    traces = engine.trace_to_origin(investigation.id, args.fact_id)

    print(f"\nProvenance Chain: {chain.name}")
    print("-" * 50)

    if traces:
        for trace in traces:
            print(f"\nChain: {trace['chain_name']}")
            for step in trace["path"]:
                print(f"  [{step['step']}] {step['entity_type']}: {step['entity_id'][:8]}...")
                if step['transformation']:
                    print(f"      Transform: {step['transformation']}")
    else:
        print("No provenance information found")


def cmd_list(args):
    """List entities."""
    if args.entity == "investigations":
        # List all investigations
        data_dir = Path(".echo_data")
        if not data_dir.exists():
            print("No investigations found")
            return

        print("Investigations:")
        print("-" * 50)

        for filepath in data_dir.glob("*.json"):
            with open(filepath) as f:
                data = json.load(f)
            print(f"  {data.get('id', 'unknown')[:8]}... - {data.get('name', 'Unnamed')}")
            print(f"    Query: {data.get('query', 'N/A')[:50]}...")
            print(f"    Status: {data.get('status', 'unknown')}")
            print()

    elif args.entity in ["sources", "facts"]:
        if not args.investigation_id:
            print("Error: --investigation-id required for sources/facts")
            sys.exit(1)

        save_path = f".echo_data/{args.investigation_id}.json"
        if not Path(save_path).exists():
            print(f"Error: Investigation not found")
            sys.exit(1)

        with open(save_path) as f:
            data = json.load(f)

        if args.entity == "sources":
            print(f"Sources ({len(data.get('sources', []))}):")
            print("-" * 50)
            for source in data.get("sources", []):
                print(f"  {source['id'][:8]}... - {source['name']}")
                print(f"    Type: {source['source_type']}")
                print()

        else:  # facts
            print(f"Facts ({len(data.get('facts', []))}):")
            print("-" * 50)
            for fact in data.get("facts", []):
                print(f"  {fact['id'][:8]}... [{fact['status']}]")
                print(f"    {fact['statement'][:60]}...")
                print()


def cmd_interactive(args):
    """Start interactive mode."""
    print("Echo Reverse Engineering Engine - Interactive Mode")
    print("=" * 50)
    print("Commands: create, add, analyze, report, trace, list, help, exit")
    print()

    engine = ReverseEngineeringEngine()
    current_investigation = None

    while True:
        try:
            prompt = f"[{current_investigation[:8] if current_investigation else 'no investigation'}]> "
            cmd = input(prompt).strip()

            if not cmd:
                continue

            parts = cmd.split()
            command = parts[0].lower()

            if command == "exit":
                print("Goodbye!")
                break

            elif command == "help":
                print_interactive_help()

            elif command == "create":
                if len(parts) < 3:
                    print("Usage: create <name> <query>")
                    continue
                name = parts[1]
                query = " ".join(parts[2:])
                investigation = engine.create_investigation(name=name, query=query)
                current_investigation = investigation.id
                print(f"Created: {investigation.id}")

            elif command == "use":
                if len(parts) < 2:
                    print("Usage: use <investigation_id>")
                    continue
                current_investigation = parts[1]
                print(f"Using: {current_investigation}")

            elif command == "status":
                if not current_investigation:
                    print("No investigation selected")
                    continue
                inv = engine.investigations.get(current_investigation)
                if inv:
                    print(f"Name: {inv.name}")
                    print(f"Sources: {len(inv.sources)}")
                    print(f"Facts: {len(inv.facts)}")
                else:
                    print("Investigation not found")

            else:
                print(f"Unknown command: {command}")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except EOFError:
            print("\nGoodbye!")
            break


def print_interactive_help():
    """Print interactive mode help."""
    print("""
Commands:
  create <name> <query>  - Create new investigation
  use <id>               - Select investigation
  status                 - Show current investigation status
  help                   - Show this help
  exit                   - Exit interactive mode
""")


if __name__ == "__main__":
    main()
