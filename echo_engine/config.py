"""Configuration management for Echo Reverse Engineering Engine."""

import os
import json
from pathlib import Path
from typing import Optional


# Default configuration
DEFAULT_CONFIG = {
    "engine": {
        "max_sources": 100,
        "max_facts_per_source": 50,
        "default_confidence_threshold": 0.5,
    },
    "extraction": {
        "min_word_count": 4,
        "max_word_count": 100,
        "extract_entities": True,
        "extract_keywords": True,
        "max_keywords": 15,
    },
    "validation": {
        "min_corroboration": 2,
        "keyword_threshold": 0.3,
        "enable_cross_validation": True,
    },
    "timeline": {
        "reference_date": None,  # Uses current date if None
        "gap_threshold_days": 30,
    },
    "cross_reference": {
        "similarity_threshold": 0.3,
        "max_connections": 500,
    },
    "reporting": {
        "default_format": "markdown",
        "include_raw_content": False,
        "max_fact_preview_length": 200,
    },
    "storage": {
        "data_directory": ".echo_data",
        "auto_save": True,
        "save_interval_minutes": 5,
    },
    "web_collector": {
        "user_agent": "Echo-Engine/0.1 (Research Bot)",
        "timeout": 30,
        "max_retries": 3,
    },
}


class Config:
    """Configuration manager for Echo Engine."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Optional path to configuration file
        """
        self._config = DEFAULT_CONFIG.copy()

        if config_path:
            self.load(config_path)
        else:
            # Try to load from default locations
            self._load_default()

    def _load_default(self):
        """Try to load configuration from default locations."""
        default_paths = [
            "echo_config.json",
            ".echo_config.json",
            os.path.expanduser("~/.echo/config.json"),
        ]

        for path in default_paths:
            if os.path.exists(path):
                self.load(path)
                break

    def load(self, filepath: str):
        """
        Load configuration from a JSON file.

        Args:
            filepath: Path to configuration file
        """
        with open(filepath, "r") as f:
            user_config = json.load(f)

        # Merge with defaults
        self._merge_config(user_config)

    def _merge_config(self, user_config: dict):
        """Merge user configuration with defaults."""
        for section, values in user_config.items():
            if section in self._config:
                if isinstance(values, dict):
                    self._config[section].update(values)
                else:
                    self._config[section] = values
            else:
                self._config[section] = values

    def save(self, filepath: str):
        """
        Save current configuration to a file.

        Args:
            filepath: Path to save configuration
        """
        with open(filepath, "w") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default=None):
        """
        Get a configuration value.

        Args:
            key: Dot-notation key (e.g., "engine.max_sources")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        parts = key.split(".")
        value = self._config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value

    def set(self, key: str, value):
        """
        Set a configuration value.

        Args:
            key: Dot-notation key
            value: Value to set
        """
        parts = key.split(".")
        config = self._config

        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]

        config[parts[-1]] = value

    def get_section(self, section: str) -> dict:
        """
        Get an entire configuration section.

        Args:
            section: Section name

        Returns:
            Section dictionary or empty dict
        """
        return self._config.get(section, {})

    def to_dict(self) -> dict:
        """Get entire configuration as dictionary."""
        return self._config.copy()

    def reset(self):
        """Reset configuration to defaults."""
        self._config = DEFAULT_CONFIG.copy()

    def validate(self) -> list[str]:
        """
        Validate configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate numeric ranges
        if self.get("engine.max_sources", 0) <= 0:
            errors.append("engine.max_sources must be positive")

        if self.get("extraction.min_word_count", 0) < 1:
            errors.append("extraction.min_word_count must be at least 1")

        if self.get("validation.min_corroboration", 0) < 1:
            errors.append("validation.min_corroboration must be at least 1")

        threshold = self.get("validation.keyword_threshold", 0)
        if not 0 <= threshold <= 1:
            errors.append("validation.keyword_threshold must be between 0 and 1")

        return errors


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def set_config(config: Config):
    """Set the global configuration instance."""
    global _global_config
    _global_config = config
