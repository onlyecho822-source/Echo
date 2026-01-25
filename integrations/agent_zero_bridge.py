"""
Echo ↔ Agent-Zero Integration Bridge
Provides interface between Echo and Agent-Zero subsystems
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add Agent-Zero to Python path
AGENT_ZERO_PATH = Path(__file__).parent.parent / "agent-zero" / "src"
sys.path.insert(0, str(AGENT_ZERO_PATH))

try:
    # Import Agent-Zero components
    from autonomous.dual_system import DualSystemAgentZero
    from autonomous.kraken_agent_zero import KrakenAgentZero
    from core.zero_operator import ZeroOperator
    AGENT_ZERO_AVAILABLE = True
except ImportError:
    AGENT_ZERO_AVAILABLE = False
    print("Warning: Agent-Zero submodule not available. Integration features disabled.")


class EchoAgentZeroBridge:
    """
    Bridge between Echo and Agent-Zero
    Provides controlled access to Agent-Zero capabilities
    """
    
    def __init__(self):
        if not AGENT_ZERO_AVAILABLE:
            self.agent_zero = None
            self.kraken = None
            self.zero_op = None
            return
        
        self.agent_zero = DualSystemAgentZero()
        self.kraken = None  # Lazy initialization
        self.zero_op = ZeroOperator()
    
    def is_available(self) -> bool:
        """Check if Agent-Zero is available"""
        return AGENT_ZERO_AVAILABLE and self.agent_zero is not None
    
    def validate_claim(self, claim: str) -> Dict[str, Any]:
        """
        Validate a claim using Agent-Zero's dual-system
        
        Args:
            claim: The claim to validate
        
        Returns:
            {
                "tension": float,
                "optimal": str,
                "controlled": str,
                "decision": str,
                "decision_maker": str,
                "available": bool
            }
        """
        if not self.is_available():
            return {
                "tension": 0.0,
                "optimal": "Agent-Zero not available",
                "controlled": "Agent-Zero not available",
                "decision": "Cannot validate - Agent-Zero not available",
                "decision_maker": "None",
                "available": False
            }
        
        decision = self.agent_zero.operate(claim)
        return {
            "tension": decision.tension,
            "optimal": decision.uncontrolled_optimal,
            "controlled": decision.controlled_alternative,
            "decision": decision.final_decision,
            "decision_maker": decision.decision_maker,
            "available": True
        }
    
    def start_kraken_mode(self, interval: int = 300) -> Dict[str, Any]:
        """
        Start continuous Kraken monitoring
        
        Args:
            interval: Monitoring cycle interval in seconds (default: 300 = 5 minutes)
        
        Returns:
            Status dictionary
        """
        if not self.is_available():
            return {
                "status": "error",
                "message": "Agent-Zero not available",
                "available": False
            }
        
        if self.kraken is None:
            self.kraken = KrakenAgentZero()
        
        try:
            # Start in background (would need threading in production)
            self.kraken.run_continuous(cycle_interval=interval)
            return {
                "status": "started",
                "interval": interval,
                "available": True
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "available": True
            }
    
    def get_zero_reference(self, domain: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Zero reference for a domain
        
        Args:
            domain: Domain name (e.g., "climate", "markets", "news")
            data: Domain-specific data
        
        Returns:
            Zero reference calculation
        """
        if not self.is_available():
            return {
                "domain": domain,
                "zero_reference": None,
                "confidence": 0.0,
                "available": False,
                "message": "Agent-Zero not available"
            }
        
        try:
            # Calculate Zero reference using ZeroOperator
            result = self.zero_op.calculate_zero(domain, data)
            return {
                "domain": domain,
                "zero_reference": result.get("zero_value"),
                "confidence": result.get("confidence", 0.0),
                "symmetry_score": result.get("symmetry_score", 0.0),
                "available": True
            }
        except Exception as e:
            return {
                "domain": domain,
                "zero_reference": None,
                "confidence": 0.0,
                "available": True,
                "error": str(e)
            }
    
    def analyze_news_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a news article for truth and bias
        
        Args:
            article: Dictionary with 'title', 'content', 'source', etc.
        
        Returns:
            Analysis results
        """
        if not self.is_available():
            return {
                "truth_score": 0.0,
                "bias_detected": False,
                "narrative_contamination": 0.0,
                "available": False
            }
        
        # Create claim from article
        claim = f"Article: {article.get('title', 'Unknown')}. Content: {article.get('content', '')[:500]}"
        
        # Validate through dual-system
        validation = self.validate_claim(claim)
        
        # Calculate metrics
        truth_score = 1.0 - validation['tension']  # Lower tension = higher truth
        bias_detected = validation['tension'] > 0.5
        narrative_contamination = validation['tension']
        
        return {
            "truth_score": truth_score,
            "bias_detected": bias_detected,
            "narrative_contamination": narrative_contamination,
            "optimal_interpretation": validation['optimal'],
            "controlled_interpretation": validation['controlled'],
            "final_assessment": validation['decision'],
            "available": True
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current status of Agent-Zero integration
        
        Returns:
            Status dictionary
        """
        return {
            "agent_zero_available": self.is_available(),
            "dual_system_active": self.agent_zero is not None,
            "kraken_mode_active": self.kraken is not None,
            "zero_operator_available": self.zero_op is not None,
            "integration_version": "1.0.0"
        }


# Singleton instance
_bridge_instance: Optional[EchoAgentZeroBridge] = None


def get_bridge() -> EchoAgentZeroBridge:
    """Get singleton bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = EchoAgentZeroBridge()
    return _bridge_instance


# Convenience functions
def validate_claim(claim: str) -> Dict[str, Any]:
    """Validate a claim using Agent-Zero"""
    return get_bridge().validate_claim(claim)


def analyze_article(article: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a news article"""
    return get_bridge().analyze_news_article(article)


def get_status() -> Dict[str, Any]:
    """Get integration status"""
    return get_bridge().get_system_status()
