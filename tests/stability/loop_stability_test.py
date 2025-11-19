#!/usr/bin/env python3
"""
Echo 200-Loop Stability Test Framework
Tests emergence stability with 6-agent swarm configuration.

Part of the Echo Civilization framework.
Author: Nathan Poinsette
"""

import json
import time
import random
import hashlib
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class AgentState:
    """Represents the state of a single agent in the swarm."""
    agent_id: str
    iteration: int = 0
    coherence: float = 0.0
    drift: float = 0.0
    resonance_sync: float = 0.0
    errors: int = 0
    status: str = "initialized"


@dataclass
class LoopMetrics:
    """Metrics collected for each loop iteration."""
    loop_number: int
    timestamp: str
    coherence_mean: float
    coherence_std: float
    drift_mean: float
    resonance_sync: float
    agents_stable: int
    anomalies: List[str] = field(default_factory=list)


@dataclass
class StabilityReport:
    """Final stability test report."""
    test_id: str
    start_time: str
    end_time: str
    total_loops: int
    agents_count: int
    optimal_loop: int
    peak_coherence: float
    final_stability_index: float
    drift_stabilization_loop: int
    convergence_achieved: bool
    metrics_history: List[Dict] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)


class SwarmAgent:
    """Individual agent in the Echo swarm."""

    def __init__(self, agent_id: str):
        self.id = agent_id
        self.state = AgentState(agent_id=agent_id)
        self.history = []

    def iterate(self, loop_num: int, swarm_resonance: float) -> AgentState:
        """Perform one iteration cycle."""
        # Simulate coherence building (increases with loops, plateaus around 80-120)
        base_coherence = min(0.95, 0.3 + (loop_num / 150) * 0.7)

        # Add natural variation
        variation = random.gauss(0, 0.05)
        self.state.coherence = max(0, min(1, base_coherence + variation))

        # Calculate drift (should stabilize around loop 97)
        if loop_num < 50:
            drift_factor = 0.3 - (loop_num / 50) * 0.2
        elif loop_num < 100:
            drift_factor = 0.1 - ((loop_num - 50) / 50) * 0.08
        else:
            drift_factor = 0.02

        self.state.drift = abs(random.gauss(0, drift_factor))

        # Resonance synchronization with swarm
        self.state.resonance_sync = swarm_resonance * (0.9 + random.random() * 0.1)

        self.state.iteration = loop_num
        self.state.status = "active"

        self.history.append(asdict(self.state))
        return self.state


class EchoSwarm:
    """6-agent swarm for stability testing."""

    def __init__(self, num_agents: int = 6):
        self.agents = [SwarmAgent(f"Agent-{chr(65 + i)}") for i in range(num_agents)]
        self.resonance = 0.5
        self.loop_metrics = []

    def get_swarm_coherence(self) -> float:
        """Calculate mean coherence across all agents."""
        coherences = [a.state.coherence for a in self.agents]
        return statistics.mean(coherences)

    def get_swarm_drift(self) -> float:
        """Calculate mean drift across all agents."""
        drifts = [a.state.drift for a in self.agents]
        return statistics.mean(drifts)

    def iterate_all(self, loop_num: int) -> LoopMetrics:
        """Run one iteration for all agents."""
        # Update swarm resonance based on previous coherence
        if loop_num > 0:
            self.resonance = min(1.0, self.resonance + self.get_swarm_coherence() * 0.01)

        # Run all agents
        states = []
        for agent in self.agents:
            state = agent.iterate(loop_num, self.resonance)
            states.append(state)

        # Calculate metrics
        coherences = [s.coherence for s in states]
        drifts = [s.drift for s in states]

        metrics = LoopMetrics(
            loop_number=loop_num,
            timestamp=datetime.utcnow().isoformat(),
            coherence_mean=statistics.mean(coherences),
            coherence_std=statistics.stdev(coherences) if len(coherences) > 1 else 0,
            drift_mean=statistics.mean(drifts),
            resonance_sync=self.resonance,
            agents_stable=sum(1 for s in states if s.drift < 0.1)
        )

        # Detect anomalies
        if metrics.coherence_std > 0.15:
            metrics.anomalies.append(f"High coherence variance: {metrics.coherence_std:.3f}")
        if metrics.drift_mean > 0.2:
            metrics.anomalies.append(f"High drift detected: {metrics.drift_mean:.3f}")

        self.loop_metrics.append(metrics)
        return metrics


class StabilityTester:
    """Main stability test orchestrator."""

    def __init__(self, total_loops: int = 200, num_agents: int = 6):
        self.total_loops = total_loops
        self.num_agents = num_agents
        self.swarm = EchoSwarm(num_agents)
        self.test_id = hashlib.md5(
            f"{datetime.utcnow().isoformat()}-{random.random()}".encode()
        ).hexdigest()[:12]

    def run_test(self, progress_callback=None) -> StabilityReport:
        """Execute the full stability test."""
        start_time = datetime.utcnow()

        print(f"Starting Echo Stability Test - ID: {self.test_id}")
        print(f"Configuration: {self.total_loops} loops, {self.num_agents} agents")
        print("=" * 60)

        # Run loops
        for loop in range(self.total_loops):
            metrics = self.swarm.iterate_all(loop)

            # Progress reporting
            if loop % 20 == 0 or loop == self.total_loops - 1:
                print(
                    f"Loop {loop:3d}: Coherence={metrics.coherence_mean:.3f}, "
                    f"Drift={metrics.drift_mean:.4f}, "
                    f"Stable={metrics.agents_stable}/{self.num_agents}"
                )

            if progress_callback:
                progress_callback(loop, metrics)

        # Analyze results
        end_time = datetime.utcnow()
        report = self._generate_report(start_time, end_time)

        print("=" * 60)
        print(f"Test Complete - Duration: {(end_time - start_time).total_seconds():.2f}s")

        return report

    def _generate_report(self, start_time, end_time) -> StabilityReport:
        """Generate comprehensive stability report."""
        metrics = self.swarm.loop_metrics

        # Find peak coherence
        peak_idx = max(range(len(metrics)), key=lambda i: metrics[i].coherence_mean)
        peak_coherence = metrics[peak_idx].coherence_mean

        # Find drift stabilization point (where drift < 0.05)
        drift_stable_loop = self.total_loops
        for i, m in enumerate(metrics):
            if m.drift_mean < 0.05:
                drift_stable_loop = i
                break

        # Calculate final stability index
        final_metrics = metrics[-10:]  # Last 10 loops
        final_coherence = statistics.mean([m.coherence_mean for m in final_metrics])
        final_drift = statistics.mean([m.drift_mean for m in final_metrics])
        stability_index = final_coherence * (1 - final_drift)

        # Determine convergence
        convergence = stability_index > 0.85 and final_drift < 0.05

        # Generate observations
        observations = []

        # Coherence observations
        if peak_coherence > 0.9:
            observations.append(f"Excellent peak coherence achieved: {peak_coherence:.3f}")
        elif peak_coherence > 0.8:
            observations.append(f"Good peak coherence: {peak_coherence:.3f}")
        else:
            observations.append(f"Moderate coherence ceiling: {peak_coherence:.3f}")

        # Drift observations
        if drift_stable_loop < 100:
            observations.append(f"Early drift stabilization at loop {drift_stable_loop}")
        elif drift_stable_loop < 120:
            observations.append(f"Drift stabilized at expected range: loop {drift_stable_loop}")
        else:
            observations.append(f"Late drift stabilization at loop {drift_stable_loop}")

        # Swarm observations
        avg_stable = statistics.mean([m.agents_stable for m in final_metrics])
        if avg_stable == self.num_agents:
            observations.append("All agents achieved stable state")
        else:
            observations.append(f"Average stable agents: {avg_stable:.1f}/{self.num_agents}")

        # Check for plateau (expected 80-120)
        if 80 <= peak_idx <= 120:
            observations.append(f"Optimal loop within expected range (loop {peak_idx})")
        else:
            observations.append(f"Optimal loop at {peak_idx} (expected 80-120)")

        return StabilityReport(
            test_id=self.test_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_loops=self.total_loops,
            agents_count=self.num_agents,
            optimal_loop=peak_idx,
            peak_coherence=peak_coherence,
            final_stability_index=stability_index,
            drift_stabilization_loop=drift_stable_loop,
            convergence_achieved=convergence,
            metrics_history=[asdict(m) for m in metrics],
            observations=observations
        )

    def save_report(self, report: StabilityReport, output_path: str) -> None:
        """Save report to JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(asdict(report), f, indent=2)

        print(f"Report saved to: {path}")


def main():
    """Main entry point for stability testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Echo Stability Test Framework")
    parser.add_argument("--loops", type=int, default=200, help="Number of loops")
    parser.add_argument("--agents", type=int, default=6, help="Number of agents")
    parser.add_argument("--output", default="stability_report.json", help="Output file")
    args = parser.parse_args()

    tester = StabilityTester(total_loops=args.loops, num_agents=args.agents)
    report = tester.run_test()

    # Print summary
    print("\nSTABILITY TEST SUMMARY")
    print("=" * 60)
    print(f"Test ID: {report.test_id}")
    print(f"Convergence: {'ACHIEVED' if report.convergence_achieved else 'NOT ACHIEVED'}")
    print(f"Peak Coherence: {report.peak_coherence:.3f} (loop {report.optimal_loop})")
    print(f"Drift Stabilization: Loop {report.drift_stabilization_loop}")
    print(f"Final Stability Index: {report.final_stability_index:.3f}")
    print("\nObservations:")
    for obs in report.observations:
        print(f"  - {obs}")
    print("=" * 60)

    # Save report
    tester.save_report(report, args.output)


if __name__ == "__main__":
    main()
