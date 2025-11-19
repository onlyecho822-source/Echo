"""
Hydra Orchestrator - The Master Controller
===========================================

The orchestrator brings together the brain, load balancer, and all tentacles
into a unified system. It's the main entry point for the Hydra system.
"""

import asyncio
from typing import Dict, List, Any, Optional, Type
import logging
import uuid
from datetime import datetime

from ..config import HydraConfig, TentacleMode
from .brain import HydraBrain, Task, TaskResult, TaskPriority
from .load_balancer import LoadBalancer


class HydraOrchestrator:
    """
    Master orchestrator for the Hydra multi-AI fusion system.

    This is the main entry point. It:
    - Initializes all components
    - Manages tentacle lifecycle
    - Provides high-level API for task execution
    - Handles system-wide events
    """

    def __init__(self, config: Optional[HydraConfig] = None):
        self.config = config or HydraConfig()
        self.logger = logging.getLogger("hydra.orchestrator")

        # Core components
        self.brain = HydraBrain(self.config)
        self.load_balancer = LoadBalancer(self.config.load_balancer)

        # Tentacle registry
        self._tentacles: Dict[str, Any] = {}
        self._tentacle_classes: Dict[str, Type] = {}

        # System state
        self._running = False
        self._started_at: Optional[datetime] = None
        self._task_processor: Optional[asyncio.Task] = None

        # Event handlers
        self._event_handlers: Dict[str, List] = {}

    async def start(self) -> None:
        """Start the Hydra system"""
        if self._running:
            self.logger.warning("Hydra is already running")
            return

        self.logger.info("Starting Hydra Orchestrator...")
        self._running = True
        self._started_at = datetime.utcnow()

        # Start the brain's task processor
        self._task_processor = asyncio.create_task(self.brain.process_tasks())

        # Initialize all registered tentacles
        for tentacle_id, tentacle in self._tentacles.items():
            if hasattr(tentacle, 'initialize'):
                await tentacle.initialize()
            await self.load_balancer.register_tentacle(tentacle_id)

        self.logger.info(f"Hydra started with {len(self._tentacles)} tentacles")
        await self._emit_event("system_started", {"tentacles": list(self._tentacles.keys())})

    async def stop(self) -> None:
        """Stop the Hydra system"""
        if not self._running:
            return

        self.logger.info("Stopping Hydra Orchestrator...")
        self._running = False

        # Stop task processor
        if self._task_processor:
            self._task_processor.cancel()
            try:
                await self._task_processor
            except asyncio.CancelledError:
                pass

        # Shutdown all tentacles
        for tentacle_id, tentacle in self._tentacles.items():
            if hasattr(tentacle, 'shutdown'):
                await tentacle.shutdown()

        await self._emit_event("system_stopped", {})
        self.logger.info("Hydra stopped")

    def register_tentacle_class(self, name: str, tentacle_class: Type) -> None:
        """Register a tentacle class for later instantiation"""
        self._tentacle_classes[name] = tentacle_class

    async def add_tentacle(
        self,
        tentacle_id: str,
        tentacle: Any,
        auto_start: bool = True
    ) -> None:
        """Add a tentacle to the system"""
        self._tentacles[tentacle_id] = tentacle
        await self.brain.register_tentacle(tentacle_id, tentacle)

        if self._running:
            await self.load_balancer.register_tentacle(tentacle_id)
            if auto_start and hasattr(tentacle, 'initialize'):
                await tentacle.initialize()

        self.logger.info(f"Added tentacle: {tentacle_id}")
        await self._emit_event("tentacle_added", {"tentacle_id": tentacle_id})

    async def remove_tentacle(self, tentacle_id: str) -> bool:
        """Remove a tentacle from the system"""
        if tentacle_id not in self._tentacles:
            return False

        tentacle = self._tentacles[tentacle_id]

        if hasattr(tentacle, 'shutdown'):
            await tentacle.shutdown()

        await self.brain.unregister_tentacle(tentacle_id)
        del self._tentacles[tentacle_id]

        self.logger.info(f"Removed tentacle: {tentacle_id}")
        await self._emit_event("tentacle_removed", {"tentacle_id": tentacle_id})
        return True

    async def execute(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        tentacles: Optional[List[str]] = None,
        timeout: int = 60
    ) -> TaskResult:
        """
        Execute a task across the Hydra system.

        This is the main method for running cybersecurity operations.

        Args:
            task_type: Type of task (e.g., 'recon', 'audit', 'forensics')
            payload: Task data and parameters
            priority: Task priority level
            tentacles: Specific tentacles to use (optional)
            timeout: Task timeout in seconds

        Returns:
            Fused result from the best tentacles
        """
        if not self._running:
            raise RuntimeError("Hydra is not running. Call start() first.")

        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            type=task_type,
            payload=payload,
            priority=priority,
            required_tentacles=tentacles or [],
            timeout=timeout
        )

        # Submit to brain
        task_id = await self.brain.submit_task(task)

        # Wait for result
        result = None
        deadline = asyncio.get_event_loop().time() + timeout + 5

        while asyncio.get_event_loop().time() < deadline:
            result = await self.brain.get_task_result(task_id)
            if result:
                break
            await asyncio.sleep(0.1)

        if not result:
            result = TaskResult(
                task_id=task_id,
                tentacle_id="orchestrator",
                success=False,
                data=None,
                error="Task timeout"
            )

        return result

    async def execute_swarm(
        self,
        tasks: List[Dict[str, Any]],
        parallel: bool = True
    ) -> List[TaskResult]:
        """
        Execute multiple tasks as a swarm.

        Perfect for coordinated cybersecurity operations that need
        multiple perspectives or parallel analysis.
        """
        if parallel:
            # Execute all tasks concurrently
            coroutines = [
                self.execute(
                    task_type=t.get("type", "general"),
                    payload=t.get("payload", {}),
                    priority=t.get("priority", TaskPriority.MEDIUM),
                    tentacles=t.get("tentacles"),
                    timeout=t.get("timeout", 60)
                )
                for t in tasks
            ]
            return await asyncio.gather(*coroutines)
        else:
            # Execute sequentially
            results = []
            for t in tasks:
                result = await self.execute(
                    task_type=t.get("type", "general"),
                    payload=t.get("payload", {}),
                    priority=t.get("priority", TaskPriority.MEDIUM),
                    tentacles=t.get("tentacles"),
                    timeout=t.get("timeout", 60)
                )
                results.append(result)
            return results

    def get_tentacle(self, tentacle_id: str) -> Optional[Any]:
        """Get a tentacle by ID"""
        return self._tentacles.get(tentacle_id)

    def list_tentacles(self) -> List[str]:
        """List all registered tentacle IDs"""
        return list(self._tentacles.keys())

    async def set_tentacle_mode(
        self,
        tentacle_id: str,
        mode: TentacleMode
    ) -> bool:
        """Set operating mode for a tentacle"""
        return await self.brain.set_tentacle_mode(tentacle_id, mode)

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        brain_metrics = self.brain.get_metrics()
        load_metrics = self.load_balancer.get_metrics()

        uptime = None
        if self._started_at:
            uptime = (datetime.utcnow() - self._started_at).total_seconds()

        return {
            "running": self._running,
            "uptime_seconds": uptime,
            "tentacles": {
                "count": len(self._tentacles),
                "ids": list(self._tentacles.keys()),
                "health": {
                    tid: {
                        "state": h.circuit_state.value,
                        "success_rate": h.success_rate,
                        "tokens_used": h.tokens_used_minute
                    }
                    for tid, h in self.load_balancer.get_all_health().items()
                }
            },
            "brain": brain_metrics,
            "load": {
                "active_tentacles": load_metrics.active_tentacles,
                "tokens_per_minute": load_metrics.tokens_per_minute,
                "avg_response_time": load_metrics.avg_response_time
            }
        }

    def on(self, event: str, handler) -> None:
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    async def _emit_event(self, event: str, data: Dict[str, Any]) -> None:
        """Emit an event to all registered handlers"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                self.logger.error(f"Event handler error: {e}")
