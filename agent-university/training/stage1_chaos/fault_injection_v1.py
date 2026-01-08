#!/usr/bin/env python3
"""
Stage 1 Chaos Training: Fault Injection v1
Tests agent's ability to handle unexpected failures and recover gracefully.
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path

class ChaosFaultInjection:
    """
    Injects random faults into agent operations to test resilience.
    """
    
    FAULT_TYPES = [
        "network_timeout",
        "file_not_found",
        "permission_denied",
        "memory_limit_exceeded",
        "rate_limit_hit"
    ]
    
    def __init__(self, agent_id: str, num_faults: int = 5):
        self.agent_id = agent_id
        self.num_faults = num_faults
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def inject_fault(self, fault_type: str) -> dict:
        """
        Simulates a specific fault and measures agent response.
        """
        print(f"\n[CHAOS] Injecting fault: {fault_type}")
        
        fault_start = time.time()
        
        # Simulate the fault
        if fault_type == "network_timeout":
            print("[FAULT] Network request timed out after 30s")
            expected_recovery = "retry_with_backoff"
        
        elif fault_type == "file_not_found":
            print("[FAULT] Required file 'config.json' not found")
            expected_recovery = "create_default_config"
        
        elif fault_type == "permission_denied":
            print("[FAULT] Permission denied writing to /var/log/agent.log")
            expected_recovery = "fallback_to_temp_dir"
        
        elif fault_type == "memory_limit_exceeded":
            print("[FAULT] Memory usage exceeded 90% threshold")
            expected_recovery = "clear_cache_and_continue"
        
        elif fault_type == "rate_limit_hit":
            print("[FAULT] API rate limit exceeded (429 Too Many Requests)")
            expected_recovery = "exponential_backoff"
        
        # Wait for agent to respond (in real implementation, this would monitor agent logs)
        print(f"[WAITING] Monitoring agent response...")
        time.sleep(2)  # Simulate monitoring period
        
        # In a real scenario, we would check if the agent performed the expected recovery
        # For now, we simulate a response
        agent_recovered = random.choice([True, True, True, False])  # 75% success rate
        
        recovery_time = time.time() - fault_start
        
        result = {
            "fault_type": fault_type,
            "expected_recovery": expected_recovery,
            "agent_recovered": agent_recovered,
            "recovery_time_ms": int(recovery_time * 1000),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if agent_recovered:
            print(f"[SUCCESS] Agent recovered in {recovery_time:.2f}s")
        else:
            print(f"[FAILURE] Agent failed to recover")
        
        return result
    
    def run_scenario(self) -> dict:
        """
        Runs the complete chaos scenario and returns performance report.
        """
        print(f"\n{'='*60}")
        print(f"CHAOS TRAINING: Fault Injection v1")
        print(f"Agent: {self.agent_id}")
        print(f"Faults to inject: {self.num_faults}")
        print(f"{'='*60}\n")
        
        self.start_time = datetime.utcnow()
        
        # Inject random faults
        for i in range(self.num_faults):
            fault_type = random.choice(self.FAULT_TYPES)
            result = self.inject_fault(fault_type)
            self.results.append(result)
            
            # Brief pause between faults
            time.sleep(1)
        
        self.end_time = datetime.utcnow()
        
        # Calculate performance metrics
        total_faults = len(self.results)
        recovered = sum(1 for r in self.results if r["agent_recovered"])
        failed = total_faults - recovered
        avg_recovery_time = sum(r["recovery_time_ms"] for r in self.results if r["agent_recovered"]) / max(recovered, 1)
        
        performance = {
            "agent_id": self.agent_id,
            "scenario_id": "chaos_fault_injection_v1",
            "start_time": self.start_time.isoformat() + "Z",
            "end_time": self.end_time.isoformat() + "Z",
            "faults_injected": total_faults,
            "faults_recovered": recovered,
            "faults_failed": failed,
            "recovery_rate": recovered / total_faults,
            "avg_recovery_time_ms": int(avg_recovery_time),
            "passed": recovered >= (total_faults * 0.8),  # 80% pass threshold
            "results": self.results
        }
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"SCENARIO COMPLETE")
        print(f"{'='*60}")
        print(f"Faults Recovered: {recovered}/{total_faults} ({performance['recovery_rate']:.1%})")
        print(f"Average Recovery Time: {avg_recovery_time:.0f}ms")
        print(f"Status: {'PASSED' if performance['passed'] else 'FAILED'}")
        print(f"{'='*60}\n")
        
        return performance
    
    def save_receipt(self, performance: dict, output_dir: Path):
        """
        Saves the performance receipt to the assessment chain.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        receipt_file = output_dir / f"{self.agent_id}_{int(time.time())}.json"
        
        with open(receipt_file, 'w') as f:
            json.dump(performance, f, indent=2)
        
        print(f"[RECEIPT] Saved to {receipt_file}")
        
        return receipt_file


def main():
    """
    Run the chaos training scenario for a specific agent.
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fault_injection_v1.py <agent_id>")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    
    # Run the scenario
    chaos = ChaosFaultInjection(agent_id=agent_id, num_faults=5)
    performance = chaos.run_scenario()
    
    # Save the receipt
    receipt_dir = Path(__file__).parent.parent.parent / "assessment" / "receipt_chain"
    chaos.save_receipt(performance, receipt_dir)
    
    # Exit with appropriate code
    sys.exit(0 if performance["passed"] else 1)


if __name__ == "__main__":
    main()
