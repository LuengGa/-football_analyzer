"""
AFA FTS5 Memory Search — 基于SQLite FTS5的全文本搜索
=====================================================

Hermes Agent风格的记忆检索：
- 支持全文本搜索（FTS5）
- 支持中文分词（unicode61）
- 支持时间范围过滤
- 支持标签和分类过滤

FTS5优势：
- 毫秒级全文搜索
- 内置于Python的sqlite3，无需额外依赖
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Any, Optional, List, Dict
from pathlib import Path
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


@dataclass
class MemoryRecord:
    id: int
    key: str
    content: str
    category: str
    tags: List[str]
    importance: float
    created_at: str
    metadata: Dict[str, Any]


class FTS5MemorySearch:
    _instance: Optional["FTS5MemorySearch"] = None
    _lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        if self._initialized:
            return

        if db_path is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            memory_dir = project_root / "memory"
            memory_dir.mkdir(exist_ok=True)
            db_path = str(memory_dir / "memory_fts5.db")

        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()
        self._initialized = True

    def _init_db(self) -> None:
        try:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")

            cursor = self._conn.cursor()
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                    key,
                    content,
                    category,
                    tags,
                    metadata,
                    tokenize='unicode61 remove_diacritics 2'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    raw_content TEXT,
                    category TEXT DEFAULT 'general',
                    tags TEXT DEFAULT '[]',
                    importance REAL DEFAULT 0.5,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata TEXT DEFAULT '{}'
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_category ON memory_records(category)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created ON memory_records(created_at)
            """)
            self._conn.commit()
            logger.info(f"FTS5 memory initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize FTS5: {e}")
            raise

    def _sync_fts(self, key: str, content_str: str, category: str, tags_str: str, metadata_str: str) -> None:
        cursor = self._conn.cursor()  # type: ignore[union-attr]
        cursor.execute("DELETE FROM memory_fts WHERE key = ?", (key,))
        cursor.execute("""
            INSERT INTO memory_fts (key, content, category, tags, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (key, content_str, category, tags_str, metadata_str))

    def index_memory(self, key: str, content: Any, category: str = "general",
                     tags: Optional[List[str]] = None, importance: float = 0.5,
                     metadata: Optional[Dict] = None) -> bool:
        try:
            content_str = json.dumps(content, ensure_ascii=False) if not isinstance(content, str) else content
            tags_str = json.dumps(tags or [], ensure_ascii=False)
            metadata_str = json.dumps(metadata or {}, ensure_ascii=False)
            now = datetime.now().isoformat()

            cursor = self._conn.cursor()  # type: ignore[union-attr]
            cursor.execute("SELECT created_at FROM memory_records WHERE key = ?", (key,))
            row = cursor.fetchone()
            created_at = row[0] if row else now

            cursor.execute("""
                INSERT INTO memory_records (key, raw_content, category, tags, importance, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    raw_content = excluded.raw_content,
                    category = excluded.category,
                    tags = excluded.tags,
                    importance = excluded.importance,
                    updated_at = excluded.updated_at,
                    metadata = excluded.metadata
            """, (key, content_str, category, tags_str, importance, created_at, now, metadata_str))

            self._sync_fts(key, content_str, category, tags_str, metadata_str)
            self._conn.commit()  # type: ignore[union-attr]
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to index memory '{key}': {e}")
            return False

    def search(self, query: str, category: Optional[str] = None,
               tags: Optional[List[str]] = None, limit: int = 10,
               order_by: str = "bm25") -> List[MemoryRecord]:
        try:
            sql_parts = ["SELECT m.id, m.key, m.raw_content, m.category, m.tags, m.importance, m.created_at, m.metadata FROM memory_fts f JOIN memory_records m ON f.key = m.key WHERE memory_fts MATCH ?"]
            params: List[Any] = [query]

            if category:
                sql_parts.append("AND m.category = ?")
                params.append(category)

            if order_by == "bm25":
                sql_parts.append("ORDER BY bm25(memory_fts) LIMIT ?")
            elif order_by == "importance":
                sql_parts.append("ORDER BY m.importance DESC LIMIT ?")
            elif order_by == "recency":
                sql_parts.append("ORDER BY m.created_at DESC LIMIT ?")
            else:
                sql_parts.append("LIMIT ?")
            params.append(limit)

            sql = " ".join(sql_parts)
            cursor = self._conn.cursor()
            cursor.execute(sql, params)

            results = []
            for row in cursor.fetchall():
                tags_list = json.loads(row[4] or "[]")
                if tags and not any(t in tags_list for t in tags):
                    continue
                results.append(MemoryRecord(
                    id=row[0],
                    key=row[1],
                    content=row[2],
                    category=row[3],
                    tags=tags_list,
                    importance=row[5],
                    created_at=row[6],
                    metadata=json.loads(row[7] or "{}")
                ))
            return results
        except sqlite3.Error as e:
            logger.error(f"Search failed: {e}")
            return []

    def search_related(self, key: str, limit: int = 5) -> List[MemoryRecord]:
        try:
            cursor = self._conn.cursor()  # type: ignore[union-attr]
            cursor.execute("SELECT raw_content FROM memory_records WHERE key = ?", (key,))
            row = cursor.fetchone()
            if not row:
                return []

            content = row[0][:500]
            words = content.split()[:5]
            query = " OR ".join(f'"{w}"' for w in words if len(w) > 3)
            if not query:
                query = f'"{content[:50]}"'
            return self.search(query, limit=limit)
        except sqlite3.Error as e:
            logger.error(f"Related search failed: {e}")
            return []

    def get_recent(self, category: Optional[str] = None, limit: int = 20) -> List[MemoryRecord]:
        try:
            cursor = self._conn.cursor()  # type: ignore[union-attr]
            if category:
                cursor.execute("""
                    SELECT id, key, raw_content, category, tags, importance, created_at, metadata
                    FROM memory_records WHERE category = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (category, limit))
            else:
                cursor.execute("""
                    SELECT id, key, raw_content, category, tags, importance, created_at, metadata
                    FROM memory_records ORDER BY created_at DESC LIMIT ?
                """, (limit,))

            results = []
            for row in cursor.fetchall():
                results.append(MemoryRecord(
                    id=row[0],
                    key=row[1],
                    content=row[2],
                    category=row[3],
                    tags=json.loads(row[4] or "[]"),
                    importance=row[5],
                    created_at=row[6],
                    metadata=json.loads(row[7] or "{}")
                ))
            return results
        except sqlite3.Error as e:
            logger.error(f"Get recent failed: {e}")
            return []

    def delete(self, key: str) -> bool:
        try:
            cursor = self._conn.cursor()  # type: ignore[union-attr]
            cursor.execute("DELETE FROM memory_fts WHERE key = ?", (key,))
            cursor.execute("DELETE FROM memory_records WHERE key = ?", (key,))
            self._conn.commit()  # type: ignore[union-attr]
            return True
        except sqlite3.Error as e:
            logger.error(f"Delete failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        try:
            cursor = self._conn.cursor()  # type: ignore[union-attr]
            cursor.execute("SELECT COUNT(*) FROM memory_records")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT category, COUNT(*) FROM memory_records GROUP BY category")
            categories = dict(cursor.fetchall())
            cursor.execute("SELECT AVG(importance) FROM memory_records")
            avg_importance = cursor.fetchone()[0] or 0
            return {
                "total_records": total,
                "categories": categories,
                "avg_importance": round(avg_importance, 3),
                "db_path": self.db_path,
            }
        except sqlite3.Error as e:
            logger.error(f"Get stats failed: {e}")
            return {}

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


FTS5_MEMORY = FTS5MemorySearch()

__all__ = ["FTS5MemorySearch", "FTS5_MEMORY", "MemoryRecord"]
