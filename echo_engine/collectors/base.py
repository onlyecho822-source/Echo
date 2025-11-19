"""Base collector class for all source collectors."""

from abc import ABC, abstractmethod
from typing import Optional
from echo_engine.core.models import Source, SourceType


class BaseCollector(ABC):
    """
    Abstract base class for all source collectors.

    Collectors are responsible for gathering information from
    various sources and converting them into Source objects.
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize collector with optional configuration."""
        self.config = config or {}

    @abstractmethod
    def collect(self, *args, **kwargs) -> Source:
        """
        Collect a source.

        Returns:
            A Source object containing the collected information
        """
        pass

    @abstractmethod
    def validate_input(self, *args, **kwargs) -> bool:
        """
        Validate that the input can be collected.

        Returns:
            True if input is valid, False otherwise
        """
        pass

    def get_source_type(self) -> SourceType:
        """Get the type of source this collector produces."""
        return SourceType.UNKNOWN

    def preprocess(self, content: str) -> str:
        """
        Preprocess collected content.

        Override this method to add custom preprocessing.
        """
        # Remove excessive whitespace
        lines = content.split('\n')
        cleaned_lines = [' '.join(line.split()) for line in lines]
        return '\n'.join(cleaned_lines)
