"""Fact extraction and analysis module."""

import re
from typing import Optional
from datetime import datetime
from echo_engine.core.models import (
    Source,
    Fact,
    FactStatus,
    ConfidenceLevel,
)


class FactExtractor:
    """
    Extracts factual statements from source content.

    Uses pattern matching and linguistic analysis to identify
    statements that can be verified or investigated.
    """

    # Patterns that indicate factual statements
    FACT_PATTERNS = [
        r'\b(?:is|are|was|were)\s+(?:a|an|the)\s+',
        r'\b(?:has|have|had)\s+(?:been|a|an)\s+',
        r'\b(?:occurred|happened|took place)\s+',
        r'\b(?:according to|stated that|reported that)\s+',
        r'\b(?:found|discovered|revealed|showed)\s+that\s+',
        r'\b(?:confirmed|verified|established)\s+',
        r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',  # Dates
        r'\b(?:\d+(?:\.\d+)?%)',  # Percentages
        r'\b(?:\$\d+(?:,\d{3})*(?:\.\d{2})?)',  # Currency
    ]

    # Patterns that suggest opinion rather than fact
    OPINION_PATTERNS = [
        r'\b(?:I think|I believe|in my opinion)\b',
        r'\b(?:probably|possibly|maybe|perhaps)\b',
        r'\b(?:should|could|might|would)\b',
        r'\b(?:best|worst|greatest|most)\b',
    ]

    def __init__(self, config: Optional[dict] = None):
        """Initialize the fact extractor."""
        self.config = config or {}
        self.min_word_count = self.config.get("min_word_count", 4)
        self.max_word_count = self.config.get("max_word_count", 100)

    def extract(self, source: Source) -> list[Fact]:
        """
        Extract facts from a source.

        Args:
            source: The source to extract facts from

        Returns:
            List of extracted Fact objects
        """
        facts = []
        sentences = self._split_sentences(source.content)

        for sentence in sentences:
            sentence = sentence.strip()

            # Skip if too short or too long
            word_count = len(sentence.split())
            if word_count < self.min_word_count or word_count > self.max_word_count:
                continue

            # Check if it's likely a fact (not an opinion)
            if self._is_likely_fact(sentence):
                fact = self._create_fact(sentence, source)
                facts.append(fact)

        return facts

    def _is_likely_fact(self, sentence: str) -> bool:
        """Determine if a sentence is likely a factual statement."""
        sentence_lower = sentence.lower()

        # Check for opinion patterns
        for pattern in self.OPINION_PATTERNS:
            if re.search(pattern, sentence_lower, re.IGNORECASE):
                return False

        # Check for fact patterns
        for pattern in self.FACT_PATTERNS:
            if re.search(pattern, sentence_lower, re.IGNORECASE):
                return True

        # Default: check for declarative structure
        return self._is_declarative(sentence)

    def _is_declarative(self, sentence: str) -> bool:
        """Check if sentence has declarative structure."""
        # Simplified check - sentence doesn't end with ? and has a verb
        if sentence.endswith('?'):
            return False

        # Check for common verbs
        verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'did', 'does']
        words = sentence.lower().split()
        return any(verb in words for verb in verbs)

    def _create_fact(self, statement: str, source: Source) -> Fact:
        """Create a Fact object from a statement."""
        entities = self._extract_entities(statement)
        keywords = self._extract_keywords(statement)
        confidence = self._assess_initial_confidence(statement)

        return Fact(
            statement=statement,
            source_ids=[source.id],
            status=FactStatus.UNVERIFIED,
            confidence=confidence,
            context=source.name,
            entities=entities,
            keywords=keywords,
            metadata={
                "source_type": source.source_type.value,
                "extraction_method": "pattern_matching",
            },
        )

    def _extract_entities(self, text: str) -> list[str]:
        """Extract named entities from text."""
        entities = []

        # Extract capitalized words (likely proper nouns)
        words = text.split()
        for i, word in enumerate(words):
            clean_word = word.strip('.,!?;:\'"()[]{}')
            if clean_word and clean_word[0].isupper() and len(clean_word) > 1:
                # Skip if it's the first word (sentence start)
                if i == 0:
                    # Only include if it's a common proper noun pattern
                    if len(clean_word) > 3:
                        entities.append(clean_word)
                else:
                    entities.append(clean_word)

        # Extract quoted strings
        quoted = re.findall(r'"([^"]+)"', text)
        entities.extend(quoted)

        return list(set(entities))

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from text."""
        # Common stop words to filter
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            'as', 'into', 'through', 'during', 'before', 'after',
            'and', 'but', 'or', 'if', 'that', 'this', 'it', 'its',
        }

        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        # Return unique keywords, maintaining order
        seen = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)

        return unique[:15]  # Limit to top 15

    def _assess_initial_confidence(self, statement: str) -> ConfidenceLevel:
        """Assess initial confidence level of a statement."""
        confidence_score = 3  # Start at medium

        # Increase for specific indicators
        if re.search(r'\d', statement):  # Contains numbers
            confidence_score += 1
        if re.search(r'according to|stated|reported', statement, re.I):
            confidence_score += 1

        # Decrease for vague language
        if re.search(r'some|many|few|several', statement, re.I):
            confidence_score -= 1

        # Map to confidence level
        if confidence_score >= 5:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 4:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 3:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Handle common abbreviations
        text = re.sub(r'\bMr\.', 'Mr', text)
        text = re.sub(r'\bMrs\.', 'Mrs', text)
        text = re.sub(r'\bDr\.', 'Dr', text)
        text = re.sub(r'\bvs\.', 'vs', text)

        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def extract_claims(self, source: Source) -> list[dict]:
        """
        Extract specific claims that can be investigated.

        Returns structured claim data with attribution.
        """
        claims = []
        content = source.content

        # Look for attribution patterns
        attribution_patterns = [
            r'([^.]+)\s+(?:said|stated|claimed|reported|announced)\s+(?:that\s+)?([^.]+\.)',
            r'(?:According to\s+)([^,]+),\s+([^.]+\.)',
            r'"([^"]+)"\s+(?:said|stated)\s+([^.]+)',
        ]

        for pattern in attribution_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    claims.append({
                        "claim": match[1] if len(match[0]) < len(match[1]) else match[0],
                        "attribution": match[0] if len(match[0]) < len(match[1]) else match[1],
                        "source_id": source.id,
                        "timestamp": datetime.now().isoformat(),
                    })

        return claims
