"""
ECHO ORGANISM v2.1 - MILITARY MONITORING SYSTEM
Classification: PRODUCTION-READY

Real-time monitoring for:
- System performance (CPU, memory)
- Organism health metrics
- Stability indicators
- Alert management
"""

import numpy as np
import time
import logging
from typing import Dict, Any, List, Optional
from collections import deque
from enum import Enum

# Try to import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    GREEN = "GREEN"       # Normal operations
    YELLOW = "YELLOW"     # Caution advised
    ORANGE = "ORANGE"     # Significant concern
    RED = "RED"           # Critical situation


class MonitoringSystem:
    """
    Production-grade monitoring for Echo Organism.

    Features:
    - Real-time system metrics
    - Organism health tracking
    - Alert management
    - Performance history
    """

    def __init__(self):
        self.step_times: deque = deque(maxlen=100)
        self.metrics_history: deque = deque(maxlen=1000)
        self.alerts: deque = deque(maxlen=100)

        # Thresholds
        self.thresholds = {
            'cpu_usage': 0.85,
            'memory_usage': 0.90,
            'step_duration': 1.0,
            'error_rate': 0.05,
            'energy_variance': 5.0,  # Increased for normal exploration
            'stress_level': 0.8,
            'novelty_collapse': 0.05,
            'gradient_explosion': 5.0
        }

        self.current_alert_level = AlertLevel.GREEN

        logger.info("MonitoringSystem initialized")

    def monitor_step(self, organism, step_start_time: float) -> Dict[str, Any]:
        """
        Monitor a single organism step.

        Args:
            organism: Echo organism instance
            step_start_time: Time when step began

        Returns:
            Monitoring report
        """
        step_duration = time.time() - step_start_time
        self.step_times.append(step_duration)

        # Collect metrics
        metrics = {
            'timestamp': time.time(),
            'step': organism.step_count,
            'step_duration': step_duration,
            'system': self._get_system_metrics(),
            'organism': self._get_organism_metrics(organism),
            'stability': self._get_stability_metrics(organism)
        }

        # Check for alerts
        alerts = self._check_thresholds(metrics)
        if alerts:
            for alert in alerts:
                self._raise_alert(alert)

        # Update alert level
        self.current_alert_level = self._compute_alert_level(alerts)

        metrics['alerts'] = alerts
        metrics['alert_level'] = self.current_alert_level.value

        self.metrics_history.append(metrics)

        return metrics

    def _get_system_metrics(self) -> Dict[str, float]:
        """Get system performance metrics"""
        if not PSUTIL_AVAILABLE:
            return {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'available': False
            }

        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'available': True
            }
        except Exception as e:
            logger.warning(f"System metrics failed: {e}")
            return {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'available': False
            }

    def _get_organism_metrics(self, organism) -> Dict[str, Any]:
        """Get organism-specific metrics"""
        metrics = {
            'resources': float(np.mean(organism.h.resources)),
            'stress': float(np.mean(organism.h.stress)),
            'gains': float(np.mean(organism.h.gains)),
        }

        # Recent averages if available
        if hasattr(organism, 'metrics_history'):
            if organism.metrics_history.get('novelty'):
                metrics['novelty'] = float(np.mean(organism.metrics_history['novelty'][-10:]))
            if organism.metrics_history.get('coherence'):
                metrics['coherence'] = float(np.mean(organism.metrics_history['coherence'][-10:]))
            if organism.metrics_history.get('global_energy'):
                metrics['energy'] = float(organism.metrics_history['global_energy'][-1])

        return metrics

    def _get_stability_metrics(self, organism) -> Dict[str, Any]:
        """Get stability indicators"""
        metrics = {}

        if hasattr(organism, 'metrics_history'):
            # Novelty stability
            if organism.metrics_history.get('novelty') and len(organism.metrics_history['novelty']) > 5:
                novelty_values = organism.metrics_history['novelty'][-20:]
                metrics['novelty_mean'] = float(np.mean(novelty_values))
                metrics['novelty_std'] = float(np.std(novelty_values))
                metrics['novelty_collapsed'] = metrics['novelty_mean'] < self.thresholds['novelty_collapse']

            # Energy stability
            if organism.metrics_history.get('global_energy') and len(organism.metrics_history['global_energy']) > 5:
                energy_values = organism.metrics_history['global_energy'][-20:]
                metrics['energy_variance'] = float(np.var(energy_values))
                metrics['energy_trend'] = float(np.mean(np.diff(energy_values[-10:])))

            # Gradient stability
            if organism.metrics_history.get('gradient_norms') and len(organism.metrics_history['gradient_norms']) > 5:
                grad_norms = organism.metrics_history['gradient_norms'][-20:]
                metrics['gradient_mean'] = float(np.mean(grad_norms))
                metrics['gradient_max'] = float(np.max(grad_norms))

        return metrics

    def _check_thresholds(self, metrics: Dict[str, Any]) -> List[str]:
        """Check metrics against thresholds and return alerts"""
        alerts = []

        # System checks
        sys_metrics = metrics.get('system', {})
        if sys_metrics.get('cpu_percent', 0) > self.thresholds['cpu_usage'] * 100:
            alerts.append("HIGH_CPU_USAGE")
        if sys_metrics.get('memory_percent', 0) > self.thresholds['memory_usage'] * 100:
            alerts.append("HIGH_MEMORY_USAGE")

        # Step duration
        if metrics.get('step_duration', 0) > self.thresholds['step_duration']:
            alerts.append("SLOW_STEP_EXECUTION")

        # Organism checks
        org_metrics = metrics.get('organism', {})
        if org_metrics.get('stress', 0) > self.thresholds['stress_level']:
            alerts.append("HIGH_STRESS_LEVEL")

        # Stability checks
        stab_metrics = metrics.get('stability', {})
        if stab_metrics.get('novelty_collapsed', False):
            alerts.append("NOVELTY_COLLAPSE")
        if stab_metrics.get('energy_variance', 0) > self.thresholds['energy_variance']:
            alerts.append("ENERGY_INSTABILITY")
        if stab_metrics.get('gradient_max', 0) > self.thresholds['gradient_explosion']:
            alerts.append("GRADIENT_EXPLOSION")

        return alerts

    def _compute_alert_level(self, alerts: List[str]) -> AlertLevel:
        """Compute overall alert level from current alerts"""
        if not alerts:
            return AlertLevel.GREEN

        critical_alerts = ['NOVELTY_COLLAPSE', 'GRADIENT_EXPLOSION', 'HIGH_MEMORY_USAGE']
        warning_alerts = ['HIGH_CPU_USAGE', 'SLOW_STEP_EXECUTION', 'ENERGY_INSTABILITY']

        critical_count = sum(1 for a in alerts if a in critical_alerts)
        warning_count = sum(1 for a in alerts if a in warning_alerts)

        if critical_count >= 2:
            return AlertLevel.RED
        elif critical_count >= 1:
            return AlertLevel.ORANGE
        elif warning_count >= 2:
            return AlertLevel.YELLOW
        else:
            return AlertLevel.GREEN

    def _raise_alert(self, alert: str):
        """Record an alert"""
        self.alerts.append({
            'timestamp': time.time(),
            'alert': alert,
            'level': self.current_alert_level.value
        })
        logger.warning(f"ALERT: {alert}")

    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary"""
        if not self.metrics_history:
            return {}

        # Aggregate over history
        step_times = [m['step_duration'] for m in self.metrics_history]
        cpu_usage = [m['system'].get('cpu_percent', 0) for m in self.metrics_history]

        return {
            'total_steps': len(self.metrics_history),
            'avg_step_time': np.mean(step_times),
            'max_step_time': np.max(step_times),
            'avg_cpu_usage': np.mean(cpu_usage),
            'total_alerts': len(self.alerts),
            'current_alert_level': self.current_alert_level.value
        }

    def get_health_score(self) -> float:
        """Compute overall system health score (0-1)"""
        if not self.metrics_history:
            return 1.0

        recent = list(self.metrics_history)[-20:]

        # Components
        step_time_score = 1.0 - min(1.0, np.mean([m['step_duration'] for m in recent]) / self.thresholds['step_duration'])
        alert_score = 1.0 - min(1.0, len([m for m in recent if m.get('alerts')]) / len(recent))

        # Organism health
        org_scores = []
        for m in recent:
            org = m.get('organism', {})
            stress = org.get('stress', 0.5)
            resources = org.get('resources', 0.5)
            org_scores.append((1.0 - stress) * resources)

        org_health = np.mean(org_scores) if org_scores else 0.5

        # Weighted combination
        health = 0.3 * step_time_score + 0.3 * alert_score + 0.4 * org_health

        return np.clip(health, 0.0, 1.0)
