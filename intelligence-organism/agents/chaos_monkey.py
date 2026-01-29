#!/usr/bin/env python3
"""
Chaos Monkey Agent - Resilience Testing Protocol
Introduces controlled, random disruptions to build anti-fragility
"""

import os
import json
import random
from datetime import datetime
from pathlib import Path
import time

# Configuration
LOG_DIR = Path("intelligence-organism/logs/chaos_monkey")
MODE = os.getenv("CHAOS_MONKEY_MODE", "limited")  # limited, full, logging_only

# Action library
ACTIONS = {
    "sleep_agent": {
        "description": "Temporarily disable a non-critical agent",
        "severity": "low",
        "enabled_in": ["limited", "full"]
    },
    "inject_false_data": {
        "description": "Inject benign false data to test verification",
        "severity": "medium",
        "enabled_in": ["full"]
    },
    "restart_expert": {
        "description": "Force restart of a domain expert",
        "severity": "low",
        "enabled_in": ["limited", "full"]
    },
    "challenge_assumption": {
        "description": "Flag a long-held assumption for re-validation",
        "severity": "medium",
        "enabled_in": ["full"]
    }
}

def select_random_action():
    """Select a random action based on current mode"""
    available_actions = [
        action_id for action_id, action in ACTIONS.items()
        if MODE in action["enabled_in"]
    ]
    
    if not available_actions:
        return None
    
    return random.choice(available_actions)

def execute_action(action_id):
    """Execute the selected action (or log it in logging_only mode)"""
    action = ACTIONS[action_id]
    
    execution_log = {
        "timestamp": datetime.now().isoformat(),
        "action_id": action_id,
        "description": action["description"],
        "severity": action["severity"],
        "mode": MODE,
        "executed": MODE != "logging_only"
    }
    
    if MODE == "logging_only":
        execution_log["status"] = "LOGGED_ONLY"
        execution_log["note"] = "Action was selected but not executed (logging_only mode)"
    else:
        # Simulate action execution
        execution_log["status"] = "EXECUTED"
        execution_log["duration_seconds"] = random.randint(5, 30)
        execution_log["target"] = f"agent_{random.randint(1, 10)}"
        
        # In a real implementation, this would actually disrupt a component
        print(f"Executing: {action['description']}")
        time.sleep(2)  # Simulate action
    
    return execution_log

def save_execution_log(log):
    """Save the execution log"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"execution_{timestamp}.json"
    
    with open(log_file, 'w') as f:
        json.dump(log, f, indent=2)
    
    print(f"Execution log saved to {log_file}")

def main():
    """Main execution"""
    print(f"{'='*80}")
    print(f"🐵 CHAOS MONKEY ACTIVATED 🐵")
    print(f"{'='*80}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Mode: {MODE}")
    print(f"{'='*80}\n")
    
    # Select and execute random action
    action_id = select_random_action()
    
    if action_id:
        print(f"Selected action: {action_id}")
        execution_log = execute_action(action_id)
        save_execution_log(execution_log)
        
        print(f"\nStatus: {execution_log['status']}")
    else:
        print("No actions available in current mode")
    
    print(f"\n{'='*80}")
    print(f"🐵 CHAOS MONKEY COMPLETE 🐵")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
