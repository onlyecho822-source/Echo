"""
Echo Harmonic Learning - Core Module

Don't converge to stillness; converge to a pattern.
Learn by courting error, then tuning it into rhythm.
"""

from .learning_event import LearningEvent
from .correction_record import CorrectionRecord
from .harmony_scorer import HarmonyScorer
from .learning_loop import EchoHarmonicLearningLoop

__all__ = [
    'LearningEvent',
    'CorrectionRecord',
    'HarmonyScorer',
    'EchoHarmonicLearningLoop'
]
