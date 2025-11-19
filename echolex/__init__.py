"""
EchoLex - Global Legal Research Engine

A comprehensive legal research platform providing:
- Case analysis across all legal domains (traffic violations to capital offenses)
- Judge scorecards with bench follow-rate analytics
- Predictive models for case outcomes
- Real-time legal updates and notifications

DISCLAIMER: This system is for RESEARCH PURPOSES ONLY.
It does not constitute legal advice. Always consult a licensed attorney
for legal matters in your jurisdiction.
"""

__version__ = "1.0.0"
__author__ = "Echo Civilization"
__license__ = "MIT"

from echolex.models.case import Case, CaseType, CaseSeverity
from echolex.models.judge import Judge, JudgeScorecard
from echolex.models.jurisdiction import Jurisdiction
from echolex.analytics.judge_analytics import JudgeAnalytics
from echolex.predictions.case_predictor import CasePredictor

__all__ = [
    "Case",
    "CaseType",
    "CaseSeverity",
    "Judge",
    "JudgeScorecard",
    "Jurisdiction",
    "JudgeAnalytics",
    "CasePredictor",
]
