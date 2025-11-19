"""
Helper utility functions.
"""

import re
from datetime import datetime


def format_timestamp(seconds: float) -> str:
    """
    Format seconds into HH:MM:SS or MM:SS format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def sanitize_text(text: str) -> str:
    """
    Clean and sanitize text for processing.

    Args:
        text: Input text

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')

    return text.strip()


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Input text
        max_length: Maximum characters
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix


def calculate_word_count(text: str) -> int:
    """
    Count words in text.

    Args:
        text: Input text

    Returns:
        Word count
    """
    if not text:
        return 0
    return len(text.split())


def extract_urls(text: str) -> list[str]:
    """
    Extract URLs from text.

    Args:
        text: Input text

    Returns:
        List of URLs found
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def format_file_size(bytes_size: int) -> str:
    """
    Format bytes into human readable size.

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"
