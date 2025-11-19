"""
Hydra Main Entry Point
======================

Launch the Hydra multi-AI fusion system.

Usage:
    python -m hydra.main [command]

Commands:
    start       Start the Hydra system
    dashboard   Launch the web dashboard
    demo        Run a demonstration
"""

import asyncio
import argparse
import logging
import sys

from .config import HydraConfig
from .core.orchestrator import HydraOrchestrator
from .tentacles.ai_models import ClaudeTentacle, GeminiTentacle, ChatGPTTentacle, LocalLLMTentacle
from .tentacles.security import (
    ReconTentacle, VulnScanTentacle, ForensicsTentacle,
    AuditTentacle, ExploitTentacle, ThreatIntelTentacle
)
from .swarm.factory import SwarmFactory
from .swarm.coordinator import SwarmCoordinator


def setup_logging(level: str = "INFO") -> None:
    """Configure logging"""
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


async def create_hydra() -> HydraOrchestrator:
    """
    Create and configure the Hydra system with all tentacles.
    """
    config = HydraConfig.from_env()
    orchestrator = HydraOrchestrator(config)

    # Add AI model tentacles
    ai_tentacles = [
        ClaudeTentacle("claude_primary"),
        GeminiTentacle("gemini_primary"),
        ChatGPTTentacle("chatgpt_primary"),
        LocalLLMTentacle("local_llm"),
    ]

    # Add security tentacles
    security_tentacles = [
        ReconTentacle("recon"),
        VulnScanTentacle("vulnscan"),
        ForensicsTentacle("forensics"),
        AuditTentacle("audit"),
        ExploitTentacle("exploit"),
        ThreatIntelTentacle("threatintel"),
    ]

    # Register all tentacles
    for tentacle in ai_tentacles + security_tentacles:
        await orchestrator.add_tentacle(tentacle.tentacle_id, tentacle)

    # Create swarm factory
    orchestrator.swarm_factory = SwarmFactory(orchestrator)
    orchestrator.swarm_coordinator = SwarmCoordinator(orchestrator.swarm_factory)

    return orchestrator


async def run_demo(orchestrator: HydraOrchestrator) -> None:
    """Run a demonstration of Hydra capabilities"""
    print("\n" + "=" * 60)
    print("🐙 HYDRA DEMO - Multi-AI Fusion Cybersecurity System")
    print("=" * 60 + "\n")

    # Start the system
    await orchestrator.start()
    print("✅ Hydra system started\n")

    # Show status
    status = orchestrator.get_status()
    print(f"📊 Active tentacles: {status['tentacles']['count']}")
    print(f"   Tentacle IDs: {', '.join(status['tentacles']['ids'])}\n")

    # Demo 1: Simple analysis task
    print("🔍 Demo 1: Running AI analysis...")
    result = await orchestrator.execute(
        task_type="reasoning",
        payload={
            "prompt": "Analyze this log entry for security issues: 'Failed login attempt for user admin from IP 192.168.1.100 - attempt 50'",
            "system": "You are a cybersecurity analyst. Analyze the following and provide security insights."
        },
        tentacles=["claude_primary"]
    )

    if result.success:
        print(f"   Result: {result.data}\n")
    else:
        print(f"   Error: {result.error}\n")

    # Demo 2: Create a swarm
    print("🐝 Demo 2: Creating reconnaissance swarm...")
    swarm_id = await orchestrator.swarm_factory.create_swarm(template_name="recon")
    swarm_status = orchestrator.swarm_factory.get_swarm_status(swarm_id)
    print(f"   Swarm ID: {swarm_id}")
    print(f"   Agents: {swarm_status['agent_count']}\n")

    # Demo 3: Show swarm templates
    print("📋 Available swarm templates:")
    for template in orchestrator.swarm_factory.list_templates():
        print(f"   - {template['name']}: {template['description']}")

    print("\n" + "=" * 60)
    print("Demo complete! Hydra is ready for cybersecurity operations.")
    print("=" * 60 + "\n")

    # Stop the system
    await orchestrator.stop()


def run_dashboard(orchestrator: HydraOrchestrator) -> None:
    """Launch the web dashboard"""
    from .dashboard.app import HydraDashboard

    dashboard = HydraDashboard(orchestrator)
    dashboard.run()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Hydra - Multi-AI Fusion Cybersecurity System"
    )
    parser.add_argument(
        "command",
        choices=["start", "dashboard", "demo"],
        help="Command to run"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Dashboard port"
    )

    args = parser.parse_args()

    setup_logging(args.log_level)

    # Create orchestrator
    orchestrator = asyncio.run(create_hydra())

    if args.command == "demo":
        asyncio.run(run_demo(orchestrator))
    elif args.command == "dashboard":
        # Start orchestrator first
        asyncio.run(orchestrator.start())
        run_dashboard(orchestrator)
    elif args.command == "start":
        asyncio.run(orchestrator.start())
        print("Hydra system started. Press Ctrl+C to stop.")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            asyncio.run(orchestrator.stop())
            print("\nHydra system stopped.")


if __name__ == "__main__":
    main()
