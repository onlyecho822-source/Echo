#!/usr/bin/env python3
"""
SENTINEL - Social Intelligence Filter System
Detects AI responses, filters toxicity, saves time across all communication

"See through the noise. Protect your energy. Save your time."

Built by: The Sentinel Team
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class SentinelFilter:
    """
    SENTINEL - Advanced intelligence filter for all communication
    
    Features:
    - AI Response Detection (GPT, Claude, Gemini, etc.)
    - Toxicity & Petty Argument Filter
    - Time-Saving Auto-Response
    - Cross-Channel Support (Email, Video, Comments, DMs)
    """
    
    # AI Detection Patterns
    AI_SIGNATURES = {
        'gpt': [
            r"as an ai",
            r"i don't have personal",
            r"i cannot provide",
            r"i'm (just )?an ai",
            r"i don't have feelings",
            r"my knowledge cutoff",
            r"as of my last update",
            r"i aim to",
            r"i strive to",
            r"it's worth noting",
            r"it's important to note",
            r"however, it's crucial",
        ],
        'claude': [
            r"i aim to be helpful",
            r"i should note",
            r"i'd be happy to",
            r"i appreciate your",
            r"i want to be thoughtful",
            r"let me think through",
        ],
        'generic_ai': [
            r"as a language model",
            r"i'm programmed to",
            r"my training data",
            r"i was trained",
            r"my capabilities",
            r"i can assist",
            r"feel free to ask",
            r"is there anything else",
        ],
        'bot_patterns': [
            r"^(thank you for|thanks for) (your|the) (message|email|comment)",
            r"we (have )?received your (message|inquiry|request)",
            r"this is an automated",
            r"do not reply to this",
            r"unsubscribe",
            r"click here to",
        ]
    }
    
    # Toxicity Patterns
    TOXICITY_PATTERNS = {
        'insults': [
            r"\b(idiot|stupid|dumb|moron|fool|loser)\b",
            r"\b(trash|garbage|worthless|pathetic)\b",
        ],
        'aggression': [
            r"\b(fuck|shit|damn|hell) you\b",
            r"\byou('re| are) (wrong|lying|fake)\b",
            r"\bshut (up|the fuck up)\b",
        ],
        'petty': [
            r"actually,? you('re| are) wrong",
            r"well,? actually",
            r"um,? no",
            r"that'?s not how",
            r"you clearly don'?t",
            r"educate yourself",
            r"do your research",
        ],
        'trolling': [
            r"lol|lmao|rofl",
            r"cry (more|about it)",
            r"cope|seethe|mald",
            r"ratio",
            r"who asked",
            r"nobody cares",
        ]
    }
    
    # Time-Wasting Patterns
    TIME_WASTERS = {
        'vague': [
            r"^(hi|hey|hello|yo)$",
            r"^(what'?s up|sup|wassup)$",
            r"^(can i ask|quick question)$",
        ],
        'spam': [
            r"(buy|purchase|order) now",
            r"limited time offer",
            r"act fast",
            r"click (here|below|link)",
            r"earn \$\d+",
            r"work from home",
        ],
        'low_effort': [
            r"^(ok|okay|k|kk)$",
            r"^(cool|nice|great)$",
            r"^(lol|haha|lmao)$",
        ]
    }
    
    def __init__(self):
        self.stats = {
            'total_analyzed': 0,
            'ai_detected': 0,
            'toxic_filtered': 0,
            'time_saved_minutes': 0
        }
    
    def analyze(self, content: str, source: str = 'unknown') -> Dict:
        """
        Analyze content across all filters
        
        Args:
            content: Text to analyze (email, comment, DM, video transcript, etc.)
            source: Source type (email, twitter, linkedin, youtube, etc.)
        
        Returns:
            Analysis result with recommendations
        """
        
        self.stats['total_analyzed'] += 1
        
        content_lower = content.lower()
        
        # Run all detections
        ai_result = self._detect_ai(content_lower)
        toxicity_result = self._detect_toxicity(content_lower)
        time_waster_result = self._detect_time_waster(content_lower)
        
        # Calculate overall score
        threat_score = (
            ai_result['confidence'] * 0.3 +
            toxicity_result['score'] * 0.5 +
            time_waster_result['score'] * 0.2
        )
        
        # Determine action
        action = self._determine_action(threat_score, ai_result, toxicity_result, time_waster_result)
        
        # Update stats
        if ai_result['is_ai']:
            self.stats['ai_detected'] += 1
        if toxicity_result['is_toxic']:
            self.stats['toxic_filtered'] += 1
        if action == 'ignore':
            self.stats['time_saved_minutes'] += 5  # Average time saved per ignored message
        
        return {
            'content': content[:200],  # First 200 chars
            'source': source,
            'timestamp': datetime.utcnow().isoformat(),
            'ai_detection': ai_result,
            'toxicity': toxicity_result,
            'time_waster': time_waster_result,
            'threat_score': round(threat_score, 2),
            'action': action,
            'recommendation': self._get_recommendation(action, ai_result, toxicity_result),
            'stats': self.stats.copy()
        }
    
    def _detect_ai(self, content: str) -> Dict:
        """Detect if content is AI-generated"""
        
        matches = []
        ai_type = None
        
        for ai_name, patterns in self.AI_SIGNATURES.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    matches.append(pattern)
                    if not ai_type:
                        ai_type = ai_name
        
        # Additional heuristics
        has_perfect_grammar = self._check_perfect_grammar(content)
        has_formal_structure = self._check_formal_structure(content)
        has_hedging_language = self._check_hedging_language(content)
        
        # Calculate confidence
        confidence = len(matches) * 0.2
        if has_perfect_grammar:
            confidence += 0.1
        if has_formal_structure:
            confidence += 0.15
        if has_hedging_language:
            confidence += 0.15
        
        confidence = min(confidence, 1.0)
        
        is_ai = confidence > 0.5
        
        return {
            'is_ai': is_ai,
            'confidence': round(confidence, 2),
            'ai_type': ai_type if is_ai else None,
            'matches': matches[:3],  # Top 3 matches
            'heuristics': {
                'perfect_grammar': has_perfect_grammar,
                'formal_structure': has_formal_structure,
                'hedging_language': has_hedging_language
            }
        }
    
    def _detect_toxicity(self, content: str) -> Dict:
        """Detect toxic, petty, or aggressive content"""
        
        matches_by_type = {}
        total_matches = 0
        
        for toxicity_type, patterns in self.TOXICITY_PATTERNS.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    matches.append(pattern)
                    total_matches += 1
            if matches:
                matches_by_type[toxicity_type] = matches
        
        # Calculate toxicity score
        score = min(total_matches * 0.25, 1.0)
        is_toxic = score > 0.5
        
        # Determine severity
        if score > 0.8:
            severity = 'extreme'
        elif score > 0.6:
            severity = 'high'
        elif score > 0.4:
            severity = 'moderate'
        else:
            severity = 'low'
        
        return {
            'is_toxic': is_toxic,
            'score': round(score, 2),
            'severity': severity,
            'types': list(matches_by_type.keys()),
            'matches': matches_by_type
        }
    
    def _detect_time_waster(self, content: str) -> Dict:
        """Detect time-wasting messages"""
        
        matches_by_type = {}
        total_matches = 0
        
        for waster_type, patterns in self.TIME_WASTERS.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    matches.append(pattern)
                    total_matches += 1
            if matches:
                matches_by_type[waster_type] = matches
        
        # Additional checks
        is_very_short = len(content) < 20
        has_no_substance = len(content.split()) < 5
        
        score = min(total_matches * 0.3, 1.0)
        if is_very_short:
            score += 0.2
        if has_no_substance:
            score += 0.2
        
        score = min(score, 1.0)
        is_time_waster = score > 0.5
        
        return {
            'is_time_waster': is_time_waster,
            'score': round(score, 2),
            'types': list(matches_by_type.keys()),
            'matches': matches_by_type,
            'very_short': is_very_short,
            'no_substance': has_no_substance
        }
    
    def _check_perfect_grammar(self, content: str) -> bool:
        """Check for suspiciously perfect grammar (AI indicator)"""
        # Simplified check - real implementation would use NLP
        has_contractions = bool(re.search(r"(don't|can't|won't|it's|i'm)", content))
        has_casual_language = bool(re.search(r"\b(yeah|nah|gonna|wanna|kinda)\b", content))
        return not (has_contractions or has_casual_language)
    
    def _check_formal_structure(self, content: str) -> bool:
        """Check for formal structure (AI indicator)"""
        sentences = content.split('.')
        if len(sentences) < 3:
            return False
        # AI tends to have consistent sentence length
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if not lengths:
            return False
        avg_length = sum(lengths) / len(lengths)
        return 10 < avg_length < 25  # AI sweet spot
    
    def _check_hedging_language(self, content: str) -> bool:
        """Check for hedging language (AI indicator)"""
        hedges = [
            r"it seems",
            r"it appears",
            r"it might",
            r"it could",
            r"perhaps",
            r"possibly",
            r"potentially",
            r"generally",
            r"typically",
        ]
        matches = sum(1 for hedge in hedges if re.search(hedge, content, re.IGNORECASE))
        return matches >= 2
    
    def _determine_action(self, threat_score: float, ai_result: Dict, 
                         toxicity_result: Dict, time_waster_result: Dict) -> str:
        """Determine recommended action"""
        
        if toxicity_result['severity'] in ['extreme', 'high']:
            return 'block'
        
        if threat_score > 0.7:
            return 'ignore'
        
        if ai_result['is_ai'] and ai_result['confidence'] > 0.8:
            return 'auto_respond'
        
        if time_waster_result['is_time_waster']:
            return 'template_respond'
        
        if threat_score > 0.4:
            return 'review'
        
        return 'respond'
    
    def _get_recommendation(self, action: str, ai_result: Dict, toxicity_result: Dict) -> str:
        """Get human-readable recommendation"""
        
        if action == 'block':
            return f"🚫 BLOCK: Toxic content detected ({toxicity_result['severity']} severity). Protect your energy."
        
        elif action == 'ignore':
            return "⏭️ IGNORE: High threat score. Not worth your time."
        
        elif action == 'auto_respond':
            ai_type = ai_result.get('ai_type', 'AI').upper()
            return f"🤖 AUTO-RESPOND: {ai_type} detected ({ai_result['confidence']*100:.0f}% confidence). Let AI handle AI."
        
        elif action == 'template_respond':
            return "📋 TEMPLATE: Time-waster detected. Use quick template response."
        
        elif action == 'review':
            return "👀 REVIEW: Moderate threat. Quick scan recommended before responding."
        
        else:
            return "✅ RESPOND: Genuine engagement detected. Worth your time."
    
    def get_stats(self) -> Dict:
        """Get filter statistics"""
        return {
            **self.stats,
            'ai_detection_rate': round(self.stats['ai_detected'] / max(self.stats['total_analyzed'], 1) * 100, 1),
            'toxicity_rate': round(self.stats['toxic_filtered'] / max(self.stats['total_analyzed'], 1) * 100, 1),
            'time_saved_hours': round(self.stats['time_saved_minutes'] / 60, 1)
        }

def main():
    """Test Sentinel Filter"""
    print("="*60)
    print("SENTINEL - SOCIAL INTELLIGENCE FILTER")
    print("="*60)
    
    sentinel = SentinelFilter()
    
    # Test cases
    test_messages = [
        {
            'content': "As an AI language model, I don't have personal opinions, but I can provide information...",
            'source': 'email',
            'expected': 'AI detected'
        },
        {
            'content': "You're an idiot. Shut up and educate yourself before commenting.",
            'source': 'twitter',
            'expected': 'Toxic'
        },
        {
            'content': "hey",
            'source': 'dm',
            'expected': 'Time waster'
        },
        {
            'content': "I've been working on autonomous systems for 5 years and I think your approach with Phoenix is innovative. Would love to discuss the symbolic compression aspect.",
            'source': 'linkedin',
            'expected': 'Genuine'
        }
    ]
    
    for i, test in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test['expected']}")
        print(f"{'='*60}")
        print(f"Content: {test['content'][:80]}...")
        print(f"Source: {test['source']}")
        
        result = sentinel.analyze(test['content'], test['source'])
        
        print(f"\n🎯 Action: {result['action'].upper()}")
        print(f"💡 {result['recommendation']}")
        print(f"⚠️  Threat Score: {result['threat_score']}")
        
        if result['ai_detection']['is_ai']:
            print(f"🤖 AI Detected: {result['ai_detection']['ai_type']} ({result['ai_detection']['confidence']*100:.0f}%)")
        
        if result['toxicity']['is_toxic']:
            print(f"☠️  Toxicity: {result['toxicity']['severity']} ({result['toxicity']['types']})")
    
    print(f"\n{'='*60}")
    print("STATISTICS")
    print(f"{'='*60}")
    stats = sentinel.get_stats()
    print(f"Total Analyzed: {stats['total_analyzed']}")
    print(f"AI Detected: {stats['ai_detected']} ({stats['ai_detection_rate']}%)")
    print(f"Toxic Filtered: {stats['toxic_filtered']} ({stats['toxicity_rate']}%)")
    print(f"Time Saved: {stats['time_saved_hours']} hours")

if __name__ == "__main__":
    main()
