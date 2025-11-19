"""Source collectors for the Echo Reverse Engineering Engine."""

from echo_engine.collectors.base import BaseCollector
from echo_engine.collectors.text import TextCollector
from echo_engine.collectors.file import FileCollector
from echo_engine.collectors.web import WebCollector

__all__ = [
    "BaseCollector",
    "TextCollector",
    "FileCollector",
    "WebCollector",
]
