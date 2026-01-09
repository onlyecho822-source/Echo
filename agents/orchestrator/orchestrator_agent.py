#!/usr/bin/env python3
"""
Orchestrator Agent - Coordinates work between all agents
Monitors system health, assigns tasks, manages priorities
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.base_agent import EchoAgent

class OrchestratorAgent(EchoAgent):
    """Agent that orchestrates and coordinates other agents"""
    
    def __init__(self, agent_id: str = "001"):
        super().__init__(
            agent_name=f'orchestrator_{agent_id}',
            agent_type='orchestrator',
            work_interval=180  # 3 minutes
        )
        self.coordination_dir = os.path.join(self.repo_path, 'coordination')
        os.makedirs(self.coordination_dir, exist_ok=True)
        
        self.tasks_file = os.path.join(self.coordination_dir, 'tasks.jsonl')
        self.health_file = os.path.join(self.coordination_dir, 'system_health.json')
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get status of all active agents"""
        agents = []
        state_path = Path(self.state_path)
        
        if not state_path.exists():
            return agents
        
        for state_file in state_path.glob("*.json"):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                agents.append({
                    "name": state_file.stem,
                    "type": state.get("agent_type", "unknown"),
                    "cycle_count": state.get("cycle_count", 0),
                    "tasks_completed": state.get("tasks_completed", 0),
                    "last_updated": state.get("last_updated", "unknown"),
                    "status": "operational"
                })
            except:
                agents.append({
                    "name": state_file.stem,
                    "status": "error"
                })
        
        return agents
    
    def count_ledger_entries_today(self) -> int:
        """Count Constitutional Ledger entries written today"""
        ledger_path = Path(self.ledger_path)
        if not ledger_path.exists():
            return 0
        
        today = datetime.now().strftime('%Y%m%d')
        count = 0
        
        for ledger_file in ledger_path.glob(f"*_{today}.jsonl"):
            try:
                with open(ledger_file, 'r') as f:
                    count += len(f.readlines())
            except:
                continue
        
        return count
    
    def assign_task(self, task_type: str, target_agent: str, priority: str = "normal") -> Dict:
        """Assign a task to an agent"""
        task = {
            "id": f"task_{int(datetime.now().timestamp())}",
            "timestamp": datetime.utcnow().isoformat(),
            "task_type": task_type,
            "target_agent": target_agent,
            "priority": priority,
            "status": "pending",
            "assigned_by": self.agent_name
        }
        
        with open(self.tasks_file, 'a') as f:
            f.write(json.dumps(task) + '\n')
        
        return task
    
    def do_work(self) -> Dict[str, Any]:
        """Perform orchestration work"""
        results = {
            'tasks_completed': 0,
            'agents_monitored': 0,
            'tasks_assigned': 0,
            'health_status': 'unknown'
        }
        
        # Get all agents
        print("Monitoring agent health...")
        agents = self.get_all_agents()
        results['agents_monitored'] = len(agents)
        
        # Count ledger entries
        ledger_count = self.count_ledger_entries_today()
        
        # Calculate system health
        operational_count = sum(1 for a in agents if a.get("status") == "operational")
        total_cycles = sum(a.get("cycle_count", 0) for a in agents)
        total_tasks = sum(a.get("tasks_completed", 0) for a in agents)
        
        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "agents_total": len(agents),
            "agents_operational": operational_count,
            "total_cycles": total_cycles,
            "total_tasks": total_tasks,
            "ledger_entries_today": ledger_count,
            "status": "healthy" if operational_count > 0 else "degraded",
            "agents": agents
        }
        
        # Write health file
        with open(self.health_file, 'w') as f:
            json.dump(health, f, indent=2)
        
        results['health_status'] = health['status']
        results['tasks_completed'] += 1
        
        print(f"✓ System health: {health['status']}")
        print(f"  Agents: {operational_count}/{len(agents)} operational")
        print(f"  Total cycles: {total_cycles}")
        print(f"  Total tasks: {total_tasks}")
        print(f"  Ledger entries today: {ledger_count}")
        
        # Auto-assign tasks based on system state
        if ledger_count > 1000:
            self.assign_task("cleanup_old_logs", "cleaner_001", priority="low")
            results['tasks_assigned'] += 1
            print("  → Assigned cleanup task (high ledger count)")
        
        if total_cycles % 10 == 0 and total_cycles > 0:
            self.assign_task("update_roadmap", "planner_001", priority="normal")
            results['tasks_assigned'] += 1
            print("  → Assigned roadmap update (milestone reached)")
        
        # Sync to GitHub
        print("Syncing orchestration data to GitHub...")
        self.git_sync(
            f"Orchestrator: Health check and task assignment (Cycle {self.cycle_count})",
            files=[self.health_file, self.tasks_file]
        )
        
        return results

if __name__ == '__main__':
    agent = OrchestratorAgent()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        agent.run_once()
    else:
        agent.run_autopilot()
