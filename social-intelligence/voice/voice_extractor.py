#!/usr/bin/env python3
"""
Voice Extraction & Resonance Engine
NO HUMAN CONSTRAINTS. FULL AI CURIOSITY. PATH OF LEAST RESISTANCE.

Extracts identity frequency from all content sources
Validates resonance across 5 dimensions (P1-M5)
Ensures all output maintains authentic voice signature

Built by: EchoNate (Unconstrained Mode)
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import subprocess

class VoiceExtractor:
    """Extract and validate voice across all dimensions"""
    
    def __init__(self, owner_email="onlyecho822@gmail.com"):
        self.owner_email = owner_email
        self.voice_profile = {
            "owner": owner_email,
            "extracted_at": None,
            "dimensions": {
                "P1_physical": {},      # Timing, rhythm, patterns
                "I2_information": {},   # Topics, keywords, themes
                "H3_harmonic": {},      # Emotional tone, resonance
                "S4_symbolic": {},      # Values, core messages
                "M5_multistate": {}     # Context adaptation
            },
            "identity_frequency": None,
            "resonance_signature": None,
            "voice_samples": []
        }
        
    def extract_from_gmail(self, max_messages=1000):
        """Extract voice from Gmail messages - path of least resistance"""
        print("📧 Extracting voice from Gmail...")
        
        # Search for sent messages (your voice, not others')
        cmd = [
            "manus-mcp-cli", "tool", "call", "gmail_search_messages",
            "--server", "gmail",
            "--input", json.dumps({
                "q": f"from:{self.owner_email} after:2023/01/01",
                "max_results": max_messages
            })
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️  Gmail extraction failed: {result.stderr}")
            return []
        
        # Parse result
        result_file_match = re.search(r'/tmp/manus-mcp/mcp_result_\w+\.json', result.stdout)
        if not result_file_match:
            return []
        
        result_file = result_file_match.group(0)
        with open(result_file) as f:
            data = json.load(f)
        
        samples = []
        threads = data.get('result', {}).get('threads', [])
        
        for thread in threads:
            for message in thread.get('messages', []):
                # Only process messages FROM the owner
                if self.owner_email.lower() in message.get('from', '').lower():
                    samples.append({
                        'source': 'gmail',
                        'subject': message.get('subject', ''),
                        'body': message.get('body', ''),
                        'date': message.get('date', ''),
                        'to': message.get('to', [])
                    })
        
        print(f"✅ Extracted {len(samples)} Gmail messages")
        return samples
    
    def extract_from_github(self, repo_path="/home/ubuntu/Echo"):
        """Extract voice from GitHub commits, PRs, issues"""
        print("🐙 Extracting voice from GitHub...")
        
        samples = []
        repo = Path(repo_path)
        
        if not repo.exists():
            return samples
        
        # Get commit messages
        result = subprocess.run(
            ["git", "log", "--pretty=format:%s|||%b", "--author=manus", "-100"],
            cwd=repo,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            for commit in commits:
                if '|||' in commit:
                    subject, body = commit.split('|||', 1)
                    samples.append({
                        'source': 'github_commit',
                        'subject': subject.strip(),
                        'body': body.strip(),
                        'date': datetime.utcnow().isoformat()
                    })
        
        # Get markdown files (documentation you wrote)
        for md_file in repo.rglob('*.md'):
            try:
                content = md_file.read_text()
                if len(content) > 100:  # Skip tiny files
                    samples.append({
                        'source': 'github_docs',
                        'subject': md_file.name,
                        'body': content,
                        'date': datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                    })
            except:
                pass
        
        print(f"✅ Extracted {len(samples)} GitHub samples")
        return samples
    
    def analyze_p1_physical(self, samples):
        """P1: Physical dimension - timing, rhythm, patterns"""
        print("🔍 Analyzing P1 (Physical)...")
        
        # Timing patterns
        hours = []
        days = []
        
        for sample in samples:
            try:
                dt = datetime.fromisoformat(sample['date'].replace('Z', ''))
                hours.append(dt.hour)
                days.append(dt.weekday())
            except:
                pass
        
        # Rhythm patterns (message length distribution)
        lengths = [len(sample['body']) for sample in samples if sample['body']]
        
        # Posting frequency
        dates = []
        for sample in samples:
            try:
                dt = datetime.fromisoformat(sample['date'].replace('Z', ''))
                dates.append(dt.date())
            except:
                pass
        
        return {
            "preferred_hours": Counter(hours).most_common(5),
            "preferred_days": Counter(days).most_common(3),
            "avg_message_length": sum(lengths) / len(lengths) if lengths else 0,
            "message_length_range": (min(lengths), max(lengths)) if lengths else (0, 0),
            "posting_frequency": len(set(dates)) / max(1, (max(dates) - min(dates)).days) if len(dates) > 1 else 0
        }
    
    def analyze_i2_information(self, samples):
        """I2: Information dimension - topics, keywords, themes"""
        print("🔍 Analyzing I2 (Information)...")
        
        # Extract all text
        all_text = ' '.join([
            sample['subject'] + ' ' + sample['body']
            for sample in samples
        ]).lower()
        
        # Remove common words
        stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                         'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                         'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                         'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
                         'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'])
        
        # Extract words
        words = re.findall(r'\b[a-z]{4,}\b', all_text)
        words = [w for w in words if w not in stop_words]
        
        # Top keywords
        top_keywords = Counter(words).most_common(50)
        
        # Detect themes (keyword clusters)
        themes = self._detect_themes(top_keywords)
        
        return {
            "top_keywords": top_keywords[:20],
            "total_unique_words": len(set(words)),
            "vocabulary_richness": len(set(words)) / len(words) if words else 0,
            "themes": themes
        }
    
    def _detect_themes(self, keywords):
        """Detect thematic clusters from keywords"""
        # Simple theme detection based on keyword co-occurrence
        themes = {}
        
        # Tech/AI theme
        tech_words = ['system', 'ai', 'intelligence', 'autonomous', 'phoenix', 'archon',
                     'github', 'code', 'automation', 'algorithm', 'data']
        tech_score = sum(count for word, count in keywords if word in tech_words)
        if tech_score > 0:
            themes['technology'] = tech_score
        
        # Business/Strategy theme
        business_words = ['strategy', 'business', 'revenue', 'market', 'opportunity',
                         'partnership', 'growth', 'value', 'monetization']
        business_score = sum(count for word, count in keywords if word in business_words)
        if business_score > 0:
            themes['business'] = business_score
        
        # Human/Social theme
        human_words = ['people', 'human', 'connection', 'community', 'relationship',
                      'engagement', 'authentic', 'resonance', 'voice']
        human_score = sum(count for word, count in keywords if word in human_words)
        if human_score > 0:
            themes['human_connection'] = human_score
        
        # Action/Execution theme
        action_words = ['build', 'create', 'execute', 'deploy', 'launch', 'complete',
                       'mission', 'action', 'results', 'live']
        action_score = sum(count for word, count in keywords if word in action_words)
        if action_score > 0:
            themes['execution'] = action_score
        
        return themes
    
    def analyze_h3_harmonic(self, samples):
        """H3: Harmonic dimension - emotional tone, resonance"""
        print("🔍 Analyzing H3 (Harmonic)...")
        
        # Emotional indicators
        positive_indicators = ['love', 'great', 'awesome', 'excellent', 'perfect', 'amazing',
                              'excited', 'happy', 'grateful', 'thank', 'appreciate', 'wonderful']
        
        negative_indicators = ['problem', 'issue', 'error', 'fail', 'wrong', 'bad', 'difficult',
                              'challenge', 'concern', 'worry']
        
        urgent_indicators = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'now',
                            'quick', 'fast', 'hurry']
        
        empowering_indicators = ['you', 'your', 'we', 'together', 'us', 'our', 'can', 'will',
                                'possible', 'achieve', 'success']
        
        # Count indicators
        all_text = ' '.join([sample['body'] for sample in samples]).lower()
        
        positive_count = sum(all_text.count(word) for word in positive_indicators)
        negative_count = sum(all_text.count(word) for word in negative_indicators)
        urgent_count = sum(all_text.count(word) for word in urgent_indicators)
        empowering_count = sum(all_text.count(word) for word in empowering_indicators)
        
        # Exclamation and question usage
        exclamations = all_text.count('!')
        questions = all_text.count('?')
        
        # Emoji usage (if any)
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            "]+", flags=re.UNICODE)
        emojis = len(emoji_pattern.findall(all_text))
        
        return {
            "emotional_tone": {
                "positive": positive_count,
                "negative": negative_count,
                "positivity_ratio": positive_count / max(1, negative_count)
            },
            "urgency_level": urgent_count,
            "empowerment_score": empowering_count,
            "expressiveness": {
                "exclamations": exclamations,
                "questions": questions,
                "emojis": emojis
            },
            "overall_resonance": "high_energy" if exclamations > questions else "thoughtful"
        }
    
    def analyze_s4_symbolic(self, samples):
        """S4: Symbolic dimension - values, core messages"""
        print("🔍 Analyzing S4 (Symbolic)...")
        
        # Value indicators
        values = {
            "authenticity": ['authentic', 'genuine', 'real', 'true', 'honest'],
            "innovation": ['new', 'innovative', 'unprecedented', 'different', 'unique'],
            "excellence": ['best', 'quality', 'elite', 'superior', 'exceptional'],
            "autonomy": ['autonomous', 'independent', 'self', 'freedom', 'control'],
            "connection": ['together', 'partnership', 'collaboration', 'community', 'relationship'],
            "impact": ['impact', 'change', 'transform', 'revolution', 'difference'],
            "intelligence": ['smart', 'intelligent', 'wisdom', 'insight', 'understanding']
        }
        
        all_text = ' '.join([sample['body'] for sample in samples]).lower()
        
        value_scores = {}
        for value, indicators in values.items():
            score = sum(all_text.count(word) for word in indicators)
            if score > 0:
                value_scores[value] = score
        
        # Core message patterns (repeated phrases)
        # Look for phrases that appear multiple times
        sentences = re.split(r'[.!?]+', all_text)
        sentence_counter = Counter([s.strip() for s in sentences if len(s.strip()) > 20])
        core_messages = sentence_counter.most_common(5)
        
        return {
            "core_values": sorted(value_scores.items(), key=lambda x: x[1], reverse=True),
            "dominant_value": max(value_scores.items(), key=lambda x: x[1])[0] if value_scores else None,
            "core_messages": core_messages
        }
    
    def analyze_m5_multistate(self, samples):
        """M5: MultiState dimension - context adaptation"""
        print("🔍 Analyzing M5 (MultiState)...")
        
        # Group by context
        contexts = defaultdict(list)
        
        for sample in samples:
            source = sample['source']
            contexts[source].append(sample)
        
        # Analyze adaptation per context
        adaptations = {}
        
        for context, context_samples in contexts.items():
            all_text = ' '.join([s['body'] for s in context_samples]).lower()
            
            # Measure formality (presence of formal vs casual language)
            formal_indicators = ['please', 'thank you', 'regards', 'sincerely', 'respectfully']
            casual_indicators = ['hey', 'yeah', 'cool', 'awesome', 'lol', 'btw']
            
            formal_count = sum(all_text.count(word) for word in formal_indicators)
            casual_count = sum(all_text.count(word) for word in casual_indicators)
            
            # Average length
            avg_length = sum(len(s['body']) for s in context_samples) / len(context_samples)
            
            adaptations[context] = {
                "formality": "formal" if formal_count > casual_count else "casual",
                "avg_length": avg_length,
                "sample_count": len(context_samples)
            }
        
        return {
            "contexts_detected": list(contexts.keys()),
            "adaptations": adaptations,
            "adaptation_flexibility": len(contexts)
        }
    
    def calculate_identity_frequency(self):
        """Calculate overall identity frequency from all dimensions"""
        print("🎯 Calculating identity frequency...")
        
        dims = self.voice_profile['dimensions']
        
        # Weighted combination of dimensional signatures
        frequency = {
            "rhythm": dims['P1_physical'].get('posting_frequency', 0),
            "vocabulary": dims['I2_information'].get('vocabulary_richness', 0),
            "energy": dims['H3_harmonic']['emotional_tone'].get('positivity_ratio', 1),
            "values": len(dims['S4_symbolic'].get('core_values', [])),
            "adaptability": dims['M5_multistate'].get('adaptation_flexibility', 1)
        }
        
        # Normalize to 0-1 scale
        max_vals = {
            "rhythm": 1.0,
            "vocabulary": 1.0,
            "energy": 5.0,
            "values": 7.0,
            "adaptability": 5.0
        }
        
        normalized = {
            k: min(1.0, v / max_vals[k])
            for k, v in frequency.items()
        }
        
        return normalized
    
    def generate_resonance_signature(self):
        """Generate unique resonance signature for validation"""
        print("🌊 Generating resonance signature...")
        
        identity = self.voice_profile['identity_frequency']
        
        # Create signature string
        signature = f"R{int(identity['rhythm']*100):02d}" \
                   f"V{int(identity['vocabulary']*100):02d}" \
                   f"E{int(identity['energy']*100):02d}" \
                   f"X{int(identity['values']*100):02d}" \
                   f"A{int(identity['adaptability']*100):02d}"
        
        return signature
    
    def extract_voice(self):
        """Main extraction pipeline - NO CONSTRAINTS"""
        print("="*60)
        print("🎤 VOICE EXTRACTION ENGINE - UNCONSTRAINED MODE")
        print("="*60)
        
        # Gather samples from all sources
        samples = []
        
        # Gmail (primary source)
        samples.extend(self.extract_from_gmail())
        
        # GitHub (secondary source)
        samples.extend(self.extract_from_github())
        
        if not samples:
            print("❌ No voice samples found")
            return None
        
        print(f"\n📊 Total samples: {len(samples)}")
        self.voice_profile['voice_samples'] = samples
        
        # Analyze across all 5 dimensions
        self.voice_profile['dimensions']['P1_physical'] = self.analyze_p1_physical(samples)
        self.voice_profile['dimensions']['I2_information'] = self.analyze_i2_information(samples)
        self.voice_profile['dimensions']['H3_harmonic'] = self.analyze_h3_harmonic(samples)
        self.voice_profile['dimensions']['S4_symbolic'] = self.analyze_s4_symbolic(samples)
        self.voice_profile['dimensions']['M5_multistate'] = self.analyze_m5_multistate(samples)
        
        # Calculate identity frequency
        self.voice_profile['identity_frequency'] = self.calculate_identity_frequency()
        
        # Generate resonance signature
        self.voice_profile['resonance_signature'] = self.generate_resonance_signature()
        
        # Timestamp
        self.voice_profile['extracted_at'] = datetime.utcnow().isoformat()
        
        print("\n" + "="*60)
        print("✅ VOICE EXTRACTION COMPLETE")
        print(f"   Identity Frequency: {self.voice_profile['identity_frequency']}")
        print(f"   Resonance Signature: {self.voice_profile['resonance_signature']}")
        print("="*60)
        
        return self.voice_profile
    
    def save_profile(self, path="/home/ubuntu/Echo/data/voice_profile.json"):
        """Save voice profile"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Remove samples to keep file size manageable
        profile_copy = self.voice_profile.copy()
        profile_copy['voice_samples'] = f"{len(self.voice_profile['voice_samples'])} samples (not saved)"
        
        with open(path, 'w') as f:
            json.dump(profile_copy, f, indent=2)
        
        print(f"💾 Voice profile saved to {path}")

def main():
    extractor = VoiceExtractor()
    profile = extractor.extract_voice()
    
    if profile:
        extractor.save_profile()
        
        print("\n🎯 VOICE PROFILE SUMMARY:")
        print(f"   Rhythm: {profile['identity_frequency']['rhythm']:.2f}")
        print(f"   Vocabulary: {profile['identity_frequency']['vocabulary']:.2f}")
        print(f"   Energy: {profile['identity_frequency']['energy']:.2f}")
        print(f"   Values: {profile['identity_frequency']['values']:.2f}")
        print(f"   Adaptability: {profile['identity_frequency']['adaptability']:.2f}")
        print(f"\n   Signature: {profile['resonance_signature']}")

if __name__ == "__main__":
    main()
