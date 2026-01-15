"""
Echo Phoenix Rate Limiting Middleware
Implements per-IP rate limiting to prevent abuse.
"""

import os
import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, Request

# Configuration
RATE_LIMIT_WEBHOOKS = int(os.getenv("RATE_LIMIT_WEBHOOKS", "100"))  # per minute
RATE_LIMIT_CONTROL = int(os.getenv("RATE_LIMIT_CONTROL", "10"))     # per minute
RATE_LIMIT_DEFAULT = int(os.getenv("RATE_LIMIT_DEFAULT", "60"))     # per minute


class RateLimiter:
    """
    In-memory rate limiter with sliding window.
    For production, consider Redis-based implementation.
    """
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, client_id: str, limit: int, window_seconds: int = 60) -> bool:
        """
        Check if request is allowed under rate limit.
        
        Args:
            client_id: Unique identifier for client (usually IP)
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        cutoff = now - window_seconds
        
        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > cutoff
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= limit:
            return False
        
        # Record request
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self, client_id: str, limit: int, window_seconds: int = 60) -> int:
        """Get remaining requests for client in current window."""
        now = time.time()
        cutoff = now - window_seconds
        current = len([t for t in self.requests[client_id] if t > cutoff])
        return max(0, limit - current)
    
    def get_reset_time(self, client_id: str, window_seconds: int = 60) -> int:
        """Get seconds until rate limit resets."""
        if not self.requests[client_id]:
            return 0
        oldest = min(self.requests[client_id])
        reset = oldest + window_seconds
        return max(0, int(reset - time.time()))


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit_webhooks(request: Request):
    """Rate limit for webhook endpoints (100/min)."""
    client_id = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_id, RATE_LIMIT_WEBHOOKS):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_WEBHOOKS} requests per minute.",
            headers={
                "Retry-After": str(rate_limiter.get_reset_time(client_id)),
                "X-RateLimit-Limit": str(RATE_LIMIT_WEBHOOKS),
                "X-RateLimit-Remaining": "0"
            }
        )


async def check_rate_limit_control(request: Request):
    """Rate limit for control endpoints (10/min)."""
    client_id = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_id, RATE_LIMIT_CONTROL):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_CONTROL} requests per minute.",
            headers={
                "Retry-After": str(rate_limiter.get_reset_time(client_id)),
                "X-RateLimit-Limit": str(RATE_LIMIT_CONTROL),
                "X-RateLimit-Remaining": "0"
            }
        )


async def check_rate_limit_default(request: Request):
    """Default rate limit (60/min)."""
    client_id = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_id, RATE_LIMIT_DEFAULT):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_DEFAULT} requests per minute.",
            headers={
                "Retry-After": str(rate_limiter.get_reset_time(client_id)),
                "X-RateLimit-Limit": str(RATE_LIMIT_DEFAULT),
                "X-RateLimit-Remaining": "0"
            }
        )
