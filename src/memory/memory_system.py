"""
ECHO ORGANISM v2.1 - MEMORY SYSTEM
Classification: CRITICAL FIX #4

Advanced memory system with:
- Entropy-weighted sampling (not just random)
- Compression for efficiency
- Integrity checking
- Pruning strategies

CRITICAL FIX #4: Memory unpredictability
- Add weighted sampling based on information content
- Prevent predictable memory access patterns
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from collections import deque
import hashlib
import logging

logger = logging.getLogger(__name__)


class MemorySystem:
    """
    Production-grade memory system for Echo Organism.

    Features:
    - Entropy-weighted sampling
    - Checksum integrity validation
    - Compression support
    - Adaptive pruning
    - Memory statistics tracking
    """

    def __init__(self, capacity: int = 1000, compression: bool = True):
        """
        Args:
            capacity: Maximum number of states to store
            compression: Enable compressed storage
        """
        self.capacity = capacity
        self.compression_enabled = compression

        # Primary storage
        self.states: deque = deque(maxlen=capacity)
        self.metadata: deque = deque(maxlen=capacity)

        # Integrity tracking
        self.checksums: deque = deque(maxlen=capacity)
        self.error_count = 0

        # Entropy weights for sampling
        self.entropy_weights: deque = deque(maxlen=capacity)

        # Statistics
        self.access_count = 0
        self.store_count = 0

        logger.info(f"MemorySystem initialized: capacity={capacity}, compression={compression}")

    def store(self, x_flat: np.ndarray, step: int = 0, influence: Optional[np.ndarray] = None):
        """
        Store state in memory with metadata.

        Args:
            x_flat: 896D flattened state
            step: Current step number
            influence: Φ(x) output for entropy weighting
        """
        try:
            # Compress if enabled
            if self.compression_enabled:
                stored_state = self._compress(x_flat)
            else:
                stored_state = x_flat.copy()

            # Compute checksum
            checksum = hashlib.sha256(stored_state.tobytes()).hexdigest()[:16]

            # Compute entropy weight for sampling
            entropy_weight = self._compute_entropy_weight(x_flat, influence)

            # Store
            self.states.append(stored_state)
            self.checksums.append(checksum)
            self.entropy_weights.append(entropy_weight)
            self.metadata.append({
                'step': step,
                'timestamp': np.datetime64('now'),
                'compressed': self.compression_enabled
            })

            self.store_count += 1

        except Exception as e:
            logger.error(f"Memory store failed: {e}")
            self.error_count += 1

    def retrieve(self, index: int) -> Optional[np.ndarray]:
        """
        Retrieve state by index.

        Args:
            index: Memory index

        Returns:
            896D state or None if failed
        """
        if index >= len(self.states) or index < 0:
            return None

        try:
            stored = self.states[index]

            # Verify integrity
            current_checksum = hashlib.sha256(stored.tobytes()).hexdigest()[:16]
            if current_checksum != self.checksums[index]:
                logger.warning(f"Memory corruption at index {index}")
                self.error_count += 1
                return None

            # Decompress if needed
            if self.compression_enabled:
                state = self._decompress(stored)
            else:
                state = stored.copy()

            self.access_count += 1
            return state

        except Exception as e:
            logger.error(f"Memory retrieve failed: {e}")
            self.error_count += 1
            return None

    def get_all(self) -> List[np.ndarray]:
        """
        Get all stored states as list of 896D arrays.
        """
        result = []
        for i in range(len(self.states)):
            state = self.retrieve(i)
            if state is not None:
                result.append(state)
        return result

    def sample(self, n: int, method: str = "entropy_weighted", rng: Optional[np.random.Generator] = None) -> List[np.ndarray]:
        """
        CRITICAL FIX #4: Entropy-weighted sampling.

        Sample states from memory using specified method.

        Args:
            n: Number of samples
            method: "entropy_weighted", "uniform", "recent", "diverse"
            rng: Random number generator

        Returns:
            List of sampled 896D states
        """
        if rng is None:
            rng = np.random.default_rng()

        if len(self.states) == 0:
            return []

        n = min(n, len(self.states))

        if method == "entropy_weighted":
            indices = self._entropy_weighted_sample(n, rng)
        elif method == "uniform":
            indices = rng.choice(len(self.states), size=n, replace=False)
        elif method == "recent":
            indices = list(range(max(0, len(self.states) - n), len(self.states)))
        elif method == "diverse":
            indices = self._diverse_sample(n, rng)
        else:
            indices = rng.choice(len(self.states), size=n, replace=False)

        samples = []
        for idx in indices:
            state = self.retrieve(int(idx))
            if state is not None:
                samples.append(state)

        return samples

    def _entropy_weighted_sample(self, n: int, rng: np.random.Generator) -> np.ndarray:
        """
        Sample with probability proportional to entropy weight.
        Higher entropy = more likely to be sampled.
        """
        weights = np.array(self.entropy_weights)

        # Handle edge cases
        if np.sum(weights) <= 0:
            return rng.choice(len(self.states), size=n, replace=False)

        # Normalize to probabilities
        probs = weights / np.sum(weights)

        # Sample without replacement
        try:
            indices = rng.choice(len(self.states), size=n, replace=False, p=probs)
        except ValueError:
            # If n > len, fall back
            indices = rng.choice(len(self.states), size=min(n, len(self.states)), replace=False)

        return indices

    def _diverse_sample(self, n: int, rng: np.random.Generator) -> List[int]:
        """
        Sample to maximize diversity (farthest point sampling).
        """
        if n >= len(self.states):
            return list(range(len(self.states)))

        # Get all states
        all_states = self.get_all()
        if len(all_states) == 0:
            return []

        # Start with random state
        indices = [rng.integers(len(all_states))]

        # Iteratively add farthest state
        while len(indices) < n:
            max_min_dist = -1
            best_idx = -1

            for i in range(len(all_states)):
                if i in indices:
                    continue

                # Minimum distance to selected set
                min_dist = min(np.linalg.norm(all_states[i] - all_states[j])
                               for j in indices)

                if min_dist > max_min_dist:
                    max_min_dist = min_dist
                    best_idx = i

            if best_idx >= 0:
                indices.append(best_idx)
            else:
                break

        return indices

    def _compute_entropy_weight(self, x_flat: np.ndarray, influence: Optional[np.ndarray]) -> float:
        """
        Compute entropy weight for sampling priority.
        Higher weight = more information content.
        """
        # Base: novelty of state
        if len(self.states) == 0:
            base_weight = 1.0
        else:
            all_states = self.get_all()
            if all_states:
                distances = [np.linalg.norm(x_flat - s) for s in all_states]
                min_dist = np.min(distances)
                base_weight = 1.0 - np.exp(-min_dist)
            else:
                base_weight = 1.0

        # Modulator: use influence if available
        if influence is not None:
            novelty = influence[0]
            coherence = influence[1]
            # Higher novelty + lower coherence = more diverse = higher weight
            modulator = 0.5 * novelty + 0.5 * (1.0 - coherence)
        else:
            modulator = 0.5

        weight = base_weight * (0.5 + modulator)
        return np.clip(weight, 0.01, 2.0)

    def _compress(self, x_flat: np.ndarray) -> np.ndarray:
        """
        Compress 896D state to smaller representation.
        Uses float16 and removes near-zero values.
        """
        # Convert to float16
        compressed = x_flat.astype(np.float16)
        return compressed

    def _decompress(self, compressed: np.ndarray) -> np.ndarray:
        """
        Decompress back to 896D float64.
        """
        return compressed.astype(np.float64)

    def prune(self, strategy: str = "oldest", fraction: float = 0.2):
        """
        Prune memory to free capacity.

        Args:
            strategy: "oldest", "lowest_entropy", "random"
            fraction: Fraction to remove
        """
        n_remove = int(len(self.states) * fraction)
        if n_remove == 0:
            return

        if strategy == "oldest":
            # Already handled by deque maxlen
            pass
        elif strategy == "lowest_entropy":
            # Remove states with lowest entropy weight
            weights = list(self.entropy_weights)
            indices = np.argsort(weights)[:n_remove]
            self._remove_indices(sorted(indices, reverse=True))
        elif strategy == "random":
            indices = np.random.choice(len(self.states), size=n_remove, replace=False)
            self._remove_indices(sorted(indices, reverse=True))

    def _remove_indices(self, indices: List[int]):
        """Remove states at specified indices (must be reverse sorted)"""
        for idx in indices:
            if 0 <= idx < len(self.states):
                del self.states[idx]
                del self.checksums[idx]
                del self.entropy_weights[idx]
                del self.metadata[idx]

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return {
            'size': len(self.states),
            'capacity': self.capacity,
            'utilization': len(self.states) / self.capacity,
            'store_count': self.store_count,
            'access_count': self.access_count,
            'error_count': self.error_count,
            'error_rate': self.error_count / max(1, self.store_count + self.access_count),
            'avg_entropy_weight': np.mean(self.entropy_weights) if self.entropy_weights else 0.0,
            'compression_enabled': self.compression_enabled
        }

    def health_metric(self) -> float:
        """Compute overall health of memory system"""
        error_rate = self.error_count / max(1, self.store_count + self.access_count)
        utilization = len(self.states) / self.capacity

        # Health decreases with errors, increases slightly with utilization
        health = (1.0 - error_rate) * (0.5 + 0.5 * (1.0 - utilization))
        return np.clip(health, 0.0, 1.0)

    def __len__(self):
        return len(self.states)

    def __repr__(self):
        return f"MemorySystem(size={len(self.states)}/{self.capacity}, health={self.health_metric():.2f})"
