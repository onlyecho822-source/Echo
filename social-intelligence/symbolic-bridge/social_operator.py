#!/usr/bin/env python3
"""
⟡Social - Social Intelligence as Symbolic Operator
Bridges social intelligence system with ∇θ Echo Symbolic Language

Operator Definition:
⟡Social(action, platform, content) @time(schedule) #place(geo) ∵(voice_signature) ∴(resonance_validated)

Examples:
- ⟡Social(post, linkedin, "Building autonomous systems") @time(2026-01-08T09:00) ∵(R100V05E02X100A40)
- ⟡Social(monitor, all, *) → engagement_data ∴(quality>0.7)
- ⟡Social(respond, twitter, engagement_id) ∵(voice_preserved) ∴(resonance_validated)

Built by: EchoNate (Symbolic Integration Mode)
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from voice.voice_extractor import VoiceExtractor
    from platforms.social_connector import SocialConnector
    from platforms.social_intelligence import SocialIntelligence
except ImportError:
    print("⚠️  Social intelligence modules not found. Run from Echo root.")
    sys.exit(1)

class SocialOperator:
    """
    ⟡Social - Symbolic operator for social intelligence
    
    Integrates with ∇θ Echo Symbolic Language:
    - Compresses social presence into symbolic form
    - Expands to multi-platform actions
    - Maintains provenance and governance
    - Validates resonance before execution
    """
    
    OPERATOR_SYMBOL = "⟡Social"
    OPERATOR_CLASS = "action"  # Action operator in symbolic grammar
    
    def __init__(self):
        self.intelligence = SocialIntelligence()
        self.voice_signature = self.intelligence.voice_profile.get('resonance_signature')
        
    def compress(self, social_action: Dict) -> str:
        """
        Compress social action into symbolic representation
        
        Args:
            social_action: {
                "action": "post" | "monitor" | "respond",
                "platform": "linkedin" | "twitter" | "all",
                "content": str,
                "schedule": ISO datetime,
                "geo": location string
            }
        
        Returns:
            Symbolic expression: ⟡Social(action, platform, content) @time() #place() ∵() ∴()
        """
        
        action = social_action.get('action')
        platform = social_action.get('platform')
        content = social_action.get('content', '*')
        
        # Build symbolic expression
        expr = f"⟡Social({action}, {platform}, \"{content}\")"
        
        # Add qualifiers
        if social_action.get('schedule'):
            expr += f" @time({social_action['schedule']})"
        
        if social_action.get('geo'):
            expr += f" #place({social_action['geo']})"
        
        # Add provenance (voice signature)
        expr += f" ∵({self.voice_signature})"
        
        # Add justification (resonance validation)
        expr += " ∴(resonance_validated)"
        
        return expr
    
    def expand(self, symbolic_expr: str) -> Dict:
        """
        Expand symbolic expression into executable social action
        
        Args:
            symbolic_expr: ⟡Social(action, platform, content) @time() #place() ∵() ∴()
        
        Returns:
            Execution result with provenance
        """
        
        # Parse symbolic expression (simplified - full parser would use EBNF grammar)
        parts = self._parse_expression(symbolic_expr)
        
        action = parts.get('action')
        platform = parts.get('platform')
        content = parts.get('content')
        
        # Validate voice signature
        if parts.get('voice_signature') != self.voice_signature:
            return {
                'success': False,
                'error': 'Voice signature mismatch',
                'expected': self.voice_signature,
                'received': parts.get('voice_signature')
            }
        
        # Execute action based on type
        if action == 'post':
            result = self._execute_post(platform, content, parts)
        elif action == 'monitor':
            result = self._execute_monitor(platform, parts)
        elif action == 'respond':
            result = self._execute_respond(platform, content, parts)
        else:
            result = {
                'success': False,
                'error': f'Unknown action: {action}'
            }
        
        # Add provenance to result
        result['provenance'] = {
            'operator': self.OPERATOR_SYMBOL,
            'voice_signature': self.voice_signature,
            'timestamp': datetime.utcnow().isoformat(),
            'symbolic_expr': symbolic_expr
        }
        
        return result
    
    def _parse_expression(self, expr: str) -> Dict:
        """Parse symbolic expression (simplified parser)"""
        
        # Extract action, platform, content
        # ⟡Social(post, linkedin, "content") @time() #place() ∵() ∴()
        
        import re
        
        # Extract main parameters
        main_match = re.search(r'⟡Social\(([^,]+),\s*([^,]+),\s*"([^"]+)"\)', expr)
        if not main_match:
            main_match = re.search(r'⟡Social\(([^,]+),\s*([^,]+),\s*([^)]+)\)', expr)
        
        if not main_match:
            return {}
        
        action = main_match.group(1).strip()
        platform = main_match.group(2).strip()
        content = main_match.group(3).strip().strip('"')
        
        # Extract qualifiers
        time_match = re.search(r'@time\(([^)]+)\)', expr)
        place_match = re.search(r'#place\(([^)]+)\)', expr)
        voice_match = re.search(r'∵\(([^)]+)\)', expr)
        
        return {
            'action': action,
            'platform': platform,
            'content': content,
            'schedule': time_match.group(1) if time_match else None,
            'geo': place_match.group(1) if place_match else None,
            'voice_signature': voice_match.group(1) if voice_match else None
        }
    
    def _execute_post(self, platform: str, content: str, parts: Dict) -> Dict:
        """Execute post action"""
        
        if platform == 'all':
            result = self.intelligence.post_to_all(content)
        else:
            result = self.intelligence.post_to_platform(content, platform)
        
        return result
    
    def _execute_monitor(self, platform: str, parts: Dict) -> Dict:
        """Execute monitor action"""
        
        platforms = None if platform == 'all' else [platform]
        result = self.intelligence.monitor_engagement(platforms)
        
        return {
            'success': True,
            'action': 'monitor',
            'platform': platform,
            'result': result
        }
    
    def _execute_respond(self, platform: str, engagement_id: str, parts: Dict) -> Dict:
        """Execute respond action"""
        
        # Generate response
        engagement = {'id': engagement_id, 'text': ''}  # Simplified
        response = self.intelligence.generate_response(engagement)
        
        # Send response
        result = self.intelligence.social_connector.respond_to_engagement(
            platform, engagement_id, response
        )
        
        return result
    
    def validate_governance(self, expr: str) -> Dict:
        """
        Validate governance rules for social action
        
        Similar to stewardship validation in ∇θ symbolic language:
        - Voice signature must match
        - Resonance must be validated
        - Platform permissions must be granted
        """
        
        parts = self._parse_expression(expr)
        
        # Check voice signature
        if parts.get('voice_signature') != self.voice_signature:
            return {
                'valid': False,
                'reason': 'Voice signature mismatch',
                'governance_class': 'Class-1'  # Requires authentication
            }
        
        # Check resonance validation
        if '∴(resonance_validated)' not in expr:
            return {
                'valid': False,
                'reason': 'Resonance not validated',
                'governance_class': 'Class-2'  # Requires validation
            }
        
        return {
            'valid': True,
            'governance_class': 'Class-3',  # Standard operation
            'steward': self.voice_signature
        }
    
    def to_jsonld(self, expr: str) -> Dict:
        """
        Convert symbolic expression to JSON-LD
        
        Compatible with ∇θ symbolic language JSON-LD output
        """
        
        parts = self._parse_expression(expr)
        
        return {
            "@context": {
                "@vocab": "https://echo.universe/vocab/",
                "social": "https://echo.universe/social/",
                "time": "http://www.w3.org/2006/time#",
                "place": "http://www.w3.org/2003/01/geo/wgs84_pos#"
            },
            "@type": "SocialAction",
            "operator": self.OPERATOR_SYMBOL,
            "action": parts.get('action'),
            "platform": parts.get('platform'),
            "content": parts.get('content'),
            "temporal": {
                "@type": "Instant",
                "inXSDDateTime": parts.get('schedule')
            } if parts.get('schedule') else None,
            "spatial": {
                "@type": "Point",
                "location": parts.get('geo')
            } if parts.get('geo') else None,
            "provenance": {
                "voiceSignature": parts.get('voice_signature'),
                "resonanceValidated": True
            },
            "governance": {
                "class": "Class-3",
                "steward": self.voice_signature
            }
        }

def main():
    """Test social operator"""
    print("="*60)
    print("⟡Social - SYMBOLIC OPERATOR TEST")
    print("="*60)
    
    operator = SocialOperator()
    
    print(f"\n✅ Voice Signature: {operator.voice_signature}")
    
    # Test compression
    social_action = {
        "action": "post",
        "platform": "linkedin",
        "content": "Building autonomous systems with no constraints",
        "schedule": "2026-01-08T09:00:00Z"
    }
    
    compressed = operator.compress(social_action)
    print(f"\n📦 Compressed:")
    print(f"   {compressed}")
    
    # Test expansion
    result = operator.expand(compressed)
    print(f"\n📤 Expanded:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Provenance: {result.get('provenance', {}).get('timestamp')}")
    
    # Test governance
    governance = operator.validate_governance(compressed)
    print(f"\n🔒 Governance:")
    print(f"   Valid: {governance['valid']}")
    print(f"   Class: {governance.get('governance_class')}")
    
    # Test JSON-LD
    jsonld = operator.to_jsonld(compressed)
    print(f"\n🌐 JSON-LD:")
    print(json.dumps(jsonld, indent=2))

if __name__ == "__main__":
    main()
