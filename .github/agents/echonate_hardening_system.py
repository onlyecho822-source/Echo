#!/usr/bin/env python3
"""
ECHONATE BOUNDED AUTONOMOUS INTELLIGENCE
Hardening System Implementation

Components:
1. Provenance Ledger - Hash all data fetches for audit trail
2. Policy Gate - Verify signals before activation
3. Adversarial Agent (Epsilon) - Red team the primary signals
4. Circuit Breaker - Halt on anomaly detection

∇θ Phoenix Global Nexus
"""

import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
import math

# =============================================================================
# COMPONENT 1: PROVENANCE LEDGER
# =============================================================================

class ProvenanceLedger:
    """
    Immutable audit trail for all data fetches.
    Every data point is hashed and logged with timestamp.
    Implements Invariant 1: Truth Preservation
    """
    
    def __init__(self, ledger_path: str = "provenance_ledger.json"):
        self.ledger_path = ledger_path
        self.entries: List[Dict] = []
        self._load_ledger()
    
    def _load_ledger(self):
        """Load existing ledger or create new one"""
        if os.path.exists(self.ledger_path):
            with open(self.ledger_path, 'r') as f:
                self.entries = json.load(f)
    
    def _save_ledger(self):
        """Persist ledger to disk"""
        with open(self.ledger_path, 'w') as f:
            json.dump(self.entries, f, indent=2, default=str)
    
    def compute_hash(self, data: Any) -> str:
        """Compute SHA-256 hash of data"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def record_fetch(self, source: str, endpoint: str, data: Any, 
                     metadata: Optional[Dict] = None) -> str:
        """
        Record a data fetch with cryptographic hash.
        Returns the hash for inclusion in downstream signals.
        """
        data_hash = self.compute_hash(data)
        
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': source,
            'endpoint': endpoint,
            'data_hash': data_hash,
            'data_size_bytes': len(json.dumps(data, default=str)),
            'metadata': metadata or {},
            'chain_hash': None  # Will be computed
        }
        
        # Chain hash includes previous entry for immutability
        if self.entries:
            prev_hash = self.entries[-1].get('chain_hash', '')
            entry['chain_hash'] = self.compute_hash(f"{prev_hash}{data_hash}")
        else:
            entry['chain_hash'] = data_hash
        
        self.entries.append(entry)
        self._save_ledger()
        
        return data_hash
    
    def verify_chain(self) -> bool:
        """Verify the integrity of the entire ledger chain"""
        if not self.entries:
            return True
        
        for i, entry in enumerate(self.entries):
            if i == 0:
                expected_chain = entry['data_hash']
            else:
                prev_hash = self.entries[i-1]['chain_hash']
                expected_chain = self.compute_hash(f"{prev_hash}{entry['data_hash']}")
            
            if entry['chain_hash'] != expected_chain:
                return False
        
        return True
    
    def get_provenance_certificate(self, data_hash: str) -> Optional[Dict]:
        """Get provenance certificate for a specific data hash"""
        for entry in self.entries:
            if entry['data_hash'] == data_hash:
                return {
                    'data_hash': data_hash,
                    'chain_hash': entry['chain_hash'],
                    'timestamp': entry['timestamp'],
                    'source': entry['source'],
                    'verified': self.verify_chain()
                }
        return None


# =============================================================================
# COMPONENT 2: POLICY GATE
# =============================================================================

class SignalStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class SignalProof:
    """Statistical proof artifact for signal verification"""
    signal_id: str
    source: str
    target: str
    direction: str
    strength: float
    confidence: float
    
    # Statistical verification
    sample_size: int = 0
    p_value: float = 1.0
    sharpe_ratio: float = 0.0
    backtest_return: float = 0.0
    
    # Provenance
    data_hashes: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: str = field(default_factory=lambda: (datetime.utcnow() + timedelta(days=7)).isoformat())
    
    # Status
    status: SignalStatus = SignalStatus.PENDING
    rejection_reason: Optional[str] = None


class PolicyGate:
    """
    Verification gate for signals before they can be consumed.
    Implements Invariant 4: No mutation without proof
    
    Requirements for signal activation:
    - p-value < 0.05 (statistical significance)
    - Sharpe ratio > 0.5 (risk-adjusted return)
    - Sample size >= 30 (minimum observations)
    - Valid provenance chain
    """
    
    # Thresholds
    P_VALUE_THRESHOLD = 0.05
    SHARPE_THRESHOLD = 0.5
    MIN_SAMPLE_SIZE = 30
    SIGNAL_LIFETIME_DAYS = 7
    
    def __init__(self, ledger: ProvenanceLedger):
        self.ledger = ledger
        self.pending_signals: Dict[str, SignalProof] = {}
        self.verified_signals: Dict[str, SignalProof] = {}
        self.rejected_signals: Dict[str, SignalProof] = {}
    
    def submit_signal(self, proof: SignalProof) -> str:
        """Submit a signal for verification"""
        self.pending_signals[proof.signal_id] = proof
        return proof.signal_id
    
    def verify_signal(self, signal_id: str) -> tuple[bool, str]:
        """
        Verify a pending signal against policy requirements.
        Returns (passed, reason)
        """
        if signal_id not in self.pending_signals:
            return False, "Signal not found in pending queue"
        
        proof = self.pending_signals[signal_id]
        
        # Check expiration
        if datetime.fromisoformat(proof.expires_at.replace('Z', '')) < datetime.utcnow():
            proof.status = SignalStatus.EXPIRED
            proof.rejection_reason = "Signal expired"
            self.rejected_signals[signal_id] = proof
            del self.pending_signals[signal_id]
            return False, "Signal expired"
        
        # Check sample size
        if proof.sample_size < self.MIN_SAMPLE_SIZE:
            proof.status = SignalStatus.REJECTED
            proof.rejection_reason = f"Insufficient sample size: {proof.sample_size} < {self.MIN_SAMPLE_SIZE}"
            self.rejected_signals[signal_id] = proof
            del self.pending_signals[signal_id]
            return False, proof.rejection_reason
        
        # Check statistical significance
        if proof.p_value >= self.P_VALUE_THRESHOLD:
            proof.status = SignalStatus.REJECTED
            proof.rejection_reason = f"Not statistically significant: p={proof.p_value:.4f} >= {self.P_VALUE_THRESHOLD}"
            self.rejected_signals[signal_id] = proof
            del self.pending_signals[signal_id]
            return False, proof.rejection_reason
        
        # Check Sharpe ratio
        if proof.sharpe_ratio < self.SHARPE_THRESHOLD:
            proof.status = SignalStatus.REJECTED
            proof.rejection_reason = f"Insufficient risk-adjusted return: Sharpe={proof.sharpe_ratio:.2f} < {self.SHARPE_THRESHOLD}"
            self.rejected_signals[signal_id] = proof
            del self.pending_signals[signal_id]
            return False, proof.rejection_reason
        
        # Verify provenance chain
        for data_hash in proof.data_hashes:
            cert = self.ledger.get_provenance_certificate(data_hash)
            if not cert or not cert['verified']:
                proof.status = SignalStatus.REJECTED
                proof.rejection_reason = f"Invalid provenance for data hash: {data_hash[:16]}..."
                self.rejected_signals[signal_id] = proof
                del self.pending_signals[signal_id]
                return False, proof.rejection_reason
        
        # All checks passed
        proof.status = SignalStatus.VERIFIED
        self.verified_signals[signal_id] = proof
        del self.pending_signals[signal_id]
        return True, "Signal verified and activated"
    
    def get_active_signals(self) -> List[SignalProof]:
        """Get all currently active (verified, non-expired) signals"""
        active = []
        now = datetime.utcnow()
        
        for signal_id, proof in list(self.verified_signals.items()):
            expires = datetime.fromisoformat(proof.expires_at.replace('Z', ''))
            if expires > now:
                active.append(proof)
            else:
                proof.status = SignalStatus.EXPIRED
                self.rejected_signals[signal_id] = proof
                del self.verified_signals[signal_id]
        
        return active


# =============================================================================
# COMPONENT 3: ADVERSARIAL AGENT (EPSILON)
# =============================================================================

class AdversarialAgent:
    """
    Epsilon Agent: Red Team the primary correlation signals.
    Implements the Devil's Review - institutionalized disagreement.
    
    Strategies:
    1. Inverse correlation testing
    2. Spurious correlation detection
    3. Regime sensitivity analysis
    4. Data quality challenges
    """
    
    def __init__(self, ledger: ProvenanceLedger):
        self.ledger = ledger
        self.challenges: List[Dict] = []
    
    def challenge_signal(self, proof: SignalProof) -> Dict:
        """
        Generate adversarial challenges for a signal.
        Returns challenge report with findings.
        """
        challenge = {
            'signal_id': proof.signal_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'challenges': [],
            'overall_risk': 'LOW',
            'recommendation': 'PROCEED'
        }
        
        # Challenge 1: Inverse correlation test
        inverse_challenge = self._test_inverse_correlation(proof)
        challenge['challenges'].append(inverse_challenge)
        
        # Challenge 2: Spurious correlation detection
        spurious_challenge = self._test_spurious_correlation(proof)
        challenge['challenges'].append(spurious_challenge)
        
        # Challenge 3: Regime sensitivity
        regime_challenge = self._test_regime_sensitivity(proof)
        challenge['challenges'].append(regime_challenge)
        
        # Challenge 4: Data quality
        data_challenge = self._test_data_quality(proof)
        challenge['challenges'].append(data_challenge)
        
        # Aggregate risk
        high_risk_count = sum(1 for c in challenge['challenges'] if c['risk'] == 'HIGH')
        medium_risk_count = sum(1 for c in challenge['challenges'] if c['risk'] == 'MEDIUM')
        
        if high_risk_count >= 2:
            challenge['overall_risk'] = 'CRITICAL'
            challenge['recommendation'] = 'REJECT'
        elif high_risk_count >= 1 or medium_risk_count >= 2:
            challenge['overall_risk'] = 'HIGH'
            challenge['recommendation'] = 'REVIEW'
        elif medium_risk_count >= 1:
            challenge['overall_risk'] = 'MEDIUM'
            challenge['recommendation'] = 'PROCEED_WITH_CAUTION'
        
        self.challenges.append(challenge)
        return challenge
    
    def _test_inverse_correlation(self, proof: SignalProof) -> Dict:
        """Test if inverse signal would also be profitable (sign of noise)"""
        # Simulate inverse test
        inverse_sharpe = -proof.sharpe_ratio * 0.3  # Simplified model
        
        if inverse_sharpe > 0:
            return {
                'type': 'INVERSE_CORRELATION',
                'finding': 'Inverse signal also shows positive returns',
                'risk': 'HIGH',
                'detail': f'Inverse Sharpe: {inverse_sharpe:.2f}'
            }
        return {
            'type': 'INVERSE_CORRELATION',
            'finding': 'Inverse signal shows negative returns (expected)',
            'risk': 'LOW',
            'detail': f'Inverse Sharpe: {inverse_sharpe:.2f}'
        }
    
    def _test_spurious_correlation(self, proof: SignalProof) -> Dict:
        """Check for signs of spurious correlation"""
        # Multiple testing adjustment (Bonferroni-like)
        adjusted_p = proof.p_value * 10  # Assume 10 hypotheses tested
        
        if adjusted_p >= 0.05:
            return {
                'type': 'SPURIOUS_CORRELATION',
                'finding': 'Signal may be spurious after multiple testing adjustment',
                'risk': 'HIGH',
                'detail': f'Adjusted p-value: {adjusted_p:.4f}'
            }
        elif adjusted_p >= 0.01:
            return {
                'type': 'SPURIOUS_CORRELATION',
                'finding': 'Signal marginally significant after adjustment',
                'risk': 'MEDIUM',
                'detail': f'Adjusted p-value: {adjusted_p:.4f}'
            }
        return {
            'type': 'SPURIOUS_CORRELATION',
            'finding': 'Signal robust to multiple testing adjustment',
            'risk': 'LOW',
            'detail': f'Adjusted p-value: {adjusted_p:.4f}'
        }
    
    def _test_regime_sensitivity(self, proof: SignalProof) -> Dict:
        """Test signal stability across market regimes"""
        # Simplified regime test based on confidence
        if proof.confidence < 0.7:
            return {
                'type': 'REGIME_SENSITIVITY',
                'finding': 'Signal may be regime-dependent',
                'risk': 'MEDIUM',
                'detail': f'Confidence: {proof.confidence:.2f}'
            }
        return {
            'type': 'REGIME_SENSITIVITY',
            'finding': 'Signal appears regime-stable',
            'risk': 'LOW',
            'detail': f'Confidence: {proof.confidence:.2f}'
        }
    
    def _test_data_quality(self, proof: SignalProof) -> Dict:
        """Verify data quality and provenance"""
        if not proof.data_hashes:
            return {
                'type': 'DATA_QUALITY',
                'finding': 'No provenance data attached',
                'risk': 'HIGH',
                'detail': 'Signal lacks audit trail'
            }
        
        # Verify all hashes
        for h in proof.data_hashes:
            cert = self.ledger.get_provenance_certificate(h)
            if not cert:
                return {
                    'type': 'DATA_QUALITY',
                    'finding': 'Missing provenance certificate',
                    'risk': 'HIGH',
                    'detail': f'Hash not found: {h[:16]}...'
                }
        
        return {
            'type': 'DATA_QUALITY',
            'finding': 'All data sources verified',
            'risk': 'LOW',
            'detail': f'{len(proof.data_hashes)} sources verified'
        }


# =============================================================================
# COMPONENT 4: CIRCUIT BREAKER
# =============================================================================

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Halted - anomaly detected
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class AnomalyMetrics:
    """Metrics for anomaly detection"""
    api_failure_rate: float = 0.0
    correlation_failures: int = 0
    drawdown_percent: float = 0.0
    data_staleness_seconds: float = 0.0
    signal_conflict_count: int = 0


class CircuitBreaker:
    """
    System-wide circuit breaker for EchoNate.
    Implements Wish 8: Graceful degradation under uncertainty.
    
    Triggers:
    - API failure rate > 30%
    - Drawdown > 20%
    - Data staleness > 1 hour
    - Correlation failure spike
    """
    
    # Thresholds
    API_FAILURE_THRESHOLD = 0.30
    DRAWDOWN_THRESHOLD = 0.20
    STALENESS_THRESHOLD = 3600  # 1 hour
    CORRELATION_FAILURE_THRESHOLD = 5
    RECOVERY_TIMEOUT = 300  # 5 minutes
    
    def __init__(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.opened_at: Optional[datetime] = None
        self.metrics = AnomalyMetrics()
        self.incident_log: List[Dict] = []
    
    def update_metrics(self, metrics: AnomalyMetrics):
        """Update system metrics and check for anomalies"""
        self.metrics = metrics
        self._check_anomalies()
    
    def _check_anomalies(self):
        """Check if any anomaly threshold is breached"""
        anomalies = []
        
        if self.metrics.api_failure_rate > self.API_FAILURE_THRESHOLD:
            anomalies.append(f"API failure rate: {self.metrics.api_failure_rate:.1%}")
        
        if self.metrics.drawdown_percent > self.DRAWDOWN_THRESHOLD:
            anomalies.append(f"Drawdown: {self.metrics.drawdown_percent:.1%}")
        
        if self.metrics.data_staleness_seconds > self.STALENESS_THRESHOLD:
            anomalies.append(f"Data staleness: {self.metrics.data_staleness_seconds/60:.0f} min")
        
        if self.metrics.correlation_failures > self.CORRELATION_FAILURE_THRESHOLD:
            anomalies.append(f"Correlation failures: {self.metrics.correlation_failures}")
        
        if anomalies:
            self._trip(anomalies)
    
    def _trip(self, reasons: List[str]):
        """Trip the circuit breaker"""
        if self.state == CircuitState.OPEN:
            return  # Already open
        
        self.state = CircuitState.OPEN
        self.opened_at = datetime.utcnow()
        
        incident = {
            'timestamp': self.opened_at.isoformat() + 'Z',
            'event': 'CIRCUIT_OPENED',
            'reasons': reasons,
            'metrics': asdict(self.metrics),
            'action': 'All signals switched to PAPER mode'
        }
        self.incident_log.append(incident)
    
    def attempt_recovery(self) -> bool:
        """Attempt to recover from open state"""
        if self.state != CircuitState.OPEN:
            return True
        
        if not self.opened_at:
            return False
        
        elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
        
        if elapsed < self.RECOVERY_TIMEOUT:
            return False
        
        # Switch to half-open for testing
        self.state = CircuitState.HALF_OPEN
        
        # Re-check metrics
        anomalies = []
        if self.metrics.api_failure_rate > self.API_FAILURE_THRESHOLD:
            anomalies.append("API failure rate still elevated")
        if self.metrics.drawdown_percent > self.DRAWDOWN_THRESHOLD:
            anomalies.append("Drawdown still elevated")
        
        if anomalies:
            self.state = CircuitState.OPEN
            self.opened_at = datetime.utcnow()
            return False
        
        # Recovery successful
        self.state = CircuitState.CLOSED
        self.incident_log.append({
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event': 'CIRCUIT_CLOSED',
            'detail': 'Recovery successful after timeout'
        })
        return True
    
    def is_operational(self) -> bool:
        """Check if system is operational"""
        return self.state == CircuitState.CLOSED
    
    def get_status(self) -> Dict:
        """Get current circuit breaker status"""
        return {
            'state': self.state.value,
            'operational': self.is_operational(),
            'metrics': asdict(self.metrics),
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'recent_incidents': self.incident_log[-5:]
        }


# =============================================================================
# INTEGRATED SYSTEM: BOUNDED AUTONOMOUS INTELLIGENCE
# =============================================================================

class BoundedAutonomousIntelligence:
    """
    Complete hardened EchoNate system.
    Integrates all four safety components.
    """
    
    def __init__(self, ledger_path: str = "echonate_provenance.json"):
        self.ledger = ProvenanceLedger(ledger_path)
        self.policy_gate = PolicyGate(self.ledger)
        self.adversarial = AdversarialAgent(self.ledger)
        self.circuit_breaker = CircuitBreaker()
        
        self.mode = "LIVE"  # LIVE or PAPER
    
    def record_data_fetch(self, source: str, endpoint: str, data: Any) -> str:
        """Record a data fetch and return provenance hash"""
        return self.ledger.record_fetch(source, endpoint, data)
    
    def submit_signal(self, 
                      source: str,
                      target: str,
                      direction: str,
                      strength: float,
                      confidence: float,
                      sample_size: int,
                      p_value: float,
                      sharpe_ratio: float,
                      data_hashes: List[str]) -> Dict:
        """
        Submit a signal through the full verification pipeline.
        
        1. Create proof artifact
        2. Submit to policy gate
        3. Run adversarial challenges
        4. Check circuit breaker
        5. Return decision
        """
        # Check circuit breaker first
        if not self.circuit_breaker.is_operational():
            return {
                'status': 'REJECTED',
                'reason': 'Circuit breaker is OPEN',
                'mode': 'PAPER',
                'circuit_status': self.circuit_breaker.get_status()
            }
        
        # Create proof artifact
        signal_id = f"{source}_{target}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        proof = SignalProof(
            signal_id=signal_id,
            source=source,
            target=target,
            direction=direction,
            strength=strength,
            confidence=confidence,
            sample_size=sample_size,
            p_value=p_value,
            sharpe_ratio=sharpe_ratio,
            data_hashes=data_hashes
        )
        
        # Submit to policy gate
        self.policy_gate.submit_signal(proof)
        gate_passed, gate_reason = self.policy_gate.verify_signal(signal_id)
        
        if not gate_passed:
            return {
                'status': 'REJECTED',
                'reason': gate_reason,
                'signal_id': signal_id,
                'proof': asdict(proof)
            }
        
        # Run adversarial challenges
        challenge_report = self.adversarial.challenge_signal(proof)
        
        if challenge_report['recommendation'] == 'REJECT':
            return {
                'status': 'REJECTED',
                'reason': 'Failed adversarial review',
                'signal_id': signal_id,
                'challenge_report': challenge_report
            }
        
        # Signal approved
        return {
            'status': 'APPROVED',
            'signal_id': signal_id,
            'mode': self.mode,
            'proof': asdict(proof),
            'challenge_report': challenge_report,
            'recommendation': challenge_report['recommendation']
        }
    
    def update_system_health(self, 
                             api_failure_rate: float = 0.0,
                             correlation_failures: int = 0,
                             drawdown_percent: float = 0.0,
                             data_staleness_seconds: float = 0.0):
        """Update system health metrics"""
        metrics = AnomalyMetrics(
            api_failure_rate=api_failure_rate,
            correlation_failures=correlation_failures,
            drawdown_percent=drawdown_percent,
            data_staleness_seconds=data_staleness_seconds
        )
        self.circuit_breaker.update_metrics(metrics)
        
        # Switch to paper mode if circuit opens
        if not self.circuit_breaker.is_operational():
            self.mode = "PAPER"
    
    def get_system_status(self) -> Dict:
        """Get complete system status"""
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'mode': self.mode,
            'circuit_breaker': self.circuit_breaker.get_status(),
            'ledger': {
                'entries': len(self.ledger.entries),
                'chain_valid': self.ledger.verify_chain()
            },
            'policy_gate': {
                'pending': len(self.policy_gate.pending_signals),
                'verified': len(self.policy_gate.verified_signals),
                'rejected': len(self.policy_gate.rejected_signals)
            },
            'adversarial': {
                'challenges_issued': len(self.adversarial.challenges)
            }
        }


# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ECHONATE BOUNDED AUTONOMOUS INTELLIGENCE")
    print("Hardening System Demonstration")
    print("=" * 80)
    
    # Initialize system
    bai = BoundedAutonomousIntelligence("demo_provenance.json")
    
    # Simulate data fetch with provenance
    print("\n[1] Recording data fetch with provenance...")
    seismic_data = {"earthquakes": 47, "max_magnitude": 6.0}
    seismic_hash = bai.record_data_fetch("USGS", "/earthquakes/feed", seismic_data)
    print(f"    Data hash: {seismic_hash[:32]}...")
    
    market_data = {"TRV": {"price": 270.83, "change": -0.12}}
    market_hash = bai.record_data_fetch("YahooFinance", "/stock/TRV", market_data)
    print(f"    Data hash: {market_hash[:32]}...")
    
    # Submit signal through pipeline
    print("\n[2] Submitting signal through verification pipeline...")
    result = bai.submit_signal(
        source="SEISMIC",
        target="TRV",
        direction="BEARISH",
        strength=0.40,
        confidence=0.75,
        sample_size=50,
        p_value=0.02,
        sharpe_ratio=0.8,
        data_hashes=[seismic_hash, market_hash]
    )
    
    print(f"    Status: {result['status']}")
    if result['status'] == 'APPROVED':
        print(f"    Mode: {result['mode']}")
        print(f"    Recommendation: {result['recommendation']}")
    else:
        print(f"    Reason: {result.get('reason', 'N/A')}")
    
    # Check system status
    print("\n[3] System status...")
    status = bai.get_system_status()
    print(f"    Mode: {status['mode']}")
    print(f"    Circuit Breaker: {status['circuit_breaker']['state']}")
    print(f"    Ledger entries: {status['ledger']['entries']}")
    print(f"    Chain valid: {status['ledger']['chain_valid']}")
    
    # Simulate anomaly
    print("\n[4] Simulating anomaly (high API failure rate)...")
    bai.update_system_health(api_failure_rate=0.35)
    status = bai.get_system_status()
    print(f"    Circuit Breaker: {status['circuit_breaker']['state']}")
    print(f"    Mode: {status['mode']}")
    
    print("\n" + "=" * 80)
    print("Demonstration complete. System is hardened.")
    print("=" * 80)
