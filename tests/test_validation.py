"""
Tests for validation module
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validation import InputValidator, SecurityScanner, PathSanitizer


class TestInputValidator:
    """Tests for InputValidator"""

    def test_valid_domain(self):
        """Test valid domain validation"""
        is_valid, sanitized, error = InputValidator.validate_domain("healthcare")
        assert is_valid
        assert sanitized == "healthcare"
        assert error == ""

    def test_domain_with_spaces(self):
        """Test domain with spaces gets sanitized"""
        is_valid, sanitized, error = InputValidator.validate_domain("health care")
        assert is_valid
        assert sanitized == "health_care"

    def test_empty_domain(self):
        """Test empty domain is rejected"""
        is_valid, sanitized, error = InputValidator.validate_domain("")
        assert not is_valid
        assert "empty" in error.lower()

    def test_domain_too_long(self):
        """Test overly long domain is rejected"""
        long_domain = "a" * 200
        is_valid, sanitized, error = InputValidator.validate_domain(long_domain)
        assert not is_valid
        assert "too long" in error.lower()

    def test_path_traversal_blocked(self):
        """Test path traversal attempts are blocked"""
        is_valid, sanitized, error = InputValidator.validate_domain("../etc/passwd")
        assert not is_valid
        assert "path" in error.lower()

    def test_sql_injection_blocked(self):
        """Test SQL injection attempts are blocked"""
        is_valid, sanitized, error = InputValidator.validate_domain("test'; DROP TABLE apps; --")
        assert not is_valid
        assert "keyword" in error.lower()

    def test_valid_features_list(self):
        """Test valid features list"""
        features = ["Feature 1", "Feature 2"]
        is_valid, sanitized, error = InputValidator.validate_features(features)
        assert is_valid
        assert len(sanitized) == 2

    def test_features_not_list(self):
        """Test non-list features rejected"""
        is_valid, sanitized, error = InputValidator.validate_features("not a list")
        assert not is_valid

    def test_too_many_features(self):
        """Test too many features rejected"""
        features = [f"Feature {i}" for i in range(100)]
        is_valid, sanitized, error = InputValidator.validate_features(features)
        assert not is_valid
        assert "too many" in error.lower()

    def test_feature_too_long(self):
        """Test overly long feature rejected"""
        features = ["a" * 300]
        is_valid, sanitized, error = InputValidator.validate_features(features)
        assert not is_valid
        assert "too long" in error.lower()

    def test_app_name_validation(self):
        """Test app name validation"""
        is_valid, sanitized, error = InputValidator.validate_app_name("My App")
        assert is_valid
        assert sanitized == "My_App"

    def test_app_name_dangerous_chars(self):
        """Test dangerous characters removed from app name"""
        is_valid, sanitized, error = InputValidator.validate_app_name("App<>|/\\")
        assert is_valid
        assert "<" not in sanitized
        assert ">" not in sanitized


class TestSecurityScanner:
    """Tests for SecurityScanner"""

    def test_no_warnings_clean_code(self):
        """Test clean code produces no warnings"""
        code = """
def hello():
    print("Hello world")
        """
        warnings = SecurityScanner.scan_code(code, "test.py")
        assert len(warnings) == 0

    def test_detects_hardcoded_secret(self):
        """Test detection of hardcoded secrets"""
        code = '''
password = "super_secret_123"
        '''
        warnings = SecurityScanner.scan_code(code, "test.py")
        assert len(warnings) > 0
        assert warnings[0]["type"] == "hardcoded_secret"

    def test_ignores_todo_secrets(self):
        """Test that TODO placeholders are ignored"""
        code = '''
# TODO: Set password = "your_password"
password = None
        '''
        warnings = SecurityScanner.scan_code(code, "test.py")
        # Should not flag the TODO line
        assert len([w for w in warnings if "TODO" not in code[w["line"]]]) == 0

    def test_detects_eval_usage(self):
        """Test detection of eval/exec"""
        code = '''
result = eval(user_input)
        '''
        warnings = SecurityScanner.scan_code(code, "test.py")
        assert any(w["type"] == "eval_exec" for w in warnings)


class TestPathSanitizer:
    """Tests for PathSanitizer"""

    def test_safe_path(self):
        """Test safe path is allowed"""
        is_safe, path, error = PathSanitizer.sanitize_path("/tmp/base", "subdir/file.txt")
        assert is_safe
        assert "subdir" in path

    def test_path_traversal_blocked(self):
        """Test path traversal is blocked"""
        is_safe, path, error = PathSanitizer.sanitize_path("/tmp/base", "../../etc/passwd")
        assert not is_safe
        assert "traversal" in error.lower()

    def test_absolute_path_within_base(self):
        """Test handling of absolute paths"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            is_safe, path, error = PathSanitizer.sanitize_path(tmpdir, "test.txt")
            assert is_safe
            assert path.startswith(tmpdir)
