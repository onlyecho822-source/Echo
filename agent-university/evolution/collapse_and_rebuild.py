#!/usr/bin/env python3
"""
Collapse & Rebuild Evolution Engine
Triggers system evolution when performance degrades or stagnates.
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class EvolutionTrigger:
    """Represents a condition that triggers evolution."""
    trigger_type: str
    severity: str  # "warning" | "critical"
    description: str
    detected_at: str


class EvolutionEngine:
    """
    Monitors system health and triggers collapse/rebuild cycles.
    """
    
    def __init__(self, university_root: Path):
        self.university_root = university_root
        self.credentials_dir = university_root / "credentials"
        self.teams_dir = university_root / "teams" / "active"
        self.receipts_dir = university_root / "assessment" / "receipt_chain"
        self.reports_dir = university_root / "evolution" / "reports"
        self.archived_dir = university_root / "teams" / "archived"
        
        self.triggers = []
    
    def check_performance_degradation(self) -> Optional[EvolutionTrigger]:
        """
        Check if team success rates have degraded.
        """
        if not self.teams_dir.exists():
            return None
        
        team_files = list(self.teams_dir.glob("*.json"))
        
        if not team_files:
            return None
        
        # In a real system, we would track mission outcomes
        # For now, we simulate by checking team scores
        
        low_performing_teams = 0
        
        for team_file in team_files:
            with open(team_file, 'r') as f:
                team_data = json.load(f)
                team_score = team_data.get("team_score", 1.0)
                
                if team_score < 0.7:  # 70% threshold
                    low_performing_teams += 1
        
        if low_performing_teams / len(team_files) > 0.3:  # More than 30% underperforming
            return EvolutionTrigger(
                trigger_type="performance_degradation",
                severity="critical",
                description=f"{low_performing_teams}/{len(team_files)} teams below performance threshold",
                detected_at=datetime.utcnow().isoformat() + "Z"
            )
        
        return None
    
    def check_stagnation(self) -> Optional[EvolutionTrigger]:
        """
        Check if no new capabilities have been verified recently.
        """
        if not self.receipts_dir.exists():
            return None
        
        receipt_files = sorted(self.receipts_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
        
        if not receipt_files:
            return None
        
        # Check last receipt timestamp
        latest_receipt = receipt_files[-1]
        last_modified = datetime.fromtimestamp(latest_receipt.stat().st_mtime)
        days_since_last_training = (datetime.now() - last_modified).days
        
        if days_since_last_training > 30:
            return EvolutionTrigger(
                trigger_type="stagnation",
                severity="warning",
                description=f"No training activity for {days_since_last_training} days",
                detected_at=datetime.utcnow().isoformat() + "Z"
            )
        
        return None
    
    def check_incompatibility(self) -> Optional[EvolutionTrigger]:
        """
        Check if teams have repeated failures due to agent conflicts.
        """
        # In a real system, we would analyze mission failure logs
        # For now, we return None (no incompatibility detected)
        return None
    
    def detect_triggers(self) -> List[EvolutionTrigger]:
        """
        Run all health checks and detect evolution triggers.
        """
        print("\n[EVOLUTION] Running system health checks...")
        
        checks = [
            ("Performance Degradation", self.check_performance_degradation),
            ("Stagnation", self.check_stagnation),
            ("Incompatibility", self.check_incompatibility),
        ]
        
        for check_name, check_func in checks:
            print(f"  Checking: {check_name}...", end=" ")
            trigger = check_func()
            
            if trigger:
                self.triggers.append(trigger)
                print(f"⚠️  {trigger.severity.upper()}")
            else:
                print("✓")
        
        return self.triggers
    
    def archive_current_state(self) -> Path:
        """
        Archive the current system state before evolution.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        archive_dir = self.archived_dir / timestamp
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n[ARCHIVE] Saving current state to {archive_dir}")
        
        # Archive teams
        if self.teams_dir.exists():
            shutil.copytree(self.teams_dir, archive_dir / "teams", dirs_exist_ok=True)
            print(f"  ✓ Teams archived")
        
        # Archive credentials
        if self.credentials_dir.exists():
            shutil.copytree(self.credentials_dir, archive_dir / "credentials", dirs_exist_ok=True)
            print(f"  ✓ Credentials archived")
        
        return archive_dir
    
    def analyze_failure_patterns(self) -> Dict:
        """
        Analyze which agents/teams underperformed.
        """
        print("\n[ANALYSIS] Identifying failure patterns...")
        
        analysis = {
            "underperforming_agents": [],
            "high_performing_agents": [],
            "recommended_retraining": [],
            "recommended_reassignments": []
        }
        
        # Load all agent credentials
        if not self.credentials_dir.exists():
            return analysis
        
        for cred_file in self.credentials_dir.glob("*.json"):
            with open(cred_file, 'r') as f:
                cred = json.load(f)
                agent_id = cred["agent_id"]
                pass_rate = cred.get("pass_rate", 0.0)
                
                if pass_rate < 0.6:
                    analysis["underperforming_agents"].append(agent_id)
                    analysis["recommended_retraining"].append({
                        "agent_id": agent_id,
                        "reason": f"Pass rate below threshold ({pass_rate:.1%})",
                        "recommended_stage": "stage1_chaos"
                    })
                elif pass_rate > 0.9:
                    analysis["high_performing_agents"].append(agent_id)
        
        print(f"  Underperforming: {len(analysis['underperforming_agents'])} agents")
        print(f"  High-performing: {len(analysis['high_performing_agents'])} agents")
        
        return analysis
    
    def execute_rebuild(self, analysis: Dict) -> Dict:
        """
        Execute the rebuild process based on analysis.
        """
        print("\n[REBUILD] Executing evolution cycle...")
        
        rebuild_actions = {
            "agents_retrained": [],
            "teams_reformed": [],
            "roles_reassigned": []
        }
        
        # Clear current teams (they will be reformed)
        if self.teams_dir.exists():
            for team_file in self.teams_dir.glob("*.json"):
                team_file.unlink()
            print(f"  ✓ Cleared {len(list(self.teams_dir.glob('*.json')))} active teams")
        
        # Mark agents for retraining
        for recommendation in analysis["recommended_retraining"]:
            agent_id = recommendation["agent_id"]
            rebuild_actions["agents_retrained"].append(agent_id)
            print(f"  ⚙️  Marked {agent_id} for retraining")
        
        # In a real system, we would:
        # 1. Automatically trigger retraining scenarios
        # 2. Re-form teams with updated compatibility data
        # 3. Reassign agents to new specializations
        
        print(f"\n[REBUILD] Complete")
        print(f"  Agents marked for retraining: {len(rebuild_actions['agents_retrained'])}")
        
        return rebuild_actions
    
    def generate_evolution_report(self, archive_dir: Path, analysis: Dict, rebuild_actions: Dict) -> Path:
        """
        Generate a comprehensive evolution report.
        """
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        report = {
            "evolution_cycle_id": archive_dir.name,
            "triggered_at": datetime.utcnow().isoformat() + "Z",
            "triggers": [
                {
                    "type": t.trigger_type,
                    "severity": t.severity,
                    "description": t.description,
                    "detected_at": t.detected_at
                }
                for t in self.triggers
            ],
            "analysis": analysis,
            "rebuild_actions": rebuild_actions,
            "archived_state": str(archive_dir),
            "lessons_learned": [
                "Agents with pass rates below 60% require additional chaos training",
                "Team compatibility scores should be weighted more heavily in formation",
                "Regular training prevents stagnation and maintains system resilience"
            ]
        }
        
        report_file = self.reports_dir / f"evolution_{archive_dir.name}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[REPORT] Evolution report saved: {report_file}")
        
        return report_file
    
    def run_evolution_cycle(self) -> bool:
        """
        Execute a complete collapse & rebuild cycle.
        """
        print("\n" + "="*60)
        print("EVOLUTION CYCLE: Collapse & Rebuild")
        print("="*60)
        
        # Detect triggers
        triggers = self.detect_triggers()
        
        if not triggers:
            print("\n[RESULT] No evolution triggers detected. System healthy.")
            return False
        
        print(f"\n[TRIGGERED] {len(triggers)} evolution trigger(s) detected:")
        for trigger in triggers:
            print(f"  - {trigger.trigger_type}: {trigger.description}")
        
        # Archive current state
        archive_dir = self.archive_current_state()
        
        # Analyze failure patterns
        analysis = self.analyze_failure_patterns()
        
        # Execute rebuild
        rebuild_actions = self.execute_rebuild(analysis)
        
        # Generate report
        report_file = self.generate_evolution_report(archive_dir, analysis, rebuild_actions)
        
        print("\n" + "="*60)
        print("EVOLUTION CYCLE COMPLETE")
        print("="*60)
        print(f"Archived State: {archive_dir}")
        print(f"Evolution Report: {report_file}")
        print("\nThe system has been rebuilt. Agents marked for retraining.")
        print("Teams will be reformed once retraining is complete.")
        print("="*60 + "\n")
        
        return True


def main():
    """
    Run the evolution engine.
    """
    import sys
    
    # Determine university root
    script_dir = Path(__file__).parent
    university_root = script_dir.parent
    
    # Initialize engine
    engine = EvolutionEngine(university_root)
    
    # Run evolution cycle
    evolved = engine.run_evolution_cycle()
    
    sys.exit(0 if evolved else 1)


if __name__ == "__main__":
    main()
