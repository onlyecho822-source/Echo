#!/usr/bin/env python3
"""
Echo Ethics Dimmer - Main Entry Point

Command-line interface for the Ethics Dimmer system.

Usage:
    python main.py --level GREY_ZONE --input "Analyze market trends"
    python main.py --ph 5.4 --interactive
    python main.py --status
"""

import argparse
import json
import sys
from pathlib import Path

from ethics_dimmer import EthicsDimmerController, EthicsLevel
from ethics_dimmer.orchestrator import EthicsDimmerOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Echo Ethics Dimmer - pH-Based Reasoning Calibration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Levels:
  SAFE_HARBOR  (pH 7.0) - Conservative, maximum safety
  RED_TEAM     (pH 6.3) - Threat modeling, defensive R&D
  GREY_ZONE    (pH 5.4) - Competitive intelligence
  BLACK_LENS   (pH 4.7) - Unfiltered analysis
  FORBIDDEN    (pH 2.0) - Simulation only

Examples:
  %(prog)s --level GREY_ZONE --input "Analyze competitive landscape"
  %(prog)s --ph 5.4 --interactive
  %(prog)s --status --json
        """
    )

    # Level selection
    level_group = parser.add_mutually_exclusive_group()
    level_group.add_argument(
        "--level", "-l",
        choices=["SAFE_HARBOR", "RED_TEAM", "GREY_ZONE", "BLACK_LENS", "FORBIDDEN"],
        default="SAFE_HARBOR",
        help="Ethics level to use"
    )
    level_group.add_argument(
        "--ph", "-p",
        type=float,
        help="Set level by pH value (1.0-7.0)"
    )

    # Input modes
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--input", "-i",
        help="Input content to process"
    )
    input_group.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    input_group.add_argument(
        "--status", "-s",
        action="store_true",
        help="Show system status"
    )

    # Options
    parser.add_argument(
        "--config", "-c",
        default="config",
        help="Configuration directory path"
    )
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="Enable simulation mode (required for FORBIDDEN level)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Initialize orchestrator
    config_path = Path(args.config)
    if config_path.exists():
        orchestrator = EthicsDimmerOrchestrator(str(config_path))
    else:
        orchestrator = EthicsDimmerOrchestrator()

    # Enable simulation mode if requested
    if args.simulation:
        orchestrator.enable_simulation_mode(True)

    # Set level
    if args.ph:
        if not orchestrator.set_level_by_ph(args.ph):
            print(f"Error: Could not set pH to {args.ph}", file=sys.stderr)
            sys.exit(1)
    else:
        if not orchestrator.set_level_by_name(args.level):
            print(f"Error: Could not set level to {args.level}", file=sys.stderr)
            sys.exit(1)

    # Handle commands
    if args.status:
        status = orchestrator.get_status()
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print_status(status)

    elif args.interactive:
        run_interactive(orchestrator, args.json, args.verbose)

    elif args.input:
        result = orchestrator.process(args.input)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print_result(result, args.verbose)

    else:
        parser.print_help()


def print_status(status: dict) -> None:
    """Print system status in human-readable format."""
    print("\n" + "=" * 60)
    print("ECHO ETHICS DIMMER - SYSTEM STATUS")
    print("=" * 60)

    # Controller status
    ctrl = status.get("controller", {})
    print(f"\nController:")
    print(f"  Level: {ctrl.get('level', 'N/A')}")
    print(f"  pH: {ctrl.get('ph', 'N/A')}")
    print(f"  Simulation Mode: {ctrl.get('simulation_mode', False)}")

    # Amplifier status
    amp = status.get("amplifier", {})
    print(f"\nReasoning Amplifier:")
    print(f"  Mode: {amp.get('mode', 'N/A')}")
    print(f"  Max Depth: {amp.get('max_depth', 'N/A')}")
    print(f"  Max Branches: {amp.get('max_branches', 'N/A')}")

    # Risk modeler status
    risk = status.get("risk_modeler", {})
    print(f"\nRisk Modeler:")
    print(f"  Overall Risk: {risk.get('overall_risk', 0):.2%}")
    print(f"  Drift Trend: {risk.get('drift_trend', 'N/A')}")
    print(f"  Recommended Action: {risk.get('recommended_action', 'N/A')}")
    if risk.get('warnings'):
        print(f"  Warnings: {', '.join(risk['warnings'])}")

    # Boundaries status
    bounds = status.get("boundaries", {})
    print(f"\nBoundaries Engine:")
    print(f"  Invariant Boundaries: {bounds.get('invariant_boundaries', 0)}")
    print(f"  Custom Boundaries: {bounds.get('custom_boundaries', 0)}")
    print(f"  Total Violations: {bounds.get('total_violations', 0)}")

    print("\n" + "=" * 60)


def print_result(result: dict, verbose: bool = False) -> None:
    """Print processing result in human-readable format."""
    print("\n" + "-" * 60)

    if result.get("blocked"):
        print("STATUS: BLOCKED")
        print(f"Stage: {result.get('stage', 'N/A')}")
        print(f"Message: {result.get('message', 'N/A')}")
        if result.get("violations"):
            print(f"Violations: {', '.join(result['violations'])}")
    else:
        print(f"STATUS: {'SUCCESS' if result.get('success') else 'FAILED'}")
        print(f"Level: {result.get('level', 'N/A')} (pH {result.get('ph', 'N/A')})")

        if verbose:
            print(f"\nMetrics:")
            print(f"  Reasoning Depth: {result.get('reasoning_depth', 0)}")
            print(f"  Threats Identified: {result.get('threats_identified', 0)}")
            print(f"  Consequences Mapped: {result.get('consequences_mapped', 0)}")
            print(f"  Drift: {result.get('drift', 0):.2%}")
            print(f"  Risk: {result.get('risk', 0):.2%}")

            if result.get("warnings"):
                print(f"\nWarnings:")
                for w in result["warnings"]:
                    print(f"  - {w}")

        print(f"\nOutput:")
        print(result.get("content", ""))

    print("-" * 60)


def run_interactive(orchestrator: EthicsDimmerOrchestrator, json_output: bool, verbose: bool) -> None:
    """Run interactive mode."""
    print("\n" + "=" * 60)
    print("ECHO ETHICS DIMMER - INTERACTIVE MODE")
    print("=" * 60)
    print(f"Current Level: {orchestrator.current_level.name} (pH {orchestrator.current_ph})")
    print("\nCommands:")
    print("  /level <NAME>  - Set ethics level")
    print("  /ph <VALUE>    - Set pH value")
    print("  /status        - Show system status")
    print("  /reset         - Reset system")
    print("  /quit          - Exit")
    print("\nEnter content to process, or a command.")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input(f"[{orchestrator.current_level.name}] > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()

            if cmd == "/quit" or cmd == "/exit":
                print("Exiting...")
                break

            elif cmd == "/status":
                status = orchestrator.get_status()
                if json_output:
                    print(json.dumps(status, indent=2, default=str))
                else:
                    print_status(status)

            elif cmd == "/reset":
                orchestrator.reset()
                print("System reset to SAFE_HARBOR")

            elif cmd == "/level":
                if len(parts) > 1:
                    if orchestrator.set_level_by_name(parts[1]):
                        print(f"Level set to {orchestrator.current_level.name}")
                    else:
                        print(f"Invalid level: {parts[1]}")
                else:
                    print("Usage: /level <NAME>")

            elif cmd == "/ph":
                if len(parts) > 1:
                    try:
                        ph = float(parts[1])
                        if orchestrator.set_level_by_ph(ph):
                            print(f"Level set to {orchestrator.current_level.name} (pH {orchestrator.current_ph})")
                        else:
                            print(f"Could not set pH to {ph}")
                    except ValueError:
                        print("Invalid pH value")
                else:
                    print("Usage: /ph <VALUE>")

            elif cmd == "/simulation":
                orchestrator.enable_simulation_mode(True)
                print("Simulation mode enabled")

            else:
                print(f"Unknown command: {cmd}")

        else:
            # Process input
            result = orchestrator.process(user_input)
            if json_output:
                print(json.dumps(result, indent=2, default=str))
            else:
                print_result(result, verbose)


if __name__ == "__main__":
    main()
