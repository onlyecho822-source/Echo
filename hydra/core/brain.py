"""
Hydra Brain - Central Intelligence
===================================

The brain coordinates all tentacles, makes strategic decisions,
and ensures no single tentacle is overstimulated.

Like an octopus brain, it distributes intelligence while maintaining
central coordination.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import logging
from dataclasses import dataclass, field

from ..config import HydraConfig, TentacleMode


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class Task:
    """A task to be distributed to tentacles"""
    id: str
    type: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    required_tentacles: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    timeout: int = 60
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result from tentacle task execution"""
    task_id: str
    tentacle_id: str
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    tokens_used: int = 0


class HydraBrain:
    """
    Central coordination system for all tentacles.

    Responsibilities:
    - Task distribution and prioritization
    - Tentacle state management
    - Strategic decision making
    - Fusion of multi-AI outputs
    - Preventing overstimulation
    """

    def __init__(self, config: HydraConfig):
        self.config = config
        self.logger = logging.getLogger("hydra.brain")

        # State tracking
        self._tentacles: Dict[str, Any] = {}
        self._task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._active_tasks: Dict[str, Task] = {}
        self._results_cache: Dict[str, TaskResult] = {}

        # Coordination locks
        self._tentacle_locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

        # Metrics
        self._metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_tokens": 0,
            "tentacle_activations": {},
        }

    async def register_tentacle(self, tentacle_id: str, tentacle: Any) -> None:
        """Register a tentacle with the brain"""
        async with self._global_lock:
            self._tentacles[tentacle_id] = tentacle
            self._tentacle_locks[tentacle_id] = asyncio.Lock()
            self._metrics["tentacle_activations"][tentacle_id] = 0
            self.logger.info(f"Registered tentacle: {tentacle_id}")

    async def unregister_tentacle(self, tentacle_id: str) -> None:
        """Unregister a tentacle"""
        async with self._global_lock:
            if tentacle_id in self._tentacles:
                del self._tentacles[tentacle_id]
                del self._tentacle_locks[tentacle_id]
                self.logger.info(f"Unregistered tentacle: {tentacle_id}")

    async def submit_task(self, task: Task) -> str:
        """Submit a task to the brain for distribution"""
        # Priority queue uses (priority_value, task) tuples
        await self._task_queue.put((task.priority.value, task))
        self.logger.debug(f"Task submitted: {task.id} with priority {task.priority}")
        return task.id

    async def process_tasks(self) -> None:
        """Main task processing loop"""
        while True:
            try:
                # Get highest priority task
                _, task = await asyncio.wait_for(
                    self._task_queue.get(),
                    timeout=1.0
                )

                # Determine which tentacles to use
                tentacles = await self._select_tentacles(task)

                if not tentacles:
                    self.logger.warning(f"No suitable tentacles for task {task.id}")
                    continue

                # Execute task across selected tentacles
                results = await self._execute_distributed(task, tentacles)

                # Fuse results from multiple tentacles
                fused_result = await self._fuse_results(task, results)

                # Store result
                self._results_cache[task.id] = fused_result
                self._metrics["tasks_completed"] += 1

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Task processing error: {e}")
                self._metrics["tasks_failed"] += 1

    async def _select_tentacles(self, task: Task) -> List[str]:
        """
        Intelligently select which tentacles to activate.

        Key principle: Don't overstimulate - use minimum necessary tentacles.
        """
        available = []

        for tentacle_id, tentacle in self._tentacles.items():
            # Check if tentacle is suitable and not overloaded
            if await self._is_tentacle_suitable(tentacle_id, tentacle, task):
                available.append(tentacle_id)

        # If specific tentacles required, filter to those
        if task.required_tentacles:
            available = [t for t in available if t in task.required_tentacles]

        # Limit concurrent tentacles to prevent overstimulation
        max_tentacles = min(
            len(available),
            self.config.load_balancer.max_concurrent_tentacles
        )

        # Select based on task type and tentacle specialization
        return await self._rank_and_select(available, task, max_tentacles)

    async def _is_tentacle_suitable(
        self,
        tentacle_id: str,
        tentacle: Any,
        task: Task
    ) -> bool:
        """Check if a tentacle is suitable for a task"""
        # Check if tentacle is active
        if hasattr(tentacle, 'mode') and tentacle.mode == TentacleMode.DORMANT:
            return False

        # Check if tentacle is currently locked (busy)
        if self._tentacle_locks[tentacle_id].locked():
            return False

        # Check tentacle's capabilities match task requirements
        if hasattr(tentacle, 'capabilities'):
            if task.type not in tentacle.capabilities:
                return False

        return True

    async def _rank_and_select(
        self,
        tentacles: List[str],
        task: Task,
        max_count: int
    ) -> List[str]:
        """Rank tentacles by suitability and select top performers"""
        if not tentacles:
            return []

        # Score each tentacle
        scores = {}
        for tentacle_id in tentacles:
            tentacle = self._tentacles[tentacle_id]
            score = 0

            # Prefer tentacles specialized for this task type
            if hasattr(tentacle, 'specialization'):
                if tentacle.specialization == task.type:
                    score += 100

            # Consider recent performance
            if hasattr(tentacle, 'success_rate'):
                score += tentacle.success_rate * 50

            # Balance load - prefer less recently used
            activations = self._metrics["tentacle_activations"].get(tentacle_id, 0)
            score -= activations * 0.1

            scores[tentacle_id] = score

        # Sort by score and return top N
        ranked = sorted(scores.keys(), key=lambda t: scores[t], reverse=True)
        return ranked[:max_count]

    async def _execute_distributed(
        self,
        task: Task,
        tentacles: List[str]
    ) -> List[TaskResult]:
        """Execute task across multiple tentacles in parallel"""
        async def execute_on_tentacle(tentacle_id: str) -> TaskResult:
            async with self._tentacle_locks[tentacle_id]:
                tentacle = self._tentacles[tentacle_id]
                self._metrics["tentacle_activations"][tentacle_id] += 1

                start_time = asyncio.get_event_loop().time()

                try:
                    # Execute the task
                    if hasattr(tentacle, 'execute'):
                        result = await asyncio.wait_for(
                            tentacle.execute(task),
                            timeout=task.timeout
                        )
                    else:
                        result = {"error": "Tentacle has no execute method"}

                    execution_time = asyncio.get_event_loop().time() - start_time

                    return TaskResult(
                        task_id=task.id,
                        tentacle_id=tentacle_id,
                        success=True,
                        data=result,
                        execution_time=execution_time,
                        tokens_used=result.get("tokens_used", 0) if isinstance(result, dict) else 0
                    )

                except asyncio.TimeoutError:
                    return TaskResult(
                        task_id=task.id,
                        tentacle_id=tentacle_id,
                        success=False,
                        data=None,
                        error="Timeout"
                    )
                except Exception as e:
                    return TaskResult(
                        task_id=task.id,
                        tentacle_id=tentacle_id,
                        success=False,
                        data=None,
                        error=str(e)
                    )

        # Execute on all tentacles in parallel
        tasks = [execute_on_tentacle(tid) for tid in tentacles]
        results = await asyncio.gather(*tasks)

        return list(results)

    async def _fuse_results(
        self,
        task: Task,
        results: List[TaskResult]
    ) -> TaskResult:
        """
        Fuse results from multiple tentacles into a unified response.

        This is where the multi-AI fusion magic happens - combining
        the strengths of different AI models.
        """
        successful_results = [r for r in results if r.success]

        if not successful_results:
            # All failed
            return TaskResult(
                task_id=task.id,
                tentacle_id="brain",
                success=False,
                data=None,
                error="All tentacles failed"
            )

        if len(successful_results) == 1:
            # Single result, no fusion needed
            return successful_results[0]

        # Multi-result fusion
        fused_data = {
            "fusion_type": "multi_tentacle",
            "sources": [],
            "consensus": None,
            "divergent_views": [],
            "confidence": 0.0,
        }

        # Collect all responses
        for result in successful_results:
            fused_data["sources"].append({
                "tentacle": result.tentacle_id,
                "data": result.data,
                "execution_time": result.execution_time
            })

        # Find consensus (simplified - in production, use more sophisticated fusion)
        # This is where you'd implement voting, weighted averaging, or ML-based fusion
        fused_data["consensus"] = await self._find_consensus(
            [r.data for r in successful_results]
        )

        # Calculate confidence based on agreement
        fused_data["confidence"] = await self._calculate_confidence(successful_results)

        total_tokens = sum(r.tokens_used for r in results)
        total_time = max(r.execution_time for r in results)

        return TaskResult(
            task_id=task.id,
            tentacle_id="brain_fusion",
            success=True,
            data=fused_data,
            execution_time=total_time,
            tokens_used=total_tokens
        )

    async def _find_consensus(self, results: List[Any]) -> Any:
        """Find consensus among multiple AI results"""
        # Simplified consensus - take first result
        # In production: implement voting, semantic similarity, etc.
        return results[0] if results else None

    async def _calculate_confidence(self, results: List[TaskResult]) -> float:
        """Calculate confidence score based on result agreement"""
        if len(results) <= 1:
            return 0.8  # Single source, moderate confidence

        # More results agreeing = higher confidence
        return min(0.95, 0.6 + (len(results) * 0.1))

    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Retrieve result for a completed task"""
        return self._results_cache.get(task_id)

    def get_metrics(self) -> Dict[str, Any]:
        """Get brain performance metrics"""
        return {
            **self._metrics,
            "active_tentacles": len(self._tentacles),
            "queued_tasks": self._task_queue.qsize(),
            "cached_results": len(self._results_cache),
        }

    async def set_tentacle_mode(self, tentacle_id: str, mode: TentacleMode) -> bool:
        """Set operating mode for a tentacle"""
        if tentacle_id not in self._tentacles:
            return False

        tentacle = self._tentacles[tentacle_id]
        if hasattr(tentacle, 'set_mode'):
            await tentacle.set_mode(mode)
            self.logger.info(f"Set {tentacle_id} to mode: {mode}")
            return True

        return False
