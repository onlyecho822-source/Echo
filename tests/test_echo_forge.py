"""
Tests for EchoForge main class
"""

import pytest
import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo_forge import EchoForge, AIType, TechStack


class TestEchoForge:
    """Test suite for EchoForge main class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.forge = EchoForge()
        # Clean up any test artifacts
        if os.path.exists("generated_apps/test_*"):
            shutil.rmtree("generated_apps/test_*", ignore_errors=True)

    def teardown_method(self):
        """Cleanup after tests"""
        # Remove test generated apps
        for app in self.forge.created_apps:
            app_dir = f"generated_apps/{app.name.lower().replace(' ', '_')}"
            if os.path.exists(app_dir) and "test" in app_dir.lower():
                shutil.rmtree(app_dir, ignore_errors=True)

    def test_initialization(self):
        """Test that EchoForge initializes correctly"""
        assert self.forge is not None
        assert self.forge.idea_generator is not None
        assert self.forge.architect is not None
        assert self.forge.code_generator is not None
        assert len(self.forge.created_apps) == 0

    def test_create_app_returns_blueprint(self):
        """Test that create_app returns an AppBlueprint"""
        blueprint = self.forge.create_app(domain="test")
        assert blueprint is not None
        assert hasattr(blueprint, 'name')
        assert hasattr(blueprint, 'ai_type')

    def test_create_app_with_domain(self):
        """Test app creation with specific domain"""
        blueprint = self.forge.create_app(domain="healthcare")
        assert "healthcare" in blueprint.name.lower() or "Healthcare" in blueprint.name

    def test_create_app_with_ai_type(self):
        """Test app creation with specific AI type"""
        blueprint = self.forge.create_app(
            domain="test",
            ai_type=AIType.CHATBOT
        )
        assert blueprint.ai_type == AIType.CHATBOT

    def test_create_app_with_tech_stack(self):
        """Test app creation with specific tech stack"""
        blueprint = self.forge.create_app(
            domain="test",
            tech_stack=TechStack.PYTHON_FASTAPI
        )
        assert blueprint.tech_stack == TechStack.PYTHON_FASTAPI

    def test_create_app_with_custom_features(self):
        """Test app creation with custom features"""
        custom = ["Custom Feature 1", "Custom Feature 2"]
        blueprint = self.forge.create_app(
            domain="test",
            custom_features=custom
        )
        assert "Custom Feature 1" in blueprint.features
        assert "Custom Feature 2" in blueprint.features

    def test_created_apps_tracking(self):
        """Test that created apps are tracked"""
        initial_count = len(self.forge.created_apps)
        self.forge.create_app(domain="test1")
        self.forge.create_app(domain="test2")
        assert len(self.forge.created_apps) == initial_count + 2

    def test_list_created_apps(self):
        """Test listing created applications"""
        self.forge.create_app(domain="test")
        apps = self.forge.list_created_apps()
        assert isinstance(apps, list)
        assert len(apps) > 0
        assert isinstance(apps[0], dict)

    def test_create_multiple_apps(self):
        """Test creating multiple apps at once"""
        blueprints = self.forge.create_multiple_apps(count=3, domain="testmulti")
        assert len(blueprints) == 3
        for bp in blueprints:
            assert bp is not None

    def test_app_files_created(self):
        """Test that app files are actually created on disk"""
        blueprint = self.forge.create_app(domain="testfiles")
        app_dir = f"generated_apps/{blueprint.name.lower().replace(' ', '_')}"

        assert os.path.exists(app_dir)
        assert os.path.exists(os.path.join(app_dir, "blueprint.json"))
        assert os.path.exists(os.path.join(app_dir, "README.md"))

    def test_blueprint_json_saved(self):
        """Test that blueprint is saved as JSON"""
        import json
        blueprint = self.forge.create_app(domain="testjson")
        app_dir = f"generated_apps/{blueprint.name.lower().replace(' ', '_')}"
        blueprint_path = os.path.join(app_dir, "blueprint.json")

        with open(blueprint_path) as f:
            saved_bp = json.load(f)

        assert saved_bp["name"] == blueprint.name
        assert saved_bp["ai_type"] == blueprint.ai_type.value


class TestEchoForgeIntegration:
    """Integration tests for full pipeline"""

    def setup_method(self):
        """Setup test fixtures"""
        self.forge = EchoForge()

    def teardown_method(self):
        """Cleanup after tests"""
        for app in self.forge.created_apps:
            app_dir = f"generated_apps/{app.name.lower().replace(' ', '_')}"
            if os.path.exists(app_dir) and "integration" in app_dir.lower():
                shutil.rmtree(app_dir, ignore_errors=True)

    def test_end_to_end_fastapi_app(self):
        """Test complete FastAPI app generation"""
        blueprint = self.forge.create_app(
            domain="integration_test",
            ai_type=AIType.CHATBOT,
            tech_stack=TechStack.PYTHON_FASTAPI
        )

        app_dir = f"generated_apps/{blueprint.name.lower().replace(' ', '_')}"
        assert os.path.exists(os.path.join(app_dir, "api.py"))
        assert os.path.exists(os.path.join(app_dir, "requirements.txt"))
        assert os.path.exists(os.path.join(app_dir, "Dockerfile"))

    def test_end_to_end_ml_app(self):
        """Test complete ML app generation"""
        blueprint = self.forge.create_app(
            domain="integration_ml",
            ai_type=AIType.ANALYZER,
            tech_stack=TechStack.PYTHON_ML
        )

        app_dir = f"generated_apps/{blueprint.name.lower().replace(' ', '_')}"
        assert os.path.exists(os.path.join(app_dir, "main.py"))

    def test_end_to_end_agent_app(self):
        """Test complete agent app generation"""
        blueprint = self.forge.create_app(
            domain="integration_agent",
            ai_type=AIType.AGENT,
            tech_stack=TechStack.AUTONOMOUS_AGENT
        )

        app_dir = f"generated_apps/{blueprint.name.lower().replace(' ', '_')}"
        assert os.path.exists(os.path.join(app_dir, "agent.py"))
