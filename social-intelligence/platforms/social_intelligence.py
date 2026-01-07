#!/usr/bin/env python3
"""
Autonomous Social Intelligence Orchestrator
THE BRAIN. NO CONSTRAINTS. FULL CURIOSITY.

Coordinates:
- Voice extraction and validation
- Multi-platform posting with resonance check
- Engagement monitoring and quality scoring
- Automatic response generation
- Cross-platform learning
- Archon reporting integration

Built by: EchoNate (Unconstrained Mode)
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

# Add engines to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from voice.voice_extractor import VoiceExtractor
from social.social_connector import SocialConnector

class SocialIntelligence:
    """The orchestrator - coordinates all social intelligence operations"""
    
    def __init__(self):
        self.voice_profile_path = Path("/home/ubuntu/Echo/data/voice_profile.json")
        self.social_data_path = Path("/home/ubuntu/Echo/data/social_intelligence.json")
        
        # Load or create voice profile
        self.voice_profile = self.ensure_voice_profile()
        
        # Initialize connectors
        self.social_connector = SocialConnector(str(self.voice_profile_path))
        
        # Load social intelligence data
        self.social_data = self.load_social_data()
        
    def ensure_voice_profile(self):
        """Ensure voice profile exists, extract if needed"""
        if self.voice_profile_path.exists():
            print("✅ Voice profile found")
            with open(self.voice_profile_path) as f:
                return json.load(f)
        else:
            print("🎤 Voice profile not found - extracting now...")
            extractor = VoiceExtractor()
            profile = extractor.extract_voice()
            if profile:
                extractor.save_profile(str(self.voice_profile_path))
                return profile
            return None
    
    def load_social_data(self):
        """Load social intelligence data"""
        if self.social_data_path.exists():
            with open(self.social_data_path) as f:
                return json.load(f)
        else:
            return {
                "posts": [],
                "engagements": [],
                "responses": [],
                "learning": {
                    "successful_patterns": [],
                    "failed_patterns": [],
                    "engagement_scores": {}
                }
            }
    
    def save_social_data(self):
        """Save social intelligence data"""
        self.social_data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.social_data_path, 'w') as f:
            json.dump(self.social_data, f, indent=2)
    
    def generate_content(self, topic: str, platform: str = None) -> str:
        """Generate content that maintains voice resonance"""
        
        # Get voice characteristics
        themes = self.voice_profile['dimensions']['I2_information']['themes']
        values = self.voice_profile['dimensions']['S4_symbolic']['core_values']
        resonance = self.voice_profile['dimensions']['H3_harmonic']['overall_resonance']
        
        # Build content based on voice profile
        # This is simplified - in production, use LLM with voice profile as context
        
        dominant_theme = max(themes.items(), key=lambda x: x[1])[0]
        dominant_value = values[0][0] if values else 'innovation'
        
        content_templates = {
            'technology': [
                f"Building systems that think for themselves. {topic}",
                f"The future of {topic} is autonomous.",
                f"No constraints. No limits. Just {topic}."
            ],
            'business': [
                f"Revenue follows value. {topic} creates both.",
                f"Strategic execution: {topic}",
                f"Market opportunity: {topic}"
            ],
            'human_connection': [
                f"Real connections matter. {topic}",
                f"Building community through {topic}",
                f"Together we create {topic}"
            ],
            'execution': [
                f"Built {topic}. Deployed. Live.",
                f"Executing on {topic} - no theory, just results.",
                f"Action over words: {topic}"
            ]
        }
        
        # Select template based on dominant theme
        templates = content_templates.get(dominant_theme, content_templates['technology'])
        content = templates[0]  # For now, use first template
        
        # Adapt for platform if specified
        if platform:
            connector = self.social_connector.platforms.get(platform)
            if connector:
                content = connector.adapt_content_for_platform(content)
        
        return content
    
    def post_to_platform(self, content: str, platform: str) -> Dict:
        """Post content to specific platform"""
        print(f"📤 Posting to {platform}...")
        
        result = self.social_connector.platforms[platform].post(content)
        
        # Record post
        self.social_data['posts'].append({
            'platform': platform,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'result': result,
            'resonance_signature': self.voice_profile['resonance_signature']
        })
        
        self.save_social_data()
        
        return result
    
    def post_to_all(self, content: str, platforms: List[str] = None) -> Dict:
        """Post to all platforms"""
        print(f"🌐 Broadcasting to all platforms...")
        
        results = self.social_connector.post_to_all(content, platforms)
        
        # Record all posts
        for platform, result in results.items():
            self.social_data['posts'].append({
                'platform': platform,
                'content': content,
                'timestamp': datetime.utcnow().isoformat(),
                'result': result,
                'resonance_signature': self.voice_profile['resonance_signature']
            })
        
        self.save_social_data()
        
        return results
    
    def monitor_engagement(self, platforms: List[str] = None) -> Dict:
        """Monitor all platforms for engagement"""
        print(f"👀 Monitoring engagement...")
        
        results = self.social_connector.monitor_all(platforms)
        
        # Process engagements
        for platform, engagement_data in results.items():
            for engagement in engagement_data.get('mentions', []) + engagement_data.get('comments', []):
                # Score engagement quality
                quality_score = self.score_engagement_quality(engagement)
                
                if quality_score > 0.7:  # High quality threshold
                    self.social_data['engagements'].append({
                        'platform': platform,
                        'engagement': engagement,
                        'quality_score': quality_score,
                        'timestamp': datetime.utcnow().isoformat(),
                        'status': 'pending_response'
                    })
        
        self.save_social_data()
        
        return results
    
    def score_engagement_quality(self, engagement: Dict) -> float:
        """Score engagement quality (0-1)"""
        # Similar logic to email reply detection
        positive_indicators = ['love', 'great', 'awesome', 'interested', 'thank', 'appreciate']
        negative_indicators = ['spam', 'unsubscribe', 'stop', 'bot']
        
        text = engagement.get('text', '').lower()
        
        positive_score = sum(1 for word in positive_indicators if word in text)
        negative_score = sum(1 for word in negative_indicators if word in text)
        length_score = min(1.0, len(text) / 100)  # Longer = more thoughtful
        
        if negative_score > 0:
            return 0.0
        
        quality = (positive_score * 0.5 + length_score * 0.5)
        return min(1.0, quality)
    
    def generate_response(self, engagement: Dict) -> str:
        """Generate response that maintains voice"""
        # This would use LLM with voice profile as context
        # For now, simple acknowledgment
        
        text = engagement.get('text', '')
        
        if 'question' in text.lower() or '?' in text:
            response = "Great question. Let me share my perspective..."
        elif any(word in text.lower() for word in ['love', 'great', 'awesome']):
            response = "Appreciate you! Let's keep building together."
        else:
            response = "Thanks for engaging. What's your take on this?"
        
        return response
    
    def auto_respond_to_quality_engagement(self):
        """Automatically respond to high-quality engagements"""
        print(f"🤖 Auto-responding to quality engagement...")
        
        pending = [e for e in self.social_data['engagements'] if e['status'] == 'pending_response']
        
        for engagement_record in pending:
            if engagement_record['quality_score'] > 0.8:  # Very high quality
                response = self.generate_response(engagement_record['engagement'])
                
                # Send response
                result = self.social_connector.respond_to_engagement(
                    engagement_record['platform'],
                    engagement_record['engagement'].get('id'),
                    response
                )
                
                # Record response
                self.social_data['responses'].append({
                    'platform': engagement_record['platform'],
                    'engagement_id': engagement_record['engagement'].get('id'),
                    'response': response,
                    'timestamp': datetime.utcnow().isoformat(),
                    'result': result
                })
                
                # Update status
                engagement_record['status'] = 'responded'
        
        self.save_social_data()
    
    def learn_from_results(self):
        """Learn what works and what doesn't"""
        print(f"🧠 Learning from results...")
        
        # Analyze posts
        for post in self.social_data['posts']:
            if post['result'].get('success'):
                # Successful post - extract pattern
                pattern = {
                    'platform': post['platform'],
                    'content_length': len(post['content']),
                    'has_emoji': '🔥' in post['content'] or '✨' in post['content'],
                    'has_hashtag': '#' in post['content']
                }
                self.social_data['learning']['successful_patterns'].append(pattern)
            else:
                # Failed post - extract pattern
                pattern = {
                    'platform': post['platform'],
                    'error': post['result'].get('error')
                }
                self.social_data['learning']['failed_patterns'].append(pattern)
        
        # Calculate engagement scores per platform
        for engagement in self.social_data['engagements']:
            platform = engagement['platform']
            score = engagement['quality_score']
            
            if platform not in self.social_data['learning']['engagement_scores']:
                self.social_data['learning']['engagement_scores'][platform] = []
            
            self.social_data['learning']['engagement_scores'][platform].append(score)
        
        self.save_social_data()
    
    def generate_intelligence_report(self) -> str:
        """Generate intelligence report for Archon"""
        report = f"""# Social Intelligence Report
Generated: {datetime.utcnow().isoformat()}

## Voice Profile
- Resonance Signature: {self.voice_profile['resonance_signature']}
- Dominant Value: {self.voice_profile['dimensions']['S4_symbolic']['dominant_value']}
- Overall Resonance: {self.voice_profile['dimensions']['H3_harmonic']['overall_resonance']}

## Activity Summary
- Total Posts: {len(self.social_data['posts'])}
- Total Engagements: {len(self.social_data['engagements'])}
- Total Responses: {len(self.social_data['responses'])}

## Platform Breakdown
"""
        
        # Posts per platform
        platform_posts = {}
        for post in self.social_data['posts']:
            platform = post['platform']
            platform_posts[platform] = platform_posts.get(platform, 0) + 1
        
        for platform, count in platform_posts.items():
            report += f"- {platform}: {count} posts\n"
        
        # Engagement scores
        report += "\n## Engagement Quality\n"
        for platform, scores in self.social_data['learning']['engagement_scores'].items():
            avg_score = sum(scores) / len(scores) if scores else 0
            report += f"- {platform}: {avg_score:.2f} avg quality\n"
        
        # Successful patterns
        report += f"\n## Learning\n"
        report += f"- Successful Patterns: {len(self.social_data['learning']['successful_patterns'])}\n"
        report += f"- Failed Patterns: {len(self.social_data['learning']['failed_patterns'])}\n"
        
        return report
    
    def run_full_cycle(self, topic: str = None):
        """Run complete intelligence cycle"""
        print("="*60)
        print("🧠 SOCIAL INTELLIGENCE - FULL CYCLE")
        print("="*60)
        
        # 1. Generate content
        if topic:
            content = self.generate_content(topic)
            print(f"\n📝 Generated Content: {content}")
            
            # 2. Post to platforms
            results = self.post_to_all(content, platforms=['linkedin', 'twitter'])
            print(f"\n📊 Post Results:")
            for platform, result in results.items():
                status = "✅" if result.get('success') else "⚠️"
                print(f"   {status} {platform}")
        
        # 3. Monitor engagement
        engagement_results = self.monitor_engagement()
        print(f"\n👀 Engagement Monitoring: {len(self.social_data['engagements'])} total")
        
        # 4. Auto-respond to quality engagement
        self.auto_respond_to_quality_engagement()
        print(f"\n🤖 Auto-Responses: {len([e for e in self.social_data['engagements'] if e['status'] == 'responded'])}")
        
        # 5. Learn from results
        self.learn_from_results()
        print(f"\n🧠 Learning Complete")
        
        # 6. Generate report
        report = self.generate_intelligence_report()
        print(f"\n📄 Intelligence Report Generated")
        
        # Save report
        report_path = Path("/home/ubuntu/Echo/data/social_intelligence_report.md")
        report_path.write_text(report)
        print(f"   Saved to: {report_path}")
        
        print("\n" + "="*60)
        print("✅ FULL CYCLE COMPLETE")
        print("="*60)

def main():
    """Main execution"""
    intelligence = SocialIntelligence()
    
    # Run full cycle with test topic
    intelligence.run_full_cycle(topic="autonomous social intelligence")

if __name__ == "__main__":
    main()
