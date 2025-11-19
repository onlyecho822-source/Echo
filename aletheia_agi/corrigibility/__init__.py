"""
Corrigibility Module - Shutdown and Override Mechanisms
=======================================================

Ensures the system remains interruptible and deferential to human oversight,
with tripwires for distributional shift and incentives aligned with deference.
"""

from .corrigibility_engine import CorrigibilityEngine
from .shutdown_protocol import ShutdownProtocol
from .override_channel import OverrideChannel

__all__ = ['CorrigibilityEngine', 'ShutdownProtocol', 'OverrideChannel']
