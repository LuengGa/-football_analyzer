"""
AFA Unified Memory — 整合短时、长时、情景记忆 + 高性能搜索
"""

from typing import Any, Optional, List, Dict
from .short_term import ShortTermMemory, SHORT_TERM_MEMORY
from .long_term import LongTermMemory, LONG_TERM_MEMORY
from .episodic_store import Episode, EpisodicStore, EPISODIC_STORE
from .memory_search import MemorySearch

MEMORY_SEARCH = MemorySearch()


class UnifiedMemory:
    def __init__(self):
        self.short_term = SHORT_TERM_MEMORY
        self.long_term = LONG_TERM_MEMORY
        self.episodes = EPISODIC_STORE
        self.search = MEMORY_SEARCH

    def store_interaction(self, key: str, content: Any, importance: float = 0.5,
                          category: str = "interaction", tags: Optional[List[str]] = None) -> bool:
        self.short_term.store(key, content, importance)
        if importance > 0.8:
            self.long_term.store(key, content, category=category, tags=tags)
        return bool(self.search.index_memory(
            key=key,
            content=content,
            category=category,
            tags=tags,
            importance=importance,
            metadata={"source": "interaction"}
        ))  # type: ignore[no-any-return]

    def search_memories(self, query: str, category: Optional[str] = None,
                       tags: Optional[List[str]] = None, limit: int = 10,
                       order_by: str = "bm25") -> List[Any]:
        results = self.search.search(query, category=category, tags=tags, limit=limit, order_by=order_by)
        return [r.content for r in results]

    def search_related(self, key: str, limit: int = 5) -> List[Any]:
        results = self.search.search_related(key, limit=limit)
        return [r.content for r in results]

    def retrieve_all(self, key: str) -> dict[str, Any]:
        result = {}
        st_content = self.short_term.retrieve(key)
        if st_content is not None:
            result["short_term"] = st_content
        lt_content = self.long_term.retrieve(key)
        if lt_content is not None:
            result["long_term"] = lt_content
        return result

    def get_full_context(self) -> dict:
        return {
            "short_term": self.short_term.to_dict(),
            "long_term": self.long_term.get_knowledge_summary(),
            "episodes": self.episodes.get_episode_metrics(),
            "search_stats": self.search.get_stats(),
        }

    def get_recent_memories(self, limit: int = 20, category: Optional[str] = None) -> List[Dict]:
        records = self.search.get_recent(category=category, limit=limit)
        return [
            {
                "key": r.key,
                "content": r.content,
                "category": r.category,
                "tags": r.tags,
                "importance": r.importance,
                "created_at": r.created_at,
            }
            for r in records
        ]

    def migrate_legacy_memory(self) -> int:
        migrated = 0
        for key, item in self.long_term._memory.items():
            self.search.index_memory(
                key=key,
                content=item.content,
                category=item.category,
                tags=item.tags,
                importance=0.8,
                metadata=item.metadata
            )
            migrated += 1
        return migrated


UNIFIED_MEMORY = UnifiedMemory()

__all__ = [
    "UnifiedMemory",
    "UNIFIED_MEMORY",
    "MemorySearch",
    "MEMORY_SEARCH",
]
