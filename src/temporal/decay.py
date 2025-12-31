#!/usr/bin/env python3
"""
Temporal Decay Calculator
Implements the Broken Clock formula for confidence decay
"""

import math
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class DecayPolicy:
    """Decay parameters for different content types"""
    lambda_per_day: float  # Decay rate
    floor: float          # Minimum confidence


# Decay policies by topic type
DECAY_POLICIES = {
    "News": DecayPolicy(lambda_per_day=0.10, floor=0.05),
    "Code": DecayPolicy(lambda_per_day=0.005, floor=0.20),
    "Science": DecayPolicy(lambda_per_day=0.002, floor=0.30),
    "Legal": DecayPolicy(lambda_per_day=0.001, floor=0.40),
    "History": DecayPolicy(lambda_per_day=0.0, floor=1.00),
}


def age_days(capture_ts: str, now: datetime = None) -> float:
    """
    Calculate age in days from ISO 8601 timestamp to now.
    
    Args:
        capture_ts: ISO 8601 timestamp string
        now: Current time (defaults to now)
    
    Returns:
        Age in days (float)
    """
    now = now or datetime.now(timezone.utc)
    capture = datetime.fromisoformat(capture_ts.replace('Z', '+00:00'))
    
    if capture.tzinfo is None:
        capture = capture.replace(tzinfo=timezone.utc)
    
    return max(0.0, (now - capture).total_seconds() / 86400.0)


def calculate_confidence(
    initial: float,
    topic_type: str,
    capture_timestamp: str,
    now: datetime = None
) -> float:
    """
    Calculate current confidence using Broken Clock formula.
    
    Formula: confidence(t) = max(floor, initial × e^(-λ × days))
    
    Args:
        initial: Initial confidence (0.0 to 1.0)
        topic_type: One of: News, Code, Science, Legal, History
        capture_timestamp: ISO 8601 timestamp when artifact was created
        now: Current time (defaults to now)
    
    Returns:
        Current confidence (0.0 to 1.0)
    """
    if topic_type not in DECAY_POLICIES:
        raise ValueError(f"Unknown topic_type: {topic_type}")
    
    policy = DECAY_POLICIES[topic_type]
    days = age_days(capture_timestamp, now)
    
    # Broken Clock formula
    raw = initial * math.exp(-policy.lambda_per_day * days)
    return max(policy.floor, min(1.0, raw))


def quality_score(payload_bytes: int, source_count: int) -> float:
    """
    Calculate artifact quality score.
    
    Prevents empty artifacts from passing quality gates.
    
    Args:
        payload_bytes: Size of content in bytes
        source_count: Number of sources cited
    
    Returns:
        Quality score (0.0 to 1.0)
    """
    size_score = min(1.0, payload_bytes / 2000.0)
    source_score = min(1.0, source_count / 3.0)
    return 0.6 * size_score + 0.4 * source_score


if __name__ == "__main__":
    # Example usage
    print("Temporal Decay Calculator - Example")
    print("=" * 50)
    
    # EDR-001 example
    edr001_confidence = calculate_confidence(
        initial=0.85,
        topic_type="Code",
        capture_timestamp="2025-12-31T00:00:00Z"
    )
    
    print(f"EDR-001 Current Confidence: {edr001_confidence:.3f}")
    
    # Test at different time points
    test_date = datetime(2025, 12, 31, tzinfo=timezone.utc)
    
    for days in [0, 30, 90, 180, 365]:
        from datetime import timedelta
        future = test_date + timedelta(days=days)
        future_ts = test_date.isoformat()
        
        conf = calculate_confidence(
            initial=0.85,
            topic_type="Code",
            capture_timestamp=future_ts,
            now=future
        )
        print(f"  After {days:3d} days: {conf:.3f}")
