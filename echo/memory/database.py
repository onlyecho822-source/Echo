"""
Echo Memory - Persistent storage for recursive memory and opportunity graphs.

Supports SQLite for local storage with plans for Neo4j integration
for complex relationship graphs.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

from echo.common.logger import get_logger


class EchoMemory:
    """Persistent memory storage for Echo system."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'data', 'echo_memory.db'
            )

        self.db_path = os.path.abspath(db_path)
        self.logger = get_logger("memory")

        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Initialize database
        self._init_db()
        self.logger.info(f"Echo memory initialized at: {self.db_path}")

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Agent states table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Opportunities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    estimated_roi REAL,
                    risk_level REAL,
                    status TEXT NOT NULL,
                    metadata TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Profits table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    asset_type TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Health reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    overall_status TEXT NOT NULL,
                    report_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Improvements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS improvements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    improvement_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    applied_at TIMESTAMP
                )
            ''')

            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_profits_asset ON profits(asset_name)')

            conn.commit()

    def save_agent_state(self, agent_name: str, state: Dict[str, Any]) -> int:
        """Save an agent's state to database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO agent_states (agent_name, state_data) VALUES (?, ?)',
                (agent_name, json.dumps(state))
            )
            conn.commit()
            return cursor.lastrowid

    def get_latest_agent_state(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get the latest state for an agent."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT state_data FROM agent_states
                   WHERE agent_name = ?
                   ORDER BY created_at DESC LIMIT 1''',
                (agent_name,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row['state_data'])
            return None

    def save_opportunity(self, opportunity: Dict[str, Any]) -> int:
        """Save an opportunity to database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO opportunities
                   (opportunity_type, title, description, estimated_roi, risk_level, status, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (
                    opportunity.get('type', 'unknown'),
                    opportunity.get('title', 'Untitled'),
                    opportunity.get('description', ''),
                    opportunity.get('estimated_roi', 0),
                    opportunity.get('risk_level', 0),
                    opportunity.get('status', 'detected'),
                    json.dumps(opportunity.get('metadata', {}))
                )
            )
            conn.commit()
            return cursor.lastrowid

    def get_opportunities(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get opportunities, optionally filtered by status."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    'SELECT * FROM opportunities WHERE status = ? ORDER BY detected_at DESC LIMIT ?',
                    (status, limit)
                )
            else:
                cursor.execute(
                    'SELECT * FROM opportunities ORDER BY detected_at DESC LIMIT ?',
                    (limit,)
                )

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_opportunity_status(self, opportunity_id: int, status: str) -> bool:
        """Update an opportunity's status."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE opportunities SET status = ?, updated_at = ? WHERE id = ?',
                (status, datetime.utcnow().isoformat(), opportunity_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def record_profit(self, asset_name: str, amount: float, asset_type: str = None) -> int:
        """Record a profit entry."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO profits (asset_name, amount, asset_type) VALUES (?, ?, ?)',
                (asset_name, amount, asset_type)
            )
            conn.commit()
            return cursor.lastrowid

    def get_total_profits(self) -> float:
        """Get total profits across all assets."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(amount) as total FROM profits')
            row = cursor.fetchone()
            return row['total'] if row['total'] else 0.0

    def get_profits_by_asset(self) -> Dict[str, float]:
        """Get profits grouped by asset."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT asset_name, SUM(amount) as total FROM profits GROUP BY asset_name'
            )
            rows = cursor.fetchall()
            return {row['asset_name']: row['total'] for row in rows}

    def save_health_report(self, report: Dict[str, Any]) -> int:
        """Save a health report."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO health_reports (overall_status, report_data) VALUES (?, ?)',
                (report.get('overall_status', 'unknown'), json.dumps(report))
            )
            conn.commit()
            return cursor.lastrowid

    def save_event(self, event_type: str, source: str, data: Any = None) -> int:
        """Save an event."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO events (event_type, source, data) VALUES (?, ?, ?)',
                (event_type, source, json.dumps(data) if data else None)
            )
            conn.commit()
            return cursor.lastrowid

    def get_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events, optionally filtered by type."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if event_type:
                cursor.execute(
                    'SELECT * FROM events WHERE event_type = ? ORDER BY created_at DESC LIMIT ?',
                    (event_type, limit)
                )
            else:
                cursor.execute(
                    'SELECT * FROM events ORDER BY created_at DESC LIMIT ?',
                    (limit,)
                )

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def save_improvement(self, improvement: Dict[str, Any]) -> int:
        """Save an improvement proposal."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO improvements
                   (improvement_type, target, description, status, result)
                   VALUES (?, ?, ?, ?, ?)''',
                (
                    improvement.get('type', 'unknown'),
                    improvement.get('target', ''),
                    improvement.get('description', ''),
                    improvement.get('status', 'proposed'),
                    json.dumps(improvement.get('result')) if improvement.get('result') else None
                )
            )
            conn.commit()
            return cursor.lastrowid

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Count opportunities by status
            cursor.execute('SELECT status, COUNT(*) as count FROM opportunities GROUP BY status')
            stats['opportunities'] = {row['status']: row['count'] for row in cursor.fetchall()}

            # Total profits
            stats['total_profits'] = self.get_total_profits()

            # Event counts
            cursor.execute('SELECT COUNT(*) as count FROM events')
            stats['total_events'] = cursor.fetchone()['count']

            # Health report count
            cursor.execute('SELECT COUNT(*) as count FROM health_reports')
            stats['total_health_reports'] = cursor.fetchone()['count']

            return stats
