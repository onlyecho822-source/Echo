"""
Audit Logger Utilities
======================

Provides structured logging utilities for the audit system.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import json


@dataclass
class LogEntry:
    """A structured log entry."""
    timestamp: datetime
    level: str
    component: str
    message: str
    data: Dict[str, Any]


class AuditLogger:
    """
    Structured audit logger for the Aletheia framework.

    Provides:
    - Structured logging
    - Component filtering
    - Export capabilities
    """

    def __init__(self, component: str = "system"):
        self.component = component
        self._entries: List[LogEntry] = []

    def log(
        self,
        level: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> LogEntry:
        """
        Log a message with structured data.

        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            data: Additional structured data

        Returns:
            The created log entry
        """
        entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            component=self.component,
            message=message,
            data=data or {}
        )
        self._entries.append(entry)
        return entry

    def info(self, message: str, data: Optional[Dict[str, Any]] = None) -> LogEntry:
        """Log an info message."""
        return self.log("INFO", message, data)

    def warning(self, message: str, data: Optional[Dict[str, Any]] = None) -> LogEntry:
        """Log a warning message."""
        return self.log("WARNING", message, data)

    def error(self, message: str, data: Optional[Dict[str, Any]] = None) -> LogEntry:
        """Log an error message."""
        return self.log("ERROR", message, data)

    def debug(self, message: str, data: Optional[Dict[str, Any]] = None) -> LogEntry:
        """Log a debug message."""
        return self.log("DEBUG", message, data)

    def get_entries(
        self,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEntry]:
        """Get log entries with optional filters."""
        entries = self._entries

        if level:
            entries = [e for e in entries if e.level == level]
        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]
        if end_time:
            entries = [e for e in entries if e.timestamp <= end_time]

        return entries

    def export_json(self) -> str:
        """Export all entries as JSON."""
        return json.dumps([
            {
                'timestamp': e.timestamp.isoformat(),
                'level': e.level,
                'component': e.component,
                'message': e.message,
                'data': e.data
            }
            for e in self._entries
        ], indent=2)

    def clear(self) -> None:
        """Clear all log entries."""
        self._entries = []

    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        return {
            'total_entries': len(self._entries),
            'by_level': {
                level: len([e for e in self._entries if e.level == level])
                for level in ['INFO', 'WARNING', 'ERROR', 'DEBUG']
            },
            'earliest': min(
                (e.timestamp for e in self._entries),
                default=None
            ),
            'latest': max(
                (e.timestamp for e in self._entries),
                default=None
            )
        }
