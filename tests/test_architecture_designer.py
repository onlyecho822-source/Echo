"""
Tests for ArchitectureDesigner class
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo_forge import ArchitectureDesigner, AIType


class TestArchitectureDesigner:
    """Test suite for ArchitectureDesigner"""

    def setup_method(self):
        """Setup test fixtures"""
        self.designer = ArchitectureDesigner()

    def test_initialization(self):
        """Test that ArchitectureDesigner initializes correctly"""
        assert self.designer is not None

    def test_design_returns_dict(self):
        """Test that design returns a dictionary"""
        idea = {"ai_type": AIType.CHATBOT, "domain": "test"}
        architecture = self.designer.design(idea)
        assert isinstance(architecture, dict)

    def test_design_has_required_sections(self):
        """Test that architecture has all required sections"""
        idea = {"ai_type": AIType.ANALYZER, "domain": "test"}
        arch = self.designer.design(idea)

        assert "layers" in arch
        assert "components" in arch
        assert "data_flow" in arch
        assert "scaling_strategy" in arch
        assert "security" in arch

    def test_layers_structure(self):
        """Test that layers are properly structured"""
        idea = {"ai_type": AIType.CHATBOT, "domain": "test"}
        arch = self.designer.design(idea)

        layers = arch["layers"]
        assert len(layers) == 5
        assert "API Layer" in layers
        assert "AI/ML Processing Layer" in layers

    def test_components_have_core(self):
        """Test that components include core section"""
        idea = {"ai_type": AIType.PREDICTOR, "domain": "test"}
        arch = self.designer.design(idea)

        components = arch["components"]
        assert "core" in components
        assert "data" in components
        assert "monitoring" in components

    def test_agent_specific_components(self):
        """Test that agent types get specific components"""
        idea = {"ai_type": AIType.AGENT, "domain": "test"}
        arch = self.designer.design(idea)

        core = arch["components"]["core"]
        assert "Task Planner" in core
        assert "Execution Engine" in core

    def test_chatbot_specific_components(self):
        """Test that chatbot types get specific components"""
        idea = {"ai_type": AIType.CHATBOT, "domain": "test"}
        arch = self.designer.design(idea)

        core = arch["components"]["core"]
        assert "Context Manager" in core
        assert "Session Handler" in core

    def test_data_flow_complete(self):
        """Test that data flow is complete"""
        idea = {"ai_type": AIType.CLASSIFIER, "domain": "test"}
        arch = self.designer.design(idea)

        flow = arch["data_flow"]
        assert "Input Reception" in flow
        assert "AI Processing" in flow
        assert "Output Delivery" in flow

    def test_scaling_strategy_comprehensive(self):
        """Test that scaling strategy covers key areas"""
        idea = {"ai_type": AIType.GENERATOR, "domain": "test"}
        arch = self.designer.design(idea)

        scaling = arch["scaling_strategy"]
        assert "horizontal" in scaling
        assert "vertical" in scaling
        assert "caching" in scaling
        assert "async" in scaling

    def test_security_requirements_present(self):
        """Test that security requirements are included"""
        idea = {"ai_type": AIType.ASSISTANT, "domain": "test"}
        arch = self.designer.design(idea)

        security = arch["security"]
        assert "Input validation and sanitization" in security
        assert "API authentication" in security
        assert "Encryption at rest and in transit" in security

    def test_all_ai_types_supported(self):
        """Test that all AI types can be designed"""
        for ai_type in AIType:
            idea = {"ai_type": ai_type, "domain": "test"}
            arch = self.designer.design(idea)
            assert arch is not None
            assert len(arch) > 0
