"""Custom exceptions for the Echo Reverse Engineering Engine."""


class EchoEngineError(Exception):
    """Base exception for all Echo Engine errors."""
    pass


class SourceNotFoundError(EchoEngineError):
    """Raised when a source cannot be found or accessed."""
    pass


class ValidationError(EchoEngineError):
    """Raised when fact validation fails."""
    pass


class AnalysisError(EchoEngineError):
    """Raised when analysis encounters an error."""
    pass


class CollectionError(EchoEngineError):
    """Raised when source collection fails."""
    pass


class TimelineError(EchoEngineError):
    """Raised when timeline reconstruction fails."""
    pass


class ProvenanceError(EchoEngineError):
    """Raised when provenance tracking fails."""
    pass


class ReportGenerationError(EchoEngineError):
    """Raised when report generation fails."""
    pass
