"""
Echo Phoenix Configuration
Centralized configuration management.
"""

from .airtable import airtable_config, AirtableConfig, AirtablePermission, Tables

__all__ = [
    "airtable_config",
    "AirtableConfig",
    "AirtablePermission",
    "Tables"
]
