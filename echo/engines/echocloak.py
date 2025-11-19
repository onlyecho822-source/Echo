"""
EchoCloak - Stealth Resonance Field Generator

A privacy-focused tool for obfuscating digital signals to protect identity,
data, and intention from surveillance and predictive targeting.

Purpose:
    Obfuscate digital + emotional signal of a user or device to prevent
    surveillance, manipulation, or predictive targeting.

Goals:
    - Allow presence without detection
    - Deflect AI profiling attempts
    - Conceal signal patterns from analytics systems

Warning:
    This tool is designed for legitimate privacy protection. Misuse for
    anti-forensics, malware concealment, or criminal activity is prohibited.
"""

import os
import hashlib
import hmac
import json
import random
import secrets
import time
from datetime import datetime
from typing import Any, Optional
from enum import Enum


class CloakMode(Enum):
    """Operating modes for the cloak system."""
    STEALTH = "stealth"          # Full obfuscation
    GHOST = "ghost"              # Minimal footprint
    PHANTOM = "phantom"          # Pattern disruption
    SHADOW = "shadow"            # Timing obfuscation only


class EchoCloak:
    """
    Stealth resonance field generator for privacy protection.

    Generates non-deterministic noise layers and applies cloaking
    transformations to outgoing data to prevent pattern analysis.

    Attributes:
        sig: Identity signature for the cloak instance
        noise_layer: Current noise layer hash
        mode: Operating mode for cloaking operations
        entropy_pool: Accumulated entropy for noise generation

    Example:
        >>> cloak = EchoCloak("user-12345")
        >>> cloaked = cloak.apply_cloak({"message": "hello"})
        >>> original = cloak.reveal_cloak(cloaked)
    """

    def __init__(
        self,
        identity_signature: str,
        mode: CloakMode = CloakMode.STEALTH,
        seed_entropy: Optional[bytes] = None
    ):
        """
        Initialize EchoCloak with identity signature.

        Args:
            identity_signature: Unique identifier for this cloak instance
            mode: Operating mode for cloaking operations
            seed_entropy: Optional additional entropy for noise generation
        """
        self.sig = identity_signature
        self.mode = mode
        self._seed_entropy = seed_entropy or b""
        self.entropy_pool = self._initialize_entropy_pool()
        self.noise_layer = self._generate_cloak_layer()
        self._timing_offset = self._calculate_timing_offset()
        self._fragment_key = self._generate_fragment_key()

    def _initialize_entropy_pool(self) -> bytes:
        """Initialize the entropy pool with system randomness."""
        system_entropy = os.urandom(128)
        timestamp_bytes = str(time.time_ns()).encode()
        combined = system_entropy + timestamp_bytes + self._seed_entropy
        return hashlib.sha512(combined).digest()

    def _generate_cloak_layer(self) -> str:
        """
        Generate non-deterministic noise layer based on entropy.

        Returns:
            Hex-encoded noise layer hash
        """
        # Combine multiple entropy sources
        entropy = os.urandom(64)
        timestamp = str(datetime.utcnow().isoformat()).encode()
        sig_bytes = self.sig.encode()

        # Mix with entropy pool
        mixed = entropy + timestamp + sig_bytes + self.entropy_pool

        # Generate primary hash
        primary = hashlib.sha256(mixed).digest()

        # Add secondary mixing for additional randomness
        secondary = hashlib.blake2b(
            primary + entropy,
            digest_size=32,
            salt=os.urandom(16)
        ).digest()

        return secondary.hex()

    def _calculate_timing_offset(self) -> float:
        """Calculate random timing offset for traffic analysis prevention."""
        # Generate cryptographically secure random delay (0-100ms)
        random_bytes = secrets.token_bytes(4)
        offset = int.from_bytes(random_bytes, 'big') % 100
        return offset / 1000.0

    def _generate_fragment_key(self) -> bytes:
        """Generate key for pattern fragmentation."""
        return hashlib.pbkdf2_hmac(
            'sha256',
            self.sig.encode(),
            self.entropy_pool[:16],
            iterations=10000,
            dklen=32
        )

    def regenerate_noise(self) -> str:
        """
        Regenerate the noise layer for fresh obfuscation.

        Returns:
            New noise layer hash
        """
        # Refresh entropy pool
        self.entropy_pool = self._initialize_entropy_pool()
        self.noise_layer = self._generate_cloak_layer()
        self._timing_offset = self._calculate_timing_offset()
        return self.noise_layer

    def apply_cloak(self, outgoing_data: Any) -> dict:
        """
        Apply cloaking transformation to outgoing data.

        Scrambles metadata, adds timing obfuscation, and injects
        noise to prevent pattern analysis.

        Args:
            outgoing_data: Data to be cloaked (string, dict, or serializable)

        Returns:
            Dictionary containing cloaked payload and noise layer
        """
        # Serialize data if needed
        if isinstance(outgoing_data, dict):
            serialized = json.dumps(outgoing_data, sort_keys=True)
        elif isinstance(outgoing_data, str):
            serialized = outgoing_data
        else:
            serialized = str(outgoing_data)

        # Apply transformations based on mode
        if self.mode == CloakMode.STEALTH:
            payload = self._full_obfuscation(serialized)
        elif self.mode == CloakMode.GHOST:
            payload = self._minimal_footprint(serialized)
        elif self.mode == CloakMode.PHANTOM:
            payload = self._pattern_disruption(serialized)
        elif self.mode == CloakMode.SHADOW:
            payload = serialized  # Only timing obfuscation
        else:
            payload = serialized

        # Generate metadata noise
        metadata_noise = self._generate_metadata_noise()

        # Calculate integrity hash (HMAC for verification)
        integrity = hmac.new(
            self._fragment_key,
            serialized.encode(),
            hashlib.sha256
        ).hexdigest()

        return {
            "payload": payload,
            "noise": self.noise_layer,
            "timing_offset": self._timing_offset,
            "metadata": metadata_noise,
            "integrity": integrity,
            "mode": self.mode.value,
            "timestamp": time.time_ns()
        }

    def _full_obfuscation(self, data: str) -> str:
        """Apply full obfuscation transformation."""
        # XOR with noise layer (reversible)
        noise_bytes = bytes.fromhex(self.noise_layer)
        data_bytes = data.encode()

        obfuscated = bytearray()
        for i, byte in enumerate(data_bytes):
            obfuscated.append(byte ^ noise_bytes[i % len(noise_bytes)])

        return obfuscated.hex()

    def _minimal_footprint(self, data: str) -> str:
        """Apply minimal footprint transformation."""
        # Simple reversible transformation
        return data[::-1]

    def _pattern_disruption(self, data: str) -> str:
        """Apply pattern disruption transformation."""
        # Fragment and shuffle (deterministically based on key)
        if len(data) < 4:
            return data[::-1]

        # Split into chunks
        chunk_size = max(1, len(data) // 4)
        chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

        # Generate deterministic shuffle order from fragment key
        random.seed(int.from_bytes(self._fragment_key[:8], 'big'))
        indices = list(range(len(chunks)))
        random.shuffle(indices)

        # Store shuffle map for reversal
        shuffled = ''.join(chunks[i] for i in indices)
        shuffle_map = ','.join(map(str, indices))

        return f"{shuffle_map}|{shuffled}"

    def _generate_metadata_noise(self) -> dict:
        """Generate fake metadata to confuse analytics."""
        fake_agents = [
            "Mozilla/5.0 (compatible; Resonance/1.0)",
            "EchoBot/2.1 (Privacy Mode)",
            "Signal/3.0 (Stealth)",
        ]

        return {
            "agent": secrets.choice(fake_agents),
            "session": secrets.token_hex(16),
            "entropy_marker": hashlib.md5(os.urandom(16)).hexdigest(),
            "decoy_timestamp": time.time() + random.uniform(-3600, 3600)
        }

    def reveal_cloak(self, cloaked_data: dict) -> Any:
        """
        Remove cloaking and reveal original data.

        Args:
            cloaked_data: Previously cloaked data dictionary

        Returns:
            Original uncloaked data

        Raises:
            ValueError: If integrity check fails or data is corrupted
        """
        payload = cloaked_data.get("payload", "")
        mode = CloakMode(cloaked_data.get("mode", "stealth"))

        # Reverse transformation based on mode
        if mode == CloakMode.STEALTH:
            revealed = self._reverse_full_obfuscation(payload)
        elif mode == CloakMode.GHOST:
            revealed = payload[::-1]
        elif mode == CloakMode.PHANTOM:
            revealed = self._reverse_pattern_disruption(payload)
        elif mode == CloakMode.SHADOW:
            revealed = payload
        else:
            revealed = payload

        # Verify integrity
        stored_integrity = cloaked_data.get("integrity", "")
        calculated_integrity = hmac.new(
            self._fragment_key,
            revealed.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(stored_integrity, calculated_integrity):
            raise ValueError("Integrity check failed - data may be corrupted or tampered")

        # Try to deserialize as JSON
        try:
            return json.loads(revealed)
        except json.JSONDecodeError:
            return revealed

    def _reverse_full_obfuscation(self, payload: str) -> str:
        """Reverse full obfuscation transformation."""
        noise_bytes = bytes.fromhex(self.noise_layer)
        obfuscated_bytes = bytes.fromhex(payload)

        revealed = bytearray()
        for i, byte in enumerate(obfuscated_bytes):
            revealed.append(byte ^ noise_bytes[i % len(noise_bytes)])

        return revealed.decode()

    def _reverse_pattern_disruption(self, payload: str) -> str:
        """Reverse pattern disruption transformation."""
        if '|' not in payload:
            return payload[::-1]

        shuffle_map_str, shuffled = payload.split('|', 1)
        indices = list(map(int, shuffle_map_str.split(',')))

        # Calculate chunk size
        chunk_size = len(shuffled) // len(indices)
        if len(shuffled) % len(indices):
            chunk_size += 1

        chunks = [shuffled[i:i+chunk_size] for i in range(0, len(shuffled), chunk_size)]

        # Reverse the shuffle
        original_chunks = [''] * len(indices)
        for new_idx, orig_idx in enumerate(indices):
            if new_idx < len(chunks):
                original_chunks[orig_idx] = chunks[new_idx]

        return ''.join(original_chunks)

    def get_field_strength(self) -> dict:
        """
        Get current cloak field strength metrics.

        Returns:
            Dictionary of field strength indicators
        """
        return {
            "entropy_level": len(self.entropy_pool) * 8,  # bits
            "noise_complexity": len(set(self.noise_layer)) / 16,  # 0-1 scale
            "timing_variance": self._timing_offset * 1000,  # ms
            "mode": self.mode.value,
            "signature_hash": hashlib.sha256(self.sig.encode()).hexdigest()[:16]
        }

    def __repr__(self) -> str:
        return f"EchoCloak(sig='{self.sig[:8]}...', mode={self.mode.value})"
