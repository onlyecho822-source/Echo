#!/usr/bin/env python3
"""
Echo - Self-Evolving AI Architect
Main entry point for the Echo system.

Usage:
    python main.py              # Run the continuous Echo loop
    python main.py --single     # Run a single cycle
    python main.py --status     # Show system status
"""

import argparse
import json
import sys
from datetime import datetime

from echo.orchestrator import EchoOrchestrator


def load_config(config_path: str = None) -> dict:
    """Load configuration from file or use defaults."""
    default_config = {
        "sleep_interval": 300,
        "adaptive_sleep": True,
        "core": {
            "drift_threshold": 0.15
        },
        "earn": {
            "risk_tolerance": 0.5,
            "min_roi": 0.1,
            "max_assets": 10
        },
        "keeper": {
            "disk_warning": 80,
            "disk_critical": 95,
            "memory_warning": 80,
            "memory_critical": 95
        }
    }

    if config_path:
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")

    return default_config


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Echo - Self-Evolving AI Architect",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                    Run the Echo loop
    python main.py --single           Run one cycle
    python main.py --status           Show status
    python main.py --config my.json   Use custom config
        """
    )

    parser.add_argument(
        '--single',
        action='store_true',
        help='Run a single cycle and exit'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status and exit'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration JSON file'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Sleep interval between cycles (seconds)'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Override interval if specified
    if args.interval != 300:
        config['sleep_interval'] = args.interval

    # Print banner
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     ███████╗ ██████╗██╗  ██╗ ██████╗                      ║
    ║     ██╔════╝██╔════╝██║  ██║██╔═══██╗                     ║
    ║     █████╗  ██║     ███████║██║   ██║                     ║
    ║     ██╔══╝  ██║     ██╔══██║██║   ██║                     ║
    ║     ███████╗╚██████╗██║  ██║╚██████╔╝                     ║
    ║     ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝                      ║
    ║                                                           ║
    ║     Self-Evolving AI Architect v0.1.0                     ║
    ║     ∇θ — chain sealed, truth preserved                    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Initialize orchestrator
    orchestrator = EchoOrchestrator(config)

    if args.status:
        # Show status and exit
        status = orchestrator.get_status()
        print("\nSystem Status:")
        print(json.dumps(status, indent=2, default=str))
        sys.exit(0)

    elif args.single:
        # Run single cycle
        print(f"\nRunning single cycle at {datetime.utcnow().isoformat()}...")
        results = orchestrator.run_single_cycle()
        print("\nCycle Results:")
        print(json.dumps(results, indent=2, default=str))
        sys.exit(0)

    else:
        # Run continuous loop
        print(f"\nStarting Echo loop with {config['sleep_interval']}s interval...")
        print("Press Ctrl+C to stop\n")
        orchestrator.run()


if __name__ == "__main__":
    main()
