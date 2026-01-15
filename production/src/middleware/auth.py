"""
Echo Phoenix Authentication Middleware
Provides API key authentication for all sensitive endpoints.
"""

import os
import hmac
from fastapi import HTTPException, Header, Depends
from functools import wraps

# API key from environment (generate if not set)
API_KEY = os.getenv("ECHO_API_KEY", "")

def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    Dependency that validates API key in request header.
    Uses constant-time comparison to prevent timing attacks.
    """
    if not API_KEY:
        # In production, require API key to be set
        if os.getenv("ENVIRONMENT") == "production":
            raise HTTPException(
                status_code=500,
                detail="ECHO_API_KEY not configured"
            )
        # In development, allow requests without key
        return "development"
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-Key header"
        )
    
    # Constant-time comparison
    if not hmac.compare_digest(x_api_key, API_KEY):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return x_api_key


def get_api_key() -> str:
    """Return the configured API key (for logging/debugging)."""
    return API_KEY[:8] + "..." if API_KEY else "NOT_SET"
