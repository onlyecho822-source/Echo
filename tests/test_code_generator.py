"""
Tests for CodeGenerator class
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo_forge import CodeGenerator, AppBlueprint, AIType, TechStack
from datetime import datetime


class TestCodeGenerator:
    """Test suite for CodeGenerator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.generator = CodeGenerator()
        self.sample_blueprint = AppBlueprint(
            name="Test App",
            description="Test application",
            ai_type=AIType.CHATBOT,
            tech_stack=TechStack.PYTHON_FASTAPI,
            features=["Feature 1", "Feature 2"],
            architecture={},
            dependencies=[],
            created_at=datetime.now().isoformat()
        )

    def test_initialization(self):
        """Test that CodeGenerator initializes correctly"""
        assert self.generator is not None

    def test_generate_returns_dict(self):
        """Test that generate returns a dictionary"""
        files = self.generator.generate(self.sample_blueprint)
        assert isinstance(files, dict)

    def test_generate_creates_common_files(self):
        """Test that common files are generated"""
        files = self.generator.generate(self.sample_blueprint)

        assert "README.md" in files
        assert "Dockerfile" in files
        assert ".gitignore" in files
        assert "config.json" in files

    def test_fastapi_generation(self):
        """Test FastAPI application generation"""
        blueprint = AppBlueprint(
            name="API Test",
            description="Test API",
            ai_type=AIType.CHATBOT,
            tech_stack=TechStack.PYTHON_FASTAPI,
            features=[],
            architecture={},
            dependencies=[],
            created_at=datetime.now().isoformat()
        )
        files = self.generator.generate(blueprint)

        assert "api.py" in files
        assert "from fastapi import" in files["api.py"]
        assert "requirements.txt" in files

    def test_python_ml_generation(self):
        """Test Python ML application generation"""
        blueprint = AppBlueprint(
            name="ML Test",
            description="Test ML",
            ai_type=AIType.ANALYZER,
            tech_stack=TechStack.PYTHON_ML,
            features=[],
            architecture={},
            dependencies=[],
            created_at=datetime.now().isoformat()
        )
        files = self.generator.generate(blueprint)

        assert "main.py" in files
        assert "requirements.txt" in files

    def test_nodejs_generation(self):
        """Test Node.js application generation"""
        blueprint = AppBlueprint(
            name="Node Test",
            description="Test Node",
            ai_type=AIType.CHATBOT,
            tech_stack=TechStack.JAVASCRIPT_NODE,
            features=[],
            architecture={},
            dependencies=[],
            created_at=datetime.now().isoformat()
        )
        files = self.generator.generate(blueprint)

        assert "index.js" in files
        assert "package.json" in files
        assert "express" in files["package.json"]

    def test_agent_generation(self):
        """Test autonomous agent generation"""
        blueprint = AppBlueprint(
            name="Agent Test",
            description="Test Agent",
            ai_type=AIType.AGENT,
            tech_stack=TechStack.AUTONOMOUS_AGENT,
            features=[],
            architecture={},
            dependencies=[],
            created_at=datetime.now().isoformat()
        )
        files = self.generator.generate(blueprint)

        assert "agent.py" in files
        assert "asyncio" in files["agent.py"]
        assert "AgentState" in files["agent.py"]

    def test_requirements_generation_analyzer(self):
        """Test requirements generation for analyzer type"""
        blueprint = AppBlueprint(
            name="Test",
            description="Test",
            ai_type=AIType.ANALYZER,
            tech_stack=TechStack.PYTHON_ML,
            features=[],
            architecture={},
            dependencies=[],
            created_at=datetime.now().isoformat()
        )
        reqs = self.generator._generate_requirements(blueprint)

        assert "numpy" in reqs
        assert "pandas" in reqs
        assert "scikit-learn" in reqs

    def test_requirements_generation_chatbot(self):
        """Test requirements generation for chatbot type"""
        blueprint = AppBlueprint(
            name="Test",
            description="Test",
            ai_type=AIType.CHATBOT,
            tech_stack=TechStack.PYTHON_FASTAPI,
            features=[],
            architecture={},
            dependencies=[],
            created_at=datetime.now().isoformat()
        )
        reqs = self.generator._generate_requirements(blueprint)

        assert "openai" in reqs or "anthropic" in reqs

    def test_dockerfile_valid(self):
        """Test that generated Dockerfile is valid"""
        files = self.generator.generate(self.sample_blueprint)
        dockerfile = files["Dockerfile"]

        assert "FROM python:" in dockerfile
        assert "WORKDIR" in dockerfile
        assert "requirements.txt" in dockerfile

    def test_readme_contains_info(self):
        """Test that README contains blueprint information"""
        files = self.generator.generate(self.sample_blueprint)
        readme = files["README.md"]

        assert self.sample_blueprint.name in readme
        assert self.sample_blueprint.description in readme
        assert self.sample_blueprint.ai_type.value in readme

    def test_gitignore_comprehensive(self):
        """Test that .gitignore covers common cases"""
        files = self.generator.generate(self.sample_blueprint)
        gitignore = files[".gitignore"]

        assert "__pycache__" in gitignore
        assert ".env" in gitignore
        assert "venv" in gitignore
        assert "node_modules" in gitignore

    def test_config_json_valid(self):
        """Test that config.json is valid JSON"""
        import json
        files = self.generator.generate(self.sample_blueprint)
        config_str = files["config.json"]

        config = json.loads(config_str)
        assert "app_name" in config
        assert config["app_name"] == self.sample_blueprint.name
