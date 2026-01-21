#!/usr/bin/env python3
"""
EMPIRICAL GATE — Claim Validation System
=========================================
Every claim must have:
1. METRIC - A number that can embarrass you
2. EVIDENCE - Artifact or log proving the number
3. CONFIDENCE - Verified (0.9+) / Supported (0.7-0.9) / Hypothesis (<0.7)

No claim passes without all three.

∇θ Echo Signal Detector
"""

import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List
from enum import Enum

class ConfidenceLevel(Enum):
    VERIFIED = "verified"      # 0.9+ - Multiple independent validations
    SUPPORTED = "supported"    # 0.7-0.9 - Single validation or strong correlation
    HYPOTHESIS = "hypothesis"  # <0.7 - Theoretical or untested

@dataclass
class Claim:
    """A claim that must pass the Empirical Gate."""
    id: str
    statement: str
    metric: str
    metric_value: float
    evidence: str
    evidence_artifact: Optional[str]
    confidence_score: float
    confidence_level: ConfidenceLevel
    timestamp: str
    validated: bool = False
    validation_notes: str = ""

class EmpiricalGate:
    """Enforces empirical validation on all claims."""
    
    def __init__(self):
        self.claims: List[Claim] = []
        self.gate_log: List[dict] = []
        
    def submit_claim(self, 
                     statement: str,
                     metric: str,
                     metric_value: float,
                     evidence: str,
                     evidence_artifact: Optional[str] = None,
                     confidence_score: float = 0.5) -> Claim:
        """
        Submit a claim for validation.
        
        Args:
            statement: The claim being made
            metric: What number proves/disproves this
            metric_value: The actual measured value
            evidence: Description of how this was measured
            evidence_artifact: Path to log/file/artifact
            confidence_score: 0.0 to 1.0
        """
        
        # Determine confidence level
        if confidence_score >= 0.9:
            level = ConfidenceLevel.VERIFIED
        elif confidence_score >= 0.7:
            level = ConfidenceLevel.SUPPORTED
        else:
            level = ConfidenceLevel.HYPOTHESIS
        
        # Generate claim ID
        claim_id = hashlib.sha256(
            f"{statement}{metric}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]
        
        claim = Claim(
            id=claim_id,
            statement=statement,
            metric=metric,
            metric_value=metric_value,
            evidence=evidence,
            evidence_artifact=evidence_artifact,
            confidence_score=confidence_score,
            confidence_level=level,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        self.claims.append(claim)
        self._log_gate_event("CLAIM_SUBMITTED", claim)
        
        return claim
    
    def validate_claim(self, claim_id: str, validation_result: bool, notes: str = "") -> bool:
        """
        Validate or invalidate a claim.
        
        Args:
            claim_id: The claim to validate
            validation_result: True if validated, False if invalidated
            notes: Additional validation notes
        """
        for claim in self.claims:
            if claim.id == claim_id:
                claim.validated = validation_result
                claim.validation_notes = notes
                self._log_gate_event(
                    "CLAIM_VALIDATED" if validation_result else "CLAIM_INVALIDATED",
                    claim
                )
                return True
        return False
    
    def check_claim(self, claim: Claim) -> dict:
        """
        Check if a claim passes the Empirical Gate.
        
        Returns dict with:
        - passes: bool
        - issues: list of problems
        - recommendations: list of fixes
        """
        issues = []
        recommendations = []
        
        # Check metric exists
        if not claim.metric or claim.metric.strip() == "":
            issues.append("MISSING_METRIC: No measurable metric defined")
            recommendations.append("Define a specific, measurable metric")
        
        # Check evidence exists
        if not claim.evidence or claim.evidence.strip() == "":
            issues.append("MISSING_EVIDENCE: No evidence provided")
            recommendations.append("Provide evidence artifact or measurement log")
        
        # Check confidence is reasonable
        if claim.confidence_score > 0.9 and not claim.evidence_artifact:
            issues.append("OVERCONFIDENT: High confidence without artifact")
            recommendations.append("Provide evidence artifact for verified claims")
        
        # Check for marketing language
        marketing_words = ["revolutionary", "game-changing", "unprecedented", 
                         "best-in-class", "world-class", "cutting-edge"]
        for word in marketing_words:
            if word.lower() in claim.statement.lower():
                issues.append(f"MARKETING_LANGUAGE: '{word}' detected")
                recommendations.append("Remove marketing language, use precise terms")
        
        # Check for unbounded claims
        unbounded_words = ["always", "never", "perfect", "guaranteed", "100%"]
        for word in unbounded_words:
            if word.lower() in claim.statement.lower():
                issues.append(f"UNBOUNDED_CLAIM: '{word}' detected")
                recommendations.append("Add bounds and conditions to claim")
        
        passes = len(issues) == 0
        
        result = {
            "claim_id": claim.id,
            "passes": passes,
            "confidence_level": claim.confidence_level.value,
            "issues": issues,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        self._log_gate_event("GATE_CHECK", result)
        
        return result
    
    def _log_gate_event(self, event_type: str, data):
        """Log gate events for audit trail."""
        self.gate_log.append({
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": asdict(data) if hasattr(data, '__dataclass_fields__') else data
        })
    
    def get_all_claims(self) -> List[dict]:
        """Get all claims as dictionaries."""
        return [asdict(c) for c in self.claims]
    
    def get_claims_by_level(self, level: ConfidenceLevel) -> List[Claim]:
        """Get claims filtered by confidence level."""
        return [c for c in self.claims if c.confidence_level == level]
    
    def generate_report(self) -> dict:
        """Generate Empirical Gate status report."""
        total = len(self.claims)
        verified = len(self.get_claims_by_level(ConfidenceLevel.VERIFIED))
        supported = len(self.get_claims_by_level(ConfidenceLevel.SUPPORTED))
        hypothesis = len(self.get_claims_by_level(ConfidenceLevel.HYPOTHESIS))
        validated = len([c for c in self.claims if c.validated])
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_claims": total,
            "by_confidence": {
                "verified": verified,
                "supported": supported,
                "hypothesis": hypothesis
            },
            "validation_status": {
                "validated": validated,
                "pending": total - validated
            },
            "empirical_score": verified / max(total, 1),
            "claims": self.get_all_claims()
        }


# Pre-defined claims for Echo Signal Detector
def register_echo_claims(gate: EmpiricalGate):
    """Register all current Echo Signal Detector claims."""
    
    # Claim 1: API Success Rate
    gate.submit_claim(
        statement="Echo Signal Detector has 88.5% API success rate",
        metric="API calls successful / API calls attempted",
        metric_value=0.885,
        evidence="Measured across 26 API endpoints on 2026-01-21",
        evidence_artifact=".github/intel/INTEL_REPORT_2026-01-21.md",
        confidence_score=0.90
    )
    
    # Claim 2: SEISMIC Signal
    gate.submit_claim(
        statement="M6+ earthquakes correlate with TRV underperformance",
        metric="Average TRV return on day after M6+ earthquake",
        metric_value=-0.0012,  # -0.12%
        evidence="Backtest on 30-day window, 4 events",
        evidence_artifact="echonate_backtest_results.json",
        confidence_score=0.65  # Hypothesis - insufficient sample
    )
    
    # Claim 3: WSB Sentiment
    gate.submit_claim(
        statement="WSB sentiment ratio above 4.0 indicates extreme bullishness",
        metric="Bullish posts score / Bearish posts score",
        metric_value=4.37,
        evidence="Reddit API pull on 2026-01-21, 25 posts analyzed",
        evidence_artifact=None,
        confidence_score=0.70  # Supported - single measurement
    )
    
    # Claim 4: GitHub Workflow Success
    gate.submit_claim(
        statement="GitHub Actions workflows have 65% success rate",
        metric="Successful runs / Total runs (last 20)",
        metric_value=0.65,
        evidence="gh run list --limit 20 on 2026-01-21",
        evidence_artifact=None,
        confidence_score=0.95  # Verified - direct measurement
    )
    
    # Claim 5: Customer Count (Embarrassing)
    gate.submit_claim(
        statement="Echo Signal Detector has zero paying customers",
        metric="Number of paying customers",
        metric_value=0,
        evidence="No payment system implemented, no users onboarded",
        evidence_artifact=None,
        confidence_score=1.0  # Verified - unfortunately true
    )
    
    # Claim 6: Revenue (Embarrassing)
    gate.submit_claim(
        statement="Echo Signal Detector has generated $0 revenue",
        metric="Total revenue in USD",
        metric_value=0.0,
        evidence="No monetization implemented",
        evidence_artifact=None,
        confidence_score=1.0  # Verified - unfortunately true
    )
    
    return gate


if __name__ == "__main__":
    print("=" * 60)
    print("EMPIRICAL GATE — Claim Validation System")
    print("=" * 60)
    print()
    
    # Initialize gate
    gate = EmpiricalGate()
    
    # Register Echo claims
    gate = register_echo_claims(gate)
    
    # Check all claims
    print("CLAIM VALIDATION:")
    print("-" * 40)
    for claim in gate.claims:
        result = gate.check_claim(claim)
        status = "✅ PASSES" if result["passes"] else "❌ FAILS"
        print(f"{status} [{claim.confidence_level.value.upper()}] {claim.statement[:50]}...")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"   ⚠️ {issue}")
    
    print()
    print("EMPIRICAL GATE REPORT:")
    print("-" * 40)
    report = gate.generate_report()
    print(f"Total Claims: {report['total_claims']}")
    print(f"  Verified: {report['by_confidence']['verified']}")
    print(f"  Supported: {report['by_confidence']['supported']}")
    print(f"  Hypothesis: {report['by_confidence']['hypothesis']}")
    print(f"Empirical Score: {report['empirical_score']:.2%}")
    
    print()
    print("=" * 60)
    print(json.dumps(report, indent=2, default=str))
