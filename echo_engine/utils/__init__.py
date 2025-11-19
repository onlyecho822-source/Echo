"""Utility functions for the Echo Reverse Engineering Engine."""

from echo_engine.utils.text_processing import (
    normalize_text,
    extract_sentences,
    extract_entities,
    calculate_similarity,
)
from echo_engine.utils.hashing import (
    hash_content,
    hash_file,
    generate_id,
)

__all__ = [
    "normalize_text",
    "extract_sentences",
    "extract_entities",
    "calculate_similarity",
    "hash_content",
    "hash_file",
    "generate_id",
]
