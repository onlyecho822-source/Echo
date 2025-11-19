"""
Swarm Coordinator
=================

High-level coordination for swarm operations.
"""

from typing import Any, Dict, List, Optional
import asyncio
import logging

from .factory import SwarmFactory
from .agents import Agent, AgentMessage


class SwarmCoordinator:
    """
    Coordinates multiple swarms and their interactions.

    Handles:
    - Inter-swarm communication
    - Resource allocation
    - Global task distribution
    """

    def __init__(self, factory: SwarmFactory):
        self.factory = factory
        self.logger = logging.getLogger("hydra.swarm.coordinator")

        # Message routing
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def start(self) -> None:
        """Start the coordinator"""
        self._running = True
        asyncio.create_task(self._message_router())
        self.logger.info("Swarm coordinator started")

    async def stop(self) -> None:
        """Stop the coordinator"""
        self._running = False
        self.logger.info("Swarm coordinator stopped")

    async def _message_router(self) -> None:
        """Route messages between agents"""
        while self._running:
            try:
                # Collect messages from all agents
                for swarm_id, swarm in self.factory._swarms.items():
                    for agent in swarm["agents"].values():
                        while not agent._outbox.empty():
                            message = await agent._outbox.get()
                            await self._route_message(message)

                await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Message routing error: {e}")

    async def _route_message(self, message: AgentMessage) -> None:
        """Route a message to its destination"""
        target_agent = self._find_agent(message.to_agent)

        if target_agent:
            await target_agent.receive_message(message)
        else:
            self.logger.warning(
                f"Could not route message to {message.to_agent}"
            )

    def _find_agent(self, agent_id: str) -> Optional[Agent]:
        """Find an agent by ID across all swarms"""
        for swarm in self.factory._swarms.values():
            if agent_id in swarm["agents"]:
                return swarm["agents"][agent_id]
        return None

    async def broadcast_to_swarm(
        self,
        swarm_id: str,
        content: Any,
        msg_type: str = "broadcast"
    ) -> None:
        """Broadcast a message to all agents in a swarm"""
        if swarm_id not in self.factory._swarms:
            return

        swarm = self.factory._swarms[swarm_id]

        for agent in swarm["agents"].values():
            message = AgentMessage(
                from_agent="coordinator",
                to_agent=agent.agent_id,
                content=content,
                message_type=msg_type
            )
            await agent.receive_message(message)

    async def coordinate_multi_swarm(
        self,
        swarm_ids: List[str],
        mission: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate multiple swarms on a single mission.

        Useful for large-scale operations requiring multiple teams.
        """
        results = {}

        # Execute mission on all swarms in parallel
        tasks = [
            self.factory.execute_mission(swarm_id, mission)
            for swarm_id in swarm_ids
            if swarm_id in self.factory._swarms
        ]

        swarm_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, swarm_id in enumerate(swarm_ids):
            if i < len(swarm_results):
                results[swarm_id] = swarm_results[i]

        return {
            "mission": mission,
            "swarm_count": len(swarm_ids),
            "results": results
        }
