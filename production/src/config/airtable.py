"""
Echo Phoenix Airtable Configuration
Implements key separation for read/write/admin operations.
"""

import os
from typing import Optional
from enum import Enum


class AirtablePermission(Enum):
    """Permission levels for Airtable operations."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class AirtableConfig:
    """
    Airtable configuration with key separation.
    
    For maximum security, use separate API keys with different scopes:
    - READ: Can only read from tables
    - WRITE: Can read and write to tables
    - ADMIN: Can create/modify table schema
    
    If only one key is provided (AIRTABLE_API_KEY), it will be used for all operations.
    """
    
    def __init__(self):
        # Primary key (fallback for all operations)
        self._primary_key = os.getenv("AIRTABLE_API_KEY", "")
        
        # Separated keys (optional, for enhanced security)
        self._keys = {
            AirtablePermission.READ: os.getenv("AIRTABLE_READ_KEY", ""),
            AirtablePermission.WRITE: os.getenv("AIRTABLE_WRITE_KEY", ""),
            AirtablePermission.ADMIN: os.getenv("AIRTABLE_ADMIN_KEY", ""),
        }
        
        # Base ID
        self.base_id = os.getenv("AIRTABLE_BASE_ID", "")
    
    def get_key(self, permission: AirtablePermission = AirtablePermission.READ) -> str:
        """
        Get API key for specified permission level.
        Falls back to primary key if separated key not available.
        """
        key = self._keys.get(permission, "")
        if key:
            return key
        return self._primary_key
    
    def get_headers(self, permission: AirtablePermission = AirtablePermission.READ) -> dict:
        """Get HTTP headers for Airtable API requests."""
        return {
            "Authorization": f"Bearer {self.get_key(permission)}",
            "Content-Type": "application/json"
        }
    
    def get_table_url(self, table_name: str) -> str:
        """Get full URL for Airtable table."""
        return f"https://api.airtable.com/v0/{self.base_id}/{table_name}"
    
    @property
    def is_configured(self) -> bool:
        """Check if Airtable is properly configured."""
        return bool(self._primary_key or any(self._keys.values())) and bool(self.base_id)
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate configuration.
        Returns (is_valid, error_message).
        """
        if not self.base_id:
            return False, "AIRTABLE_BASE_ID not set"
        
        if not self._primary_key and not any(self._keys.values()):
            return False, "No Airtable API keys configured"
        
        return True, "Configuration valid"


# Global configuration instance
airtable_config = AirtableConfig()


# Table names
class Tables:
    """Airtable table names."""
    SYSTEM_THROTTLE = "system_throttle"
    SYSTEM_STATE = "system_state"
    USED_NONCES = "used_nonces"
    EVIDENCE_LEDGER = "evidence_ledger"
    AUDIT_LOG = "audit_log"
    RECONCILIATION_LOG = "reconciliation_log"
