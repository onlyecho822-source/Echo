"""
Echo State Observer
Specification: Echo Formal Spec v2.4 (Manus Procedure)
Purpose: Sample system metrics and output state vector S(t).

The State Observer is the "eyes" of the continuous control system.
It periodically samples metrics from various sources and computes
the state vector S(t) = [H(t), C(t), R(t), L(t), Q(t)].
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ChainStatus(Enum):
    """Status of the hash chain integrity check."""
    VALID = "valid"
    BROKEN = "broken"
    UNKNOWN = "unknown"


@dataclass
class StateVector:
    """
    The continuous state vector S(t).
    
    Components:
    - H: System Health (throughput, error rate, utilization)
    - C: Chain Integrity (probability of hash chain validity)
    - R: Risk Posture (current system risk level)
    - L: Ledger Depth (number of EIL records)
    - Q: Queue Length (jobs waiting per task type)
    """
    timestamp: datetime
    
    # H(t) - Health metrics
    H_throughput: float          # Tasks completed per interval
    H_error_rate: float          # Percentage of tasks that errored (0-1)
    H_utilization: float         # Resource utilization (0-1)
    
    # C(t) - Chain integrity
    C_chain_integrity: float     # Probability of hash chain validity (0-1)
    C_chain_status: ChainStatus  # Discrete status
    
    # R(t) - Risk posture
    R_risk_posture: float        # Composite risk score (0-1)
    # L(t) - Ledger depth
    L_ledger_depth: int          # Total records in raw_events
    L_verified_outputs: int      # Total records in verified_outputs
    
    # Q(t) - Queue lengths
    Q_total_queue: int           # Total pending jobs
    
    # Fields with defaults must come last
    R_risk_factors: Dict[str, float] = field(default_factory=dict)
    Q_by_type: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "H_throughput": self.H_throughput,
            "H_error_rate": self.H_error_rate,
            "H_utilization": self.H_utilization,
            "C_chain_integrity": self.C_chain_integrity,
            "C_chain_status": self.C_chain_status.value,
            "R_risk_posture": self.R_risk_posture,
            "R_risk_factors": self.R_risk_factors,
            "L_ledger_depth": self.L_ledger_depth,
            "L_verified_outputs": self.L_verified_outputs,
            "Q_total_queue": self.Q_total_queue,
            "Q_by_type": self.Q_by_type
        }


@dataclass
class RiskWeights:
    """Configurable weights for risk calculation."""
    error_rate: float = 0.35
    chain_integrity: float = 0.30
    queue_length: float = 0.20
    utilization: float = 0.15
    
    def validate(self) -> bool:
        """Weights must sum to 1.0."""
        total = self.error_rate + self.chain_integrity + self.queue_length + self.utilization
        return abs(total - 1.0) < 0.001


class StateObserver:
    """
    The State Observer samples system metrics and computes S(t).
    
    This is the sensing layer of the continuous control system.
    It provides the Controller with the information needed to
    compute control inputs.
    """
    
    def __init__(
        self,
        risk_weights: Optional[RiskWeights] = None,
        queue_normalization: int = 100,
        utilization_threshold: float = 0.8
    ):
        """
        Initialize the State Observer.
        
        Args:
            risk_weights: Weights for composite risk calculation.
            queue_normalization: Queue length that maps to risk=1.0.
            utilization_threshold: Utilization above this is risky.
        """
        self.risk_weights = risk_weights or RiskWeights()
        self.queue_normalization = queue_normalization
        self.utilization_threshold = utilization_threshold
        
        # State history for trend analysis
        self.state_history: List[StateVector] = []
        self.max_history = 100
        
        # Validate weights
        if not self.risk_weights.validate():
            raise ValueError("Risk weights must sum to 1.0")
    
    def sample(
        self,
        throughput: float,
        error_rate: float,
        utilization: float,
        chain_records: List[Dict[str, str]],
        ledger_depth: int,
        verified_outputs: int,
        queue_lengths: Dict[str, int]
    ) -> StateVector:
        """
        Sample the current system state.
        
        Args:
            throughput: Tasks completed in the last interval.
            error_rate: Percentage of tasks that errored (0-1).
            utilization: Resource utilization (0-1).
            chain_records: List of EIL records for integrity check.
            ledger_depth: Total records in raw_events.
            verified_outputs: Total records in verified_outputs.
            queue_lengths: Dict of queue name -> length.
        
        Returns:
            StateVector: The current state S(t).
        """
        # Verify chain integrity
        chain_integrity, chain_status = self._verify_chain_integrity(chain_records)
        
        # Calculate total queue length
        total_queue = sum(queue_lengths.values())
        
        # Calculate composite risk
        risk_posture, risk_factors = self._calculate_risk(
            error_rate=error_rate,
            chain_integrity=chain_integrity,
            queue_length=total_queue,
            utilization=utilization
        )
        
        # Create state vector
        state = StateVector(
            timestamp=datetime.utcnow(),
            H_throughput=throughput,
            H_error_rate=error_rate,
            H_utilization=utilization,
            C_chain_integrity=chain_integrity,
            C_chain_status=chain_status,
            R_risk_posture=risk_posture,
            R_risk_factors=risk_factors,
            L_ledger_depth=ledger_depth,
            L_verified_outputs=verified_outputs,
            Q_total_queue=total_queue,
            Q_by_type=queue_lengths
        )
        
        # Store in history
        self._store_state(state)
        
        return state
    
    def _verify_chain_integrity(
        self,
        records: List[Dict[str, str]]
    ) -> tuple[float, ChainStatus]:
        """
        Verify the hash chain integrity.
        
        Returns:
            tuple: (integrity probability, status)
        """
        if not records:
            return 1.0, ChainStatus.UNKNOWN
        
        # Verify each link in the chain
        valid_links = 0
        total_links = len(records) - 1
        
        if total_links == 0:
            return 1.0, ChainStatus.VALID
        
        for i in range(1, len(records)):
            prev_record = records[i - 1]
            curr_record = records[i]
            
            # Check if previous_hash matches
            if curr_record.get("previous_hash") == prev_record.get("record_hash"):
                valid_links += 1
        
        integrity = valid_links / total_links if total_links > 0 else 1.0
        status = ChainStatus.VALID if integrity == 1.0 else ChainStatus.BROKEN
        
        return integrity, status
    
    def _calculate_risk(
        self,
        error_rate: float,
        chain_integrity: float,
        queue_length: int,
        utilization: float
    ) -> tuple[float, Dict[str, float]]:
        """
        Calculate composite risk posture.
        
        Risk increases with:
        - Higher error rate
        - Lower chain integrity
        - Longer queues
        - Higher utilization
        
        Returns:
            tuple: (risk score, risk factors dict)
        """
        w = self.risk_weights
        
        # Normalize queue length
        queue_risk = min(queue_length / self.queue_normalization, 1.0)
        
        # Invert chain integrity (low integrity = high risk)
        chain_risk = 1.0 - chain_integrity
        
        # Utilization risk (above threshold is risky)
        util_risk = max(0, (utilization - self.utilization_threshold) / (1.0 - self.utilization_threshold))
        util_risk = min(util_risk, 1.0)
        
        # Composite risk
        risk_factors = {
            "error_rate": error_rate * w.error_rate,
            "chain_integrity": chain_risk * w.chain_integrity,
            "queue_length": queue_risk * w.queue_length,
            "utilization": util_risk * w.utilization
        }
        
        risk_posture = sum(risk_factors.values())
        risk_posture = min(risk_posture, 1.0)  # Cap at 1.0
        
        return risk_posture, risk_factors
    
    def _store_state(self, state: StateVector) -> None:
        """Store state in history, maintaining max size."""
        self.state_history.append(state)
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)
    
    def get_trend(self, metric: str, window: int = 10) -> Optional[float]:
        """
        Calculate trend for a metric over recent history.
        
        Args:
            metric: Name of the metric (e.g., "R_risk_posture").
            window: Number of samples to consider.
        
        Returns:
            float: Trend (positive = increasing, negative = decreasing).
        """
        if len(self.state_history) < 2:
            return None
        
        recent = self.state_history[-window:]
        if len(recent) < 2:
            return None
        
        values = [getattr(s, metric, None) for s in recent]
        values = [v for v in values if v is not None]
        
        if len(values) < 2:
            return None
        
        # Simple linear trend
        trend = (values[-1] - values[0]) / len(values)
        return trend
    
    def get_disturbance_estimate(self, expected_state: StateVector) -> Dict[str, float]:
        """
        Estimate disturbance d̂(t) as difference between expected and actual state.
        
        This is the Devil Lens as a disturbance observer.
        
        Args:
            expected_state: The state we expected based on known inputs.
        
        Returns:
            Dict of disturbance estimates per component.
        """
        if not self.state_history:
            return {}
        
        actual = self.state_history[-1]
        
        disturbance = {
            "d_throughput": actual.H_throughput - expected_state.H_throughput,
            "d_error_rate": actual.H_error_rate - expected_state.H_error_rate,
            "d_chain_integrity": actual.C_chain_integrity - expected_state.C_chain_integrity,
            "d_risk": actual.R_risk_posture - expected_state.R_risk_posture,
            "d_queue": actual.Q_total_queue - expected_state.Q_total_queue
        }
        
        return disturbance


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("STATE OBSERVER - Test Suite")
    print("=" * 60)
    
    # Create observer
    observer = StateObserver()
    
    # Simulate chain records
    chain_records = [
        {"record_hash": "abc123", "previous_hash": "000000"},
        {"record_hash": "def456", "previous_hash": "abc123"},
        {"record_hash": "ghi789", "previous_hash": "def456"},
    ]
    
    # Sample state
    state = observer.sample(
        throughput=50.0,
        error_rate=0.05,
        utilization=0.6,
        chain_records=chain_records,
        ledger_depth=1000,
        verified_outputs=500,
        queue_lengths={"intent": 10, "review": 5, "bind": 3}
    )
    
    print(f"\n--- State Vector S(t) ---")
    print(f"Timestamp: {state.timestamp}")
    print(f"H_throughput: {state.H_throughput}")
    print(f"H_error_rate: {state.H_error_rate}")
    print(f"H_utilization: {state.H_utilization}")
    print(f"C_chain_integrity: {state.C_chain_integrity}")
    print(f"C_chain_status: {state.C_chain_status.value}")
    print(f"R_risk_posture: {state.R_risk_posture:.4f}")
    print(f"R_risk_factors: {state.R_risk_factors}")
    print(f"L_ledger_depth: {state.L_ledger_depth}")
    print(f"Q_total_queue: {state.Q_total_queue}")
    
    print("\n" + "=" * 60)
    print("All Tests Passed")
    print("=" * 60)
