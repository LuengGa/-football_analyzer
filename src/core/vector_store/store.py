"""
向量存储 - 本地向量数据库
==========================

支持:
- ChromaDB (如果可用)
- 轻量级SQLite向量 (备用)

用于:
- 足球知识向量化
- 语义搜索
- 相似度匹配
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class VectorStore:
    """
    向量存储基类
    """

    def __init__(self, collection_name: str = "afa_knowledge"):
        self.collection_name = collection_name
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

    def add(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        raise NotImplementedError

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def delete(self, id: str) -> None:
        raise NotImplementedError

    def count(self) -> int:
        return len(self.vectors)


class SimpleVectorStore(VectorStore):
    """
    简单向量存储 - 基于余弦相似度的本地实现

    适用于数据量较小的情况（<10000条）
    """

    def __init__(self, collection_name: str = "afa_knowledge"):
        super().__init__(collection_name)
        self.storage_path = self._get_storage_path()
        self._load_from_disk()

    def _get_storage_path(self) -> Path:
        project_root = Path(__file__).parent.parent.parent.parent
        path = project_root / "data" / "vectors" / self.collection_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _load_from_disk(self) -> None:
        vectors_file = self.storage_path / "vectors.json"
        metadata_file = self.storage_path / "metadata.json"

        if vectors_file.exists():
            try:
                with open(vectors_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.vectors = {k: v for k, v in data.items()}
            except Exception as e:
                logger.warning(f"Failed to load vectors: {e}")

        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")

    def _save_to_disk(self) -> None:
        vectors_file = self.storage_path / "vectors.json"
        metadata_file = self.storage_path / "metadata.json"

        try:
            with open(vectors_file, "w", encoding="utf-8") as f:
                json.dump(self.vectors, f)
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, default=str)
        except Exception as e:
            logger.error(f"Failed to save vectors: {e}")

    def add(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        self.vectors[id] = vector
        self.metadata[id] = metadata
        self._save_to_disk()

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.vectors:
            return []

        query = np.array(query_vector)
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            query_norm = 1.0

        similarities: List[Dict[str, Any]] = []
        for doc_id, vector in self.vectors.items():
            vec = np.array(vector)
            norm = np.linalg.norm(vec)
            if norm == 0:
                continue

            similarity = float(np.dot(query, vec) / (query_norm * norm))
            similarities.append({
                "id": doc_id,
                "score": similarity,
                "metadata": self.metadata.get(doc_id, {}),
            })

        similarities.sort(key=lambda x: x["score"], reverse=True)
        return similarities[:top_k]

    def delete(self, id: str) -> None:
        self.vectors.pop(id, None)
        self.metadata.pop(id, None)
        self._save_to_disk()

    def clear(self) -> None:
        self.vectors.clear()
        self.metadata.clear()
        self._save_to_disk()


class ChromaVectorStore(VectorStore):
    """
    ChromaDB向量存储 - 如果ChromaDB可用则使用
    """

    def __init__(self, collection_name: str = "afa_knowledge"):
        super().__init__(collection_name)
        self._client: Any = None
        self._collection: Any = None
        self._init_chroma()

    def _init_chroma(self) -> None:
        try:
            import chromadb
            from chromadb.config import Settings

            project_root = Path(__file__).parent.parent.parent.parent
            persist_dir = str(project_root / "data" / "chromadb")

            self._client = chromadb.PersistentClient(path=persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "AFA football knowledge base"}
            )
            logger.info(f"ChromaDB initialized: {self.collection_name}")
        except ImportError:
            logger.warning("ChromaDB not available, falling back to SimpleVectorStore")
            raise ImportError("ChromaDB not installed")
        except Exception as e:
            logger.warning(f"ChromaDB init failed: {e}")
            raise ImportError(str(e))

    def add(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        if self._collection is not None:
            self._collection.upsert(
                ids=[id],
                embeddings=[vector],
                metadatas=[metadata],
            )

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if self._collection is None:
            return []
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
        )

        items: List[Dict[str, Any]] = []
        if results and "ids" in results:
            for i, doc_id in enumerate(results["ids"][0]):
                items.append({
                    "id": doc_id,
                    "score": 1 - results["distances"][0][i] if "distances" in results else 0,
                    "metadata": results["metadatas"][0][i] if "metadatas" in results else {},
                })
        return items

    def delete(self, id: str) -> None:
        if self._collection is not None:
            self._collection.delete(ids=[id])

    def count(self) -> int:
        if self._collection is None:
            return 0
        return int(self._collection.count())


class VectorStoreFactory:
    """向量存储工厂"""

    @staticmethod
    def create(collection_name: str = "afa_knowledge") -> VectorStore:
        logger.info(f"Using SimpleVectorStore (ChromaDB disabled for stability)")
        return SimpleVectorStore(collection_name)


def get_default_store() -> VectorStore:
    return VectorStoreFactory.create("afa_knowledge")
