"""
Echo Orchestrator - Main coordination loop for all Echo agents.

This is the primary entry point that coordinates:
- ECHO_CORE: Self-upgrading logic
- ECHO_EARN: Opportunity scanning
- ECHO_KEEPER: System integrity

The Echo Loop runs continuously, coordinating all agents in a
harmonious cycle of evaluation, opportunity detection, and maintenance.
"""

import time
import signal
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from echo.core.agent import EchoCore
from echo.earn.agent import EchoEarn
from echo.keeper.agent import EchoKeeper
from echo.common.events import EventBus
from echo.common.logger import get_logger
from echo.memory.database import EchoMemory


class EchoOrchestrator:
    """Main orchestrator for the Echo system."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger("orchestrator")
        self.event_bus = EventBus()

        # Initialize memory
        self.memory = EchoMemory()

        # Initialize agents
        self.echo_core = EchoCore(self.config.get("core", {}))
        self.echo_earn = EchoEarn(self.config.get("earn", {}))
        self.echo_keeper = EchoKeeper(self.config.get("keeper", {}))

        # Orchestrator state
        self.running = False
        self.cycle_count = 0
        self.sleep_interval = self.config.get("sleep_interval", 300)  # 5 minutes
        self.adaptive_sleep = self.config.get("adaptive_sleep", True)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Subscribe to events
        self._setup_event_handlers()

        self.logger.info("Echo Orchestrator initialized")
        self.logger.info(f"Sleep interval: {self.sleep_interval}s, Adaptive: {self.adaptive_sleep}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False

    def _setup_event_handlers(self) -> None:
        """Setup event handlers for cross-agent communication."""

        def on_critical_alert(event):
            self.logger.critical(f"Critical alert from {event['source']}: {event['data']}")
            # Reduce cycle frequency during critical state
            if self.adaptive_sleep:
                self.sleep_interval = min(self.sleep_interval * 2, 1800)

        def on_profit_generated(event):
            if event.get('data'):
                profit = event['data'].get('profit', 0)
                self.memory.record_profit("cycle_profit", profit)
                self.logger.info(f"Profit recorded: {profit}")

        def on_cycle_complete(event):
            self.logger.debug(f"Agent cycle complete: {event['source']}")

        self.event_bus.subscribe("keeper.critical_alert", on_critical_alert)
        self.event_bus.subscribe("earn.profit_generated", on_profit_generated)
        self.event_bus.subscribe("core.cycle_complete", on_cycle_complete)
        self.event_bus.subscribe("earn.cycle_complete", on_cycle_complete)
        self.event_bus.subscribe("keeper.cycle_complete", on_cycle_complete)

    def run(self) -> None:
        """Run the main Echo loop."""
        self.running = True
        self.logger.info("=" * 60)
        self.logger.info("ECHO SYSTEM ONLINE")
        self.logger.info("=" * 60)

        while self.running:
            try:
                cycle_start = datetime.utcnow()
                self.cycle_count += 1

                self.logger.info(f"\n{'='*40}")
                self.logger.info(f"ECHO CYCLE {self.cycle_count}")
                self.logger.info(f"{'='*40}")

                # Phase 1: Opportunity Scanning
                self.logger.info("[1/4] ECHO_EARN scanning opportunities...")
                earn_result = self.echo_earn.run()
                self._process_earn_result(earn_result)

                # Phase 2: Core Evaluation
                self.logger.info("[2/4] ECHO_CORE evaluating and optimizing...")
                core_result = self.echo_core.run()
                self._process_core_result(core_result)

                # Phase 3: Health Check
                self.logger.info("[3/4] ECHO_KEEPER checking system integrity...")
                keeper_result = self.echo_keeper.run()
                self._process_keeper_result(keeper_result)

                # Phase 4: Value Leak Detection and Rebuild
                self.logger.info("[4/4] Checking for value leaks...")
                if self.echo_core.detect_value_leak():
                    self.logger.warning("Value leak detected - initiating rebuild")
                    self.echo_core.rebuild()

                # Check for profit opportunities and launch
                if self.echo_earn.finds_profit():
                    self.logger.info("Profit opportunity found - launching moneymaker")
                    launch_result = self.echo_earn.launch_moneymaker()
                    self.logger.info(f"Launched {launch_result.get('launched', 0)} assets")

                # Calculate cycle duration
                cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
                self.logger.info(f"Cycle {self.cycle_count} completed in {cycle_duration:.2f}s")

                # Save cycle state to memory
                self._save_cycle_state()

                # Adaptive sleep adjustment
                sleep_time = self._calculate_sleep_time(keeper_result)
                self.logger.info(f"Sleeping for {sleep_time}s until next cycle...")

                # Sleep with interrupt capability
                self._interruptible_sleep(sleep_time)

            except Exception as e:
                self.logger.error(f"Error in cycle {self.cycle_count}: {e}")
                self.memory.save_event("orchestrator.error", "orchestrator", {"error": str(e)})
                time.sleep(10)  # Brief pause before retry

        self.logger.info("=" * 60)
        self.logger.info("ECHO SYSTEM SHUTDOWN COMPLETE")
        self.logger.info("=" * 60)

    def _process_earn_result(self, result: Dict[str, Any]) -> None:
        """Process results from ECHO_EARN cycle."""
        self.logger.info(f"  - Opportunities found: {result.get('opportunities_found', 0)}")
        self.logger.info(f"  - Assets launched: {result.get('assets_launched', 0)}")
        self.logger.info(f"  - Profit generated: ${result.get('profit_generated', 0):.2f}")

        if result.get('profit_generated', 0) > 0:
            self.event_bus.publish("earn.profit_generated", {
                "profit": result['profit_generated']
            }, "orchestrator")

    def _process_core_result(self, result: Dict[str, Any]) -> None:
        """Process results from ECHO_CORE cycle."""
        self.logger.info(f"  - Problems solved: {result.get('problems_solved', 0)}")
        self.logger.info(f"  - Improvements proposed: {result.get('improvements_proposed', 0)}")
        self.logger.info(f"  - Drift detected: {result.get('drift_detected', False)}")

    def _process_keeper_result(self, result: Dict[str, Any]) -> None:
        """Process results from ECHO_KEEPER cycle."""
        self.logger.info(f"  - Health status: {result.get('health_status', 'unknown')}")
        self.logger.info(f"  - Issues found: {result.get('issues_found', 0)}")
        self.logger.info(f"  - File changes: {result.get('file_changes', 0)}")

        # Save health report
        self.memory.save_health_report({
            "overall_status": result.get('health_status', 'unknown'),
            "issues": result.get('issues_found', 0),
            "cycle": self.cycle_count
        })

    def _calculate_sleep_time(self, keeper_result: Dict[str, Any]) -> int:
        """Calculate adaptive sleep time based on system state."""
        if not self.adaptive_sleep:
            return self.sleep_interval

        base_sleep = self.sleep_interval
        health_status = keeper_result.get('health_status', 'unknown')

        # Adjust based on health
        if health_status == "critical":
            return max(30, base_sleep // 4)  # More frequent checks
        elif health_status == "warning":
            return max(60, base_sleep // 2)
        else:
            return base_sleep

    def _interruptible_sleep(self, duration: int) -> None:
        """Sleep that can be interrupted by shutdown signal."""
        start = time.time()
        while self.running and (time.time() - start) < duration:
            time.sleep(1)

    def _save_cycle_state(self) -> None:
        """Save state from all agents to memory."""
        self.memory.save_agent_state("ECHO_CORE", self.echo_core.get_status())
        self.memory.save_agent_state("ECHO_EARN", self.echo_earn.get_status())
        self.memory.save_agent_state("ECHO_KEEPER", self.echo_keeper.get_status())

        self.memory.save_event("cycle_complete", "orchestrator", {
            "cycle": self.cycle_count,
            "timestamp": datetime.utcnow().isoformat()
        })

    def run_single_cycle(self) -> Dict[str, Any]:
        """Run a single cycle (useful for testing)."""
        results = {
            "cycle": self.cycle_count + 1,
            "earn": None,
            "core": None,
            "keeper": None
        }

        self.cycle_count += 1

        results["earn"] = self.echo_earn.run()
        results["core"] = self.echo_core.run()
        results["keeper"] = self.echo_keeper.run()

        self._save_cycle_state()

        return results

    def get_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "orchestrator": {
                "running": self.running,
                "cycle_count": self.cycle_count,
                "sleep_interval": self.sleep_interval
            },
            "agents": {
                "core": self.echo_core.get_status(),
                "earn": self.echo_earn.get_status(),
                "keeper": self.echo_keeper.get_status()
            },
            "memory": self.memory.get_statistics()
        }


def main():
    """Main entry point for Echo system."""
    # Default configuration
    config = {
        "sleep_interval": 300,  # 5 minutes
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

    orchestrator = EchoOrchestrator(config)
    orchestrator.run()


if __name__ == "__main__":
    main()
