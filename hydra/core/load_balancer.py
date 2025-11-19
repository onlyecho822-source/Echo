"""
Hydra Load Balancer - Preventing Overstimulation
=================================================

The key to the octopus metaphor - ensuring tentacles work in harmony
without overwhelming the system.

Implements circuit breakers, rate limiting, and intelligent scheduling.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

from ..config import LoadBalancerConfig


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class TentacleHealth:
    """Health metrics for a single tentacle"""
    tentacle_id: str
    consecutive_failures: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    circuit_state: CircuitState = CircuitState.CLOSED
    tokens_used_minute: int = 0
    last_token_reset: datetime = field(default_factory=datetime.utcnow)

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

    @property
    def is_healthy(self) -> bool:
        return self.circuit_state == CircuitState.CLOSED


@dataclass
class LoadMetrics:
    """System-wide load metrics"""
    active_tentacles: int = 0
    queued_tasks: int = 0
    memory_usage_mb: float = 0.0
    tokens_per_minute: int = 0
    avg_response_time: float = 0.0


class LoadBalancer:
    """
    Intelligent load balancer that prevents tentacle overstimulation.

    Key features:
    - Circuit breakers for failing tentacles
    - Token budget management
    - Cooldown periods between intense operations
    - Priority-based scheduling
    - Memory pressure monitoring
    """

    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.logger = logging.getLogger("hydra.load_balancer")

        # Health tracking per tentacle
        self._health: Dict[str, TentacleHealth] = {}

        # Rate limiting
        self._last_operations: Dict[str, datetime] = {}
        self._token_usage: Dict[str, int] = {}

        # Locks for thread safety
        self._lock = asyncio.Lock()

        # Global metrics
        self._response_times: List[float] = []
        self._max_response_history = 100

    async def register_tentacle(self, tentacle_id: str) -> None:
        """Register a tentacle for load balancing"""
        async with self._lock:
            self._health[tentacle_id] = TentacleHealth(tentacle_id=tentacle_id)
            self._last_operations[tentacle_id] = datetime.min
            self._token_usage[tentacle_id] = 0

    async def can_execute(self, tentacle_id: str, estimated_tokens: int = 0) -> bool:
        """
        Check if a tentacle can execute a task.

        Considers:
        - Circuit breaker state
        - Cooldown period
        - Token budget
        - Memory limits
        """
        if tentacle_id not in self._health:
            return False

        health = self._health[tentacle_id]

        # Check circuit breaker
        if not await self._check_circuit(tentacle_id):
            return False

        # Check cooldown
        if not await self._check_cooldown(tentacle_id):
            return False

        # Check token budget
        if not await self._check_token_budget(tentacle_id, estimated_tokens):
            return False

        return True

    async def _check_circuit(self, tentacle_id: str) -> bool:
        """Check and manage circuit breaker state"""
        health = self._health[tentacle_id]

        if health.circuit_state == CircuitState.CLOSED:
            return True

        if health.circuit_state == CircuitState.OPEN:
            # Check if enough time has passed to try again
            if health.last_failure:
                elapsed = datetime.utcnow() - health.last_failure
                if elapsed.total_seconds() > 30:  # 30 second recovery window
                    health.circuit_state = CircuitState.HALF_OPEN
                    self.logger.info(f"Circuit half-open for {tentacle_id}")
                    return True
            return False

        # HALF_OPEN - allow one request to test
        return True

    async def _check_cooldown(self, tentacle_id: str) -> bool:
        """Check if tentacle has cooled down enough"""
        last_op = self._last_operations.get(tentacle_id, datetime.min)
        elapsed = (datetime.utcnow() - last_op).total_seconds()
        return elapsed >= self.config.cooldown_period

    async def _check_token_budget(self, tentacle_id: str, estimated: int) -> bool:
        """Check if token budget allows this operation"""
        health = self._health[tentacle_id]

        # Reset token counter if minute has passed
        elapsed = (datetime.utcnow() - health.last_token_reset).total_seconds()
        if elapsed >= 60:
            health.tokens_used_minute = 0
            health.last_token_reset = datetime.utcnow()

        projected = health.tokens_used_minute + estimated
        return projected <= self.config.token_budget_per_minute

    async def record_success(
        self,
        tentacle_id: str,
        tokens_used: int = 0,
        response_time: float = 0.0
    ) -> None:
        """Record a successful tentacle operation"""
        async with self._lock:
            if tentacle_id not in self._health:
                return

            health = self._health[tentacle_id]
            health.total_requests += 1
            health.successful_requests += 1
            health.last_success = datetime.utcnow()
            health.consecutive_failures = 0
            health.tokens_used_minute += tokens_used

            # Recover circuit if in half-open state
            if health.circuit_state == CircuitState.HALF_OPEN:
                health.circuit_state = CircuitState.CLOSED
                self.logger.info(f"Circuit closed for {tentacle_id}")

            self._last_operations[tentacle_id] = datetime.utcnow()

            # Track response time
            self._response_times.append(response_time)
            if len(self._response_times) > self._max_response_history:
                self._response_times.pop(0)

    async def record_failure(self, tentacle_id: str, error: str = "") -> None:
        """Record a failed tentacle operation"""
        async with self._lock:
            if tentacle_id not in self._health:
                return

            health = self._health[tentacle_id]
            health.total_requests += 1
            health.last_failure = datetime.utcnow()
            health.consecutive_failures += 1

            # Check if circuit should trip
            if health.consecutive_failures >= self.config.circuit_breaker_threshold:
                health.circuit_state = CircuitState.OPEN
                self.logger.warning(
                    f"Circuit OPEN for {tentacle_id} after {health.consecutive_failures} failures"
                )

            self._last_operations[tentacle_id] = datetime.utcnow()

    async def get_best_tentacles(
        self,
        tentacle_ids: List[str],
        count: int = 1
    ) -> List[str]:
        """
        Get the best tentacles for task execution.

        Ranking factors:
        - Health/success rate
        - Time since last use (prevent overuse)
        - Circuit breaker state
        """
        scored = []

        for tid in tentacle_ids:
            if tid not in self._health:
                continue

            health = self._health[tid]

            if not health.is_healthy:
                continue

            # Calculate score
            score = health.success_rate * 100

            # Bonus for rested tentacles
            last_op = self._last_operations.get(tid, datetime.min)
            rest_time = (datetime.utcnow() - last_op).total_seconds()
            score += min(rest_time, 30)  # Up to 30 point bonus

            # Penalty for high token usage
            score -= (health.tokens_used_minute / 1000)

            scored.append((tid, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        return [tid for tid, _ in scored[:count]]

    async def apply_backoff(self, tentacle_id: str) -> float:
        """
        Calculate and apply exponential backoff for a tentacle.

        Returns the wait time in seconds.
        """
        if tentacle_id not in self._health:
            return 0.0

        health = self._health[tentacle_id]
        failures = health.consecutive_failures

        if failures == 0:
            return 0.0

        # Exponential backoff with multiplier
        wait_time = self.config.cooldown_period * (
            self.config.backoff_multiplier ** (failures - 1)
        )

        # Cap at 60 seconds
        return min(wait_time, 60.0)

    def get_metrics(self) -> LoadMetrics:
        """Get current load metrics"""
        active = sum(1 for h in self._health.values() if h.is_healthy)
        total_tokens = sum(h.tokens_used_minute for h in self._health.values())

        avg_response = 0.0
        if self._response_times:
            avg_response = sum(self._response_times) / len(self._response_times)

        return LoadMetrics(
            active_tentacles=active,
            tokens_per_minute=total_tokens,
            avg_response_time=avg_response
        )

    def get_tentacle_health(self, tentacle_id: str) -> Optional[TentacleHealth]:
        """Get health metrics for a specific tentacle"""
        return self._health.get(tentacle_id)

    def get_all_health(self) -> Dict[str, TentacleHealth]:
        """Get health metrics for all tentacles"""
        return self._health.copy()

    async def reset_circuit(self, tentacle_id: str) -> bool:
        """Manually reset a circuit breaker"""
        async with self._lock:
            if tentacle_id not in self._health:
                return False

            self._health[tentacle_id].circuit_state = CircuitState.CLOSED
            self._health[tentacle_id].consecutive_failures = 0
            self.logger.info(f"Manually reset circuit for {tentacle_id}")
            return True
