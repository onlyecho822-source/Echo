#!/usr/bin/env python3
"""
Hydra Quick Start Example
=========================

Shows basic usage of the Hydra multi-AI fusion system.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hydra.config import HydraConfig
from hydra.core.orchestrator import HydraOrchestrator
from hydra.tentacles.ai_models import ClaudeTentacle, LocalLLMTentacle
from hydra.tentacles.security import ReconTentacle, ForensicsTentacle


async def main():
    """Quick start demonstration"""
    print("🐙 Hydra Quick Start\n")

    # Create the orchestrator
    config = HydraConfig()
    orchestrator = HydraOrchestrator(config)

    # Add some tentacles
    await orchestrator.add_tentacle("claude", ClaudeTentacle())
    await orchestrator.add_tentacle("local", LocalLLMTentacle())
    await orchestrator.add_tentacle("recon", ReconTentacle())
    await orchestrator.add_tentacle("forensics", ForensicsTentacle())

    # Start the system
    await orchestrator.start()

    # Get status
    status = orchestrator.get_status()
    print(f"System Status: {'🟢 Online' if status['running'] else '🔴 Offline'}")
    print(f"Active Tentacles: {status['tentacles']['count']}")
    print(f"Tentacles: {', '.join(status['tentacles']['ids'])}\n")

    # Example 1: Run a security analysis
    print("📝 Example 1: Security Analysis")
    print("-" * 40)

    result = await orchestrator.execute(
        task_type="reasoning",
        payload={
            "prompt": """Analyze this security scenario:

            A server's auth.log shows 500 failed SSH login attempts
            from IP 45.33.32.156 in the last hour, all targeting
            the 'root' user.

            What type of attack is this? What are the immediate
            remediation steps?""",
            "system": "You are a senior security analyst."
        },
        tentacles=["claude"]
    )

    if result.success:
        print(f"Analysis: {result.data}\n")
    else:
        print(f"(Running in demo mode - no API key)\n")

    # Example 2: Log analysis with forensics tentacle
    print("🔍 Example 2: Log Analysis")
    print("-" * 40)

    logs = [
        "2024-01-15 10:23:45 Failed password for root from 45.33.32.156",
        "2024-01-15 10:23:46 Failed password for root from 45.33.32.156",
        "2024-01-15 10:25:00 Accepted password for admin from 192.168.1.50",
        "2024-01-15 10:30:00 sudo: admin : command not allowed ; TTY=pts/0",
        "2024-01-15 10:35:00 Connection closed by 45.33.32.156 [preauth]",
    ]

    result = await orchestrator.execute(
        task_type="log_analysis",
        payload={
            "type": "log_analysis",
            "logs": logs
        },
        tentacles=["forensics"]
    )

    if result.success:
        data = result.data
        print(f"Total logs analyzed: {data.get('total_logs', 0)}")
        print(f"Suspicious entries found: {data.get('suspicious_count', 0)}")
        for finding in data.get('findings', [])[:3]:
            print(f"  - Line {finding['line']}: {finding['pattern']}")
    print()

    # Example 3: Multi-tentacle fusion
    print("🔀 Example 3: Multi-AI Fusion")
    print("-" * 40)
    print("Running analysis across multiple AI tentacles...")

    result = await orchestrator.execute(
        task_type="reasoning",
        payload={
            "prompt": "What are the top 3 security hardening steps for a new Linux server?",
            "system": "Provide concise, actionable security recommendations."
        },
        tentacles=["claude", "local"]  # Uses both tentacles
    )

    print(f"Fusion result: {result.data}\n")

    # Cleanup
    await orchestrator.stop()
    print("✅ Example complete!")


if __name__ == "__main__":
    asyncio.run(main())
