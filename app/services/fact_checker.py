"""
Core fact-checking engine - verifies claims using AI and external sources.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional

import httpx

from app.config import settings
from app.models.schemas import (
    ClaimResult,
    FactCheckResult,
    MediaType,
    ProcessingStatus,
    SourceReference,
    VerificationStatus,
)
from app.services.claim_extractor import claim_extractor


class FactChecker:
    """Main fact-checking engine that verifies claims."""

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

    async def check_text(
        self,
        text: str,
        media_type: MediaType = MediaType.TEXT,
        context: Optional[str] = None,
    ) -> FactCheckResult:
        """
        Fact-check text content.

        Args:
            text: The text to fact-check
            media_type: Type of source media
            context: Optional context about the source

        Returns:
            FactCheckResult with verified claims
        """
        start_time = datetime.utcnow()
        request_id = str(uuid.uuid4())

        result = FactCheckResult(
            request_id=request_id,
            status=ProcessingStatus.PROCESSING,
            media_type=media_type,
            extracted_text=text,
        )

        try:
            # Extract claims
            result.status = ProcessingStatus.EXTRACTING_CLAIMS
            claims_data = await claim_extractor.extract_claims(text, context)

            if not claims_data:
                result.status = ProcessingStatus.COMPLETED
                result.summary = "No verifiable claims found in the content."
                result.total_claims = 0
                return result

            # Verify each claim
            result.status = ProcessingStatus.VERIFYING
            result.total_claims = len(claims_data)

            # Process claims in parallel (with limit)
            semaphore = asyncio.Semaphore(5)  # Max 5 concurrent verifications

            async def verify_with_semaphore(claim_data, idx):
                async with semaphore:
                    return await self._verify_claim(claim_data, idx, context)

            tasks = [
                verify_with_semaphore(claim_data, i)
                for i, claim_data in enumerate(claims_data)
            ]
            claim_results = await asyncio.gather(*tasks)
            result.claims = claim_results

            # Calculate overall credibility
            if claim_results:
                scores = []
                for claim in claim_results:
                    if claim.verification_status == VerificationStatus.TRUE:
                        scores.append(1.0)
                    elif claim.verification_status == VerificationStatus.PARTIALLY_TRUE:
                        scores.append(0.6)
                    elif claim.verification_status == VerificationStatus.MISLEADING:
                        scores.append(0.3)
                    elif claim.verification_status == VerificationStatus.FALSE:
                        scores.append(0.0)
                    else:
                        scores.append(0.5)  # Unverifiable/opinion

                result.overall_credibility = sum(scores) / len(scores)

            # Generate summary
            result.summary = self._generate_summary(result)
            result.status = ProcessingStatus.COMPLETED

        except Exception as e:
            result.status = ProcessingStatus.ERROR
            result.error_message = str(e)

        result.completed_at = datetime.utcnow()
        result.processing_time_seconds = (
            result.completed_at - start_time
        ).total_seconds()

        return result

    async def _verify_claim(
        self,
        claim_data: dict,
        index: int,
        context: Optional[str] = None,
    ) -> ClaimResult:
        """Verify a single claim."""
        claim_id = f"claim_{index}"
        claim_text = claim_data["text"]
        claim_type = claim_data.get("type", "factual")

        # Use AI to verify the claim
        verification = await self._ai_verify_claim(claim_text, claim_type, context)

        return ClaimResult(
            claim_id=claim_id,
            original_text=claim_text,
            claim_type=claim_type,
            verification_status=verification["status"],
            confidence_score=verification["confidence"],
            explanation=verification["explanation"],
            corrected_info=verification.get("correction"),
            sources=verification.get("sources", []),
            context=context,
        )

    async def _ai_verify_claim(
        self,
        claim: str,
        claim_type: str,
        context: Optional[str] = None,
    ) -> dict:
        """Use AI to verify a claim."""
        prompt = self._build_verification_prompt(claim, claim_type, context)

        # Try OpenAI
        openai = self._get_openai_client()
        if openai:
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert fact-checker. Analyze claims carefully "
                                "and provide accurate verification with sources. "
                                "Return JSON with your analysis."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )
                return self._parse_verification_response(
                    response.choices[0].message.content
                )
            except Exception as e:
                print(f"OpenAI verification failed: {e}")

        # Try Anthropic
        anthropic = self._get_anthropic_client()
        if anthropic:
            try:
                response = anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                )
                return self._parse_verification_response(response.content[0].text)
            except Exception as e:
                print(f"Anthropic verification failed: {e}")

        # Fallback - unable to verify
        return {
            "status": VerificationStatus.UNVERIFIABLE,
            "confidence": 0.0,
            "explanation": "Unable to verify claim - no AI service available.",
            "sources": [],
        }

    def _build_verification_prompt(
        self,
        claim: str,
        claim_type: str,
        context: Optional[str] = None,
    ) -> str:
        """Build the verification prompt."""
        context_str = f"\nContext: {context}" if context else ""

        return f"""Fact-check the following {claim_type} claim:

Claim: "{claim}"
{context_str}

Analyze this claim and determine its accuracy. Consider:
1. Is this claim verifiable?
2. What evidence supports or contradicts it?
3. Are there any nuances or missing context?

Return a JSON object with:
- "status": one of ["true", "false", "partially_true", "misleading", "unverifiable", "opinion", "satire"]
- "confidence": your confidence in this assessment (0-1)
- "explanation": clear explanation of your finding (2-3 sentences)
- "correction": if false/misleading, provide the correct information (optional)
- "sources": array of relevant sources, each with "title", "url" (if known), "snippet"

Be precise and objective. If you're not certain, indicate lower confidence.
Return JSON only:"""

    def _parse_verification_response(self, response_text: str) -> dict:
        """Parse AI verification response."""
        import json
        import re

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                except:
                    return self._default_verification()
            else:
                return self._default_verification()

        # Map status string to enum
        status_map = {
            "true": VerificationStatus.TRUE,
            "false": VerificationStatus.FALSE,
            "partially_true": VerificationStatus.PARTIALLY_TRUE,
            "misleading": VerificationStatus.MISLEADING,
            "unverifiable": VerificationStatus.UNVERIFIABLE,
            "opinion": VerificationStatus.OPINION,
            "satire": VerificationStatus.SATIRE,
        }

        status_str = data.get("status", "unverifiable").lower()
        status = status_map.get(status_str, VerificationStatus.UNVERIFIABLE)

        # Parse sources
        sources = []
        for src in data.get("sources", []):
            if isinstance(src, dict):
                sources.append(SourceReference(
                    title=src.get("title", "Unknown"),
                    url=src.get("url"),
                    snippet=src.get("snippet"),
                ))

        return {
            "status": status,
            "confidence": float(data.get("confidence", 0.5)),
            "explanation": data.get("explanation", "No explanation provided."),
            "correction": data.get("correction"),
            "sources": sources,
        }

    def _default_verification(self) -> dict:
        """Return default verification when parsing fails."""
        return {
            "status": VerificationStatus.UNVERIFIABLE,
            "confidence": 0.0,
            "explanation": "Unable to parse verification response.",
            "sources": [],
        }

    def _generate_summary(self, result: FactCheckResult) -> str:
        """Generate a summary of the fact-check results."""
        if not result.claims:
            return "No verifiable claims found in the content."

        # Count statuses
        status_counts = {}
        for claim in result.claims:
            status = claim.verification_status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Build summary
        parts = [f"Analyzed {result.total_claims} claims."]

        if status_counts.get("true", 0):
            parts.append(f"{status_counts['true']} verified as true.")
        if status_counts.get("false", 0):
            parts.append(f"{status_counts['false']} found to be false.")
        if status_counts.get("partially_true", 0):
            parts.append(f"{status_counts['partially_true']} partially true.")
        if status_counts.get("misleading", 0):
            parts.append(f"{status_counts['misleading']} misleading.")
        if status_counts.get("unverifiable", 0):
            parts.append(f"{status_counts['unverifiable']} could not be verified.")

        if result.overall_credibility is not None:
            credibility_pct = int(result.overall_credibility * 100)
            parts.append(f"Overall credibility score: {credibility_pct}%.")

        return " ".join(parts)

    async def check_with_google_factcheck(self, claim: str) -> list[dict]:
        """Query Google Fact Check API for existing fact-checks."""
        if not settings.google_factcheck_api_key:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://factchecktools.googleapis.com/v1alpha1/claims:search",
                    params={
                        "key": settings.google_factcheck_api_key,
                        "query": claim,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("claims", [])
        except Exception as e:
            print(f"Google Fact Check API error: {e}")

        return []


# Global instance
fact_checker = FactChecker()
