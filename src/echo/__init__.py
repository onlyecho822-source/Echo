"""
Echo Phoenix - Verified Data Translation Framework

A pragmatic implementation of multi-protocol data translation
with cryptographic verification and content addressing.
"""

__version__ = "0.1.0"

from echo.core.translator import Translator
from echo.core.verifier import Verifier, ContentHash
from echo.core.registry import SourceRegistry, Source
from echo.models.schema import EchoMessage, DataPayload

__all__ = [
    "Translator",
    "Verifier",
    "ContentHash",
    "SourceRegistry",
    "Source",
    "EchoMessage",
    "DataPayload",
]
