"""Text processing utilities."""

import re
from typing import Optional


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.

    - Converts to lowercase
    - Removes extra whitespace
    - Removes punctuation
    """
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()


def extract_sentences(text: str) -> list[str]:
    """
    Extract sentences from text.

    Handles common abbreviations and sentence boundaries.
    """
    # Protect abbreviations
    text = re.sub(r'\bMr\.', 'Mr', text)
    text = re.sub(r'\bMrs\.', 'Mrs', text)
    text = re.sub(r'\bDr\.', 'Dr', text)
    text = re.sub(r'\bvs\.', 'vs', text)
    text = re.sub(r'\betc\.', 'etc', text)
    text = re.sub(r'\be\.g\.', 'eg', text)
    text = re.sub(r'\bi\.e\.', 'ie', text)

    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)

    return [s.strip() for s in sentences if s.strip()]


def extract_entities(text: str) -> list[str]:
    """
    Extract named entities from text.

    Uses simple heuristics to identify:
    - Capitalized words (proper nouns)
    - Quoted strings
    - Numbers with units
    """
    entities = []

    # Capitalized words (likely proper nouns)
    words = text.split()
    for i, word in enumerate(words):
        clean = word.strip('.,!?;:\'"()[]{}')
        if clean and clean[0].isupper() and len(clean) > 1:
            # Skip first word unless it looks like a name
            if i == 0:
                if len(clean) > 3 and not clean.lower() in ['this', 'that', 'these', 'those']:
                    entities.append(clean)
            else:
                entities.append(clean)

    # Quoted strings
    quoted = re.findall(r'"([^"]+)"', text)
    entities.extend(quoted)

    # Single-quoted strings
    single_quoted = re.findall(r"'([^']+)'", text)
    entities.extend(single_quoted)

    # Numbers with common units
    numbers = re.findall(r'\d+(?:\.\d+)?\s*(?:percent|%|dollars|\$|years|days|hours|minutes)', text, re.I)
    entities.extend(numbers)

    return list(set(entities))


def extract_keywords(
    text: str,
    max_keywords: int = 15,
    min_length: int = 3,
) -> list[str]:
    """
    Extract keywords from text.

    Filters out common stop words and returns unique keywords.
    """
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'shall',
        'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
        'as', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'between', 'under', 'again', 'further', 'then', 'once',
        'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
        'can', 'just', 'now', 'and', 'but', 'or', 'if', 'that',
        'this', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
    }

    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [
        w for w in words
        if w not in stop_words and len(w) >= min_length
    ]

    # Return unique keywords maintaining order
    seen = set()
    unique = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique.append(kw)

    return unique[:max_keywords]


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts.

    Uses Jaccard similarity on word sets.
    """
    words1 = set(normalize_text(text1).split())
    words2 = set(normalize_text(text2).split())

    if not words1 or not words2:
        return 0.0

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


def find_common_phrases(texts: list[str], min_length: int = 3) -> list[str]:
    """
    Find common phrases across multiple texts.

    Returns phrases that appear in multiple texts.
    """
    from collections import Counter

    all_phrases = []

    for text in texts:
        words = normalize_text(text).split()
        # Extract n-grams
        for n in range(min_length, min(6, len(words) + 1)):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i + n])
                all_phrases.append(phrase)

    # Count occurrences
    phrase_counts = Counter(all_phrases)

    # Return phrases appearing more than once
    common = [phrase for phrase, count in phrase_counts.items() if count > 1]

    # Sort by frequency then length
    common.sort(key=lambda p: (-phrase_counts[p], -len(p.split())))

    return common[:20]


def highlight_matches(
    text: str,
    keywords: list[str],
    marker: str = "**"
) -> str:
    """
    Highlight keyword matches in text.

    Wraps matched keywords with markers (default: markdown bold).
    """
    result = text

    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        result = pattern.sub(f"{marker}{keyword}{marker}", result)

    return result


def truncate_text(
    text: str,
    max_length: int = 200,
    suffix: str = "..."
) -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def character_count(text: str, include_spaces: bool = True) -> int:
    """Count characters in text."""
    if include_spaces:
        return len(text)
    return len(text.replace(' ', ''))
