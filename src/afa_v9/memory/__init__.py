"""
AFA Memory System - 多层记忆 + 智能检索
========================================

灵感来源: Mem0, OpenClaw Memory, Hermes Agent Skills

架构:
├── WorkingMemory (工作记忆 - 当前会话)
├── EpisodicMemory (情景记忆 - 事件序列)
├── SemanticMemory (语义记忆 - 知识概念)
└── BM25Search (BM25全文搜索)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "importance": self.importance,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
        }


class WorkingMemory:
    """工作记忆 - 当前会话内的短期记忆"""

    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self._items: List[MemoryEntry] = []

    def store(self, key: str, value: Any, importance: float = 0.5) -> None:
        entry = MemoryEntry(
            id=key,
            content=str(value),
            importance=importance,
        )
        self._items.append(entry)
        if len(self._items) > self.max_items:
            self._items = self._items[-self.max_items:]

    def recall(self, key: str) -> Optional[Any]:
        for item in reversed(self._items):
            if item.id == key:
                item.accessed_at = datetime.now()
                item.access_count += 1
                return item.content
        return None

    def get_recent(self, count: int = 10) -> List[MemoryEntry]:
        return self._items[-count:]


class EpisodicMemory:
    """情景记忆 - 事件序列和经验"""

    def __init__(self, storage_path: Optional[str] = None):
        if storage_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            storage_path = str(project_root / "data" / "memory" / "episodes")

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._episodes: List[Dict] = []
        self._load_episodes()

    def _load_episodes(self) -> None:
        index_file = self.storage_path / "index.json"
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    self._episodes = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load episodes: {e}")

    def _save_episodes(self) -> None:
        try:
            index_file = self.storage_path / "index.json"
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(self._episodes[-1000:], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save episodes: {e}")

    def store_episode(
        self,
        event_type: str,
        content: Dict[str, Any],
        outcome: Optional[str] = None,
    ) -> str:
        episode_id = f"ep_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self._episodes)}"

        episode = {
            "id": episode_id,
            "type": event_type,
            "content": content,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat(),
        }

        self._episodes.append(episode)
        self._save_episodes()

        return episode_id

    def get_recent_episodes(self, count: int = 20) -> List[Dict]:
        return self._episodes[-count:]

    def get_episodes_by_type(self, event_type: str) -> List[Dict]:
        return [e for e in self._episodes if e.get("type") == event_type]


class SemanticMemory:
    """语义记忆 - 知识库和概念"""

    def __init__(self):
        self._knowledge: Dict[str, Any] = {}
        self._concepts: List[str] = []
        self._lottery_knowledge = None
        self._lottery_semantic = None

    def store_knowledge(self, key: str, value: Any) -> None:
        self._knowledge[key] = {
            "value": value,
            "updated_at": datetime.now().isoformat(),
        }

    def recall_knowledge(self, key: str) -> Optional[Any]:
        entry = self._knowledge.get(key)
        if entry:
            return entry.get("value")
        return None

    def add_concept(self, concept: str) -> None:
        if concept not in self._concepts:
            self._concepts.append(concept)

    def get_concepts(self) -> List[str]:
        return self._concepts.copy()

    def get_lottery_knowledge(self):
        """获取彩票官方知识库"""
        if self._lottery_knowledge is None:
            from src.calculations.lottery import LOTTERY_KNOWLEDGE
            self._lottery_knowledge = LOTTERY_KNOWLEDGE
        return self._lottery_knowledge

    def get_lottery_semantic(self):
        """获取彩票规则语义记忆"""
        if self._lottery_semantic is None:
            from src.afa_v9.memory.semantic import get_lottery_semantic_memory
            self._lottery_semantic = get_lottery_semantic_memory()
        return self._lottery_semantic

    def query_rules(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        自然语言查询彩票规则

        Args:
            query: 自然语言查询，如"竞彩返奖率是多少？"
            top_k: 返回最相关的前k个结果

        Returns:
            相关规则列表
        """
        semantic = self.get_lottery_semantic()
        return semantic.query(query, top_k)  # type: ignore[return-value,no-any-return]


class BM25Search:
    """BM25全文搜索引擎 - 真正的BM25算法实现"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self._documents: Dict[str, str] = {}
        self._doc_contents: List[List[str]] = []
        self._doc_ids: List[str] = []
        self._avgdl: float = 0.0
        self.k1 = k1
        self.b = b

    def index_document(self, doc_id: str, content: str) -> None:
        self._documents[doc_id] = content
        self._doc_contents.append(self._tokenize(content))
        self._doc_ids.append(doc_id)
        self._avgdl = sum(len(d) for d in self._doc_contents) / max(1, len(self._doc_contents))

    def _tokenize(self, text: str) -> List[str]:
        import re
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens

    def _calculate_idf(self, term: str) -> float:
        import math
        n = len(self._doc_contents)
        df = sum(1 for doc in self._doc_contents if term in doc)
        if df == 0:
            return 0.0
        return math.log((n - df + 0.5) / (df + 0.5) + 1)

    def _bm25_score(self, query_terms: List[str], doc_idx: int) -> float:
        import math
        doc = self._doc_contents[doc_idx]
        doc_len = len(doc)
        scores = []

        for term in query_terms:
            if term not in doc:
                continue

            tf = doc.count(term)
            idf = self._calculate_idf(term)

            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / max(1, self._avgdl))

            score = idf * (numerator / denominator) if denominator > 0 else 0
            scores.append(score)

        return sum(scores)

    def search(self, query: str, top_k: int = 5) -> List[tuple]:
        query_terms = self._tokenize(query)

        if not query_terms or not self._doc_contents:
            return []

        scores = []
        for i in range(len(self._doc_contents)):
            score = self._bm25_score(query_terms, i)
            if score > 0:
                scores.append((self._doc_ids[i], score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def clear(self) -> None:
        self._documents.clear()
        self._doc_contents.clear()
        self._doc_ids.clear()
        self._avgdl = 0.0


class UnifiedMemory:
    """
    统一记忆系统 - Mem0风格

    使用方式:
        memory = UnifiedMemory()

        # 存储
        memory.store("user_preference", "喜欢英超联赛", importance=0.8)

        # 检索
        results = memory.search("英超")

        # 查询规则
        rules = memory.query_rules("竞彩返奖率是多少？")

        # 获取上下文
        context = memory.get_context_for_llm("分析英超比赛")
    """

    def __init__(self):
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.search_engine = BM25Search()

    def store(
        self,
        key: str,
        value: Any,
        importance: float = 0.5,
        episodic: bool = False,
    ) -> None:
        """存储记忆"""
        self.working.store(key, value, importance)

        if episodic:
            self.episodic.store_episode(
                event_type=key,
                content={"key": key, "value": value},
            )

        self.semantic.store_knowledge(key, value)

        self.search_engine.index_document(key, str(value))

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索记忆"""
        results = self.search_engine.search(query, top_k)

        return [
            {
                "id": doc_id,
                "content": self.working.recall(doc_id) or self.semantic.recall_knowledge(doc_id) or "",
                "score": score,
            }
            for doc_id, score in results
        ]

    def query_rules(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        自然语言查询彩票规则

        Args:
            query: 自然语言查询，如"竞彩返奖率是多少？"
            top_k: 返回最相关的前k个结果

        Returns:
            相关规则列表
        """
        return self.semantic.query_rules(query, top_k)  # type: ignore[no-any-return]

    def get_context_for_llm(self, query: str, max_memories: int = 10) -> str:
        """为LLM生成记忆上下文"""
        results = self.search(query, max_memories)

        if not results:
            return ""

        context_parts = ["# Relevant Memories:\n"]
        for i, result in enumerate(results, 1):
            context_parts.append(f"{i}. {result['content']}")

        return "\n".join(context_parts)

    def complete_episode(self, outcome: str, lessons: List[str] = None) -> str:
        """记录完整的事件episode"""
        return str(self.episodic.store_episode(  # type: ignore[return-value]
            event_type="completed_episode",
            content={"outcome": outcome, "lessons": lessons or []},
            outcome=outcome,
        ))


class Memory:
    """
    Memory类 - 兼容旧API

    提供统一的记忆接口，集成所有记忆类型
    """

    def __init__(self):
        self.working = WorkingMemory()
        self.long_term = SemanticMemory()
        self.episodes = EpisodicMemory()
        self.search_engine = BM25Search()
        self.unified = UnifiedMemory()

    def store_interaction(self, key: str, value: Any, importance: float = 0.5) -> None:
        self.unified.store(key, value, importance, episodic=True)

    def search_memory(self, query: str) -> List[Dict]:
        return self.unified.search(query)  # type: ignore[no-any-return]

    def get_full_context(self) -> str:
        return self.unified.get_context_for_llm("current context")  # type: ignore[no-any-return]


MEMORY_INSTANCE = Memory()

__all__ = [
    "Memory",
    "MEMORY_INSTANCE",
    "WorkingMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "BM25Search",
    "UnifiedMemory",
    "MemoryEntry",
    "LOTTERY_KNOWLEDGE",
    "get_lottery_knowledge",
    "LOTTERY_QUERY",
    "get_lottery_query",
]

from src.calculations.lottery import (
    LOTTERY_KNOWLEDGE,
    get_lottery_knowledge,
    LOTTERY_QUERY,
    get_lottery_query,
)
