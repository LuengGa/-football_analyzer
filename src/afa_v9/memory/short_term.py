from typing import Any
from datetime import datetime, timedelta
from collections import deque
from pydantic import BaseModel, Field
import json
import os


class ShortTermMemoryItem(BaseModel):
    content: Any
    timestamp: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime = Field(default_factory=datetime.now)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)

    def access(self) -> None:
        self.access_count += 1
        self.last_accessed = datetime.now()


class ShortTermMemory:
    def __init__(self, max_size: int = 100, ttl_hours: int = 24):
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self._memory: dict[str, ShortTermMemoryItem] = {}
        self._access_order: deque[str] = deque()

    def store(self, key: str, content: Any, importance: float = 0.5) -> None:
        item = ShortTermMemoryItem(content=content, importance=importance)
        self._memory[key] = item
        if key not in self._access_order:
            self._access_order.append(key)
        self._cleanup()

    def retrieve(self, key: str) -> Any | None:
        if key in self._memory:
            self._memory[key].access()
            return self._memory[key].content
        return None

    def search(self, query: str) -> list[tuple[str, Any]]:
        results = []
        query_lower = query.lower()
        for key, item in self._memory.items():
            content_str = str(item.content).lower()
            if query_lower in content_str:
                results.append((key, item.content))
        return results

    def _cleanup(self) -> None:
        now = datetime.now()
        expired_keys = [
            k for k, v in self._memory.items()
            if now - v.timestamp > self.ttl
        ]
        for key in expired_keys:
            del self._memory[key]
            if key in self._access_order:
                self._access_order.remove(key)

        while len(self._memory) > self.max_size:
            if self._access_order:
                oldest_key = self._access_order.popleft()
                if oldest_key in self._memory:
                    del self._memory[oldest_key]

    def get_context_window(self, max_items: int = 10) -> list[dict]:
        sorted_items = sorted(
            self._memory.values(),
            key=lambda x: (x.importance, x.last_accessed),
            reverse=True
        )
        return [
            {
                "content": item.content,
                "timestamp": item.timestamp.isoformat(),
                "importance": item.importance,
            }
            for item in sorted_items[:max_items]
        ]

    def to_dict(self) -> dict:
        return {
            "item_count": len(self._memory),
            "items": {
                k: {
                    "content": v.content,
                    "timestamp": v.timestamp.isoformat(),
                    "importance": v.importance,
                }
                for k, v in list(self._memory.items())[:20]
            }
        }


SHORT_TERM_MEMORY = ShortTermMemory()
