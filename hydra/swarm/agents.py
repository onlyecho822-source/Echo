"""
Swarm Agents
============

Individual agents that can be spawned and coordinated as a swarm.
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import uuid
import logging


class AgentRole(Enum):
    """Roles that agents can play in a swarm"""
    # Leadership
    COORDINATOR = "coordinator"      # Manages other agents
    STRATEGIST = "strategist"        # Plans operations

    # Security Operations
    SCANNER = "scanner"              # Scans targets
    ANALYZER = "analyzer"            # Analyzes data
    REPORTER = "reporter"            # Generates reports
    VALIDATOR = "validator"          # Validates findings

    # Specialized
    RED_TEAM = "red_team"            # Offensive operations
    BLUE_TEAM = "blue_team"          # Defensive operations
    PURPLE_TEAM = "purple_team"      # Combined ops

    # Support
    RESEARCHER = "researcher"        # Gathers information
    DOCUMENTER = "documenter"        # Documents findings
    MESSENGER = "messenger"          # Relays information


class AgentState(Enum):
    """Agent lifecycle states"""
    SPAWNED = "spawned"
    INITIALIZING = "initializing"
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


@dataclass
class AgentTask:
    """A task assigned to an agent"""
    id: str
    description: str
    payload: Dict[str, Any]
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class AgentMessage:
    """Message between agents"""
    from_agent: str
    to_agent: str
    content: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_type: str = "general"


class Agent:
    """
    An individual agent in a swarm.

    Agents are lightweight workers that can:
    - Execute specific tasks
    - Communicate with other agents
    - Report to coordinators
    - Work autonomously or in coordination
    """

    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        name: Optional[str] = None,
        tentacle_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.role = role
        self.name = name or f"{role.value}_{agent_id[:8]}"
        self.tentacle_id = tentacle_id  # Which tentacle powers this agent
        self.parent_id = parent_id      # Parent agent/coordinator

        self.state = AgentState.SPAWNED
        self.logger = logging.getLogger(f"hydra.agent.{self.agent_id[:8]}")

        # Task tracking
        self._current_task: Optional[AgentTask] = None
        self._completed_tasks: List[AgentTask] = []
        self._task_queue: asyncio.Queue = asyncio.Queue()

        # Communication
        self._inbox: asyncio.Queue = asyncio.Queue()
        self._outbox: asyncio.Queue = asyncio.Queue()

        # Statistics
        self._spawned_at = datetime.utcnow()
        self._tasks_completed = 0
        self._tasks_failed = 0

    async def initialize(self, orchestrator: Any) -> None:
        """Initialize the agent with access to the orchestrator"""
        self.state = AgentState.INITIALIZING
        self._orchestrator = orchestrator
        self.state = AgentState.IDLE
        self.logger.info(f"Agent {self.name} initialized")

    async def assign_task(self, task: AgentTask) -> None:
        """Assign a task to this agent"""
        await self._task_queue.put(task)
        self.logger.debug(f"Task {task.id} assigned to {self.name}")

    async def work(self) -> None:
        """Main work loop - process assigned tasks"""
        while self.state not in [AgentState.TERMINATED, AgentState.FAILED]:
            try:
                # Get next task
                task = await asyncio.wait_for(
                    self._task_queue.get(),
                    timeout=1.0
                )

                self._current_task = task
                self.state = AgentState.WORKING

                # Execute the task
                result = await self._execute_task(task)

                # Record completion
                task.completed_at = datetime.utcnow()
                task.result = result
                self._completed_tasks.append(task)
                self._tasks_completed += 1

                self.state = AgentState.IDLE
                self._current_task = None

                # Notify parent/coordinator
                await self._report_completion(task)

            except asyncio.TimeoutError:
                # No task available, check messages
                await self._process_messages()
                continue

            except Exception as e:
                self.logger.error(f"Task execution failed: {e}")
                if self._current_task:
                    self._current_task.error = str(e)
                    self._tasks_failed += 1
                self.state = AgentState.IDLE

    async def _execute_task(self, task: AgentTask) -> Any:
        """Execute a task using the assigned tentacle"""
        if not self.tentacle_id or not hasattr(self, '_orchestrator'):
            # Simulate work
            await asyncio.sleep(0.1)
            return {"status": "simulated", "task": task.description}

        # Use the orchestrator to execute via tentacle
        result = await self._orchestrator.execute(
            task_type=task.payload.get("type", "general"),
            payload=task.payload,
            tentacles=[self.tentacle_id] if self.tentacle_id else None,
            timeout=task.payload.get("timeout", 60)
        )

        return result

    async def _process_messages(self) -> None:
        """Process incoming messages"""
        try:
            while not self._inbox.empty():
                message = await self._inbox.get()
                await self._handle_message(message)
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")

    async def _handle_message(self, message: AgentMessage) -> None:
        """Handle an incoming message"""
        if message.message_type == "command":
            # Execute command from coordinator
            await self._handle_command(message.content)
        elif message.message_type == "query":
            # Respond to query
            await self._respond_to_query(message)
        elif message.message_type == "data":
            # Process shared data
            self.logger.debug(f"Received data from {message.from_agent}")

    async def _handle_command(self, command: Dict) -> None:
        """Handle a command message"""
        cmd_type = command.get("type", "")

        if cmd_type == "pause":
            self.state = AgentState.WAITING
        elif cmd_type == "resume":
            self.state = AgentState.IDLE
        elif cmd_type == "terminate":
            self.state = AgentState.TERMINATED

    async def _respond_to_query(self, message: AgentMessage) -> None:
        """Respond to a query message"""
        response = AgentMessage(
            from_agent=self.agent_id,
            to_agent=message.from_agent,
            content=self.get_status(),
            message_type="response"
        )
        await self._outbox.put(response)

    async def _report_completion(self, task: AgentTask) -> None:
        """Report task completion to parent/coordinator"""
        if self.parent_id:
            message = AgentMessage(
                from_agent=self.agent_id,
                to_agent=self.parent_id,
                content={
                    "task_id": task.id,
                    "status": "completed",
                    "result": task.result
                },
                message_type="report"
            )
            await self._outbox.put(message)

    async def send_message(self, to_agent: str, content: Any, msg_type: str = "general") -> None:
        """Send a message to another agent"""
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            content=content,
            message_type=msg_type
        )
        await self._outbox.put(message)

    async def receive_message(self, message: AgentMessage) -> None:
        """Receive a message"""
        await self._inbox.put(message)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "state": self.state.value,
            "tentacle": self.tentacle_id,
            "tasks_completed": self._tasks_completed,
            "tasks_failed": self._tasks_failed,
            "current_task": self._current_task.id if self._current_task else None,
            "queue_size": self._task_queue.qsize(),
            "uptime": (datetime.utcnow() - self._spawned_at).total_seconds()
        }

    async def terminate(self) -> None:
        """Terminate the agent"""
        self.state = AgentState.TERMINATED
        self.logger.info(f"Agent {self.name} terminated")
