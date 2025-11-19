"""
Cryptographic Utilities
=======================

Provides cryptographic functions for integrity verification,
signing, and hashing throughout the framework.
"""

import hashlib
import hmac
import secrets
from typing import Tuple


def hash_content(content: str, algorithm: str = 'sha256') -> str:
    """
    Generate cryptographic hash of content.

    Args:
        content: Content to hash
        algorithm: Hash algorithm (sha256, sha384, sha512)

    Returns:
        Hexadecimal hash string
    """
    if algorithm == 'sha256':
        return hashlib.sha256(content.encode()).hexdigest()
    elif algorithm == 'sha384':
        return hashlib.sha384(content.encode()).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(content.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def sign_data(data: str, secret_key: str) -> str:
    """
    Create HMAC signature for data.

    Args:
        data: Data to sign
        secret_key: Secret key for signing

    Returns:
        Hexadecimal signature string
    """
    return hmac.new(
        secret_key.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()


def verify_signature(data: str, signature: str, secret_key: str) -> bool:
    """
    Verify HMAC signature.

    Args:
        data: Original data
        signature: Signature to verify
        secret_key: Secret key

    Returns:
        True if signature is valid
    """
    expected = sign_data(data, secret_key)
    return hmac.compare_digest(expected, signature)


def generate_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure random key.

    Args:
        length: Key length in bytes

    Returns:
        Hexadecimal key string
    """
    return secrets.token_hex(length)


def generate_id() -> str:
    """
    Generate a cryptographically secure random ID.

    Returns:
        URL-safe ID string
    """
    return secrets.token_urlsafe(16)


def hash_chain(items: list, previous_hash: str = "genesis") -> str:
    """
    Create a hash chain from a list of items.

    Args:
        items: List of items to chain
        previous_hash: Starting hash value

    Returns:
        Final hash in chain
    """
    current_hash = previous_hash
    for item in items:
        content = f"{current_hash}:{str(item)}"
        current_hash = hash_content(content)
    return current_hash


def merkle_root(items: list) -> str:
    """
    Calculate Merkle root for a list of items.

    Args:
        items: List of items

    Returns:
        Merkle root hash
    """
    if not items:
        return hash_content("")

    # Hash all items
    hashes = [hash_content(str(item)) for item in items]

    # Build tree
    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])  # Duplicate last if odd

        new_hashes = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i + 1]
            new_hashes.append(hash_content(combined))
        hashes = new_hashes

    return hashes[0]
