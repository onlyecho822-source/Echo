"""
EchoLex Services Module

Core services for legal research operations.
"""

from echolex.services.legal_research import LegalResearchService
from echolex.services.notification import NotificationService

__all__ = [
    "LegalResearchService",
    "NotificationService",
]
