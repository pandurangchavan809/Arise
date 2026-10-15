"""
SQLite asynchronous storage backend implementation using aiosqlite and FTS5.
Supports full-text indexing, BM25 ranking, structured metadata queries,
and edge database lifecycle operations.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import re
from typing import Any, Dict, List, Optional
import aiosqlite
import structlog

from adaptive_memory.models import MemoryRecord, MemoryStatus, MemoryType, SafetyTier
from adaptive_memory.storage.interface import StorageBackend

logger = structlog.get_logger(__name__)


class SQLiteStorage(StorageBackend):
    """
    aiosqlite-powered implementation with FTS5 virtual table for full-text retrieval.
    """

    def __init__(self, database_url: str = "sqlite:///./adaptive_memory.db") -> None:
        self.database_url = database_url
        self.db_path = self._parse_db_path(database_url)
        self._db: Optional[aiosqlite.Connection] = None

    @staticmethod
    def _parse_db_path(url: str) -> str:
        """Extract filesystem path from database url."""
        if url.startswith("sqlite:///"):
            return url[len("sqlite:///"):]
        if url.startswith("sqlite://"):
            return url[len("sqlite://"):]
        return url

    async def _get_connection(self) -> aiosqlite.Connection:
        """Obtain active aiosqlite connection or connect if closed."""
        if self._db is None:
            # Ensure parent directory exists if path is not memory
            if self.db_path != ":memory:":
                parent = os.path.dirname(os.path.abspath(self.db_path))
                if parent and not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)

            self._db = await aiosqlite.connect(self.db_path)
            self._db.row_factory = aiosqlite.Row
            await self._db.execute("PRAGMA foreign_keys = ON;")
            await self._db.execute("PRAGMA journal_mode = WAL;")
            await self._db.execute("PRAGMA synchronous = NORMAL;")
        return self._db

    async def initialize(self) -> None:
        """Create tables, FTS5 virtual tables, synchronization triggers, and indexes."""
        db = await self._get_connection()

        # Core memories table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                expires_at TEXT,
                source TEXT NOT NULL,
                task_context TEXT,
                confidence REAL NOT NULL,
                utility REAL NOT NULL,
                importance REAL NOT NULL,
                recency REAL NOT NULL,
                risk_level TEXT NOT NULL,
                status TEXT NOT NULL,
                embedding TEXT,
                metadata TEXT NOT NULL
            );
            """
        )

        # Performance indices
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);",
            "CREATE INDEX IF NOT EXISTS idx_memories_status ON memories(status);",
            "CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_memories_updated_at ON memories(updated_at);",
            "CREATE INDEX IF NOT EXISTS idx_memories_confidence ON memories(confidence);",
            "CREATE INDEX IF NOT EXISTS idx_memories_utility ON memories(utility);",
            "CREATE INDEX IF NOT EXISTS idx_memories_expires_at ON memories(expires_at);",
            "CREATE INDEX IF NOT EXISTS idx_memories_user_status ON memories(user_id, status);",
        ]
        for idx in indexes:
            await db.execute(idx)

        # FTS5 Virtual Table for full text search
        await db.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                id UNINDEXED,
                content,
                task_context,
                tokenize='porter unicode61'
            );
            """
        )

        # Triggers to keep FTS in sync with memories table
        await db.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_memories_ai AFTER INSERT ON memories BEGIN
                INSERT INTO memories_fts(id, content, task_context)
                VALUES (new.id, new.content, COALESCE(new.task_context, ''));
            END;
            """
        )

        await db.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_memories_ad AFTER DELETE ON memories BEGIN
                DELETE FROM memories_fts WHERE id = old.id;
            END;
            """
        )

        await db.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_memories_au AFTER UPDATE ON memories BEGIN
                DELETE FROM memories_fts WHERE id = old.id;
                INSERT INTO memories_fts(id, content, task_context)
                VALUES (new.id, new.content, COALESCE(new.task_context, ''));
            END;
            """
        )

        await db.commit()
        logger.info("SQLite storage initialized with FTS5", db_path=self.db_path)

    async def close(self) -> None:
        """Close database connection."""
        if self._db is not None:
            await self._db.close()
            self._db = None
            logger.info("SQLite storage connection closed")

    def _row_to_record(self, row: aiosqlite.Row) -> MemoryRecord:
        """Map SQLite row to MemoryRecord."""
        embedding_val = None
        if row["embedding"]:
            try:
                embedding_val = json.loads(row["embedding"])
            except Exception:
                embedding_val = None

        meta_dict = {}
        if row["metadata"]:
            try:
                meta_dict = json.loads(row["metadata"])
            except Exception:
                meta_dict = {}

        return MemoryRecord(
            id=row["id"],
            user_id=row["user_id"],
            content=row["content"],
            memory_type=MemoryType(row["memory_type"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
            source=row["source"],
            task_context=row["task_context"],
            confidence=float(row["confidence"]),
            utility=float(row["utility"]),
            importance=float(row["importance"]),
            recency=float(row["recency"]),
            risk_level=SafetyTier(row["risk_level"]),
            status=MemoryStatus(row["status"]),
            embedding=embedding_val,
            metadata=meta_dict,
        )

    async def store(self, record: MemoryRecord) -> MemoryRecord:
        """Insert or replace a memory record in the database."""
        db = await self._get_connection()
        emb_json = json.dumps(record.embedding) if record.embedding is not None else None
        meta_json = json.dumps(record.metadata)

        query = """
            INSERT INTO memories (
                id, user_id, content, memory_type, created_at, updated_at,
                expires_at, source, task_context, confidence, utility,
                importance, recency, risk_level, status, embedding, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            record.id,
            record.user_id,
            record.content,
            record.memory_type.value,
            record.created_at.isoformat(),
            record.updated_at.isoformat(),
            record.expires_at.isoformat() if record.expires_at else None,
            record.source,
            record.task_context,
            record.confidence,
            record.utility,
            record.importance,
            record.recency,
            record.risk_level.value,
            record.status.value,
            emb_json,
            meta_json,
        )

        async with db.execute(query, params):
            pass
        await db.commit()
        return record

    async def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """Fetch memory record by ID."""
        db = await self._get_connection()
        query = "SELECT * FROM memories WHERE id = ?"
        async with db.execute(query, (memory_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return self._row_to_record(row)
        return None

    @staticmethod
    def _sanitize_fts_query(query: str) -> str:
        """Sanitize raw query string for FTS5 MATCH syntax."""
        tokens = re.findall(r"\b[a-zA-Z0-9_]{2,}\b", query)
        if not tokens:
            return ""
        # SQLite FTS5 prefix match syntax: token*
        return " OR ".join(f"{t}*" for t in tokens)

    async def search(
        self,
        query: str,
        user_id: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryRecord]:
        """
        Execute FTS5 search or metadata search.
        """
        db = await self._get_connection()
        sanitized_fts = self._sanitize_fts_query(query) if query else ""

        conditions: List[str] = []
        params: List[Any] = []

        if user_id:
            conditions.append("m.user_id = ?")
            params.append(user_id)

        if memory_types:
            type_placeholders = ",".join("?" for _ in memory_types)
            conditions.append(f"m.memory_type IN ({type_placeholders})")
            params.extend(t.value for t in memory_types)

        if filters:
            if "status" in filters:
                conditions.append("m.status = ?")
                params.append(filters["status"])
            if "risk_level" in filters:
                conditions.append("m.risk_level = ?")
                params.append(filters["risk_level"])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        records: List[MemoryRecord] = []

        # If we have query tokens, attempt FTS query with BM25 rank
        if sanitized_fts:
            try:
                fts_query = f"""
                    SELECT m.*, fts.rank as fts_rank
                    FROM memories_fts fts
                    JOIN memories m ON fts.id = m.id
                    {where_clause + ' AND' if where_clause else 'WHERE'} memories_fts MATCH ?
                    ORDER BY fts.rank ASC, m.updated_at DESC
                    LIMIT ?
                """
                fts_params = list(params) + [sanitized_fts, limit]
                async with db.execute(fts_query, fts_params) as cursor:
                    rows = await cursor.fetchall()
                    for r in rows:
                        records.append(self._row_to_record(r))
            except Exception as e:
                logger.warning("FTS search encountered error, falling back to LIKE", error=str(e))
                records = []

        # Fallback or empty query retrieval
        if not records:
            fallback_conditions = list(conditions)
            fallback_params = list(params)

            if query:
                fallback_conditions.append("(m.content LIKE ? OR m.task_context LIKE ?)")
                fallback_params.extend([f"%{query}%", f"%{query}%"])

            fallback_where = f"WHERE {' AND '.join(fallback_conditions)}" if fallback_conditions else ""
            sql = f"""
                SELECT m.* FROM memories m
                {fallback_where}
                ORDER BY m.updated_at DESC
                LIMIT ?
            """
            fallback_params.append(limit)
            async with db.execute(sql, fallback_params) as cursor:
                rows = await cursor.fetchall()
                for r in rows:
                    records.append(self._row_to_record(r))

        return records

    async def update(self, memory_id: str, updates: Dict[str, Any]) -> MemoryRecord:
        """Update fields of an existing memory record."""
        db = await self._get_connection()
        record = await self.get(memory_id)
        if not record:
            raise ValueError(f"Record with id {memory_id} not found")

        set_clauses: List[str] = []
        params: List[Any] = []

        for field, value in updates.items():
            if field in ("metadata", "embedding") and isinstance(value, (dict, list)):
                value = json.dumps(value)
            set_clauses.append(f"{field} = ?")
            params.append(value)

        # Always update updated_at if not explicitly provided
        if "updated_at" not in updates:
            set_clauses.append("updated_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())

        params.append(memory_id)
        sql = f"UPDATE memories SET {', '.join(set_clauses)} WHERE id = ?"

        async with db.execute(sql, params):
            pass
        await db.commit()

        updated_record = await self.get(memory_id)
        if not updated_record:
            raise RuntimeError(f"Failed to fetch updated record {memory_id}")
        return updated_record

    async def delete(self, memory_id: str) -> bool:
        """Permanently delete a memory record."""
        db = await self._get_connection()
        async with db.execute("DELETE FROM memories WHERE id = ?", (memory_id,)) as cursor:
            affected = cursor.rowcount
        await db.commit()
        return affected > 0

    async def list_by_type(
        self,
        user_id: str,
        memory_type: MemoryType,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MemoryRecord]:
        """List memories by user and memory type with pagination."""
        db = await self._get_connection()
        query = """
            SELECT * FROM memories
            WHERE user_id = ? AND memory_type = ?
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """
        async with db.execute(query, (user_id, memory_type.value, limit, offset)) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_record(r) for r in rows]

    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Compute aggregate statistics for memories owned by user."""
        db = await self._get_connection()

        # Count by type
        type_counts: Dict[str, int] = {}
        async with db.execute(
            "SELECT memory_type, COUNT(*) as cnt FROM memories WHERE user_id = ? GROUP BY memory_type",
            (user_id,)
        ) as cursor:
            for row in await cursor.fetchall():
                type_counts[row["memory_type"]] = row["cnt"]

        # Count by status
        status_counts: Dict[str, int] = {}
        async with db.execute(
            "SELECT status, COUNT(*) as cnt FROM memories WHERE user_id = ? GROUP BY status",
            (user_id,)
        ) as cursor:
            for row in await cursor.fetchall():
                status_counts[row["status"]] = row["cnt"]

        # Total and average utility/confidence
        async with db.execute(
            """
            SELECT COUNT(*) as total, AVG(utility) as avg_utility, AVG(confidence) as avg_confidence
            FROM memories WHERE user_id = ?
            """,
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            total_records = row["total"] if row else 0
            avg_u = round(row["avg_utility"] or 0.0, 3) if row else 0.0
            avg_c = round(row["avg_confidence"] or 0.0, 3) if row else 0.0

        # Estimate storage size
        storage_bytes = 0
        if self.db_path != ":memory:" and os.path.exists(self.db_path):
            storage_bytes = os.path.getsize(self.db_path)

        return {
            "user_id": user_id,
            "total_memories": total_records,
            "counts_by_type": type_counts,
            "counts_by_status": status_counts,
            "average_utility": avg_u,
            "average_confidence": avg_c,
            "storage_bytes": storage_bytes,
        }

    async def get_expired(self, before: datetime) -> List[MemoryRecord]:
        """Fetch all memories whose expires_at timestamp is prior to before."""
        db = await self._get_connection()
        query = """
            SELECT * FROM memories
            WHERE expires_at IS NOT NULL
              AND expires_at <= ?
              AND status = 'active'
        """
        async with db.execute(query, (before.isoformat(),)) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_record(r) for r in rows]
