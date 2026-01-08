#!/usr/bin/env python3
"""
Team Formation Algorithm
Forms optimal agent teams based on verified capabilities and compatibility.
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Agent:
    """Represents an agent with verified credentials."""
    agent_id: str
    capabilities: Set[str]
    credential_level: str
    pass_rate: float
    
    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities
    
    def meets_requirements(self, required_capabilities: Set[str]) -> bool:
        return required_capabilities.issubset(self.capabilities)


@dataclass
class Mission:
    """Represents a mission requiring a team of agents."""
    mission_id: str
    required_capabilities: Set[str]
    team_size: int
    min_credential_level: str = "Cadet"


class TeamFormationEngine:
    """
    Forms optimal teams based on verified agent capabilities and past performance.
    """
    
    CREDENTIAL_LEVELS = {
        "Cadet": 0,
        "Competent": 1,
        "Proficient": 2,
        "Expert": 3
    }
    
    def __init__(self, credentials_dir: Path):
        self.credentials_dir = credentials_dir
        self.agents = []
        self.compatibility_matrix = {}
    
    def load_agents(self) -> List[Agent]:
        """
        Load all agents with verified credentials.
        """
        if not self.credentials_dir.exists():
            print(f"[ERROR] Credentials directory not found: {self.credentials_dir}")
            return []
        
        cred_files = list(self.credentials_dir.glob("*.json"))
        
        for cred_file in cred_files:
            try:
                with open(cred_file, 'r') as f:
                    cred = json.load(f)
                    
                    agent = Agent(
                        agent_id=cred["agent_id"],
                        capabilities=set(cred.get("verified_capabilities", [])),
                        credential_level=cred.get("credential_level", "Cadet"),
                        pass_rate=cred.get("pass_rate", 0.0)
                    )
                    
                    self.agents.append(agent)
            
            except Exception as e:
                print(f"[WARNING] Failed to load {cred_file.name}: {e}")
        
        print(f"[LOADED] {len(self.agents)} agents with verified credentials")
        return self.agents
    
    def filter_qualified_agents(self, mission: Mission) -> List[Agent]:
        """
        Filter agents that meet the mission requirements.
        """
        qualified = []
        
        for agent in self.agents:
            # Check credential level
            if self.CREDENTIAL_LEVELS.get(agent.credential_level, 0) < \
               self.CREDENTIAL_LEVELS.get(mission.min_credential_level, 0):
                continue
            
            # Check capabilities
            if not agent.meets_requirements(mission.required_capabilities):
                continue
            
            qualified.append(agent)
        
        return qualified
    
    def calculate_compatibility(self, agent1: Agent, agent2: Agent) -> float:
        """
        Calculate compatibility score between two agents.
        In a real system, this would be based on past collaboration performance.
        For now, we use a simple heuristic.
        """
        # Check if we have historical data
        pair_key = tuple(sorted([agent1.agent_id, agent2.agent_id]))
        
        if pair_key in self.compatibility_matrix:
            return self.compatibility_matrix[pair_key]
        
        # Default compatibility based on capability overlap
        shared_capabilities = agent1.capabilities & agent2.capabilities
        total_capabilities = agent1.capabilities | agent2.capabilities
        
        if not total_capabilities:
            return 0.5
        
        # Jaccard similarity
        compatibility = len(shared_capabilities) / len(total_capabilities)
        
        # Boost compatibility if both have high pass rates
        if agent1.pass_rate > 0.8 and agent2.pass_rate > 0.8:
            compatibility *= 1.2
        
        # Cap at 1.0
        compatibility = min(compatibility, 1.0)
        
        self.compatibility_matrix[pair_key] = compatibility
        return compatibility
    
    def score_team(self, team: List[Agent]) -> float:
        """
        Calculate overall team score based on capabilities and compatibility.
        """
        if not team:
            return 0.0
        
        # Base score: average pass rate
        base_score = sum(agent.pass_rate for agent in team) / len(team)
        
        # Compatibility bonus: average pairwise compatibility
        if len(team) > 1:
            compatibility_scores = []
            for i in range(len(team)):
                for j in range(i + 1, len(team)):
                    compat = self.calculate_compatibility(team[i], team[j])
                    compatibility_scores.append(compat)
            
            avg_compatibility = sum(compatibility_scores) / len(compatibility_scores)
            
            # Weight: 70% individual performance, 30% team compatibility
            total_score = (base_score * 0.7) + (avg_compatibility * 0.3)
        else:
            total_score = base_score
        
        return total_score
    
    def form_team(self, mission: Mission) -> Optional[List[Agent]]:
        """
        Form the optimal team for a given mission.
        """
        print(f"\n[TEAM FORMATION] Mission: {mission.mission_id}")
        print(f"  Required Capabilities: {', '.join(mission.required_capabilities)}")
        print(f"  Team Size: {mission.team_size}")
        print(f"  Min Credential Level: {mission.min_credential_level}")
        
        # Filter qualified agents
        qualified = self.filter_qualified_agents(mission)
        
        if len(qualified) < mission.team_size:
            print(f"\n[ERROR] Not enough qualified agents ({len(qualified)} available, {mission.team_size} required)")
            return None
        
        print(f"\n[QUALIFIED] {len(qualified)} agents meet requirements")
        
        # Greedy team formation: start with highest-performing agent
        qualified.sort(key=lambda a: a.pass_rate, reverse=True)
        
        best_team = None
        best_score = 0.0
        
        # Try different team compositions (simple greedy approach)
        # In a production system, we'd use more sophisticated optimization
        
        for start_idx in range(min(3, len(qualified))):  # Try top 3 as starting points
            team = [qualified[start_idx]]
            remaining = [a for a in qualified if a != qualified[start_idx]]
            
            # Add agents that maximize team score
            while len(team) < mission.team_size and remaining:
                best_addition = None
                best_addition_score = 0.0
                
                for candidate in remaining:
                    test_team = team + [candidate]
                    score = self.score_team(test_team)
                    
                    if score > best_addition_score:
                        best_addition = candidate
                        best_addition_score = score
                
                if best_addition:
                    team.append(best_addition)
                    remaining.remove(best_addition)
            
            team_score = self.score_team(team)
            
            if team_score > best_score:
                best_score = team_score
                best_team = team
        
        if best_team:
            print(f"\n[SUCCESS] Formed team with score: {best_score:.2f}")
            for i, agent in enumerate(best_team):
                print(f"  [{i+1}] {agent.agent_id} ({agent.credential_level}, {agent.pass_rate:.1%} pass rate)")
        
        return best_team
    
    def save_team(self, mission: Mission, team: List[Agent], output_dir: Path) -> Path:
        """
        Save the team composition to a file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        team_data = {
            "mission_id": mission.mission_id,
            "formed_at": datetime.utcnow().isoformat() + "Z",
            "team_size": len(team),
            "team_score": self.score_team(team),
            "members": [
                {
                    "agent_id": agent.agent_id,
                    "credential_level": agent.credential_level,
                    "pass_rate": agent.pass_rate,
                    "capabilities": list(agent.capabilities)
                }
                for agent in team
            ]
        }
        
        team_file = output_dir / f"{mission.mission_id}_{int(datetime.utcnow().timestamp())}.json"
        
        with open(team_file, 'w') as f:
            json.dump(team_data, f, indent=2)
        
        print(f"\n[SAVED] Team composition: {team_file}")
        return team_file


def main():
    """
    Form a team for a specific mission.
    """
    import sys
    
    # Determine paths
    script_dir = Path(__file__).parent
    credentials_dir = script_dir.parent / "credentials"
    teams_dir = script_dir / "active"
    
    # Initialize engine
    engine = TeamFormationEngine(credentials_dir)
    engine.load_agents()
    
    if not engine.agents:
        print("[ERROR] No agents available")
        sys.exit(1)
    
    # Example mission
    mission = Mission(
        mission_id="deploy_constitutional_ledger",
        required_capabilities={"chaos_resilience"},
        team_size=3,
        min_credential_level="Competent"
    )
    
    # Form team
    team = engine.form_team(mission)
    
    if not team:
        print("[FAILURE] Could not form team")
        sys.exit(1)
    
    # Save team
    engine.save_team(mission, team, teams_dir)
    
    print("\n[SUCCESS] Team formation complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
