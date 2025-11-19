"""
EchoLex Legal Domain Models

Core data models for legal research and analysis.
"""

from echolex.models.case import Case, CaseType, CaseSeverity, CaseStatus, CaseOutcome
from echolex.models.judge import Judge, JudgeScorecard, BenchMetrics
from echolex.models.jurisdiction import Jurisdiction, JurisdictionLevel, Court
from echolex.models.legal_precedent import LegalPrecedent, PrecedentType
from echolex.models.party import Party, PartyType, Attorney

__all__ = [
    "Case",
    "CaseType",
    "CaseSeverity",
    "CaseStatus",
    "CaseOutcome",
    "Judge",
    "JudgeScorecard",
    "BenchMetrics",
    "Jurisdiction",
    "JurisdictionLevel",
    "Court",
    "LegalPrecedent",
    "PrecedentType",
    "Party",
    "PartyType",
    "Attorney",
]
