#!/usr/bin/env python3
"""
Governance Enforcement Engine
Implements Class 0-3 rules with teeth

Based on Devil's Eye Audit recommendations
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from hashlib import sha256

class GovernanceEnforcer:
    """
    Actually enforces Class 0-3 rules
    
    Classes:
    - Class 0: Public knowledge (no restrictions)
    - Class 1: Single perspective (one steward)
    - Class 2: Multiple perspectives (contested, ≥2 stewards)
    - Class 3: Consensus reached (requires signatures)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            'consensus_threshold': 0.67,  # 67% agreement required
            'min_evidence_class_3': 3,     # Minimum evidence sources
            'max_steward_control': 0.30,   # No single steward >30% control
        }
        
        self.validation_log = []
    
    def validate_publication(self, claim: Dict, registry: Dict) -> Tuple[bool, str]:
        """
        Validate claim against governance rules
        
        Args:
            claim: Claim to validate
            registry: Current registry state
        
        Returns:
            (is_valid, reason)
        """
        
        # All claims require basic structure
        if not self._validate_structure(claim):
            return False, "Invalid claim structure"
        
        # Class-specific validation
        claim_class = claim.get("class", 0)
        
        if claim_class == 0:
            return self._validate_class_0(claim)
        elif claim_class == 1:
            return self._validate_class_1(claim)
        elif claim_class == 2:
            return self._validate_class_2(claim)
        elif claim_class == 3:
            return self._validate_class_3(claim, registry)
        else:
            return False, f"Invalid class: {claim_class}"
    
    def _validate_structure(self, claim: Dict) -> bool:
        """Validate basic claim structure"""
        required_fields = ['class', 'content', 'evidence_chain', 'timestamp']
        return all(field in claim for field in required_fields)
    
    def _validate_class_0(self, claim: Dict) -> Tuple[bool, str]:
        """
        Class 0: Public knowledge
        - No special restrictions
        - Must have evidence chain
        """
        if not claim.get("evidence_chain"):
            return False, "Class 0 requires evidence chain"
        
        return True, "Class 0 valid"
    
    def _validate_class_1(self, claim: Dict) -> Tuple[bool, str]:
        """
        Class 1: Single perspective
        - Exactly one perspective
        - One steward
        """
        perspectives = claim.get("perspectives", [])
        
        if len(perspectives) != 1:
            return False, "Class 1 requires exactly one perspective"
        
        if not claim.get("steward"):
            return False, "Class 1 requires steward"
        
        return True, "Class 1 valid"
    
    def _validate_class_2(self, claim: Dict) -> Tuple[bool, str]:
        """
        Class 2: Multiple perspectives (contested)
        - ≥2 perspectives
        - Must be marked contested
        - Must show all perspectives
        """
        perspectives = claim.get("perspectives", [])
        
        if len(perspectives) < 2:
            return False, "Class 2 requires ≥2 perspectives"
        
        if not claim.get("metadata", {}).get("contested", False):
            return False, "Class 2 must be marked contested"
        
        # Ensure all perspectives have equal visibility
        for perspective in perspectives:
            if not perspective.get("visible", True):
                return False, "Class 2 requires all perspectives visible"
        
        return True, "Class 2 valid"
    
    def _validate_class_3(self, claim: Dict, registry: Dict) -> Tuple[bool, str]:
        """
        Class 3: Consensus reached
        - Requires steward signatures
        - Sufficient consensus threshold
        - High-quality evidence
        """
        signatures = claim.get("signatures", [])
        
        if not signatures:
            return False, "Class 3 requires steward signatures"
        
        # Check consensus threshold
        if len(signatures) < self.consensus_threshold(claim, registry):
            return False, "Insufficient consensus signatures"
        
        # Verify signatures
        for sig in signatures:
            if not self._verify_signature(sig, claim, registry):
                return False, f"Invalid signature from {sig.get('steward')}"
        
        # Check evidence quality
        evidence_chain = claim.get("evidence_chain", [])
        if len(evidence_chain) < self.config['min_evidence_class_3']:
            return False, f"Class 3 requires ≥{self.config['min_evidence_class_3']} evidence sources"
        
        return True, "Class 3 valid"
    
    def consensus_threshold(self, claim: Dict, registry: Dict) -> int:
        """Calculate required number of signatures for consensus"""
        domain = claim.get("domain", "default")
        steward_count = len(registry.get("stewards", {}).get(domain, []))
        
        # Require 67% of stewards
        return max(2, int(steward_count * self.config['consensus_threshold']))
    
    def _verify_signature(self, signature: Dict, claim: Dict, registry: Dict) -> bool:
        """Verify cryptographic signature"""
        steward = signature.get("steward")
        sig_value = signature.get("signature")
        timestamp = signature.get("timestamp")
        
        if not all([steward, sig_value, timestamp]):
            return False
        
        # Get steward's public key from registry
        steward_info = registry.get("stewards", {}).get(steward)
        if not steward_info:
            return False
        
        public_key = steward_info.get("public_key")
        if not public_key:
            return False
        
        # Verify signature (simplified - real implementation would use cryptography)
        claim_hash = sha256(json.dumps(claim, sort_keys=True).encode()).hexdigest()
        expected_sig = sha256(f"{claim_hash}:{steward}:{public_key}".encode()).hexdigest()
        
        return sig_value == expected_sig
    
    def enforce_steward_limits(self, registry: Dict) -> List[str]:
        """
        Enforce steward control limits
        Returns list of violations
        """
        violations = []
        
        for domain, stewards in registry.get("stewards", {}).items():
            total_claims = registry.get("claim_counts", {}).get(domain, 0)
            
            for steward, info in stewards.items():
                steward_claims = info.get("claim_count", 0)
                control_pct = steward_claims / total_claims if total_claims > 0 else 0
                
                if control_pct > self.config['max_steward_control']:
                    violations.append(
                        f"Steward {steward} controls {control_pct*100:.1f}% of {domain} "
                        f"(max: {self.config['max_steward_control']*100}%)"
                    )
        
        return violations
    
    def log_validation(self, claim: Dict, is_valid: bool, reason: str):
        """Log validation for audit trail"""
        self.validation_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'claim_hash': sha256(json.dumps(claim, sort_keys=True).encode()).hexdigest(),
            'is_valid': is_valid,
            'reason': reason,
            'class': claim.get('class')
        })
    
    def get_audit_trail(self) -> List[Dict]:
        """Get complete validation audit trail"""
        return self.validation_log

def main():
    """Test governance enforcement"""
    print("="*60)
    print("GOVERNANCE ENFORCEMENT ENGINE")
    print("="*60)
    
    enforcer = GovernanceEnforcer()
    
    # Test claims
    test_claims = [
        {
            'name': 'Class 0: Public knowledge',
            'claim': {
                'class': 0,
                'content': 'The Earth orbits the Sun',
                'evidence_chain': ['astronomy_textbook_2024'],
                'timestamp': '2026-01-07T00:00:00Z'
            },
            'expected': True
        },
        {
            'name': 'Class 1: Single perspective',
            'claim': {
                'class': 1,
                'content': 'Modern art interpretation',
                'perspectives': [{'view': 'formalist', 'steward': 'art_historian_1'}],
                'steward': 'art_historian_1',
                'evidence_chain': ['art_analysis_2024'],
                'timestamp': '2026-01-07T00:00:00Z'
            },
            'expected': True
        },
        {
            'name': 'Class 2: Contested (INVALID - not marked)',
            'claim': {
                'class': 2,
                'content': 'Historical event interpretation',
                'perspectives': [
                    {'view': 'perspective_a', 'steward': 'historian_1'},
                    {'view': 'perspective_b', 'steward': 'historian_2'}
                ],
                'evidence_chain': ['source_1', 'source_2'],
                'timestamp': '2026-01-07T00:00:00Z'
            },
            'expected': False
        },
        {
            'name': 'Class 3: Consensus (INVALID - no signatures)',
            'claim': {
                'class': 3,
                'content': 'Consensus reached',
                'evidence_chain': ['source_1', 'source_2', 'source_3'],
                'timestamp': '2026-01-07T00:00:00Z'
            },
            'expected': False
        }
    ]
    
    registry = {
        'stewards': {
            'default': {
                'art_historian_1': {'public_key': 'key1', 'claim_count': 10},
                'historian_1': {'public_key': 'key2', 'claim_count': 15},
                'historian_2': {'public_key': 'key3', 'claim_count': 12}
            }
        },
        'claim_counts': {
            'default': 100
        }
    }
    
    for test in test_claims:
        print(f"\n{'='*60}")
        print(f"TEST: {test['name']}")
        print(f"{'='*60}")
        
        is_valid, reason = enforcer.validate_publication(test['claim'], registry)
        enforcer.log_validation(test['claim'], is_valid, reason)
        
        status = "✅ PASS" if is_valid == test['expected'] else "❌ FAIL"
        print(f"{status}: {reason}")
        print(f"Expected: {test['expected']}, Got: {is_valid}")
    
    print(f"\n{'='*60}")
    print("STEWARD CONTROL LIMITS")
    print(f"{'='*60}")
    violations = enforcer.enforce_steward_limits(registry)
    if violations:
        for violation in violations:
            print(f"⚠️  {violation}")
    else:
        print("✅ No violations")
    
    print(f"\n{'='*60}")
    print("AUDIT TRAIL")
    print(f"{'='*60}")
    print(f"Total validations: {len(enforcer.get_audit_trail())}")

if __name__ == "__main__":
    main()
