"""
EchoLex Prediction Models

Machine learning models for legal outcome prediction.

DISCLAIMER: Predictions are for RESEARCH PURPOSES ONLY and should not
be used as the sole basis for legal decisions. Always consult with
a licensed attorney.
"""

from echolex.predictions.case_predictor import CasePredictor
from echolex.predictions.sentence_predictor import SentencePredictor
from echolex.predictions.appeal_predictor import AppealPredictor

__all__ = [
    "CasePredictor",
    "SentencePredictor",
    "AppealPredictor",
]
