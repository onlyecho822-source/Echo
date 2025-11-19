"""
Memory Kernel - Core persistent storage system

Encrypted SQLite-based storage for personal data, preferences, and history.
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from .encryption import EncryptionEngine


class MemoryKernel:
    """
    Encrypted persistent memory storage for Echo Life OS.

    Provides:
    - Encrypted key-value storage
    - Preference management
    - History tracking
    - Context storage for agents
    """

    def __init__(self, db_path: str, master_password: str):
        """
        Initialize the Memory Kernel.

        Args:
            db_path: Path to SQLite database file
            master_password: Master password for encryption
        """
        self.db_path = Path(db_path)
        self.encryption = EncryptionEngine(master_password)
        self._conn: Optional[sqlite3.Connection] = None
        self._initialize_database()

    def _initialize_database(self):
        """Create database tables if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(str(self.db_path))
        cursor = self._conn.cursor()

        # Core storage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                access_count INTEGER DEFAULT 0
            )
        ''')

        # Preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # History/events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                agent TEXT
            )
        ''')

        # Agent context table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_context (
                agent_name TEXT PRIMARY KEY,
                context TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        self._conn.commit()

    def store(self, key: str, value: Any, category: str = 'general') -> bool:
        """
        Store an encrypted value in memory.

        Args:
            key: Unique key for the value
            value: Value to store (will be JSON serialized and encrypted)
            category: Category for organization

        Returns:
            True if successful
        """
        json_value = json.dumps(value)
        encrypted_value = self.encryption.encrypt_string(json_value)

        now = datetime.utcnow().isoformat()
        cursor = self._conn.cursor()

        cursor.execute('''
            INSERT INTO memory (key, value, category, created_at, updated_at, access_count)
            VALUES (?, ?, ?, ?, ?, 0)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                category = excluded.category,
                updated_at = excluded.updated_at
        ''', (key, encrypted_value, category, now, now))

        self._conn.commit()
        return True

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve and decrypt a value from memory.

        Args:
            key: Key to retrieve

        Returns:
            Decrypted value or None if not found
        """
        cursor = self._conn.cursor()
        cursor.execute(
            'SELECT value FROM memory WHERE key = ?',
            (key,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        # Update access count
        cursor.execute(
            'UPDATE memory SET access_count = access_count + 1 WHERE key = ?',
            (key,)
        )
        self._conn.commit()

        decrypted = self.encryption.decrypt_string(row[0])
        return json.loads(decrypted)

    def delete(self, key: str) -> bool:
        """
        Delete a value from memory.

        Args:
            key: Key to delete

        Returns:
            True if deleted, False if not found
        """
        cursor = self._conn.cursor()
        cursor.execute('DELETE FROM memory WHERE key = ?', (key,))
        deleted = cursor.rowcount > 0
        self._conn.commit()
        return deleted

    def list_keys(self, category: Optional[str] = None) -> List[str]:
        """
        List all keys, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of keys
        """
        cursor = self._conn.cursor()

        if category:
            cursor.execute(
                'SELECT key FROM memory WHERE category = ?',
                (category,)
            )
        else:
            cursor.execute('SELECT key FROM memory')

        return [row[0] for row in cursor.fetchall()]

    def set_preference(self, key: str, value: Any) -> bool:
        """
        Set a user preference.

        Args:
            key: Preference key
            value: Preference value

        Returns:
            True if successful
        """
        json_value = json.dumps(value)
        encrypted_value = self.encryption.encrypt_string(json_value)
        now = datetime.utcnow().isoformat()

        cursor = self._conn.cursor()
        cursor.execute('''
            INSERT INTO preferences (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        ''', (key, encrypted_value, now))

        self._conn.commit()
        return True

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference.

        Args:
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value or default
        """
        cursor = self._conn.cursor()
        cursor.execute(
            'SELECT value FROM preferences WHERE key = ?',
            (key,)
        )
        row = cursor.fetchone()

        if not row:
            return default

        decrypted = self.encryption.decrypt_string(row[0])
        return json.loads(decrypted)

    def log_event(self, event_type: str, data: Dict[str, Any],
                  agent: Optional[str] = None) -> int:
        """
        Log an event to history.

        Args:
            event_type: Type of event
            data: Event data
            agent: Optional agent that generated the event

        Returns:
            Event ID
        """
        json_data = json.dumps(data)
        encrypted_data = self.encryption.encrypt_string(json_data)
        now = datetime.utcnow().isoformat()

        cursor = self._conn.cursor()
        cursor.execute('''
            INSERT INTO history (event_type, data, timestamp, agent)
            VALUES (?, ?, ?, ?)
        ''', (event_type, encrypted_data, now, agent))

        self._conn.commit()
        return cursor.lastrowid

    def get_history(self, event_type: Optional[str] = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve event history.

        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        cursor = self._conn.cursor()

        if event_type:
            cursor.execute('''
                SELECT id, event_type, data, timestamp, agent
                FROM history
                WHERE event_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (event_type, limit))
        else:
            cursor.execute('''
                SELECT id, event_type, data, timestamp, agent
                FROM history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

        events = []
        for row in cursor.fetchall():
            decrypted_data = self.encryption.decrypt_string(row[2])
            events.append({
                'id': row[0],
                'event_type': row[1],
                'data': json.loads(decrypted_data),
                'timestamp': row[3],
                'agent': row[4]
            })

        return events

    def save_agent_context(self, agent_name: str, context: Dict[str, Any]) -> bool:
        """
        Save context for an agent.

        Args:
            agent_name: Name of the agent
            context: Context dictionary

        Returns:
            True if successful
        """
        json_context = json.dumps(context)
        encrypted_context = self.encryption.encrypt_string(json_context)
        now = datetime.utcnow().isoformat()

        cursor = self._conn.cursor()
        cursor.execute('''
            INSERT INTO agent_context (agent_name, context, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(agent_name) DO UPDATE SET
                context = excluded.context,
                updated_at = excluded.updated_at
        ''', (agent_name, encrypted_context, now))

        self._conn.commit()
        return True

    def load_agent_context(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Load context for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Context dictionary or None
        """
        cursor = self._conn.cursor()
        cursor.execute(
            'SELECT context FROM agent_context WHERE agent_name = ?',
            (agent_name,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        decrypted = self.encryption.decrypt_string(row[0])
        return json.loads(decrypted)

    def export_backup(self, output_path: str) -> bool:
        """
        Export encrypted backup of all data.

        Args:
            output_path: Path for backup file

        Returns:
            True if successful
        """
        cursor = self._conn.cursor()

        backup_data = {
            'version': '1.0',
            'timestamp': datetime.utcnow().isoformat(),
            'memory': [],
            'preferences': [],
            'history': [],
            'agent_context': []
        }

        # Export memory (already encrypted)
        cursor.execute('SELECT * FROM memory')
        for row in cursor.fetchall():
            backup_data['memory'].append({
                'key': row[0],
                'value': row[1],
                'category': row[2],
                'created_at': row[3],
                'updated_at': row[4],
                'access_count': row[5]
            })

        # Export preferences (already encrypted)
        cursor.execute('SELECT * FROM preferences')
        for row in cursor.fetchall():
            backup_data['preferences'].append({
                'key': row[0],
                'value': row[1],
                'updated_at': row[2]
            })

        # Export history (already encrypted)
        cursor.execute('SELECT * FROM history')
        for row in cursor.fetchall():
            backup_data['history'].append({
                'id': row[0],
                'event_type': row[1],
                'data': row[2],
                'timestamp': row[3],
                'agent': row[4]
            })

        # Export agent context (already encrypted)
        cursor.execute('SELECT * FROM agent_context')
        for row in cursor.fetchall():
            backup_data['agent_context'].append({
                'agent_name': row[0],
                'context': row[1],
                'updated_at': row[2]
            })

        with open(output_path, 'w') as f:
            json.dump(backup_data, f, indent=2)

        return True

    def emergency_wipe(self) -> bool:
        """
        Emergency wipe of all data.

        Returns:
            True if successful
        """
        cursor = self._conn.cursor()

        cursor.execute('DELETE FROM memory')
        cursor.execute('DELETE FROM preferences')
        cursor.execute('DELETE FROM history')
        cursor.execute('DELETE FROM agent_context')

        self._conn.commit()
        self.encryption.secure_wipe()

        return True

    def close(self):
        """Close database connection and wipe encryption keys."""
        if self._conn:
            self._conn.close()
            self._conn = None
        self.encryption.secure_wipe()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
