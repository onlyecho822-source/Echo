"""Hashing and ID generation utilities."""

import hashlib
import uuid
from pathlib import Path


def hash_content(content: str, algorithm: str = "sha256") -> str:
    """
    Generate a hash of content.

    Args:
        content: The content to hash
        algorithm: Hash algorithm (sha256, md5, sha1)

    Returns:
        Hexadecimal hash string
    """
    if algorithm == "sha256":
        return hashlib.sha256(content.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(content.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(content.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def hash_file(filepath: str, algorithm: str = "sha256") -> str:
    """
    Generate a hash of a file's contents.

    Args:
        filepath: Path to the file
        algorithm: Hash algorithm

    Returns:
        Hexadecimal hash string
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    # Read in chunks for large files
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def generate_id() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """Generate a short unique identifier."""
    return str(uuid.uuid4())[:length]


def content_fingerprint(content: str) -> str:
    """
    Generate a content fingerprint.

    Creates a unique identifier based on content that can be used
    to detect duplicates.
    """
    # Normalize content
    normalized = content.lower()
    normalized = ' '.join(normalized.split())  # Normalize whitespace

    return hash_content(normalized)[:16]


def compare_hashes(hash1: str, hash2: str) -> bool:
    """
    Compare two hashes in constant time.

    Uses constant-time comparison to prevent timing attacks.
    """
    import hmac
    return hmac.compare_digest(hash1, hash2)
