from typing import Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import json
from pathlib import Path


class Episode(BaseModel):
    id: str
    title: str
    content: dict[str, Any]
    episode_type: Literal["analysis", "decision", "outcome", "learning", "error"]
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: datetime | None = None
    outcome: Literal["success", "failure", "neutral", "pending"] = "pending"
    lessons: list[str] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)

    def complete(self, outcome: Literal["success", "failure", "neutral"], lessons: list[str] | None = None) -> None:
        self.end_time = datetime.now()
        self.outcome = outcome
        if lessons:
            self.lessons = lessons


class EpisodicStore:
    def __init__(self, storage_path: str | None = None):
        if storage_path is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            memory_dir = project_root / "memory"
            memory_dir.mkdir(exist_ok=True)
            storage_path = str(memory_dir / "episodes")
        self.storage_path = Path(storage_path)
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            self.storage_path = Path("/tmp/afa_v9_episodes")
            self.storage_path.mkdir(parents=True, exist_ok=True)
        self._episodes: list[Episode] = []
        self._current_episode: Episode | None = None
        self._load_recent()

    def _load_recent(self) -> None:
        index_file = self.storage_path / "episode_index.json"
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for ep_data in data.get("recent_episodes", [])[-50:]:
                        ep_data["start_time"] = datetime.fromisoformat(ep_data["start_time"])
                        if ep_data.get("end_time"):
                            ep_data["end_time"] = datetime.fromisoformat(ep_data["end_time"])
                        self._episodes.append(Episode(**ep_data))
            except Exception:
                self._episodes = []

    def _save_index(self) -> None:
        index_file = self.storage_path / "episode_index.json"
        recent = self._episodes[-100:] if len(self._episodes) > 100 else self._episodes
        data = {
            "recent_episodes": [
                {
                    "id": ep.id,
                    "title": ep.title,
                    "episode_type": ep.episode_type,
                    "start_time": ep.start_time.isoformat(),
                    "end_time": ep.end_time.isoformat() if ep.end_time else None,
                    "outcome": ep.outcome,
                    "lessons": ep.lessons,
                    "metrics": ep.metrics,
                }
                for ep in recent
            ]
        }
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def start_episode(
        self,
        title: str,
        episode_type: Literal["analysis", "decision", "outcome", "learning", "error"],
        initial_content: dict[str, Any] | None = None,
    ) -> str:
        episode_id = f"ep_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._current_episode = Episode(
            id=episode_id,
            title=title,
            content=initial_content or {},
            episode_type=episode_type,
        )
        return episode_id

    def add_to_episode(self, key: str, value: Any) -> None:
        if self._current_episode:
            self._current_episode.content[key] = value

    def complete_episode(
        self,
        outcome: Literal["success", "failure", "neutral"],
        lessons: list[str] | None = None,
    ) -> None:
        if self._current_episode:
            self._current_episode.complete(outcome, lessons)
            self._episodes.append(self._current_episode)
            self._save_episode(self._current_episode)
            self._current_episode = None

    def _save_episode(self, episode: Episode) -> None:
        episode_file = self.storage_path / f"{episode.id}.json"
        data = episode.model_dump(mode="json")
        with open(episode_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_recent_episodes(self, count: int = 10) -> list[Episode]:
        return self._episodes[-count:] if self._episodes else []

    def get_successful_episodes(self) -> list[Episode]:
        return [ep for ep in self._episodes if ep.outcome == "success"]

    def get_lessons(self) -> list[str]:
        lessons = []
        for ep in self._episodes:
            lessons.extend(ep.lessons)
        return list(set(lessons))

    def get_episode_metrics(self) -> dict:
        if not self._episodes:
            return {"total": 0, "success_rate": 0.0}

        total = len(self._episodes)
        success = len([ep for ep in self._episodes if ep.outcome == "success"])
        return {
            "total": total,
            "success": success,
            "failure": len([ep for ep in self._episodes if ep.outcome == "failure"]),
            "neutral": len([ep for ep in self._episodes if ep.outcome == "neutral"]),
            "success_rate": success / total if total > 0 else 0.0,
        }


EPISODIC_STORE = EpisodicStore()
