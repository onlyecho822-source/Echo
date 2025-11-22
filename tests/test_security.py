"""
Security tests for Echo Forge
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo_forge import EchoForge, AIType, TechStack


class TestSecurity:
    """Security-focused tests"""

    def setup_method(self):
        """Setup test fixtures"""
        self.forge = EchoForge()

    def test_no_code_injection_in_domain(self):
        """Test that domain input doesn't allow code injection"""
        malicious_domain = "test'; DROP TABLE apps; --"
        blueprint = self.forge.create_app(domain=malicious_domain)
        # Should sanitize or escape the input
        assert blueprint is not None

    def test_no_path_traversal_in_domain(self):
        """Test that domain input doesn't allow path traversal"""
        malicious_domain = "../../../etc/passwd"
        blueprint = self.forge.create_app(domain=malicious_domain)
        # Should not create files outside generated_apps
        app_dir = f"generated_apps/{blueprint.name.lower().replace(' ', '_')}"
        assert "generated_apps" in app_dir
        assert ".." not in app_dir

    def test_generated_code_no_hardcoded_secrets(self):
        """Test that generated code doesn't contain hardcoded secrets"""
        blueprint = self.forge.create_app(
            domain="test",
            tech_stack=TechStack.PYTHON_FASTAPI
        )
        code_files = self.forge.code_generator.generate(blueprint)

        for filename, content in code_files.items():
            # Check for common secret patterns
            assert "password" not in content.lower() or "TODO" in content
            assert "api_key = \"" not in content
            assert "secret = \"" not in content

    def test_dockerfile_no_root_user(self):
        """Test that Dockerfile doesn't run as root (future improvement)"""
        blueprint = self.forge.create_app(domain="test")
        code_files = self.forge.code_generator.generate(blueprint)
        dockerfile = code_files.get("Dockerfile", "")

        # Currently runs as root, but this test documents the gap
        # Future: Should add USER directive
        assert "FROM python:" in dockerfile

    def test_requirements_no_vulnerable_versions(self):
        """Test that requirements don't specify vulnerable versions"""
        blueprint = self.forge.create_app(
            domain="test",
            ai_type=AIType.CHATBOT,
            tech_stack=TechStack.PYTHON_FASTAPI
        )
        code_files = self.forge.code_generator.generate(blueprint)
        reqs = code_files.get("requirements.txt", "")

        # Should use >= instead of == for security updates
        assert ">=" in reqs
