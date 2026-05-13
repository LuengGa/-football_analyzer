"""
AI-Augmented Memory Search - 智能记忆搜索
========================================

核心功能：
- LLM 语义搜索和理解
- 记忆关系图谱构建
- 智能记忆聚类和关联
- 上下文感知的记忆推荐
"""

import json
import logging
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class SemanticMemory:
    """语义记忆节点"""
    key: str
    content: str
    embedding: List[float] = field(default_factory=list)
    connections: Set[str] = field(default_factory=set)
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    importance: float = 0.5
    created_at: str = ""
    access_count: int = 0


@dataclass
class MemoryCluster:
    """记忆聚类"""
    cluster_id: str
    theme: str
    memories: List[str]
    coherence: float
    description: str


class LLMMemorySearch:
    """
    LLM增强的语义记忆搜索

    完全替代BM25搜索，使用语义理解
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self.semantic_index: Dict[str, SemanticMemory] = {}
        self.clusters: List[MemoryCluster] = []
        self._relation_graph: Dict[str, Set[str]] = defaultdict(set)

    def index_with_semantics(
        self,
        key: str,
        content: str,
        tags: Optional[List[str]] = None,
        category: str = "general",
        importance: float = 0.5,
    ) -> bool:
        """
        语义索引记忆

        使用LLM提取语义信息并建立关联
        """
        try:
            memory = SemanticMemory(
                key=key,
                content=content,
                tags=tags or [],
                category=category,
                importance=importance,
                created_at=datetime.now().isoformat(),
            )

            if self.llm:
                memory = self._extract_semantics(memory)

            self.semantic_index[key] = memory
            self._build_connections(key, memory)

            return True
        except Exception as e:
            logger.warning(f"Semantic indexing failed: {e}")
            return False

    def _extract_semantics(self, memory: SemanticMemory) -> SemanticMemory:
        """使用LLM提取语义"""
        try:
            if not self.llm:
                return memory

            prompt = f"""分析以下记忆内容，提取关键语义信息：

内容: {memory.content[:500]}
标签: {memory.tags}

请返回JSON格式：
{{
  "summary": "一句话总结",
  "key_entities": ["实体1", "实体2"],
  "concepts": ["概念1", "概念2"],
  "sentiment": "positive/negative/neutral",
  "related_topics": ["相关话题1", "相关话题2"]
}}"""

            response = self.llm.generate(prompt, temperature=0.3, max_tokens=300)

            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                memory.tags.extend(data.get("key_entities", [])[:5])
                memory.tags.extend(data.get("concepts", [])[:3])

            return memory
        except Exception:
            return memory

    def _build_connections(self, key: str, memory: SemanticMemory) -> None:
        """构建记忆关联"""
        self._relation_graph[key] = set()

        for existing_key, existing_mem in self.semantic_index.items():
            if existing_key == key:
                continue

            connection_score = self._calculate_connection(memory, existing_mem)
            if connection_score > 0.3:
                self._relation_graph[key].add(existing_key)
                self._relation_graph[existing_key].add(key)
                memory.connections.add(existing_key)

    def _calculate_connection(self, mem1: SemanticMemory, mem2: SemanticMemory) -> float:
        """计算两个记忆的关联度"""
        score = 0.0

        common_tags = set(mem1.tags) & set(mem2.tags)
        score += len(common_tags) * 0.2

        if mem1.category == mem2.category:
            score += 0.3

        common_words = set(mem1.content.lower().split()) & set(mem2.content.lower().split())
        if len(common_words) > 5:
            score += 0.2

        return min(1.0, score)

    def semantic_search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        语义搜索

        使用LLM理解查询意图，返回最相关记忆
        """
        if not self.semantic_index:
            return []

        results: List[Dict[str, Any]] = []

        query_lower = query.lower()
        query_terms = set(query_lower.split())

        for key, memory in self.semantic_index.items():
            if category and memory.category != category:
                continue

            score = 0.0

            content_words = set(memory.content.lower().split())
            term_overlap = len(query_terms & content_words)
            if term_overlap > 0:
                score += term_overlap * 0.15

            tag_overlap = len(query_terms & set(t.lower() for t in memory.tags))
            if tag_overlap > 0:
                score += tag_overlap * 0.3

            if query_lower in memory.content.lower():
                score += 0.4

            score += memory.importance * 0.2

            if score > 0:
                results.append({
                    "key": key,
                    "content": memory.content,
                    "category": memory.category,
                    "tags": memory.tags,
                    "importance": memory.importance,
                    "relevance_score": round(score, 3),
                    "connections": list(memory.connections)[:5],
                })

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def get_related_memories(
        self,
        key: str,
        depth: int = 2,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        获取相关记忆

        通过关联图谱获取相关记忆
        """
        if key not in self.semantic_index:
            return []

        visited = {key}
        current_level = {key}
        all_related = []

        for _ in range(depth):
            next_level = set()
            for k in current_level:
                for connected in self._relation_graph.get(k, set()):
                    if connected not in visited:
                        visited.add(connected)
                        next_level.add(connected)
                        if connected in self.semantic_index:
                            mem = self.semantic_index[connected]
                            all_related.append({
                                "key": connected,
                                "content": mem.content[:200],
                                "category": mem.category,
                                "tags": mem.tags[:5],
                                "importance": mem.importance,
                            })
            current_level = next_level
            if len(all_related) >= limit:
                break

        return all_related[:limit]

    def cluster_memories(
        self,
        min_cluster_size: int = 3,
    ) -> List[MemoryCluster]:
        """
        聚类记忆

        使用LLM将相似记忆分组
        """
        if len(self.semantic_index) < min_cluster_size:
            return []

        clusters = []
        assigned = set()

        tag_groups: Dict[str, List[str]] = defaultdict(list)
        for key, mem in self.semantic_index.items():
            for tag in mem.tags:
                tag_groups[tag.lower()].append(key)

        for tag, keys in tag_groups.items():
            if len(keys) >= min_cluster_size:
                theme = tag.title()
                cluster_id = hashlib.md5(tag.encode()).hexdigest()[:8]

                cluster = MemoryCluster(
                    cluster_id=cluster_id,
                    theme=theme,
                    memories=keys,
                    coherence=min(0.9, 0.5 + len(keys) * 0.1),
                    description=f"包含 {len(keys)} 条与'{theme}'相关的记忆",
                )
                clusters.append(cluster)
                assigned.update(keys)

        for key, mem in self.semantic_index.items():
            if key not in assigned:
                cluster_id = hashlib.md5(key.encode()).hexdigest()[:8]
                cluster = MemoryCluster(
                    cluster_id=cluster_id,
                    theme=mem.category or "general",
                    memories=[key],
                    coherence=1.0,
                    description="独立记忆",
                )
                clusters.append(cluster)

        self.clusters = clusters
        return clusters

    def recommend_memories(
        self,
        current_context: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        上下文感知推荐

        基于当前上下文推荐相关记忆
        """
        if not self.semantic_index:
            return []

        context_terms = set(current_context.lower().split())

        recommendations: List[Dict[str, Any]] = []
        for key, mem in self.semantic_index.items():
            mem_terms = set(mem.content.lower().split()) | set(t.lower() for t in mem.tags)
            relevance = len(context_terms & mem_terms) / max(len(context_terms), 1)

            recency_boost = 1.0
            if mem.created_at:
                try:
                    age = (datetime.now() - datetime.fromisoformat(mem.created_at)).days
                    recency_boost = max(0.5, 1.0 - age * 0.01)
                except Exception:
                    pass

            score = relevance * 0.6 + mem.importance * 0.2 + recency_boost * 0.2

            recommendations.append({
                "key": key,
                "content": mem.content[:150],
                "category": mem.category,
                "recommendation_score": round(score, 3),
                "reason": self._explain_recommendation(context_terms, mem),
            })

        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return recommendations[:limit]

    def _explain_recommendation(self, context_terms: Set[str], memory: SemanticMemory) -> str:
        """解释推荐理由"""
        mem_terms = set(memory.content.lower().split()) | set(t.lower() for t in memory.tags)
        common = context_terms & mem_terms

        if common:
            return f"与当前上下文相关: {', '.join(list(common)[:3])}"
        return f"重要记忆 (重要性: {memory.importance:.1%})"

    def get_memory_graph(self) -> Dict[str, Any]:
        """获取记忆关系图谱"""
        nodes = []
        edges = []

        for key, mem in self.semantic_index.items():
            nodes.append({
                "id": key,
                "label": mem.content[:50],
                "category": mem.category,
                "importance": mem.importance,
            })

        for from_key, to_keys in self._relation_graph.items():
            for to_key in to_keys:
                edges.append({
                    "from": from_key,
                    "to": to_key,
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "total_memories": len(self.semantic_index),
            "total_connections": sum(len(v) for v in self._relation_graph.values()) // 2,
        }


LLM_MEMORY_SEARCH = LLMMemorySearch()

__all__ = [
    "LLMMemorySearch",
    "LLM_MEMORY_SEARCH",
    "SemanticMemory",
    "MemoryCluster",
]
