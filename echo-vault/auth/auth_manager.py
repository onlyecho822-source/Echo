"""
Echo Vault - Authentication Manager
Handles identity verification, API keys, and OAuth flows
"""

import hashlib
import secrets
import jwt
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum


class AuthMethod(Enum):
    """Supported authentication methods"""
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"


class AuthManager:
    """
    Manages authentication and authorization for Echo system
    """

    def __init__(self, secret_key: str, token_expiry_hours: int = 24):
        self.secret_key = secret_key
        self.token_expiry_hours = token_expiry_hours
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def generate_api_key(self, user_id: str, permissions: List[str]) -> str:
        """
        Generate a new API key for a user

        Args:
            user_id: User identifier
            permissions: List of permissions for this key

        Returns:
            str: Generated API key
        """
        # Generate secure random API key
        api_key = f"echo_{secrets.token_urlsafe(32)}"

        self.api_keys[api_key] = {
            "user_id": user_id,
            "permissions": permissions,
            "created_at": datetime.now(),
            "last_used": None,
            "active": True
        }

        return api_key

    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify an API key and return associated metadata

        Args:
            api_key: The API key to verify

        Returns:
            Optional[Dict]: Key metadata if valid, None otherwise
        """
        if api_key not in self.api_keys:
            return None

        key_data = self.api_keys[api_key]

        if not key_data["active"]:
            return None

        # Update last used timestamp
        key_data["last_used"] = datetime.now()

        return key_data

    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key"""
        if api_key not in self.api_keys:
            return False

        self.api_keys[api_key]["active"] = False
        return True

    def create_jwt_token(self, user_id: str, permissions: List[str],
                         custom_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a JWT token for a user

        Args:
            user_id: User identifier
            permissions: List of permissions
            custom_claims: Additional claims to include

        Returns:
            str: JWT token
        """
        now = datetime.utcnow()
        expiry = now + timedelta(hours=self.token_expiry_hours)

        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "iat": now,
            "exp": expiry,
            "iss": "echo-vault"
        }

        if custom_claims:
            payload.update(custom_claims)

        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token

        Args:
            token: JWT token to verify

        Returns:
            Optional[Dict]: Decoded token payload if valid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"],
                issuer="echo-vault"
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def create_session(self, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session for a user

        Args:
            user_id: User identifier
            metadata: Additional session metadata

        Returns:
            str: Session ID
        """
        session_id = secrets.token_urlsafe(32)

        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_active": datetime.now(),
            "metadata": metadata or {}
        }

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        session = self.sessions.get(session_id)

        if session:
            session["last_active"] = datetime.now()

        return session

    def destroy_session(self, session_id: str) -> bool:
        """Destroy a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def has_permission(self, user_id: str, required_permission: str,
                      auth_token: Optional[str] = None) -> bool:
        """
        Check if a user has a specific permission

        Args:
            user_id: User identifier
            required_permission: Permission to check
            auth_token: Optional JWT token or API key

        Returns:
            bool: Whether user has permission
        """
        if auth_token:
            # Try API key
            key_data = self.verify_api_key(auth_token)
            if key_data:
                return required_permission in key_data["permissions"]

            # Try JWT
            jwt_data = self.verify_jwt_token(auth_token)
            if jwt_data:
                return required_permission in jwt_data.get("permissions", [])

        return False

    def get_api_keys_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all API keys for a user"""
        return [
            {
                "key": key,
                "created_at": data["created_at"],
                "last_used": data["last_used"],
                "active": data["active"]
            }
            for key, data in self.api_keys.items()
            if data["user_id"] == user_id
        ]


# Example usage
if __name__ == "__main__":
    # Initialize auth manager
    auth = AuthManager(secret_key="your-secret-key-here")

    # Generate API key
    api_key = auth.generate_api_key(
        user_id="user123",
        permissions=["read", "write", "admin"]
    )
    print(f"Generated API key: {api_key}")

    # Verify API key
    key_data = auth.verify_api_key(api_key)
    print(f"Key verified: {key_data}")

    # Create JWT token
    jwt_token = auth.create_jwt_token(
        user_id="user123",
        permissions=["read", "write"]
    )
    print(f"JWT token: {jwt_token}")

    # Verify JWT
    jwt_data = auth.verify_jwt_token(jwt_token)
    print(f"JWT verified: {jwt_data}")

    # Create session
    session_id = auth.create_session(
        user_id="user123",
        metadata={"ip": "192.168.1.1"}
    )
    print(f"Session created: {session_id}")
