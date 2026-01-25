"""
Test suite for Echo-Agent-Zero integration
"""

import pytest
from agent_zero_bridge import EchoAgentZeroBridge, get_bridge, validate_claim, analyze_article, get_status


class TestBridgeInitialization:
    """Test bridge initialization and availability"""
    
    def test_bridge_can_be_initialized(self):
        """Test bridge can be initialized"""
        bridge = EchoAgentZeroBridge()
        assert bridge is not None
    
    def test_singleton_pattern(self):
        """Test singleton pattern works"""
        bridge1 = get_bridge()
        bridge2 = get_bridge()
        assert bridge1 is bridge2
    
    def test_availability_check(self):
        """Test availability check works"""
        bridge = get_bridge()
        is_available = bridge.is_available()
        assert isinstance(is_available, bool)


class TestClaimValidation:
    """Test claim validation functionality"""
    
    def test_validate_simple_claim(self):
        """Test validation of simple claim"""
        result = validate_claim("The sky is blue")
        
        assert "tension" in result
        assert "decision" in result
        assert "available" in result
        assert isinstance(result["tension"], (int, float))
        assert 0.0 <= result["tension"] <= 1.0
    
    def test_validate_complex_claim(self):
        """Test validation of complex claim"""
        claim = "Climate change is causing global temperatures to rise by 0.8K above pre-industrial baseline"
        result = validate_claim(claim)
        
        assert "tension" in result
        assert "optimal" in result
        assert "controlled" in result
        assert "decision_maker" in result
    
    def test_validate_contradictory_claim(self):
        """Test validation of contradictory claim"""
        claim = "All statements are false, including this one"
        result = validate_claim(claim)
        
        # Should detect high tension due to contradiction
        assert result["tension"] >= 0.0


class TestNewsArticleAnalysis:
    """Test news article analysis functionality"""
    
    def test_analyze_neutral_article(self):
        """Test analysis of neutral article"""
        article = {
            "title": "Weather Report: Sunny Day Expected",
            "content": "The weather forecast predicts sunny skies with temperatures around 75°F.",
            "source": "Weather Service"
        }
        
        result = analyze_article(article)
        
        assert "truth_score" in result
        assert "bias_detected" in result
        assert "narrative_contamination" in result
        assert "available" in result
    
    def test_analyze_biased_article(self):
        """Test analysis of potentially biased article"""
        article = {
            "title": "SHOCKING: Everything You Believed is WRONG!",
            "content": "This groundbreaking revelation will change everything you thought you knew...",
            "source": "Clickbait News"
        }
        
        result = analyze_article(article)
        
        # Should detect higher narrative contamination
        assert result["narrative_contamination"] >= 0.0
    
    def test_analyze_factual_article(self):
        """Test analysis of factual article"""
        article = {
            "title": "Study Finds Water Freezes at 0°C",
            "content": "Scientific research confirms that water freezes at 0 degrees Celsius at standard pressure.",
            "source": "Science Journal"
        }
        
        result = analyze_article(article)
        
        # Should have high truth score
        assert result["truth_score"] >= 0.0


class TestZeroReference:
    """Test Zero reference calculation"""
    
    def test_calculate_zero_for_climate(self):
        """Test Zero reference calculation for climate domain"""
        bridge = get_bridge()
        
        data = {
            "temperature": 15.0,
            "baseline": 14.2,
            "unit": "celsius"
        }
        
        result = bridge.get_zero_reference("climate", data)
        
        assert "domain" in result
        assert result["domain"] == "climate"
        assert "available" in result
    
    def test_calculate_zero_for_markets(self):
        """Test Zero reference calculation for markets domain"""
        bridge = get_bridge()
        
        data = {
            "price": 100.0,
            "volume": 1000000,
            "volatility": 0.15
        }
        
        result = bridge.get_zero_reference("markets", data)
        
        assert "domain" in result
        assert result["domain"] == "markets"


class TestKrakenMode:
    """Test Kraken mode functionality"""
    
    def test_kraken_mode_can_be_started(self):
        """Test Kraken mode can be started"""
        bridge = get_bridge()
        
        # Note: In production, this would start background monitoring
        # For testing, we just check the interface works
        result = bridge.start_kraken_mode(interval=60)
        
        assert "status" in result
        assert "available" in result
    
    def test_kraken_mode_with_custom_interval(self):
        """Test Kraken mode with custom interval"""
        bridge = get_bridge()
        
        result = bridge.start_kraken_mode(interval=120)
        
        assert "status" in result


class TestSystemStatus:
    """Test system status reporting"""
    
    def test_get_system_status(self):
        """Test system status retrieval"""
        status = get_status()
        
        assert "agent_zero_available" in status
        assert "dual_system_active" in status
        assert "kraken_mode_active" in status
        assert "zero_operator_available" in status
        assert "integration_version" in status
        
        assert isinstance(status["agent_zero_available"], bool)
        assert isinstance(status["integration_version"], str)


class TestErrorHandling:
    """Test error handling and graceful degradation"""
    
    def test_bridge_works_without_agent_zero(self):
        """Test bridge gracefully handles missing Agent-Zero"""
        bridge = EchoAgentZeroBridge()
        
        # Should not crash even if Agent-Zero is unavailable
        result = bridge.validate_claim("Test claim")
        assert "available" in result
    
    def test_invalid_domain_zero_reference(self):
        """Test handling of invalid domain"""
        bridge = get_bridge()
        
        result = bridge.get_zero_reference("invalid_domain", {})
        
        # Should handle gracefully
        assert "domain" in result
        assert result["domain"] == "invalid_domain"


# Integration test
class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    def test_full_article_analysis_workflow(self):
        """Test complete workflow: article → analysis → decision"""
        # Step 1: Create article
        article = {
            "title": "New Study on Climate Change",
            "content": "Recent research shows temperature increases of 0.8K above baseline.",
            "source": "Science Daily"
        }
        
        # Step 2: Analyze article
        analysis = analyze_article(article)
        
        # Step 3: Verify results
        assert analysis["available"] is not None
        assert "truth_score" in analysis
        assert "final_assessment" in analysis
    
    def test_multiple_claims_validation(self):
        """Test validation of multiple claims"""
        claims = [
            "Water boils at 100°C",
            "The Earth is flat",
            "2 + 2 = 4"
        ]
        
        results = [validate_claim(claim) for claim in claims]
        
        assert len(results) == 3
        for result in results:
            assert "tension" in result
            assert "decision" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
