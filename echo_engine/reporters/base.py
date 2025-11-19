"""Base reporter class."""

from abc import ABC, abstractmethod
from typing import Optional
from echo_engine.core.models import Investigation


class BaseReporter(ABC):
    """Abstract base class for report generators."""

    def __init__(self, config: Optional[dict] = None):
        """Initialize reporter with optional configuration."""
        self.config = config or {}

    @abstractmethod
    def generate(self, investigation: Investigation) -> str:
        """
        Generate a report for an investigation.

        Args:
            investigation: The investigation to report on

        Returns:
            The generated report as a string
        """
        pass

    @abstractmethod
    def save(self, investigation: Investigation, filepath: str) -> None:
        """
        Save a report to a file.

        Args:
            investigation: The investigation to report on
            filepath: Path to save the report
        """
        pass

    def get_summary_stats(self, investigation: Investigation) -> dict:
        """Get summary statistics for an investigation."""
        return {
            "total_sources": len(investigation.sources),
            "total_facts": len(investigation.facts),
            "verified_facts": len(investigation.get_verified_facts()),
            "disputed_facts": len(investigation.get_disputed_facts()),
            "total_connections": len(investigation.connections),
            "total_timelines": len(investigation.timelines),
            "provenance_chains": len(investigation.provenance_chains),
        }
