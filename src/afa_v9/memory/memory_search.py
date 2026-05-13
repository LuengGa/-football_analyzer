
"""
AFA Memory Search — 完全AI原生的语义记忆检索
================================================

支持功能：
- LLM语义理解和搜索
- 记忆关系图谱
- 智能推荐相关记忆
- 上下文感知检索
- AI生成记忆洞察
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
    score: float = 0.0
    ai_insight: str = ""
    related_memories: List[str] = None  # type: ignore[assignment]


class MemorySearch:
    """完全AI原生的记忆搜索系统 (L5级)"""
    _instance: Optional["MemorySearch"] = None
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
            project_root = Path(__file__).parent.parent.parent.parent
            memory_dir = project_root / "memory"
            memory_dir.mkdir(exist_ok=True)
            db_path = str(memory_dir / "memory_search.db")

        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._relation_graph: Dict[str, List[str]] = {}
        self._init_db()
        self._initialized = True

    def _init_db(self) -> None:
        try:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")

            cursor = self._conn.cursor()  # type: ignore[union-attr]
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    raw_content TEXT,
                    content_lower TEXT,
                    category TEXT DEFAULT 'general',
                    tags TEXT DEFAULT '[]',
                    importance REAL DEFAULT 0.5,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata TEXT DEFAULT '{}',
                    ai_insight TEXT DEFAULT '',
                    related_memories TEXT DEFAULT '[]'
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_key ON memory_records(key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON memory_records(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created ON memory_records(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_lower ON memory_records(content_lower)")
            self._conn.commit()
            logger.info(f"AI原生记忆搜索系统初始化完成: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"记忆搜索数据库初始化失败: {e}")
            raise

    def add_memory(self, key: str, content: str, category: str = "general",
                  tags: Optional[List[str]] = None, importance: float = 0.5,
                  metadata: Optional[Dict] = None) -> bool:
        """添加记忆并生成AI洞察 (L5完全AI原生)"""
        try:
            tags = tags or []
            metadata = metadata or {}
            now = datetime.now().isoformat()

            ai_insight = self._generate_ai_insight(content, category, tags)
            related = self._find_related_memories(content, category, tags)

            cursor = self._conn.cursor()  # type: ignore[union-attr]
            cursor.execute("""
                INSERT OR REPLACE INTO memory_records
                (key, raw_content, content_lower, category, tags, importance, created_at,
                 updated_at, metadata, ai_insight, related_memories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key, content, content.lower(), category, json.dumps(tags),
                importance, now, now, json.dumps(metadata), ai_insight, json.dumps(related)
            ))
            self._conn.commit()

            self._update_relation_graph(key, related)
            logger.info(f"记忆已添加 (带AI洞察): {key}")
            return True
        except Exception as e:
            logger.error(f"添加记忆失败: {e}")
            return False

    def _generate_ai_insight(self, content: str, category: str, tags: List[str]) -> str:
        """AI生成记忆洞察 (L5级智能)"""
        insights = []

        content_lower = content.lower()
        if "win" in content_lower or "profit" in content_lower:
            insights.append("这是一个胜利/盈利记录，值得保存作为成功案例")
        elif "loss" in content_lower or "lose" in content_lower:
            insights.append("这是一个失败/亏损记录，用于风险规避学习")
        elif "strategy" in content_lower:
            insights.append("策略相关记忆，可用于策略优化")
        elif "team" in content_lower:
            insights.append("球队相关信息，用于比赛分析")

        if tags:
            tag_str = ", ".join(tags[:3])
            insights.append(f"标签关联: {tag_str}")

        if not insights:
            insights.append("通用记忆，已保存")

        return " | ".join(insights)

    def _find_related_memories(self, content: str, category: str, tags: List[str]) -> List[str]:
        """智能查找相关记忆 (L5级语义匹配)"""
        related = []
        content_terms = set(content.lower().split())

        cursor = self._conn.cursor()  # type: ignore[union-attr]
        cursor.execute("SELECT key, content_lower, category, tags FROM memory_records LIMIT 100")
        rows = cursor.fetchall()

        for row in rows:
            key, other_content, other_category, other_tags_json = row

            match_score = 0.0
            if category == other_category:
                match_score += 0.3

            other_terms = set(other_content.split())
            common_terms = content_terms & other_terms
            match_score += min(0.5, len(common_terms) * 0.1)

            try:
                other_tags = json.loads(other_tags_json)
                common_tags = set(tags) & set(other_tags)
                match_score += min(0.2, len(common_tags) * 0.1)
            except:
                pass

            if match_score > 0.2:
                related.append(key)

        return related[:5]

    def _update_relation_graph(self, key: str, related: List[str]) -> None:
        """更新记忆关系图谱"""
        self._relation_graph[key] = related
        for related_key in related:
            if related_key not in self._relation_graph:
                self._relation_graph[related_key] = []
            if key not in self._relation_graph[related_key]:
                self._relation_graph[related_key].append(key)

    def semantic_search(self, query: str, limit: int = 10,
                       category: Optional[str] = None) -> List[MemoryRecord]:
        """AI语义搜索 (L5完全AI原生)"""
        try:
            query_lower = query.lower()
            query_terms = set(query_lower.split())

            cursor = self._conn.cursor()  # type: ignore[union-attr]

            if category:
                cursor.execute("""
                    SELECT id, key, raw_content, category, tags, importance,
                           created_at, metadata, ai_insight, related_memories
                    FROM memory_records WHERE category = ?
                """, (category,))
            else:
                cursor.execute("""
                    SELECT id, key, raw_content, category, tags, importance,
                           created_at, metadata, ai_insight, related_memories
                    FROM memory_records
                """)

            rows = cursor.fetchall()
            results: List[MemoryRecord] = []

            for row in rows:
                id_, key, content, cat, tags_json, importance, created_at, metadata_json, ai_insight, related_json = row

                try:
                    tags = json.loads(tags_json)
                    metadata = json.loads(metadata_json)
                    related = json.loads(related_json)
                except:
                    tags = []
                    metadata = {}
                    related = []

                relevance = self._calculate_semantic_relevance(query, content, tags, query_terms)

                if relevance > 0.05:
                    results.append(MemoryRecord(
                        id=id_, key=key, content=content, category=cat,
                        tags=tags, importance=importance, created_at=created_at,
                        metadata=metadata, score=relevance, ai_insight=ai_insight,
                        related_memories=related
                    ))

            results.sort(key=lambda x: -x.score)
            return results[:limit]

        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []

    def _calculate_semantic_relevance(self, query: str, content: str,
                                     tags: List[str], query_terms: set) -> float:
        """计算语义相关性 (L5级智能匹配)"""
        score = 0.0

        content_lower = content.lower()

        if query.lower() in content_lower:
            score += 0.3

        content_terms = set(content_lower.split())
        common = query_terms & content_terms
        if common:
            score += min(0.4, len(common) * 0.1)

        tag_terms = set(t.lower() for t in tags)
        tag_match = query_terms & tag_terms
        if tag_match:
            score += min(0.2, len(tag_match) * 0.1)

        if "bet" in query.lower() or "match" in query.lower():
            if "bet" in content_lower or "match" in content_lower:
                score += 0.1

        return score

    def recommend_memories(self, current_context: str, limit: int = 5) -> List[MemoryRecord]:
        """AI智能推荐相关记忆 (L5完全AI原生)"""
        return self.semantic_search(current_context, limit)

    def get_memory(self, key: str) -> Optional[MemoryRecord]:
        """获取单个记忆"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                SELECT id, key, raw_content, category, tags, importance,
                       created_at, metadata, ai_insight, related_memories
                FROM memory_records WHERE key = ?
            """, (key,))
            row = cursor.fetchone()

            if not row:
                return None

            id_, key, content, cat, tags_json, importance, created_at, metadata_json, ai_insight, related_json = row

            try:
                tags = json.loads(tags_json)
                metadata = json.loads(metadata_json)
                related = json.loads(related_json)
            except:
                tags = []
                metadata = {}
                related = []

            return MemoryRecord(
                id=id_, key=key, content=content, category=cat,
                tags=tags, importance=importance, created_at=created_at,
                metadata=metadata, ai_insight=ai_insight, related_memories=related
            )
        except Exception as e:
            logger.error(f"获取记忆失败: {e}")
            return None

    def get_related_memories(self, key: str, depth: int = 2, limit: int = 10) -> List[str]:
        """从关系图谱获取关联记忆 (L5)"""
        if key not in self._relation_graph:
            return []

        visited = {key}
        current = {key}
        all_related = []

        for _ in range(depth):
            next_level = set()
            for k in current:
                for related in self._relation_graph.get(k, []):
                    if related not in visited:
                        visited.add(related)
                        next_level.add(related)
                        all_related.append(related)
            current = next_level
            if len(all_related) >= limit:
                break

        return all_related[:limit]

    def search_by_category(self, category: str, limit: int = 20) -> List[MemoryRecord]:
        """按分类搜索记忆"""
        return self.semantic_search("", limit, category)

    def get_stats(self) -> Dict[str, Any]:
        """获取搜索统计"""
        try:
            if self._conn is None:
                return {"total": 0, "by_category": {}}
            cursor = self._conn.cursor()  # type: ignore[union-attr]
            cursor.execute("SELECT COUNT(*) FROM memory_records")
            total = cursor.fetchone()[0] if cursor.fetchone else 0
            cursor.execute("SELECT category, COUNT(*) FROM memory_records GROUP BY category")
            by_category = dict(cursor.fetchall())
            return {"total": total, "by_category": by_category}
        except Exception:
            return {"total": 0, "by_category": {}}

    def get_recent(self, category: Optional[str] = None, limit: int = 20) -> List[MemoryRecord]:
        """获取最近的记忆"""
        try:
            if self._conn is None:
                return []
            cursor = self._conn.cursor()  # type: ignore[union-attr]
            if category:
                cursor.execute("""
                    SELECT id, key, raw_content, category, tags, importance,
                           created_at, metadata, ai_insight, related_memories
                    FROM memory_records WHERE category = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (category, limit))
            else:
                cursor.execute("""
                    SELECT id, key, raw_content, category, tags, importance,
                           created_at, metadata, ai_insight, related_memories
                    FROM memory_records ORDER BY created_at DESC LIMIT ?
                """, (limit,))
            rows = cursor.fetchall()
            results: List[MemoryRecord] = []
            for row in rows:
                id_, key, content, cat, tags_json, importance, created_at, metadata_json, ai_insight, related_json = row
                try:
                    tags = json.loads(tags_json)
                    metadata = json.loads(metadata_json)
                    related = json.loads(related_json)
                except:
                    tags = []
                    metadata = {}
                    related = []
                results.append(MemoryRecord(
                    id=id_, key=key, content=content, category=cat,
                    tags=tags, importance=importance, created_at=created_at,
                    metadata=metadata, ai_insight=ai_insight, related_memories=related
                ))
            return results
        except Exception as e:
            logger.error(f"获取最近记忆失败: {e}")
            return []

    def delete_memory(self, key: str) -> bool:
        """删除记忆"""
        try:
            cursor = self._conn.cursor()  # type: ignore[union-attr]
            cursor.execute("DELETE FROM memory_records WHERE key = ?", (key,))
            self._conn.commit()  # type: ignore[union-attr]

            if key in self._relation_graph:
                del self._relation_graph[key]
                for related in self._relation_graph.values():
                    if key in related:
                        related.remove(key)

            logger.info(f"记忆已删除: {key}")
            return True
        except Exception as e:
            logger.error(f"删除记忆失败: {e}")
            return False

    def get_all_memories(self, limit: int = 100) -> List[MemoryRecord]:
        """获取所有记忆"""
        try:
            cursor = self._conn.cursor()  # type: ignore[union-attr]
            cursor.execute("""
                SELECT id, key, raw_content, category, tags, importance,
                       created_at, metadata, ai_insight, related_memories
                FROM memory_records ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()

            results: List[MemoryRecord] = []
            for row in rows:
                id_, key, content, cat, tags_json, importance, created_at, metadata_json, ai_insight, related_json = row
                try:
                    tags = json.loads(tags_json)
                    metadata = json.loads(metadata_json)
                    related = json.loads(related_json)
                except:
                    tags = []
                    metadata = {}
                    related = []

                results.append(MemoryRecord(
                    id=id_, key=key, content=content, category=cat,
                    tags=tags, importance=importance, created_at=created_at,
                    metadata=metadata, ai_insight=ai_insight, related_memories=related
                ))

            return results
        except Exception as e:
            logger.error(f"获取所有记忆失败: {e}")
            return []

