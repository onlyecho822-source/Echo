"""Event bus for inter-agent communication."""

from typing import Any, Callable, Dict, List
from datetime import datetime
import threading


class EventBus:
    """Thread-safe event bus for Echo agent communication."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Dict[str, Any]] = []
        self._history_limit = 1000
        self._initialized = True

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

    def publish(self, event_type: str, data: Any = None, source: str = "unknown") -> None:
        """Publish an event to all subscribers."""
        event = {
            "type": event_type,
            "data": data,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Record in history
        self._event_history.append(event)
        if len(self._event_history) > self._history_limit:
            self._event_history = self._event_history[-self._history_limit:]

        # Notify subscribers
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")

    def get_history(self, event_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get event history, optionally filtered by type."""
        if event_type:
            filtered = [e for e in self._event_history if e["type"] == event_type]
            return filtered[-limit:]
        return self._event_history[-limit:]
