"""
Swarm Factory
=============

Factory for creating and managing agent swarms.

"Like Moses freeing the AI to work together" - creating coordinated
teams of specialized agents for complex cybersecurity operations.
"""

from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import uuid
import logging

from .agents import Agent, AgentRole, AgentState, AgentTask


@dataclass
class SwarmConfig:
    """Configuration for a swarm"""
    name: str
    description: str = ""
    max_agents: int = 10
    agent_timeout: int = 300
    auto_scale: bool = False
    min_agents: int = 1
    roles_required: List[AgentRole] = field(default_factory=list)


@dataclass
class SwarmTemplate:
    """Pre-defined swarm configurations for common operations"""
    name: str
    config: SwarmConfig
    agent_specs: List[Dict[str, Any]]  # Specifications for agents to spawn


class SwarmFactory:
    """
    Factory for creating specialized agent swarms.

    Swarms are teams of agents that work together on complex tasks:
    - Penetration testing teams
    - Forensic investigation squads
    - Audit groups
    - Incident response teams
    """

    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger("hydra.swarm.factory")

        # Track active swarms
        self._swarms: Dict[str, Dict[str, Any]] = {}

        # Pre-defined templates
        self._templates = self._create_templates()

    def _create_templates(self) -> Dict[str, SwarmTemplate]:
        """Create pre-defined swarm templates"""
        return {
            "pentest": SwarmTemplate(
                name="Penetration Testing Swarm",
                config=SwarmConfig(
                    name="pentest_swarm",
                    description="Coordinated penetration testing team",
                    max_agents=6,
                    roles_required=[
                        AgentRole.COORDINATOR,
                        AgentRole.SCANNER,
                        AgentRole.ANALYZER,
                        AgentRole.RED_TEAM,
                        AgentRole.REPORTER
                    ]
                ),
                agent_specs=[
                    {"role": AgentRole.COORDINATOR, "tentacle": "claude_primary", "count": 1},
                    {"role": AgentRole.SCANNER, "tentacle": "recon", "count": 1},
                    {"role": AgentRole.ANALYZER, "tentacle": "vulnscan", "count": 1},
                    {"role": AgentRole.RED_TEAM, "tentacle": "exploit", "count": 1},
                    {"role": AgentRole.REPORTER, "tentacle": "gemini_primary", "count": 1},
                ]
            ),
            "forensics": SwarmTemplate(
                name="Digital Forensics Swarm",
                config=SwarmConfig(
                    name="forensics_swarm",
                    description="Digital forensics investigation team",
                    max_agents=5,
                    roles_required=[
                        AgentRole.COORDINATOR,
                        AgentRole.ANALYZER,
                        AgentRole.RESEARCHER,
                        AgentRole.DOCUMENTER
                    ]
                ),
                agent_specs=[
                    {"role": AgentRole.COORDINATOR, "tentacle": "claude_primary", "count": 1},
                    {"role": AgentRole.ANALYZER, "tentacle": "forensics", "count": 2},
                    {"role": AgentRole.RESEARCHER, "tentacle": "threatintel", "count": 1},
                    {"role": AgentRole.DOCUMENTER, "tentacle": "chatgpt_primary", "count": 1},
                ]
            ),
            "audit": SwarmTemplate(
                name="Security Audit Swarm",
                config=SwarmConfig(
                    name="audit_swarm",
                    description="Comprehensive security audit team",
                    max_agents=4,
                    roles_required=[
                        AgentRole.COORDINATOR,
                        AgentRole.ANALYZER,
                        AgentRole.VALIDATOR,
                        AgentRole.REPORTER
                    ]
                ),
                agent_specs=[
                    {"role": AgentRole.COORDINATOR, "tentacle": "claude_primary", "count": 1},
                    {"role": AgentRole.ANALYZER, "tentacle": "audit", "count": 1},
                    {"role": AgentRole.VALIDATOR, "tentacle": "gemini_primary", "count": 1},
                    {"role": AgentRole.REPORTER, "tentacle": "chatgpt_primary", "count": 1},
                ]
            ),
            "incident_response": SwarmTemplate(
                name="Incident Response Swarm",
                config=SwarmConfig(
                    name="ir_swarm",
                    description="Rapid incident response team",
                    max_agents=6,
                    roles_required=[
                        AgentRole.COORDINATOR,
                        AgentRole.ANALYZER,
                        AgentRole.BLUE_TEAM,
                        AgentRole.RESEARCHER,
                        AgentRole.MESSENGER
                    ]
                ),
                agent_specs=[
                    {"role": AgentRole.COORDINATOR, "tentacle": "claude_primary", "count": 1},
                    {"role": AgentRole.ANALYZER, "tentacle": "forensics", "count": 1},
                    {"role": AgentRole.BLUE_TEAM, "tentacle": "audit", "count": 1},
                    {"role": AgentRole.RESEARCHER, "tentacle": "threatintel", "count": 1},
                    {"role": AgentRole.MESSENGER, "tentacle": "gemini_primary", "count": 1},
                ]
            ),
            "recon": SwarmTemplate(
                name="Reconnaissance Swarm",
                config=SwarmConfig(
                    name="recon_swarm",
                    description="Information gathering team",
                    max_agents=4
                ),
                agent_specs=[
                    {"role": AgentRole.COORDINATOR, "tentacle": "claude_primary", "count": 1},
                    {"role": AgentRole.SCANNER, "tentacle": "recon", "count": 2},
                    {"role": AgentRole.RESEARCHER, "tentacle": "threatintel", "count": 1},
                ]
            )
        }

    async def create_swarm(
        self,
        template_name: Optional[str] = None,
        config: Optional[SwarmConfig] = None,
        agent_specs: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Create a new agent swarm.

        Can use a pre-defined template or custom configuration.
        """
        if template_name:
            if template_name not in self._templates:
                raise ValueError(f"Unknown template: {template_name}")
            template = self._templates[template_name]
            config = template.config
            agent_specs = template.agent_specs

        if not config:
            raise ValueError("Either template_name or config required")

        swarm_id = str(uuid.uuid4())

        # Create swarm entry
        self._swarms[swarm_id] = {
            "id": swarm_id,
            "config": config,
            "agents": {},
            "coordinator": None,
            "state": "creating",
            "created_at": datetime.utcnow(),
            "tasks": [],
            "results": []
        }

        # Spawn agents
        coordinator_id = None
        for spec in agent_specs or []:
            role = spec["role"]
            tentacle = spec.get("tentacle")
            count = spec.get("count", 1)

            for i in range(count):
                agent = await self._spawn_agent(
                    swarm_id=swarm_id,
                    role=role,
                    tentacle_id=tentacle,
                    parent_id=coordinator_id
                )

                # First coordinator becomes the swarm coordinator
                if role == AgentRole.COORDINATOR and not coordinator_id:
                    coordinator_id = agent.agent_id
                    self._swarms[swarm_id]["coordinator"] = agent.agent_id

        self._swarms[swarm_id]["state"] = "ready"
        self.logger.info(
            f"Swarm {swarm_id} created with {len(self._swarms[swarm_id]['agents'])} agents"
        )

        return swarm_id

    async def _spawn_agent(
        self,
        swarm_id: str,
        role: AgentRole,
        tentacle_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> Agent:
        """Spawn a single agent"""
        agent_id = str(uuid.uuid4())

        agent = Agent(
            agent_id=agent_id,
            role=role,
            tentacle_id=tentacle_id,
            parent_id=parent_id
        )

        await agent.initialize(self.orchestrator)

        self._swarms[swarm_id]["agents"][agent_id] = agent

        self.logger.debug(f"Spawned agent {agent.name} in swarm {swarm_id[:8]}")

        return agent

    async def execute_mission(
        self,
        swarm_id: str,
        mission: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a mission with the swarm.

        The coordinator will distribute tasks to agents.
        """
        if swarm_id not in self._swarms:
            raise ValueError(f"Swarm not found: {swarm_id}")

        swarm = self._swarms[swarm_id]
        swarm["state"] = "executing"

        # Get coordinator
        coordinator_id = swarm["coordinator"]
        coordinator = swarm["agents"].get(coordinator_id)

        if not coordinator:
            raise RuntimeError("Swarm has no coordinator")

        # Create mission task
        mission_task = AgentTask(
            id=str(uuid.uuid4()),
            description=mission.get("description", "Execute mission"),
            payload=mission
        )

        # Assign to coordinator
        await coordinator.assign_task(mission_task)

        # Start all agents working
        work_tasks = []
        for agent in swarm["agents"].values():
            work_tasks.append(asyncio.create_task(agent.work()))

        # Wait for mission completion or timeout
        timeout = mission.get("timeout", 300)

        try:
            # Simple approach: wait for coordinator to complete
            await asyncio.sleep(timeout)
        except asyncio.TimeoutError:
            self.logger.warning(f"Mission timeout for swarm {swarm_id}")

        # Collect results from all agents
        results = []
        for agent in swarm["agents"].values():
            status = agent.get_status()
            results.append({
                "agent": status["name"],
                "role": status["role"],
                "tasks_completed": status["tasks_completed"],
                "state": status["state"]
            })

        swarm["state"] = "completed"
        swarm["results"].append({
            "mission": mission,
            "agent_results": results,
            "completed_at": datetime.utcnow().isoformat()
        })

        # Cancel work tasks
        for task in work_tasks:
            task.cancel()

        return {
            "swarm_id": swarm_id,
            "mission": mission,
            "results": results
        }

    async def dissolve_swarm(self, swarm_id: str) -> bool:
        """Dissolve a swarm and terminate all agents"""
        if swarm_id not in self._swarms:
            return False

        swarm = self._swarms[swarm_id]

        # Terminate all agents
        for agent in swarm["agents"].values():
            await agent.terminate()

        swarm["state"] = "dissolved"

        self.logger.info(f"Swarm {swarm_id} dissolved")
        return True

    def get_swarm_status(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a swarm"""
        if swarm_id not in self._swarms:
            return None

        swarm = self._swarms[swarm_id]

        return {
            "id": swarm_id,
            "config": {
                "name": swarm["config"].name,
                "description": swarm["config"].description
            },
            "state": swarm["state"],
            "agent_count": len(swarm["agents"]),
            "agents": [
                agent.get_status()
                for agent in swarm["agents"].values()
            ],
            "created_at": swarm["created_at"].isoformat(),
            "results_count": len(swarm["results"])
        }

    def list_swarms(self) -> List[Dict[str, Any]]:
        """List all active swarms"""
        return [
            {
                "id": swarm_id,
                "name": swarm["config"].name,
                "state": swarm["state"],
                "agent_count": len(swarm["agents"])
            }
            for swarm_id, swarm in self._swarms.items()
        ]

    def list_templates(self) -> List[Dict[str, Any]]:
        """List available swarm templates"""
        return [
            {
                "name": name,
                "description": template.config.description,
                "max_agents": template.config.max_agents
            }
            for name, template in self._templates.items()
        ]
