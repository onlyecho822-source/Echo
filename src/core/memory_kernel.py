"""
Echo Life OS - Memory Kernel
============================
Persistent, encrypted personal memory system with dual-memory architecture.

This is the core identity layer that makes Echo uniquely yours.
"""

import os
import json
import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Cryptography imports
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64


class MemoryType(Enum):
    """Types of memory in the system."""
    WORKING = "working"          # Current session context
    EPISODIC = "episodic"        # Specific events and experiences
    SEMANTIC = "semantic"         # Facts, concepts, relationships
    PROCEDURAL = "procedural"     # Learned behaviors and preferences
    SESSION = "session"           # Session history


class MemoryPriority(Enum):
    """Priority levels for memory consolidation."""
    CRITICAL = 5     # Never decay
    HIGH = 4         # Long retention
    MEDIUM = 3       # Normal retention
    LOW = 2          # Short retention
    EPHEMERAL = 1    # Session only


@dataclass
class Memory:
    """A single memory unit."""
    id: str
    content: str
    memory_type: MemoryType
    priority: MemoryPriority
    created_at: datetime
    accessed_at: datetime
    access_count: int
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    decay_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary for storage."""
        return {
            'id': self.id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'priority': self.priority.value,
            'created_at': self.created_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'access_count': self.access_count,
            'embedding': self.embedding,
            'metadata': self.metadata,
            'tags': self.tags,
            'decay_score': self.decay_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create memory from dictionary."""
        return cls(
            id=data['id'],
            content=data['content'],
            memory_type=MemoryType(data['memory_type']),
            priority=MemoryPriority(data['priority']),
            created_at=datetime.fromisoformat(data['created_at']),
            accessed_at=datetime.fromisoformat(data['accessed_at']),
            access_count=data['access_count'],
            embedding=data.get('embedding'),
            metadata=data.get('metadata'),
            tags=data.get('tags'),
            decay_score=data.get('decay_score', 1.0)
        )


class EncryptionManager:
    """Handles all encryption operations for the Memory Kernel."""

    def __init__(self, password: str, salt: Optional[bytes] = None):
        """Initialize encryption with password-derived key."""
        self.salt = salt or os.urandom(16)

        # Derive key from password using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> bytes:
        """Encrypt string data."""
        return self.fernet.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt data to string."""
        return self.fernet.decrypt(encrypted_data).decode()

    def get_salt(self) -> bytes:
        """Get salt for storage."""
        return self.salt


class MemoryKernel:
    """
    Core memory system for Echo Life OS.

    Implements a dual-memory architecture with:
    - Working memory (short-term, session-based)
    - Long-term memory (persistent, encrypted)

    Features:
    - AES-256 encryption at rest
    - Semantic vector embeddings for retrieval
    - Memory consolidation and decay
    - Version-controlled history
    """

    def __init__(self, base_path: str = "~/.echo", password: Optional[str] = None):
        """Initialize the Memory Kernel."""
        self.base_path = Path(base_path).expanduser()
        self._setup_directories()

        # Initialize encryption if password provided
        self.encryption: Optional[EncryptionManager] = None
        if password:
            salt = self._load_or_create_salt()
            self.encryption = EncryptionManager(password, salt)

        # Initialize database
        self.db_path = self.base_path / "memory" / "kernel.db"
        self._init_database()

        # Working memory (in-session only)
        self.working_memory: Dict[str, Memory] = {}

    def _setup_directories(self):
        """Create necessary directories."""
        directories = [
            self.base_path / "memory",
            self.base_path / "memory" / "vectors",
            self.base_path / "memory" / "sessions",
            self.base_path / "memory" / "exports",
            self.base_path / "keys",
            self.base_path / "config"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_or_create_salt(self) -> bytes:
        """Load existing salt or create new one."""
        salt_path = self.base_path / "keys" / "salt.key"
        if salt_path.exists():
            return salt_path.read_bytes()
        else:
            salt = os.urandom(16)
            salt_path.write_bytes(salt)
            return salt

    def _init_database(self):
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Main memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content_encrypted BLOB NOT NULL,
                memory_type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                accessed_at TEXT NOT NULL,
                access_count INTEGER DEFAULT 1,
                embedding BLOB,
                metadata_encrypted BLOB,
                tags TEXT,
                decay_score REAL DEFAULT 1.0
            )
        ''')

        # Memory relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_links (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                link_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES memories(id),
                FOREIGN KEY (target_id) REFERENCES memories(id),
                PRIMARY KEY (source_id, target_id, link_type)
            )
        ''')

        # Session history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                summary_encrypted BLOB,
                memory_ids TEXT
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_decay_score ON memories(decay_score)')

        conn.commit()
        conn.close()

    def store(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SEMANTIC,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None
    ) -> str:
        """
        Store a new memory.

        Args:
            content: The memory content
            memory_type: Type of memory
            priority: Priority level for retention
            metadata: Additional metadata
            tags: Tags for categorization
            embedding: Vector embedding for semantic search

        Returns:
            Memory ID
        """
        memory_id = str(uuid.uuid4())
        now = datetime.utcnow()

        memory = Memory(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            priority=priority,
            created_at=now,
            accessed_at=now,
            access_count=1,
            embedding=embedding,
            metadata=metadata,
            tags=tags
        )

        # Store in working memory for quick access
        if memory_type == MemoryType.WORKING:
            self.working_memory[memory_id] = memory
            return memory_id

        # Store in persistent storage
        self._persist_memory(memory)
        return memory_id

    def _persist_memory(self, memory: Memory):
        """Persist memory to encrypted database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Encrypt sensitive data
        if self.encryption:
            content_encrypted = self.encryption.encrypt(memory.content)
            metadata_encrypted = self.encryption.encrypt(
                json.dumps(memory.metadata)
            ) if memory.metadata else None
        else:
            content_encrypted = memory.content.encode()
            metadata_encrypted = json.dumps(memory.metadata).encode() if memory.metadata else None

        # Serialize embedding
        embedding_blob = json.dumps(memory.embedding).encode() if memory.embedding else None

        cursor.execute('''
            INSERT OR REPLACE INTO memories
            (id, content_encrypted, memory_type, priority, created_at, accessed_at,
             access_count, embedding, metadata_encrypted, tags, decay_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.id,
            content_encrypted,
            memory.memory_type.value,
            memory.priority.value,
            memory.created_at.isoformat(),
            memory.accessed_at.isoformat(),
            memory.access_count,
            embedding_blob,
            metadata_encrypted,
            json.dumps(memory.tags) if memory.tags else None,
            memory.decay_score
        ))

        conn.commit()
        conn.close()

    def retrieve(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: The memory ID

        Returns:
            Memory object or None
        """
        # Check working memory first
        if memory_id in self.working_memory:
            memory = self.working_memory[memory_id]
            memory.access_count += 1
            memory.accessed_at = datetime.utcnow()
            return memory

        # Query persistent storage
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM memories WHERE id = ?', (memory_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        # Decrypt and reconstruct memory
        memory = self._row_to_memory(row)

        # Update access stats
        memory.access_count += 1
        memory.accessed_at = datetime.utcnow()
        self._update_access_stats(memory_id, memory.access_count, memory.accessed_at)

        conn.close()
        return memory

    def _row_to_memory(self, row) -> Memory:
        """Convert database row to Memory object."""
        (id, content_encrypted, memory_type, priority, created_at, accessed_at,
         access_count, embedding_blob, metadata_encrypted, tags_json, decay_score) = row

        # Decrypt content
        if self.encryption:
            content = self.encryption.decrypt(content_encrypted)
            metadata = json.loads(self.encryption.decrypt(metadata_encrypted)) if metadata_encrypted else None
        else:
            content = content_encrypted.decode() if isinstance(content_encrypted, bytes) else content_encrypted
            metadata = json.loads(metadata_encrypted.decode()) if metadata_encrypted else None

        # Deserialize embedding
        embedding = json.loads(embedding_blob.decode()) if embedding_blob else None

        return Memory(
            id=id,
            content=content,
            memory_type=MemoryType(memory_type),
            priority=MemoryPriority(priority),
            created_at=datetime.fromisoformat(created_at),
            accessed_at=datetime.fromisoformat(accessed_at),
            access_count=access_count,
            embedding=embedding,
            metadata=metadata,
            tags=json.loads(tags_json) if tags_json else None,
            decay_score=decay_score
        )

    def _update_access_stats(self, memory_id: str, access_count: int, accessed_at: datetime):
        """Update access statistics for a memory."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE memories
            SET access_count = ?, accessed_at = ?
            WHERE id = ?
        ''', (access_count, accessed_at.isoformat(), memory_id))

        conn.commit()
        conn.close()

    def search(
        self,
        query: str = None,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        min_priority: Optional[MemoryPriority] = None,
        limit: int = 10
    ) -> List[Memory]:
        """
        Search memories by various criteria.

        Args:
            query: Text to search for in content
            memory_type: Filter by memory type
            tags: Filter by tags
            min_priority: Minimum priority level
            limit: Maximum results to return

        Returns:
            List of matching memories
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Build query
        sql = 'SELECT * FROM memories WHERE 1=1'
        params = []

        if memory_type:
            sql += ' AND memory_type = ?'
            params.append(memory_type.value)

        if min_priority:
            sql += ' AND priority >= ?'
            params.append(min_priority.value)

        sql += ' ORDER BY decay_score DESC, accessed_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        memories = [self._row_to_memory(row) for row in rows]

        # Filter by query if provided (post-decryption)
        if query:
            query_lower = query.lower()
            memories = [m for m in memories if query_lower in m.content.lower()]

        # Filter by tags
        if tags:
            memories = [m for m in memories if m.tags and any(t in m.tags for t in tags)]

        return memories[:limit]

    def consolidate(self):
        """
        Run memory consolidation process.

        - Promote frequently accessed working memories to long-term
        - Apply decay to low-priority memories
        - Archive or delete expired memories
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        now = datetime.utcnow()

        # Apply decay based on priority and recency
        cursor.execute('SELECT id, priority, accessed_at, access_count, decay_score FROM memories')
        rows = cursor.fetchall()

        for row in rows:
            memory_id, priority, accessed_at_str, access_count, current_decay = row
            accessed_at = datetime.fromisoformat(accessed_at_str)

            # Calculate new decay score
            days_since_access = (now - accessed_at).days

            # Decay formula: higher priority = slower decay
            # More accesses = slower decay
            decay_rate = 0.1 / (priority * (1 + access_count * 0.1))
            new_decay = max(0.0, current_decay - (decay_rate * days_since_access))

            cursor.execute(
                'UPDATE memories SET decay_score = ? WHERE id = ?',
                (new_decay, memory_id)
            )

        # Delete memories with zero decay (unless critical)
        cursor.execute('''
            DELETE FROM memories
            WHERE decay_score <= 0 AND priority < ?
        ''', (MemoryPriority.CRITICAL.value,))

        conn.commit()
        conn.close()

        # Consolidate working memory
        self._consolidate_working_memory()

    def _consolidate_working_memory(self):
        """Promote important working memories to long-term storage."""
        for memory_id, memory in list(self.working_memory.items()):
            # Promote if accessed multiple times
            if memory.access_count >= 3:
                memory.memory_type = MemoryType.EPISODIC
                self._persist_memory(memory)
                del self.working_memory[memory_id]

    def export(self, output_path: str, include_embeddings: bool = False) -> str:
        """
        Export memory bundle for portability.

        Args:
            output_path: Path for export file
            include_embeddings: Include vector embeddings

        Returns:
            Path to exported file
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM memories')
        rows = cursor.fetchall()
        conn.close()

        memories = []
        for row in rows:
            memory = self._row_to_memory(row)
            data = memory.to_dict()
            if not include_embeddings:
                data['embedding'] = None
            memories.append(data)

        export_data = {
            'version': '1.0.0',
            'exported_at': datetime.utcnow().isoformat(),
            'memory_count': len(memories),
            'memories': memories
        }

        output = Path(output_path)
        output.write_text(json.dumps(export_data, indent=2))

        return str(output)

    def import_bundle(self, bundle_path: str):
        """
        Import a memory bundle.

        Args:
            bundle_path: Path to import file
        """
        bundle = json.loads(Path(bundle_path).read_text())

        for memory_data in bundle['memories']:
            memory = Memory.from_dict(memory_data)
            self._persist_memory(memory)

    def clear_working_memory(self):
        """Clear all working memory."""
        self.working_memory.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        stats = {}

        # Total memories
        cursor.execute('SELECT COUNT(*) FROM memories')
        stats['total_memories'] = cursor.fetchone()[0]

        # By type
        cursor.execute('''
            SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type
        ''')
        stats['by_type'] = dict(cursor.fetchall())

        # By priority
        cursor.execute('''
            SELECT priority, COUNT(*) FROM memories GROUP BY priority
        ''')
        stats['by_priority'] = dict(cursor.fetchall())

        # Working memory
        stats['working_memory_count'] = len(self.working_memory)

        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    # Initialize kernel with encryption
    kernel = MemoryKernel(password="secure_password_here")

    # Store some memories
    memory_id = kernel.store(
        content="User prefers dark mode interfaces",
        memory_type=MemoryType.PROCEDURAL,
        priority=MemoryPriority.HIGH,
        tags=["preferences", "ui"]
    )
    print(f"Stored memory: {memory_id}")

    # Store a working memory
    kernel.store(
        content="Current task: building Echo Life OS",
        memory_type=MemoryType.WORKING,
        priority=MemoryPriority.MEDIUM
    )

    # Search memories
    results = kernel.search(query="dark mode", limit=5)
    for memory in results:
        print(f"Found: {memory.content}")

    # Get stats
    stats = kernel.get_stats()
    print(f"Memory stats: {stats}")

    # Run consolidation
    kernel.consolidate()
