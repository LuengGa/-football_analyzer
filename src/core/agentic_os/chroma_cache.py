"""
ChromaDB 缓存层 - TTL 和 LRU 淘汰机制

职责：
- 为 ChromaDB 向量存储添加 TTL (Time-To-Live) 过期机制
- 实现 LRU (Least Recently Used) 淘汰策略控制内存使用
- 自动清理过期和最久未使用的向量数据
- 提供高性能的语义搜索缓存接口
"""
import os
import time
import json
import heapq
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass(order=True)
class LRUCacheEntry:
    """LRU 缓存条目（用于优先级队列）"""
    last_accessed: float  # 最后访问时间戳（用于排序）
    key: str = field(compare=False)  # 缓存键
    value: Any = field(compare=False)  # 缓存值
    embedding: Optional[List[float]] = field(compare=False, default=None)  # 向量嵌入
    metadata: Dict[str, Any] = field(compare=False, default_factory=dict)  # 元数据
    ttl: Optional[float] = None  # 过期时间戳（None表示永不过期）
    access_count: int = field(compare=False, default=0)  # 访问次数统计
    version: int = field(compare=False, default=0)  # 版本号，用于区分更新的条目


class ChromaCacheManager:
    """
    ChromaDB 缓存管理器
    
    提供双层缓存机制：
    1. TTL 过期：基于时间的自动清理
    2. LRU 淘汰：基于访问频率的容量控制
    """
    
    def __init__(
        self,
        max_entries: int = 10000,
        default_ttl_seconds: float = 86400.0,  # 默认 24 小时
        cleanup_interval_seconds: float = 3600.0,  # 清理间隔 1 小时
        cache_dir: Optional[str] = None
    ):
        """
        初始化缓存管理器
        
        Args:
            max_entries: 最大缓存条目数（LRU 容量限制）
            default_ttl_seconds: 默认 TTL 时间（秒）
            cleanup_interval_seconds: 自动清理间隔（秒）
            cache_dir: 缓存持久化目录（可选）
        """
        self.max_entries = max_entries
        self.default_ttl = default_ttl_seconds
        self.cleanup_interval = cleanup_interval_seconds
        
        # LRU 优先级队列（最小堆，按最后访问时间排序）
        self._lru_heap: List[LRUCacheEntry] = []
        self._heap_lock = False  # 简化锁标志
        
        # 快速查找字典（key -> entry）
        self._cache_dict: Dict[str, LRUCacheEntry] = {}
        
        # 统计信息
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
            "total_inserts": 0,
        }
        
        # 上次清理时间
        self._last_cleanup_time = time.time()
        
        # 持久化路径
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()
        
        logger.info(
            f"✓ ChromaCacheManager initialized | "
            f"max_entries={max_entries}, default_ttl={default_ttl_seconds}s"
        )
    
    def put(
        self,
        key: str,
        value: Any,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[float] = None
    ):
        """
        插入或更新缓存条目
        
        Args:
            key: 缓存键（唯一标识符）
            value: 缓存值
            embedding: 向量嵌入（可选）
            metadata: 元数据（可选）
            ttl: 自定义 TTL（秒），None 使用默认值
        """
        now = time.time()
        
        # 计算过期时间
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        expiration_time = now + ttl_seconds if ttl_seconds > 0 else None
        
        # 如果 key 已存在，先移除旧条目
        if key in self._cache_dict:
            self._remove_entry(key)
        
        # 检查是否需要淘汰（LRU）
        if len(self._cache_dict) >= self.max_entries:
            self._evict_lru()
        
        # 创建新条目
        entry = LRUCacheEntry(
            last_accessed=now,
            key=key,
            value=value,
            embedding=embedding,
            metadata=metadata or {},
            ttl=expiration_time,
            access_count=0
        )
        
        # 添加到数据结构
        heapq.heappush(self._lru_heap, entry)
        self._cache_dict[key] = entry
        
        # 更新统计
        self._stats["total_inserts"] += 1
        
        # 定期清理
        if now - self._last_cleanup_time > self.cleanup_interval:
            self.cleanup()
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回 None
        """
        now = time.time()
        
        # 检查是否存在
        if key not in self._cache_dict:
            self._stats["misses"] += 1
            return None
        
        entry = self._cache_dict[key]
        
        # 检查是否过期（TTL）
        if entry.ttl is not None and now > entry.ttl:
            self._remove_entry(key)
            self._stats["expirations"] += 1
            self._stats["misses"] += 1
            return None
        
        # 更新访问信息（LRU）- 创建新对象以避免引用问题
        new_entry = LRUCacheEntry(
            last_accessed=now,
            key=entry.key,
            value=entry.value,
            embedding=entry.embedding,
            metadata=entry.metadata,
            ttl=entry.ttl,
            access_count=entry.access_count + 1
        )
        
        # 更新字典中的引用
        self._cache_dict[key] = new_entry
        
        # 将新条目推入堆中
        heapq.heappush(self._lru_heap, new_entry)
        
        self._stats["hits"] += 1
        return entry.value
    
    def get_with_embedding(self, key: str) -> Optional[Tuple[Any, Optional[List[float]]]]:
        """
        获取缓存值和向量嵌入
        
        Args:
            key: 缓存键
            
        Returns:
            (value, embedding) 元组，如果不存在则返回 None
        """
        if key not in self._cache_dict:
            return None
        
        entry = self._cache_dict[key]
        now = time.time()
        
        # 检查 TTL
        if entry.ttl is not None and now > entry.ttl:
            self._remove_entry(key)
            return None
        
        # 更新访问信息 - 创建新对象
        new_entry = LRUCacheEntry(
            last_accessed=now,
            key=entry.key,
            value=entry.value,
            embedding=entry.embedding,
            metadata=entry.metadata,
            ttl=entry.ttl,
            access_count=entry.access_count + 1
        )
        
        self._cache_dict[key] = new_entry
        heapq.heappush(self._lru_heap, new_entry)
        
        self._stats["hits"] += 1
        return (entry.value, entry.embedding)
    
    def delete(self, key: str) -> bool:
        """
        删除缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        if key in self._cache_dict:
            self._remove_entry(key)
            return True
        return False
    
    def clear(self):
        """清空所有缓存"""
        self._lru_heap.clear()
        self._cache_dict.clear()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
            "total_inserts": 0,
        }
        logger.info("✓ Cache cleared")
    
    def cleanup(self) -> Dict[str, int]:
        """
        执行清理操作（TTL 过期 + LRU 淘汰）
        
        Returns:
            清理统计信息
        """
        now = time.time()
        expired_keys = []
        
        # Phase 1: 清理过期的 TTL 条目
        for key, entry in list(self._cache_dict.items()):
            if entry.ttl is not None and now > entry.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_entry(key)
            self._stats["expirations"] += 1
        
        # Phase 2: LRU 淘汰（如果仍然超出容量）
        evicted_count = 0
        while len(self._cache_dict) > self.max_entries:
            self._evict_lru()
            evicted_count += 1
        
        self._last_cleanup_time = now
        
        stats = {
            "expired": len(expired_keys),
            "evicted": evicted_count,
            "remaining": len(self._cache_dict)
        }
        
        if expired_keys or evicted_count:
            logger.info(f"✓ Cache cleanup: {stats}")
        
        return stats
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (
            self._stats["hits"] / total_requests
            if total_requests > 0 else 0.0
        )
        
        return {
            **self._stats,
            "current_size": len(self._cache_dict),
            "max_size": self.max_entries,
            "hit_rate": hit_rate,
            "utilization": len(self._cache_dict) / self.max_entries if self.max_entries > 0 else 0,
        }
    
    def _remove_entry(self, key: str):
        """从数据结构中移除条目（懒惰删除）"""
        if key in self._cache_dict:
            del self._cache_dict[key]
            # 注意：堆中的旧条目会在后续操作中自然被跳过
    
    def _evict_lru(self):
        """LRU 淘汰：移除最久未使用的条目
        
        使用懒惰删除策略：跳过堆中已过时的条目副本，
        直到找到一个与字典中当前条目匹配的条目。
        """
        while self._lru_heap:
            entry = heapq.heappop(self._lru_heap)
            
            # 检查这个条目是否仍然在字典中
            if entry.key not in self._cache_dict:
                continue  # 已被删除，跳过
            
            current_entry = self._cache_dict[entry.key]
            
            # 验证 last_accessed 是否匹配（允许小的浮点误差）
            # 如果不匹配，说明这个条目已被更新（有新的副本在堆中），跳过
            if abs(current_entry.last_accessed - entry.last_accessed) >= 0.001:
                continue  # 这是旧副本，跳过
            
            # 找到有效的最久未使用条目，删除它
            del self._cache_dict[entry.key]
            self._stats["evictions"] += 1
            logger.debug(f"LRU evicted: {entry.key}")
            return
        
        logger.warning("Failed to evict LRU entry")
    
    def _load_from_disk(self):
        """从磁盘加载缓存（如果存在）"""
        if not self.cache_dir:
            return
        
        cache_file = self.cache_dir / "chroma_cache.json"
        if not cache_file.exists():
            return
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data.get("entries", []):
                key = item["key"]
                value = item["value"]
                embedding = item.get("embedding")
                metadata = item.get("metadata", {})
                ttl = item.get("ttl")
                last_accessed = item.get("last_accessed", time.time())
                
                # 检查是否过期
                if ttl is not None and time.time() > ttl:
                    continue
                
                entry = LRUCacheEntry(
                    last_accessed=last_accessed,
                    key=key,
                    value=value,
                    embedding=embedding,
                    metadata=metadata,
                    ttl=ttl,
                    access_count=item.get("access_count", 0)
                )
                
                heapq.heappush(self._lru_heap, entry)
                self._cache_dict[key] = entry
            
            logger.info(f"✓ Loaded {len(self._cache_dict)} entries from disk")
        except Exception as e:
            logger.warning(f"Failed to load cache from disk: {e}")
    
    def save_to_disk(self):
        """保存缓存到磁盘"""
        if not self.cache_dir:
            return
        
        cache_file = self.cache_dir / "chroma_cache.json"
        
        try:
            entries = []
            for entry in self._cache_dict.values():
                entries.append({
                    "key": entry.key,
                    "value": entry.value,
                    "embedding": entry.embedding,
                    "metadata": entry.metadata,
                    "ttl": entry.ttl,
                    "last_accessed": entry.last_accessed,
                    "access_count": entry.access_count,
                })
            
            data = {
                "timestamp": time.time(),
                "stats": self._stats,
                "entries": entries
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✓ Saved {len(entries)} entries to disk")
        except Exception as e:
            logger.warning(f"Failed to save cache to disk: {e}")


class ChromaVectorStoreWithCache:
    """
    带缓存的 ChromaDB 向量存储
    
    在标准 ChromaDB 之上添加智能缓存层，减少重复的向量计算和数据库查询
    """
    
    def __init__(
        self,
        collection_name: str = "semantic_memory",
        chroma_path: Optional[str] = None,
        cache_max_entries: int = 5000,
        cache_ttl_seconds: float = 43200.0,  # 12 小时
        enable_cache: bool = True
    ):
        """
        初始化带缓存的向量存储
        
        Args:
            collection_name: ChromaDB 集合名称
            chroma_path: ChromaDB 持久化路径
            cache_max_entries: 缓存最大条目数
            cache_ttl_seconds: 缓存 TTL（秒）
            enable_cache: 是否启用缓存
        """
        self.collection_name = collection_name
        self.enable_cache = enable_cache
        
        self._client: Optional[Any] = None
        self._collection: Optional[Any] = None
        self._init_chromadb(chroma_path)
        
        # 初始化缓存管理器
        self.cache = ChromaCacheManager(
            max_entries=cache_max_entries,
            default_ttl_seconds=cache_ttl_seconds
        ) if enable_cache else None
    
    def _init_chromadb(self, chroma_path: Optional[str]):
        """初始化 ChromaDB 客户端"""
        try:
            import chromadb
            
            path = chroma_path or "./chroma_db"
            os.makedirs(path, exist_ok=True)
            
            self._client = chromadb.PersistentClient(path=path)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Semantic memory with caching"}
            )
            
            logger.info(f"✓ ChromaDB collection '{self.collection_name}' initialized")
        except ImportError:
            logger.error("chromadb not installed. Please run: pip install chromadb")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ttl: Optional[float] = None
    ):
        """
        添加文档到向量存储（并缓存）
        
        Args:
            ids: 文档 ID 列表
            documents: 文档文本列表
            embeddings: 向量嵌入列表（可选，如不提供则自动生成）
            metadatas: 元数据列表（可选）
            ttl: 缓存 TTL（秒）
        """
        # 添加到 ChromaDB
        add_kwargs: Dict[str, Any] = {
            "ids": ids,
            "documents": documents,
        }
        
        if embeddings:
            add_kwargs["embeddings"] = embeddings
        
        if metadatas:
            add_kwargs["metadatas"] = metadatas
        
        self._collection.add(**add_kwargs)  # type: ignore[union-attr]
        
        # 缓存每个条目
        if self.cache:
            for i, doc_id in enumerate(ids):
                embedding = embeddings[i] if embeddings else None
                metadata = metadatas[i] if metadatas else {}
                
                self.cache.put(
                    key=f"doc:{doc_id}",
                    value=documents[i],
                    embedding=embedding,
                    metadata=metadata,
                    ttl=ttl
                )
        
        logger.debug(f"Added {len(ids)} documents to vector store")
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        查询相似文档
        
        Args:
            query_text: 查询文本
            n_results: 返回结果数量
            where: 过滤条件（可选）
            use_cache: 是否使用缓存
            
        Returns:
            查询结果字典
        """
        # 尝试从缓存获取（基于查询文本的哈希）
        cache_key = f"query:{hash(query_text)}:{n_results}"
        
        if use_cache and self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit for query: {query_text[:50]}...")
                return cached_result  # type: ignore[return-value,no-any-return]
        
        # 执行 ChromaDB 查询
        query_kwargs = {
            "query_texts": [query_text],
            "n_results": n_results,
        }
        
        if where:
            query_kwargs["where"] = where
        
        result = self._collection.query(**query_kwargs)  # type: ignore[union-attr]
        
        # 格式化结果
        formatted_result: Dict[str, Any] = {
            "ids": result["ids"][0] if result["ids"] else [],
            "documents": result["documents"][0] if result["documents"] else [],
            "distances": result["distances"][0] if result["distances"] else [],
            "metadatas": result["metadatas"][0] if result["metadatas"] else [],
        }
        
        # 缓存结果
        if use_cache and self.cache:
            self.cache.put(
                key=cache_key,
                value=formatted_result,
                ttl=300.0  # 查询结果缓存 5 分钟
            )
        
        return formatted_result
    
    def get(self, ids: List[str]) -> Dict[str, Any]:
        """
        根据 ID 获取文档
        
        Args:
            ids: 文档 ID 列表
            
        Returns:
            文档数据字典
        """
        # 尝试从缓存获取
        if self.cache:
            cached_docs = {}
            missing_ids = []
            
            for doc_id in ids:
                cached = self.cache.get(f"doc:{doc_id}")
                if cached:
                    cached_docs[doc_id] = cached
                else:
                    missing_ids.append(doc_id)
            
            if not missing_ids:
                logger.debug(f"All {len(ids)} documents served from cache")
                return {"ids": ids, "documents": [cached_docs[doc_id] for doc_id in ids]}
        
        # 从 ChromaDB 获取缺失的文档
        result = self._collection.get(ids=missing_ids if missing_ids else ids)  # type: ignore[union-attr]
        
        # 缓存新获取的文档
        if self.cache and missing_ids:
            for i, doc_id in enumerate(missing_ids):
                if i < len(result["documents"]):
                    self.cache.put(
                        key=f"doc:{doc_id}",
                        value=result["documents"][i],
                        metadata=result["metadatas"][i] if result["metadatas"] else {}
                    )
        
        return result  # type: ignore[return-value,no-any-return]
    
    def delete(self, ids: List[str]):
        """删除文档"""
        self._collection.delete(ids=ids)  # type: ignore[union-attr]
    
    def count(self) -> int:
        """获取文档总数"""
        return self._collection.count()  # type: ignore[union-attr,no-any-return]
    
    def cleanup_cache(self) -> Dict[str, int]:
        """清理缓存（TTL 过期 + LRU 淘汰）"""
        if self.cache:
            return self.cache.cleanup()
        return {"expired": 0, "evicted": 0, "remaining": 0}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if self.cache:
            return self.cache.get_stats()
        return {"enabled": False}
    
    def close(self):
        """关闭连接并保存缓存"""
        if self.cache:
            self.cache.save_to_disk()
        logger.info("Vector store closed")


# 便捷函数
def create_cached_vector_store(
    collection_name: str = "default",
    chroma_path: Optional[str] = None,
    **kwargs
) -> ChromaVectorStoreWithCache:
    """
    创建带缓存的向量存储实例
    
    Args:
        collection_name: 集合名称
        chroma_path: ChromaDB 路径
        **kwargs: 其他参数传递给 ChromaVectorStoreWithCache
        
    Returns:
        ChromaVectorStoreWithCache 实例
    """
    return ChromaVectorStoreWithCache(
        collection_name=collection_name,
        chroma_path=chroma_path,
        **kwargs
    )


if __name__ == "__main__":
    # 测试示例
    print("=" * 60)
    print("ChromaDB TTL & LRU 缓存机制测试")
    print("=" * 60)
    
    # 测试缓存管理器
    cache = ChromaCacheManager(max_entries=5, default_ttl_seconds=2.0)
    
    print("\n--- 测试 1: 基本缓存操作 ---")
    cache.put("key1", "value1", metadata={"type": "test"})
    cache.put("key2", "value2")
    cache.put("key3", "value3")
    
    val = cache.get("key1")
    print(f"✓ Get key1: {val}")
    
    print("\n--- 测试 2: TTL 过期 ---")
    import time
    time.sleep(2.5)
    val = cache.get("key1")
    print(f"✓ After TTL expiry: {val} (应为 None)")
    
    print("\n--- 测试 3: LRU 淘汰 ---")
    cache2 = ChromaCacheManager(max_entries=3, default_ttl_seconds=3600.0)
    cache2.put("a", 1)
    cache2.put("b", 2)
    cache2.put("c", 3)
    cache2.get("a")  # 访问 a，使其变为最近使用
    cache2.put("d", 4)  # 应该淘汰 b（最久未使用）
    
    print(f"✓ After LRU eviction:")
    print(f"  - a exists: {cache2.get('a') is not None}")
    print(f"  - b exists: {cache2.get('b') is not None} (应为 False)")
    print(f"  - c exists: {cache2.get('c') is not None}")
    print(f"  - d exists: {cache2.get('d') is not None}")
    
    print("\n--- 测试 4: 统计信息 ---")
    stats = cache2.get_stats()
    print(f"✓ Stats: {json.dumps(stats, indent=2)}")
    
    print("\n✅ 测试完成!")
