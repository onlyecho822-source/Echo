"""
Defense Wall - Security and Privacy Protection

The Defense Wall provides:
- Identity protection
- Risk mapping
- Privacy enforcement
- Fraud detection
- Leak detection
- Emergency controls
"""

from .defense_wall import DefenseWall
from .monitors import BehaviorMonitor, BreachDetector

__all__ = ['DefenseWall', 'BehaviorMonitor', 'BreachDetector']
