from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field
import json
import os
from pathlib import Path


class LongTermMemoryItem(BaseModel):
    key: str
    content: Any
    category: str = "general"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    def access(self) -> None:
        self.access_count += 1
        self.last_accessed = datetime.now()

    def update(self, content: Any) -> None:
        self.content = content
        self.updated_at = datetime.now()


class LongTermMemory:
    def __init__(self, storage_path: str | None = None):
        self._use_tmp = False
        if storage_path is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            memory_dir = project_root / "memory"
            storage_path = str(memory_dir / "long_term_memory.json")
        self.storage_path = Path(storage_path)
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "a"):
                pass
        except (PermissionError, OSError):
            self.storage_path = Path("/tmp/afa_v9_long_term_memory.json")
            self._use_tmp = True
        self._memory: dict[str, LongTermMemoryItem] = {}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key, item_data in data.items():
                        item_data["created_at"] = datetime.fromisoformat(item_data["created_at"])
                        item_data["updated_at"] = datetime.fromisoformat(item_data["updated_at"])
                        if item_data.get("last_accessed"):
                            item_data["last_accessed"] = datetime.fromisoformat(item_data["last_accessed"])
                        self._memory[key] = LongTermMemoryItem(**item_data)
            except Exception:
                self._memory = {}

    def _save(self) -> None:
        if self._use_tmp:
            return
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        key: {
                            "key": item.key,
                            "content": item.content,
                            "category": item.category,
                            "created_at": item.created_at.isoformat(),
                            "updated_at": item.updated_at.isoformat(),
                            "access_count": item.access_count,
                            "last_accessed": item.last_accessed.isoformat() if item.last_accessed else None,
                            "tags": item.tags,
                            "metadata": item.metadata,
                        }
                        for key, item in self._memory.items()
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except (PermissionError, OSError):
            self._use_tmp = True

    def store(
        self,
        key: str,
        content: Any,
        category: str = "general",
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> None:
        item = LongTermMemoryItem(
            key=key,
            content=content,
            category=category,
            tags=tags or [],
            metadata=metadata or {},
        )
        self._memory[key] = item
        self._save()

    def retrieve(self, key: str) -> Any | None:
        if key in self._memory:
            self._memory[key].access()
            self._save()
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

    def get_by_category(self, category: str) -> list[LongTermMemoryItem]:
        return [item for item in self._memory.values() if item.category == category]

    def get_by_tag(self, tag: str) -> list[LongTermMemoryItem]:
        return [item for item in self._memory.values() if tag in item.tags]

    def get_knowledge_summary(self) -> dict:
        categories: dict[str, dict[str, Any]] = {}
        for item in self._memory.values():
            if item.category not in categories:
                categories[item.category] = {"count": 0, "tags": set()}
            categories[item.category]["count"] += 1
            categories[item.category]["tags"].update(item.tags)

        return {
            "total_items": len(self._memory),
            "categories": {
                cat: {"count": data["count"], "tags": list(data["tags"])}
                for cat, data in categories.items()
            }
        }


LONG_TERM_MEMORY = LongTermMemory()
