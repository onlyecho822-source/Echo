"""Web collector for URL-based sources."""

import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse
from echo_engine.collectors.base import BaseCollector
from echo_engine.core.models import Source, SourceType
from echo_engine.core.exceptions import CollectionError


class WebCollector(BaseCollector):
    """
    Collector for web-based sources.

    Note: This is a framework implementation. For actual web scraping,
    you would need to install additional dependencies like requests
    and beautifulsoup4.
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize web collector."""
        super().__init__(config)
        self.user_agent = config.get(
            "user_agent",
            "Echo-Engine/0.1 (Research Bot)"
        ) if config else "Echo-Engine/0.1 (Research Bot)"
        self.timeout = config.get("timeout", 30) if config else 30

    def collect(
        self,
        url: str,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Source:
        """
        Collect content from a URL.

        Args:
            url: The URL to collect from
            name: Optional name (defaults to URL domain)
            metadata: Additional metadata

        Returns:
            A Source object

        Note:
            This is a placeholder implementation. For production use,
            integrate with requests/beautifulsoup or similar libraries.
        """
        if not self.validate_input(url):
            raise CollectionError(f"Invalid URL: {url}")

        parsed = urlparse(url)

        # Placeholder content - in production, this would fetch actual content
        content = self._fetch_content(url)

        source_metadata = {
            "url": url,
            "domain": parsed.netloc,
            "scheme": parsed.scheme,
            **(metadata or {}),
        }

        return Source(
            name=name or parsed.netloc,
            source_type=self.get_source_type(),
            content=content,
            url=url,
            timestamp=datetime.now(),
            metadata=source_metadata,
        )

    def _fetch_content(self, url: str) -> str:
        """
        Fetch content from URL.

        This is a placeholder that returns a message about the URL.
        In production, this would use requests/beautifulsoup.
        """
        try:
            # Try to import requests if available
            import urllib.request

            req = urllib.request.Request(
                url,
                headers={"User-Agent": self.user_agent}
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content = response.read().decode("utf-8", errors="ignore")

            # Basic HTML tag removal
            content = self._strip_html(content)
            return content

        except ImportError:
            return f"[Content from {url} - install requests for actual fetching]"
        except Exception as e:
            raise CollectionError(f"Failed to fetch URL: {e}")

    def _strip_html(self, html: str) -> str:
        """Strip HTML tags from content."""
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        html = re.sub(r'<[^>]+>', ' ', html)

        # Clean up whitespace
        html = re.sub(r'\s+', ' ', html)

        return html.strip()

    def validate_input(self, url: str) -> bool:
        """Validate URL."""
        if not url:
            return False

        try:
            parsed = urlparse(url)
            return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
        except Exception:
            return False

    def get_source_type(self) -> SourceType:
        """Get source type."""
        return SourceType.WEB

    def collect_multiple(
        self,
        urls: list[str],
        metadata: Optional[dict] = None,
    ) -> list[Source]:
        """
        Collect from multiple URLs.

        Args:
            urls: List of URLs
            metadata: Common metadata for all sources

        Returns:
            List of Source objects
        """
        sources = []
        for url in urls:
            try:
                source = self.collect(url, metadata=metadata)
                sources.append(source)
            except CollectionError:
                continue
        return sources
