#!/usr/bin/env python3
"""
Input Validation and Security Module for Echo Forge
Ensures safe handling of user inputs and prevents security vulnerabilities
"""

import re
import os
from typing import Any, Tuple


class InputValidator:
    """Validates and sanitizes user inputs"""

    # Allowed characters for domain names
    DOMAIN_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\s]+$')

    # Maximum lengths to prevent resource exhaustion
    MAX_DOMAIN_LENGTH = 100
    MAX_FEATURE_LENGTH = 200
    MAX_FEATURES_COUNT = 50

    @staticmethod
    def validate_domain(domain: str) -> Tuple[bool, str, str]:
        """
        Validate and sanitize domain input

        Args:
            domain: User-provided domain string

        Returns:
            Tuple of (is_valid, sanitized_domain, error_message)
        """
        if not domain:
            return False, "", "Domain cannot be empty"

        if len(domain) > InputValidator.MAX_DOMAIN_LENGTH:
            return False, "", f"Domain too long (max {InputValidator.MAX_DOMAIN_LENGTH} characters)"

        # Remove leading/trailing whitespace
        sanitized = domain.strip()

        # Check for path traversal attempts
        if ".." in sanitized or "/" in sanitized or "\\" in sanitized:
            return False, "", "Domain contains invalid path characters"

        # Check for SQL injection patterns
        sql_keywords = ["DROP", "SELECT", "INSERT", "UPDATE", "DELETE", "EXEC", "UNION"]
        upper_domain = sanitized.upper()
        for keyword in sql_keywords:
            if keyword in upper_domain:
                return False, "", f"Domain contains disallowed keyword: {keyword}"

        # Check against allowed pattern
        if not InputValidator.DOMAIN_PATTERN.match(sanitized):
            return False, "", "Domain contains invalid characters (allowed: a-z, A-Z, 0-9, _, -, space)"

        # Replace spaces with underscores for safety
        sanitized = sanitized.replace(" ", "_")

        return True, sanitized, ""

    @staticmethod
    def validate_features(features: list) -> Tuple[bool, list, str]:
        """
        Validate and sanitize feature list

        Args:
            features: List of feature strings

        Returns:
            Tuple of (is_valid, sanitized_features, error_message)
        """
        if not isinstance(features, list):
            return False, [], "Features must be a list"

        if len(features) > InputValidator.MAX_FEATURES_COUNT:
            return False, [], f"Too many features (max {InputValidator.MAX_FEATURES_COUNT})"

        sanitized = []
        for feature in features:
            if not isinstance(feature, str):
                return False, [], "All features must be strings"

            if len(feature) > InputValidator.MAX_FEATURE_LENGTH:
                return False, [], f"Feature too long (max {InputValidator.MAX_FEATURE_LENGTH} characters)"

            # Sanitize feature string
            clean_feature = feature.strip()
            if clean_feature:
                sanitized.append(clean_feature)

        return True, sanitized, ""

    @staticmethod
    def validate_app_name(name: str) -> Tuple[bool, str, str]:
        """
        Validate app name for filesystem safety

        Args:
            name: Proposed app name

        Returns:
            Tuple of (is_valid, sanitized_name, error_message)
        """
        if not name:
            return False, "", "Name cannot be empty"

        # Remove dangerous characters
        sanitized = re.sub(r'[^\w\s\-]', '', name)
        sanitized = sanitized.strip().replace(" ", "_")

        if not sanitized:
            return False, "", "Name contains only invalid characters"

        # Prevent directory traversal
        if ".." in sanitized or sanitized.startswith("."):
            return False, "", "Name cannot start with . or contain .."

        return True, sanitized, ""


class SecurityScanner:
    """Scans generated code for security vulnerabilities"""

    # Patterns that indicate potential security issues
    SECURITY_PATTERNS = {
        "hardcoded_secret": re.compile(r'(password|secret|api_key|token)\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
        "sql_concat": re.compile(r'(SELECT|INSERT|UPDATE|DELETE).*\+.*["\']', re.IGNORECASE),
        "eval_exec": re.compile(r'\b(eval|exec)\s*\('),
        "shell_injection": re.compile(r'(os\.system|subprocess\.call|subprocess\.run).*\+'),
    }

    @staticmethod
    def scan_code(code: str, filename: str) -> list:
        """
        Scan code for security vulnerabilities

        Args:
            code: Code content to scan
            filename: Name of the file being scanned

        Returns:
            List of security warnings
        """
        warnings = []

        for pattern_name, pattern in SecurityScanner.SECURITY_PATTERNS.items():
            matches = pattern.finditer(code)
            for match in matches:
                # Skip if it's in a comment or TODO
                line = code[max(0, match.start() - 50):match.end()].split('\n')[-1]
                if "TODO" in line or "#" in line.split(match.group())[0]:
                    continue

                warnings.append({
                    "file": filename,
                    "type": pattern_name,
                    "line": code[:match.start()].count('\n') + 1,
                    "match": match.group(),
                    "severity": "HIGH" if pattern_name in ["hardcoded_secret", "sql_concat"] else "MEDIUM"
                })

        return warnings

    @staticmethod
    def validate_dependencies(requirements: str) -> list:
        """
        Check dependencies for known vulnerabilities

        Args:
            requirements: Contents of requirements.txt

        Returns:
            List of warnings about vulnerable dependencies
        """
        warnings = []

        # List of known vulnerable versions (examples - would be updated from CVE database)
        vulnerable_patterns = [
            (re.compile(r'requests==2\.6\.'), "requests 2.6.x has known vulnerabilities"),
            (re.compile(r'flask==0\.12\.'), "Flask 0.12.x has security issues"),
            (re.compile(r'django==1\.'), "Django 1.x is end-of-life"),
        ]

        for pattern, message in vulnerable_patterns:
            if pattern.search(requirements):
                warnings.append({
                    "type": "vulnerable_dependency",
                    "message": message,
                    "severity": "HIGH"
                })

        return warnings


class PathSanitizer:
    """Ensures safe file path operations"""

    @staticmethod
    def sanitize_path(base_dir: str, user_path: str) -> Tuple[bool, str, str]:
        """
        Sanitize a file path to prevent directory traversal

        Args:
            base_dir: Base directory that should contain the file
            user_path: User-provided path component

        Returns:
            Tuple of (is_safe, full_path, error_message)
        """
        # Remove any path traversal attempts
        clean_path = os.path.normpath(user_path)

        # Combine with base directory
        full_path = os.path.join(base_dir, clean_path)

        # Resolve to absolute path
        abs_base = os.path.abspath(base_dir)
        abs_full = os.path.abspath(full_path)

        # Ensure the final path is within the base directory
        if not abs_full.startswith(abs_base):
            return False, "", "Path traversal detected"

        return True, abs_full, ""


# Convenience functions
def validate_and_sanitize_domain(domain: str) -> str:
    """
    Validate and sanitize domain, raising exception if invalid

    Args:
        domain: User-provided domain

    Returns:
        Sanitized domain

    Raises:
        ValueError: If domain is invalid
    """
    is_valid, sanitized, error = InputValidator.validate_domain(domain)
    if not is_valid:
        raise ValueError(f"Invalid domain: {error}")
    return sanitized


def scan_generated_code(files: dict) -> list:
    """
    Scan all generated files for security issues

    Args:
        files: Dictionary of filename -> content

    Returns:
        List of all security warnings found
    """
    all_warnings = []

    for filename, content in files.items():
        if filename.endswith(('.py', '.js')):
            warnings = SecurityScanner.scan_code(content, filename)
            all_warnings.extend(warnings)

        if filename == "requirements.txt":
            warnings = SecurityScanner.validate_dependencies(content)
            all_warnings.extend(warnings)

    return all_warnings
