"""
Security Monitors - Behavior and Breach Detection

Provides continuous monitoring for anomalies and breaches.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import statistics


@dataclass
class BehaviorBaseline:
    """Baseline behavior metrics for anomaly detection."""
    metric: str
    mean: float
    std_dev: float
    min_val: float
    max_val: float
    sample_count: int


class BehaviorMonitor:
    """
    Monitors user and system behavior for anomalies.

    Establishes baselines and detects deviations that may
    indicate security issues or unauthorized access.
    """

    def __init__(self):
        self._baselines: Dict[str, BehaviorBaseline] = {}
        self._observations: Dict[str, List[float]] = {}
        self._anomalies: List[Dict[str, Any]] = []

        # Configuration
        self._config = {
            'min_samples_for_baseline': 10,
            'anomaly_threshold_std': 3.0,  # Standard deviations
            'observation_window': 100  # Keep last N observations
        }

    def record_observation(self, metric: str, value: float) -> Optional[Dict[str, Any]]:
        """
        Record a behavioral observation.

        Args:
            metric: Name of the metric
            value: Observed value

        Returns:
            Anomaly details if detected, None otherwise
        """
        if metric not in self._observations:
            self._observations[metric] = []

        observations = self._observations[metric]
        observations.append(value)

        # Trim to window size
        if len(observations) > self._config['observation_window']:
            observations.pop(0)

        # Update baseline if enough samples
        if len(observations) >= self._config['min_samples_for_baseline']:
            self._update_baseline(metric, observations)

            # Check for anomaly
            if metric in self._baselines:
                anomaly = self._check_anomaly(metric, value)
                if anomaly:
                    self._anomalies.append(anomaly)
                    return anomaly

        return None

    def _update_baseline(self, metric: str, observations: List[float]):
        """Update baseline for a metric."""
        if len(observations) < 2:
            return

        mean = statistics.mean(observations)
        std_dev = statistics.stdev(observations) if len(observations) > 1 else 0
        min_val = min(observations)
        max_val = max(observations)

        self._baselines[metric] = BehaviorBaseline(
            metric=metric,
            mean=mean,
            std_dev=std_dev,
            min_val=min_val,
            max_val=max_val,
            sample_count=len(observations)
        )

    def _check_anomaly(self, metric: str, value: float) -> Optional[Dict[str, Any]]:
        """Check if a value is anomalous."""
        baseline = self._baselines.get(metric)
        if not baseline or baseline.std_dev == 0:
            return None

        z_score = abs(value - baseline.mean) / baseline.std_dev

        if z_score > self._config['anomaly_threshold_std']:
            return {
                'type': 'behavioral_anomaly',
                'metric': metric,
                'value': value,
                'expected_mean': baseline.mean,
                'z_score': z_score,
                'severity': 'high' if z_score > 5 else 'medium',
                'timestamp': datetime.utcnow().isoformat()
            }

        return None

    def get_baseline(self, metric: str) -> Optional[Dict[str, Any]]:
        """Get baseline for a metric."""
        baseline = self._baselines.get(metric)
        if not baseline:
            return None

        return {
            'metric': baseline.metric,
            'mean': baseline.mean,
            'std_dev': baseline.std_dev,
            'range': [baseline.min_val, baseline.max_val],
            'samples': baseline.sample_count
        }

    def get_anomalies(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent anomalies."""
        return self._anomalies[-limit:]

    def clear_anomalies(self):
        """Clear anomaly history."""
        self._anomalies = []


class BreachDetector:
    """
    Detects potential security breaches.

    Monitors for indicators of compromise including:
    - Unusual access patterns
    - Data exfiltration attempts
    - Credential misuse
    """

    def __init__(self):
        self._indicators: List[Dict[str, Any]] = []
        self._breach_events: List[Dict[str, Any]] = []

        # Known breach indicators
        self._patterns = {
            'multiple_failed_auth': {
                'threshold': 5,
                'window_seconds': 300,
                'severity': 'high'
            },
            'unusual_data_access': {
                'threshold': 100,  # records accessed
                'window_seconds': 60,
                'severity': 'high'
            },
            'off_hours_access': {
                'hours': [0, 1, 2, 3, 4, 5],  # Midnight to 5 AM
                'severity': 'medium'
            },
            'large_export': {
                'threshold_mb': 50,
                'severity': 'high'
            }
        }

        self._event_counts: Dict[str, List[float]] = {}

    def check_indicator(self, indicator_type: str, value: Any,
                        context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Check for breach indicators.

        Args:
            indicator_type: Type of indicator to check
            value: Value to check
            context: Additional context

        Returns:
            Breach alert if detected, None otherwise
        """
        if context is None:
            context = {}

        now = datetime.utcnow()

        if indicator_type == 'failed_auth':
            return self._check_failed_auth(value, now)
        elif indicator_type == 'data_access':
            return self._check_data_access(value, now)
        elif indicator_type == 'access_time':
            return self._check_access_time(now)
        elif indicator_type == 'data_export':
            return self._check_data_export(value)

        return None

    def _check_failed_auth(self, source: str, timestamp: datetime) -> Optional[Dict[str, Any]]:
        """Check for multiple failed authentication attempts."""
        key = f'failed_auth_{source}'
        pattern = self._patterns['multiple_failed_auth']

        if key not in self._event_counts:
            self._event_counts[key] = []

        events = self._event_counts[key]
        events.append(timestamp.timestamp())

        # Remove old events outside window
        cutoff = timestamp.timestamp() - pattern['window_seconds']
        events[:] = [e for e in events if e > cutoff]

        if len(events) >= pattern['threshold']:
            breach = {
                'type': 'multiple_failed_auth',
                'source': source,
                'count': len(events),
                'window_seconds': pattern['window_seconds'],
                'severity': pattern['severity'],
                'timestamp': timestamp.isoformat()
            }
            self._breach_events.append(breach)
            return breach

        return None

    def _check_data_access(self, record_count: int, timestamp: datetime) -> Optional[Dict[str, Any]]:
        """Check for unusual data access volume."""
        pattern = self._patterns['unusual_data_access']

        if record_count >= pattern['threshold']:
            breach = {
                'type': 'unusual_data_access',
                'records_accessed': record_count,
                'threshold': pattern['threshold'],
                'severity': pattern['severity'],
                'timestamp': timestamp.isoformat()
            }
            self._breach_events.append(breach)
            return breach

        return None

    def _check_access_time(self, timestamp: datetime) -> Optional[Dict[str, Any]]:
        """Check for off-hours access."""
        pattern = self._patterns['off_hours_access']

        if timestamp.hour in pattern['hours']:
            breach = {
                'type': 'off_hours_access',
                'hour': timestamp.hour,
                'severity': pattern['severity'],
                'timestamp': timestamp.isoformat()
            }
            self._breach_events.append(breach)
            return breach

        return None

    def _check_data_export(self, size_mb: float) -> Optional[Dict[str, Any]]:
        """Check for large data exports."""
        pattern = self._patterns['large_export']

        if size_mb >= pattern['threshold_mb']:
            breach = {
                'type': 'large_export',
                'size_mb': size_mb,
                'threshold_mb': pattern['threshold_mb'],
                'severity': pattern['severity'],
                'timestamp': datetime.utcnow().isoformat()
            }
            self._breach_events.append(breach)
            return breach

        return None

    def get_breach_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent breach events."""
        return self._breach_events[-limit:]

    def get_status(self) -> Dict[str, Any]:
        """Get breach detector status."""
        high_severity = sum(
            1 for e in self._breach_events
            if e.get('severity') == 'high'
        )

        return {
            'total_events': len(self._breach_events),
            'high_severity_count': high_severity,
            'patterns_monitored': len(self._patterns)
        }
