"""
Service modules for Echo Fact-Check.
"""

from app.services.audio_processor import AudioProcessor
from app.services.video_processor import VideoProcessor
from app.services.document_processor import DocumentProcessor
from app.services.fact_checker import FactChecker
from app.services.claim_extractor import ClaimExtractor

__all__ = [
    "AudioProcessor",
    "VideoProcessor",
    "DocumentProcessor",
    "FactChecker",
    "ClaimExtractor",
]
