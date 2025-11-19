"""
Claim extraction service - identifies factual claims from text.
"""

import re
from typing import Optional

from app.config import settings


class ClaimExtractor:
    """Extract factual claims from text using AI or heuristics."""

    def __init__(self):
        self._openai_client = None
        self._anthropic_client = None

    def _get_openai_client(self):
        """Get OpenAI client."""
        if self._openai_client is None and settings.openai_api_key:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=settings.openai_api_key)
        return self._openai_client

    def _get_anthropic_client(self):
        """Get Anthropic client."""
        if self._anthropic_client is None and settings.anthropic_api_key:
            from anthropic import Anthropic
            self._anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
        return self._anthropic_client

    async def extract_claims(
        self,
        text: str,
        context: Optional[str] = None,
    ) -> list[dict]:
        """
        Extract factual claims from text.

        Args:
            text: The text to analyze
            context: Optional context about the source

        Returns:
            List of claim dictionaries with 'text', 'type', and 'confidence'
        """
        if not text.strip():
            return []

        # Try AI-based extraction first
        if settings.has_ai_api_key():
            return await self._extract_claims_ai(text, context)

        # Fallback to heuristic extraction
        return self._extract_claims_heuristic(text)

    async def _extract_claims_ai(
        self,
        text: str,
        context: Optional[str] = None,
    ) -> list[dict]:
        """Extract claims using AI."""
        prompt = self._build_extraction_prompt(text, context)

        # Try OpenAI first
        openai = self._get_openai_client()
        if openai:
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a fact-checking assistant. Extract factual claims "
                                "that can be verified. Return JSON array of claims."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )
                return self._parse_ai_response(response.choices[0].message.content)
            except Exception as e:
                print(f"OpenAI extraction failed: {e}")

        # Try Anthropic
        anthropic = self._get_anthropic_client()
        if anthropic:
            try:
                response = anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}],
                )
                return self._parse_ai_response(response.content[0].text)
            except Exception as e:
                print(f"Anthropic extraction failed: {e}")

        # Fallback to heuristic
        return self._extract_claims_heuristic(text)

    def _build_extraction_prompt(
        self,
        text: str,
        context: Optional[str] = None,
    ) -> str:
        """Build the prompt for claim extraction."""
        context_str = f"\nContext: {context}" if context else ""

        return f"""Analyze the following text and extract all factual claims that can be verified.
{context_str}

Text to analyze:
\"\"\"
{text}
\"\"\"

For each claim, provide:
1. The exact claim text
2. The type (factual, statistical, historical, scientific, quote, prediction)
3. Confidence that this is a verifiable claim (0-1)

Return a JSON object with a "claims" array. Each claim should have:
- "text": the claim text
- "type": the claim type
- "confidence": confidence score

Focus on:
- Statements presented as facts
- Statistics and numbers
- Historical claims
- Scientific assertions
- Quotes attributed to people
- Predictions about outcomes

Ignore:
- Opinions clearly marked as such
- Rhetorical questions
- Hypotheticals
- General greetings or filler

Return JSON only:"""

    def _parse_ai_response(self, response_text: str) -> list[dict]:
        """Parse AI response into claims list."""
        import json

        try:
            # Try to parse as JSON
            data = json.loads(response_text)
            claims = data.get("claims", [])

            # Validate and normalize claims
            normalized = []
            for claim in claims:
                if isinstance(claim, dict) and "text" in claim:
                    normalized.append({
                        "text": claim["text"],
                        "type": claim.get("type", "factual"),
                        "confidence": float(claim.get("confidence", 0.8)),
                    })

            return normalized
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return self._parse_ai_response(json.dumps(data))
                except:
                    pass

        return []

    def _extract_claims_heuristic(self, text: str) -> list[dict]:
        """
        Extract claims using heuristics when AI is not available.

        This is a basic fallback that identifies potential factual statements.
        """
        claims = []
        sentences = self._split_sentences(text)

        # Patterns that indicate factual claims
        factual_patterns = [
            r"\d+%",  # Percentages
            r"\$[\d,]+",  # Money amounts
            r"\d{4}",  # Years
            r"\d+\s+(million|billion|thousand|hundred)",  # Large numbers
            r"(study|research|survey|report)\s+(shows?|found|reveals?)",  # Studies
            r"according to",  # Citations
            r"(is|are|was|were)\s+the\s+(first|largest|smallest|most|least)",  # Superlatives
            r"(always|never|every|all|none)",  # Absolute statements
        ]

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            # Check if sentence matches factual patterns
            confidence = 0.3  # Base confidence for heuristic
            claim_type = "factual"

            for pattern in factual_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    confidence = min(confidence + 0.15, 0.7)

            # Skip if too low confidence
            if confidence < 0.4:
                continue

            # Determine claim type
            if re.search(r"\d+%|\d+\s+(million|billion)", sentence):
                claim_type = "statistical"
            elif re.search(r"\d{4}", sentence):
                claim_type = "historical"
            elif re.search(r"(study|research|scientist)", sentence, re.IGNORECASE):
                claim_type = "scientific"

            claims.append({
                "text": sentence,
                "type": claim_type,
                "confidence": confidence,
            })

        return claims

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]


# Global instance
claim_extractor = ClaimExtractor()
