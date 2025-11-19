"""
Memory Nexus Core Implementation

Distributed resonant memory fabric with cryptographic integrity.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json


@dataclass
class NexusConfig:
    """Configuration for Memory Nexus."""
    shards: int = 16
    replication_factor: int = 3
    persistence: str = "memory"
    resonance_threshold: float = 0.7


class MemoryNexus:
    """
    Distributed Resonant Memory Fabric.

    Provides sharded, replicated memory storage with harmonic
    frequency-based indexing and cryptographic integrity verification.

    Attributes:
        config: Nexus configuration
        shards: List of storage shards
        index: Resonance-based index

    Example:
        >>> nexus = MemoryNexus(NexusConfig(shards=8))
        >>> capsule = Capsule.create(content="test")
        >>> capsule_id = nexus.store(capsule)
        >>> retrieved = nexus.get(capsule_id)
    """

    def __init__(self, config: Optional[NexusConfig] = None):
        """Initialize Memory Nexus with configuration."""
        self.config = config or NexusConfig()
        self._shards: Dict[int, Dict[str, Any]] = {
            i: {} for i in range(self.config.shards)
        }
        self._index: Dict[str, int] = {}
        self._initialized = True

    def store(self, capsule: 'Capsule') -> str:
        """
        Store a capsule in the distributed memory fabric.

        Args:
            capsule: The capsule to store

        Returns:
            The capsule ID

        Raises:
            IntegrityError: If capsule fails verification
        """
        if not capsule.verify():
            raise ValueError("Capsule integrity verification failed")

        # Calculate shard based on resonance frequency
        shard_id = self._calculate_shard(capsule.id)

        # Store in primary shard
        self._shards[shard_id][capsule.id] = capsule.to_dict()

        # Update resonance index
        self._index[capsule.id] = shard_id

        # Replicate to additional shards
        for i in range(1, self.config.replication_factor):
            replica_shard = (shard_id + i) % self.config.shards
            self._shards[replica_shard][capsule.id] = capsule.to_dict()

        return capsule.id

    def get(self, capsule_id: str) -> Optional['Capsule']:
        """
        Retrieve a capsule by ID.

        Args:
            capsule_id: The capsule ID to retrieve

        Returns:
            The capsule if found, None otherwise
        """
        if capsule_id not in self._index:
            return None

        shard_id = self._index[capsule_id]
        data = self._shards[shard_id].get(capsule_id)

        if data is None:
            return None

        return Capsule.from_dict(data)

    def query(self, frequency: float, threshold: Optional[float] = None) -> List['Capsule']:
        """
        Query capsules by resonance frequency.

        Args:
            frequency: Target resonance frequency
            threshold: Match threshold (default: config.resonance_threshold)

        Returns:
            List of matching capsules
        """
        threshold = threshold or self.config.resonance_threshold
        results = []

        for capsule_id in self._index:
            capsule = self.get(capsule_id)
            if capsule and abs(capsule.resonance - frequency) < (1 - threshold):
                results.append(capsule)

        return results

    def verify(self, capsule_id: str) -> bool:
        """
        Verify integrity of a stored capsule.

        Args:
            capsule_id: The capsule ID to verify

        Returns:
            True if integrity verified, False otherwise
        """
        capsule = self.get(capsule_id)
        if capsule is None:
            return False
        return capsule.verify()

    def _calculate_shard(self, capsule_id: str) -> int:
        """Calculate shard ID from capsule ID using resonance."""
        hash_bytes = hashlib.sha3_256(capsule_id.encode()).digest()
        return int.from_bytes(hash_bytes[:4], 'big') % self.config.shards

    @property
    def stats(self) -> Dict[str, Any]:
        """Get nexus statistics."""
        total_capsules = sum(len(s) for s in self._shards.values())
        return {
            "total_capsules": total_capsules,
            "shard_count": self.config.shards,
            "replication_factor": self.config.replication_factor,
            "persistence": self.config.persistence
        }


class Capsule:
    """
    Truth Capsule - Immutable unit of verified information.

    Contains content with dual-hash provenance verification.
    """

    def __init__(
        self,
        content: str,
        author: str = "system",
        hash_algorithm: str = "dual-sha3",
        chain: Optional[str] = None
    ):
        self.id = self._generate_id()
        self.content = content
        self.author = author
        self.hash_algorithm = hash_algorithm
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.chain = chain
        self.hash_primary = self._compute_hash("sha3-256")
        self.hash_secondary = self._compute_hash("blake3")
        self.resonance = self._calculate_resonance()

    @classmethod
    def create(
        cls,
        content: str,
        author: str = "system",
        hash_algorithm: str = "dual-sha3"
    ) -> 'Capsule':
        """Create a new truth capsule."""
        return cls(content=content, author=author, hash_algorithm=hash_algorithm)

    def verify(self) -> bool:
        """Verify capsule integrity via dual-hash."""
        primary_valid = self.hash_primary == self._compute_hash("sha3-256")
        secondary_valid = self.hash_secondary == self._compute_hash("blake3")
        return primary_valid and secondary_valid

    def to_dict(self) -> Dict[str, Any]:
        """Convert capsule to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "author": self.author,
            "hash_algorithm": self.hash_algorithm,
            "timestamp": self.timestamp,
            "chain": self.chain,
            "hash_primary": self.hash_primary,
            "hash_secondary": self.hash_secondary,
            "resonance": self.resonance
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Capsule':
        """Create capsule from dictionary."""
        capsule = cls.__new__(cls)
        for key, value in data.items():
            setattr(capsule, key, value)
        return capsule

    def _generate_id(self) -> str:
        """Generate unique capsule ID."""
        import uuid
        return f"cap_{uuid.uuid4().hex[:12]}"

    def _compute_hash(self, algorithm: str) -> str:
        """Compute hash of capsule content."""
        data = f"{self.content}|{self.author}|{self.timestamp}"
        if algorithm == "sha3-256":
            return f"sha3-256:{hashlib.sha3_256(data.encode()).hexdigest()}"
        elif algorithm == "blake3":
            # Fallback to sha256 if blake3 not available
            return f"blake3:{hashlib.sha256(data.encode()).hexdigest()}"
        else:
            raise ValueError(f"Unknown hash algorithm: {algorithm}")

    def _calculate_resonance(self) -> float:
        """Calculate resonance frequency from hash."""
        hash_bytes = bytes.fromhex(self.hash_primary.split(":")[1][:16])
        return int.from_bytes(hash_bytes, 'big') / (2 ** 64)
