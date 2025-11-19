"""
Tests for the fact-checking service.
"""

import pytest
from app.models.schemas import MediaType, VerificationStatus


class TestClaimExtractor:
    """Tests for claim extraction."""

    def test_extract_claims_empty_text(self):
        """Empty text should return no claims."""
        from app.services.claim_extractor import claim_extractor

        # Heuristic extraction for empty text
        claims = claim_extractor._extract_claims_heuristic("")
        assert claims == []

    def test_extract_claims_heuristic_statistical(self):
        """Should identify statistical claims."""
        from app.services.claim_extractor import claim_extractor

        text = "The unemployment rate is 5.2% according to the latest report."
        claims = claim_extractor._extract_claims_heuristic(text)

        assert len(claims) > 0
        assert any(c["type"] == "statistical" for c in claims)

    def test_extract_claims_heuristic_historical(self):
        """Should identify historical claims."""
        from app.services.claim_extractor import claim_extractor

        text = "World War II ended in 1945."
        claims = claim_extractor._extract_claims_heuristic(text)

        assert len(claims) > 0

    def test_split_sentences(self):
        """Should correctly split sentences."""
        from app.services.claim_extractor import claim_extractor

        text = "First sentence. Second sentence! Third sentence?"
        sentences = claim_extractor._split_sentences(text)

        assert len(sentences) == 3


class TestFactChecker:
    """Tests for fact verification."""

    def test_generate_summary_no_claims(self):
        """Summary for no claims."""
        from app.services.fact_checker import fact_checker
        from app.models.schemas import FactCheckResult, ProcessingStatus

        result = FactCheckResult(
            request_id="test",
            status=ProcessingStatus.COMPLETED,
            media_type=MediaType.TEXT,
            claims=[],
        )

        summary = fact_checker._generate_summary(result)
        assert "No verifiable claims" in summary

    def test_default_verification(self):
        """Default verification when parsing fails."""
        from app.services.fact_checker import fact_checker

        verification = fact_checker._default_verification()

        assert verification["status"] == VerificationStatus.UNVERIFIABLE
        assert verification["confidence"] == 0.0


class TestSchemas:
    """Tests for Pydantic schemas."""

    def test_claim_result_creation(self):
        """Create a ClaimResult."""
        from app.models.schemas import ClaimResult

        claim = ClaimResult(
            claim_id="test_1",
            original_text="Test claim",
            verification_status=VerificationStatus.TRUE,
            confidence_score=0.95,
            explanation="Test explanation",
        )

        assert claim.claim_id == "test_1"
        assert claim.verification_status == VerificationStatus.TRUE
        assert claim.confidence_score == 0.95

    def test_verification_status_values(self):
        """All verification statuses should be valid."""
        statuses = [
            VerificationStatus.TRUE,
            VerificationStatus.FALSE,
            VerificationStatus.PARTIALLY_TRUE,
            VerificationStatus.MISLEADING,
            VerificationStatus.UNVERIFIABLE,
            VerificationStatus.OPINION,
            VerificationStatus.SATIRE,
        ]

        assert len(statuses) == 7

    def test_media_type_values(self):
        """All media types should be valid."""
        types = [
            MediaType.AUDIO,
            MediaType.VIDEO,
            MediaType.IMAGE,
            MediaType.DOCUMENT,
            MediaType.TEXT,
            MediaType.LIVE_STREAM,
        ]

        assert len(types) == 6


class TestHelpers:
    """Tests for utility helpers."""

    def test_format_timestamp(self):
        """Format seconds to timestamp."""
        from app.utils.helpers import format_timestamp

        assert format_timestamp(65) == "01:05"
        assert format_timestamp(3665) == "01:01:05"

    def test_sanitize_text(self):
        """Sanitize text removes excessive whitespace."""
        from app.utils.helpers import sanitize_text

        text = "  Hello    world  \n\n  test  "
        result = sanitize_text(text)

        assert result == "Hello world test"

    def test_truncate_text(self):
        """Truncate long text."""
        from app.utils.helpers import truncate_text

        text = "This is a very long text that should be truncated"
        result = truncate_text(text, max_length=20)

        assert len(result) <= 20
        assert result.endswith("...")

    def test_format_file_size(self):
        """Format bytes to readable size."""
        from app.utils.helpers import format_file_size

        assert "1.0 KB" in format_file_size(1024)
        assert "1.0 MB" in format_file_size(1024 * 1024)
