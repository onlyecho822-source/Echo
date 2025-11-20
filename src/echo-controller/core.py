"""
Echo Controller - Core Implementation
Adaptive supervisory control system for complex systems

This module implements the main control loop and state management
for the Echo Controller system.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
import numpy as np


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterventionType(Enum):
    """Types of interventions the system can perform"""
    SCALE_RESOURCES = "scale_resources"
    RESTART_COMPONENT = "restart_component"
    ADJUST_CONFIG = "adjust_config"
    FAILOVER = "failover"
    ALERT_HUMAN = "alert_human"


@dataclass
class SystemState:
    """
    Comprehensive system state representation

    Captures all relevant metrics and context needed for
    stability analysis and intervention planning.
    """
    timestamp: datetime
    system_id: str

    # Resource metrics
    cpu_usage: float  # 0.0 - 1.0
    memory_usage: float  # 0.0 - 1.0
    disk_usage: float  # 0.0 - 1.0
    network_io_mbps: float

    # Performance metrics
    request_rate: float  # requests per second
    error_rate: float  # 0.0 - 1.0
    response_time_p50: float  # milliseconds
    response_time_p95: float  # milliseconds
    response_time_p99: float  # milliseconds

    # Health indicators
    active_connections: int
    queue_depth: int
    dependency_health_scores: Dict[str, float] = field(default_factory=dict)

    # Historical context
    previous_states: List['SystemState'] = field(default_factory=list)

    def to_feature_vector(self) -> np.ndarray:
        """Convert state to feature vector for ML models"""
        features = [
            self.cpu_usage,
            self.memory_usage,
            self.disk_usage,
            self.network_io_mbps / 1000,  # Normalize
            self.request_rate / 1000,  # Normalize
            self.error_rate,
            self.response_time_p95 / 1000,  # Normalize to seconds
            self.response_time_p99 / 1000,
            self.active_connections / 1000,  # Normalize
            self.queue_depth / 100,  # Normalize
        ]
        return np.array(features)

    def add_to_history(self, previous_state: 'SystemState'):
        """Add a previous state to history (limited to last 100)"""
        self.previous_states.append(previous_state)
        if len(self.previous_states) > 100:
            self.previous_states.pop(0)


@dataclass
class StabilityMetrics:
    """Results of stability analysis"""
    stability_score: float  # 0.0 (unstable) to 1.0 (stable)
    drift_rate: float  # Rate of change from baseline
    collapse_risk: float  # 0.0 (safe) to 1.0 (imminent failure)
    health_indicators: Dict[str, float]
    recommended_interventions: List['Intervention']


@dataclass
class Intervention:
    """Represents an intervention to stabilize the system"""
    intervention_id: str
    intervention_type: InterventionType
    description: str
    parameters: Dict[str, Any]
    expected_impact: float  # Expected improvement in stability
    risk_level: float  # 0.0 (safe) to 1.0 (risky)
    estimated_duration: float  # seconds

    def validate(self, system_state: SystemState) -> bool:
        """Check if intervention is safe to execute"""
        # Basic validation logic
        if self.risk_level > 0.8:
            logger.warning(f"High-risk intervention: {self.intervention_id}")
            return False
        return True


@dataclass
class InterventionResult:
    """Result of executing an intervention"""
    intervention_id: str
    success: bool
    execution_time: float  # seconds
    impact: Optional[float]  # Actual improvement in stability
    error_message: Optional[str] = None


class StabilityCalculator:
    """
    Calculates system stability using multiple metrics
    """

    def __init__(self):
        # Weights for different stability components
        self.weights = {
            'resource': 0.25,
            'error': 0.30,
            'performance': 0.25,
            'dependency': 0.20
        }

    def calculate(self, system_state: SystemState) -> float:
        """
        Calculate composite stability score [0.0 - 1.0]

        Higher score = more stable
        """
        scores = {
            'resource': self._resource_score(system_state),
            'error': self._error_score(system_state),
            'performance': self._performance_score(system_state),
            'dependency': self._dependency_score(system_state)
        }

        # Weighted average
        stability = sum(scores[k] * self.weights[k] for k in scores)
        return max(0.0, min(1.0, stability))

    def _resource_score(self, state: SystemState) -> float:
        """Score based on resource utilization (lower is better up to a point)"""
        # Ideal utilization is 50-70%, penalize extremes
        cpu_score = 1.0 - abs(0.6 - state.cpu_usage) * 2
        memory_score = 1.0 - abs(0.6 - state.memory_usage) * 2
        disk_score = 1.0 - state.disk_usage  # Penalize high disk usage

        return (cpu_score + memory_score + disk_score) / 3

    def _error_score(self, state: SystemState) -> float:
        """Score based on error rate (lower is better)"""
        # Error rate of 0 = 1.0, error rate of 0.1 = 0.0
        return max(0.0, 1.0 - (state.error_rate * 10))

    def _performance_score(self, state: SystemState) -> float:
        """Score based on response times"""
        # Penalize P95 > 200ms, P99 > 500ms
        p95_score = max(0.0, 1.0 - (state.response_time_p95 / 200))
        p99_score = max(0.0, 1.0 - (state.response_time_p99 / 500))

        return (p95_score + p99_score) / 2

    def _dependency_score(self, state: SystemState) -> float:
        """Score based on dependency health"""
        if not state.dependency_health_scores:
            return 1.0  # No dependencies = healthy

        return np.mean(list(state.dependency_health_scores.values()))


class DriftDetector:
    """
    Detects when system is drifting from normal behavior
    """

    def __init__(self, threshold: float = 2.0):
        self.threshold = threshold  # Standard deviations
        self.baseline_window = 30  # Number of historical states to consider

    def calculate_drift(self, system_state: SystemState) -> float:
        """
        Calculate drift rate from baseline behavior

        Returns: Drift rate (0 = no drift, >2.0 = significant drift)
        """
        if len(system_state.previous_states) < 10:
            return 0.0  # Not enough history

        # Get recent history
        history = system_state.previous_states[-self.baseline_window:]

        # Calculate baseline metrics
        baseline_cpu = np.mean([s.cpu_usage for s in history])
        baseline_error = np.mean([s.error_rate for s in history])
        baseline_response = np.mean([s.response_time_p95 for s in history])

        # Calculate standard deviations
        std_cpu = np.std([s.cpu_usage for s in history])
        std_error = np.std([s.error_rate for s in history])
        std_response = np.std([s.response_time_p95 for s in history])

        # Calculate z-scores for current state
        z_cpu = abs(system_state.cpu_usage - baseline_cpu) / (std_cpu + 0.01)
        z_error = abs(system_state.error_rate - baseline_error) / (std_error + 0.01)
        z_response = abs(system_state.response_time_p95 - baseline_response) / (std_response + 0.01)

        # Maximum z-score is the drift indicator
        drift = max(z_cpu, z_error, z_response)

        return drift


class RiskPredictor:
    """
    Predicts probability of system collapse
    """

    def predict_collapse_risk(self, system_state: SystemState, stability_score: float, drift_rate: float) -> float:
        """
        Predict probability of system collapse [0.0 - 1.0]

        Uses simple heuristics for now, can be replaced with ML model
        """
        # Base risk from low stability
        risk = 1.0 - stability_score

        # Increase risk if drifting
        if drift_rate > 2.0:
            risk *= 1.5

        # Increase risk if error rate is high
        if system_state.error_rate > 0.05:
            risk *= 1.3

        # Increase risk if resources are maxed out
        if system_state.cpu_usage > 0.9 or system_state.memory_usage > 0.9:
            risk *= 1.4

        return min(1.0, risk)


class InterventionEngine:
    """
    Plans and executes interventions to stabilize systems
    """

    def plan_interventions(
        self,
        system_state: SystemState,
        metrics: StabilityMetrics
    ) -> List[Intervention]:
        """Generate list of recommended interventions"""
        interventions = []

        # High CPU usage -> scale resources
        if system_state.cpu_usage > 0.8:
            interventions.append(Intervention(
                intervention_id=f"scale-{system_state.system_id}-{datetime.now().isoformat()}",
                intervention_type=InterventionType.SCALE_RESOURCES,
                description="Scale up CPU resources",
                parameters={'resource': 'cpu', 'scale_factor': 1.5},
                expected_impact=0.3,
                risk_level=0.2,
                estimated_duration=60
            ))

        # High error rate -> restart component
        if system_state.error_rate > 0.1:
            interventions.append(Intervention(
                intervention_id=f"restart-{system_state.system_id}-{datetime.now().isoformat()}",
                intervention_type=InterventionType.RESTART_COMPONENT,
                description="Restart failing component",
                parameters={'component': 'primary'},
                expected_impact=0.5,
                risk_level=0.4,
                estimated_duration=30
            ))

        # Critical stability -> alert human
        if metrics.collapse_risk > 0.9:
            interventions.append(Intervention(
                intervention_id=f"alert-{system_state.system_id}-{datetime.now().isoformat()}",
                intervention_type=InterventionType.ALERT_HUMAN,
                description="Critical system state - human intervention required",
                parameters={'severity': 'critical', 'channel': 'pagerduty'},
                expected_impact=0.0,  # Doesn't directly improve stability
                risk_level=0.0,
                estimated_duration=1
            ))

        # Sort by expected impact (highest first)
        interventions.sort(key=lambda i: i.expected_impact, reverse=True)

        return interventions

    async def execute_intervention(
        self,
        intervention: Intervention,
        system_state: SystemState
    ) -> InterventionResult:
        """Execute an intervention"""
        start_time = datetime.now()

        try:
            # Validate before execution
            if not intervention.validate(system_state):
                return InterventionResult(
                    intervention_id=intervention.intervention_id,
                    success=False,
                    execution_time=0,
                    impact=None,
                    error_message="Intervention failed validation"
                )

            # Simulate execution (replace with actual implementation)
            logger.info(f"Executing intervention: {intervention.description}")
            await asyncio.sleep(intervention.estimated_duration / 10)  # Simulated delay

            execution_time = (datetime.now() - start_time).total_seconds()

            return InterventionResult(
                intervention_id=intervention.intervention_id,
                success=True,
                execution_time=execution_time,
                impact=intervention.expected_impact
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Intervention failed: {str(e)}")
            return InterventionResult(
                intervention_id=intervention.intervention_id,
                success=False,
                execution_time=execution_time,
                impact=None,
                error_message=str(e)
            )


class EchoController:
    """
    Main Echo Controller - Adaptive supervisory control system
    """

    def __init__(
        self,
        system_id: str,
        stability_threshold: float = 0.3,
        drift_threshold: float = 2.0,
        risk_threshold: float = 0.7,
        cycle_interval: float = 10.0
    ):
        self.system_id = system_id
        self.stability_threshold = stability_threshold
        self.drift_threshold = drift_threshold
        self.risk_threshold = risk_threshold
        self.cycle_interval = cycle_interval

        # Components
        self.stability_calculator = StabilityCalculator()
        self.drift_detector = DriftDetector(threshold=drift_threshold)
        self.risk_predictor = RiskPredictor()
        self.intervention_engine = InterventionEngine()

        # State
        self.current_state: Optional[SystemState] = None
        self.running = False

        logger.info(f"Echo Controller initialized for system: {system_id}")

    def analyze_stability(self, system_state: SystemState) -> StabilityMetrics:
        """
        Comprehensive stability analysis
        """
        # Calculate core metrics
        stability_score = self.stability_calculator.calculate(system_state)
        drift_rate = self.drift_detector.calculate_drift(system_state)
        collapse_risk = self.risk_predictor.predict_collapse_risk(
            system_state,
            stability_score,
            drift_rate
        )

        # Health indicators
        health_indicators = {
            'cpu_health': 1.0 - system_state.cpu_usage,
            'memory_health': 1.0 - system_state.memory_usage,
            'error_health': 1.0 - system_state.error_rate,
            'performance_health': max(0, 1.0 - system_state.response_time_p95 / 500)
        }

        # Plan interventions if needed
        recommended_interventions = []
        if collapse_risk > self.risk_threshold:
            recommended_interventions = self.intervention_engine.plan_interventions(
                system_state,
                StabilityMetrics(
                    stability_score=stability_score,
                    drift_rate=drift_rate,
                    collapse_risk=collapse_risk,
                    health_indicators=health_indicators,
                    recommended_interventions=[]
                )
            )

        return StabilityMetrics(
            stability_score=stability_score,
            drift_rate=drift_rate,
            collapse_risk=collapse_risk,
            health_indicators=health_indicators,
            recommended_interventions=recommended_interventions
        )

    async def control_loop(self):
        """
        Main control loop - runs continuously
        """
        self.running = True
        logger.info(f"Starting control loop for {self.system_id}")

        while self.running:
            try:
                # 1. Observe system state (mock for now)
                system_state = await self.observe_system()

                # 2. Analyze stability
                metrics = self.analyze_stability(system_state)

                # 3. Log metrics
                logger.info(
                    f"System: {self.system_id} | "
                    f"Stability: {metrics.stability_score:.2f} | "
                    f"Drift: {metrics.drift_rate:.2f} | "
                    f"Risk: {metrics.collapse_risk:.2f}"
                )

                # 4. Execute interventions if needed
                if metrics.collapse_risk > self.risk_threshold:
                    logger.warning(f"High collapse risk detected: {metrics.collapse_risk:.2f}")

                    for intervention in metrics.recommended_interventions:
                        result = await self.intervention_engine.execute_intervention(
                            intervention,
                            system_state
                        )

                        if result.success:
                            logger.info(f"Intervention successful: {intervention.description}")
                        else:
                            logger.error(f"Intervention failed: {result.error_message}")

                # 5. Update state history
                if self.current_state:
                    system_state.add_to_history(self.current_state)
                self.current_state = system_state

                # 6. Sleep until next cycle
                await asyncio.sleep(self.cycle_interval)

            except Exception as e:
                logger.error(f"Error in control loop: {str(e)}")
                await asyncio.sleep(self.cycle_interval)

    async def observe_system(self) -> SystemState:
        """
        Observe current system state

        This is a mock implementation - replace with actual monitoring
        """
        import random

        # Generate semi-realistic mock data
        return SystemState(
            timestamp=datetime.now(),
            system_id=self.system_id,
            cpu_usage=random.uniform(0.3, 0.9),
            memory_usage=random.uniform(0.4, 0.8),
            disk_usage=random.uniform(0.5, 0.7),
            network_io_mbps=random.uniform(100, 1000),
            request_rate=random.uniform(500, 2000),
            error_rate=random.uniform(0.0, 0.05),
            response_time_p50=random.uniform(50, 150),
            response_time_p95=random.uniform(100, 300),
            response_time_p99=random.uniform(200, 600),
            active_connections=random.randint(100, 1000),
            queue_depth=random.randint(0, 100),
            dependency_health_scores={
                'database': random.uniform(0.8, 1.0),
                'cache': random.uniform(0.9, 1.0),
                'api': random.uniform(0.7, 1.0)
            }
        )

    def stop(self):
        """Stop the control loop"""
        logger.info(f"Stopping control loop for {self.system_id}")
        self.running = False


# Example usage
async def main():
    """Example usage of Echo Controller"""
    controller = EchoController(
        system_id="production-api",
        stability_threshold=0.3,
        drift_threshold=2.0,
        risk_threshold=0.7,
        cycle_interval=5.0
    )

    # Run for 60 seconds
    task = asyncio.create_task(controller.control_loop())
    await asyncio.sleep(60)
    controller.stop()
    await task


if __name__ == "__main__":
    asyncio.run(main())
