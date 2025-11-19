"""Text collector for direct text input."""

from datetime import datetime
from typing import Optional
from echo_engine.collectors.base import BaseCollector
from echo_engine.core.models import Source, SourceType


class TextCollector(BaseCollector):
    """Collector for direct text input."""

    def collect(
        self,
        content: str,
        name: str = "Text Input",
        author: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[dict] = None,
    ) -> Source:
        """
        Collect text as a source.

        Args:
            content: The text content
            name: Name/title for this source
            author: Optional author
            timestamp: Optional timestamp
            metadata: Additional metadata

        Returns:
            A Source object
        """
        if not self.validate_input(content):
            raise ValueError("Invalid text input")

        processed_content = self.preprocess(content)

        return Source(
            name=name,
            source_type=self.get_source_type(),
            content=processed_content,
            author=author,
            timestamp=timestamp or datetime.now(),
            metadata=metadata or {},
        )

    def validate_input(self, content: str) -> bool:
        """Validate text input."""
        return isinstance(content, str) and len(content.strip()) > 0

    def get_source_type(self) -> SourceType:
        """Get source type."""
        return SourceType.TEXT

    def collect_multiple(
        self,
        texts: list[tuple[str, str]],  # List of (content, name) tuples
        author: Optional[str] = None,
    ) -> list[Source]:
        """
        Collect multiple text sources.

        Args:
            texts: List of (content, name) tuples
            author: Optional common author

        Returns:
            List of Source objects
        """
        sources = []
        for content, name in texts:
            source = self.collect(content, name=name, author=author)
            sources.append(source)
        return sources
