"""
Tests for IdeaGenerator class
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo_forge import IdeaGenerator, AIType


class TestIdeaGenerator:
    """Test suite for IdeaGenerator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.generator = IdeaGenerator()

    def test_initialization(self):
        """Test that IdeaGenerator initializes correctly"""
        assert self.generator is not None
        assert len(self.generator.idea_templates) > 0

    def test_generate_idea_returns_dict(self):
        """Test that generate_idea returns a dictionary"""
        idea = self.generator.generate_idea()
        assert isinstance(idea, dict)

    def test_generate_idea_has_required_fields(self):
        """Test that generated idea has all required fields"""
        idea = self.generator.generate_idea("healthcare")

        assert "domain" in idea
        assert "ai_type" in idea
        assert "pattern" in idea
        assert "description" in idea
        assert "potential_features" in idea

    def test_generate_idea_domain(self):
        """Test that domain is correctly set"""
        domain = "finance"
        idea = self.generator.generate_idea(domain)
        assert idea["domain"] == domain

    def test_generate_idea_ai_type_is_valid(self):
        """Test that generated AI type is valid"""
        idea = self.generator.generate_idea()
        assert isinstance(idea["ai_type"], AIType)
        assert idea["ai_type"] in list(AIType)

    def test_generate_idea_features_not_empty(self):
        """Test that features list is not empty"""
        idea = self.generator.generate_idea()
        assert len(idea["potential_features"]) > 0

    def test_generate_features_chatbot(self):
        """Test feature generation for chatbot"""
        features = self.generator._generate_features(AIType.CHATBOT, "test")
        assert "Natural language understanding" in features

    def test_generate_features_analyzer(self):
        """Test feature generation for analyzer"""
        features = self.generator._generate_features(AIType.ANALYZER, "test")
        assert "Data ingestion pipeline" in features

    def test_generate_features_agent(self):
        """Test feature generation for agent"""
        features = self.generator._generate_features(AIType.AGENT, "test")
        assert "Goal-based planning" in features

    def test_template_patterns_valid(self):
        """Test that all template patterns are valid"""
        valid_patterns = ["data_analysis", "content_generation", "decision_making", "classification", "conversation"]
        for template in self.generator.idea_templates:
            assert template["pattern"] in valid_patterns

    def test_multiple_generations_unique(self):
        """Test that multiple generations can produce different results"""
        ideas = [self.generator.generate_idea("test") for _ in range(10)]
        # At least some variety in AI types
        ai_types = set(idea["ai_type"] for idea in ideas)
        assert len(ai_types) >= 2
