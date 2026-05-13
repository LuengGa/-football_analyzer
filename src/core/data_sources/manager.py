
"""
数据源管理器 - AI原生增强版 (L5级)
====================================

AI质量评估、智能源选择、自动性能跟踪
完全AI原生数据源管理
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Optional, List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AIDataSourceQuality:
    """AI数据源质量评估 (L5)"""
    source_name: str
    quality_score: float
    reliability: float
    freshness: float
    completeness: float
    recommendations: List[str]
    is_reliable: bool
    last_evaluated: str


@dataclass
class AISourceSelection:
    """AI智能源选择 (L5)"""
    best_source: str
    all_scores: Dict[str, float]
    selection_reasoning: str
    fallback_sources: List[str]


class DataCache:
    """本地缓存 - 减少API调用"""

    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            project_root = Path(__file__).parent.parent.parent.parent
            cache_dir = str(project_root / "data" / "cache")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: dict[str, tuple[Any, float]] = {}
        self.lock = Lock()
        self.default_ttl = 3600

    def _get_cache_path(self, key: str) -> Path:
        safe_key = key.replace("/", "_").replace(":", "_")
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str, max_age: Optional[int] = None) -> Optional[Any]:
        ttl = max_age or self.default_ttl

        with self.lock:
            if key in self.memory_cache:
                data, timestamp = self.memory_cache[key]
                if time.time() - timestamp < ttl:
                    return data

            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                try:
                    with open(cache_path, "r", encoding="utf-8") as f:
                        cache_data = json.load(f)

                    if time.time() - cache_data["timestamp"] < ttl:
                        self.memory_cache[key] = (
                            cache_data["data"],
                            time.time(),
                        )
                        return cache_data["data"]
                except Exception:
                    pass
        return None

    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        ttl_seconds = ttl or self.default_ttl
        timestamp = time.time()

        with self.lock:
            self.memory_cache[key] = (data, timestamp)

            cache_path = self._get_cache_path(key)
            try:
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "data": data,
                        "timestamp": timestamp,
                        "ttl": ttl_seconds,
                    }, f, ensure_ascii=False)
            except Exception:
                pass


class DataSourceManager:
    """完全AI原生的智能数据源管理器 (L5级)"""

    def __init__(self, config=None, cache_dir: Optional[str] = None):
        self.config = config
        self.cache = DataCache(cache_dir)
        self.source_performance: Dict[str, Dict[str, Any]] = {}
        self._load_performance()

    def _load_performance(self) -> None:
        """加载性能历史"""
        try:
            storage_path = Path(__file__).parent.parent.parent.parent / "data" / "source_performance.json"
            if storage_path.exists():
                with open(storage_path, "r", encoding="utf-8") as f:
                    self.source_performance = json.load(f)
        except Exception:
            pass

    def _save_performance(self) -> None:
        """保存性能历史"""
        try:
            storage_path = Path(__file__).parent.parent.parent.parent / "data" / "source_performance.json"
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(storage_path, "w", encoding="utf-8") as f:
                json.dump(self.source_performance, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def ai_evaluate_data_source(
        self,
        source_name: str,
        sample_data: Any,
        context: Optional[Dict] = None
    ) -> AIDataSourceQuality:
        """AI评估数据源质量 (L5完全AI原生)"""
        completeness = self._assess_completeness(sample_data)
        freshness = self._assess_freshness(context)
        reliability = self._get_reliability_score(source_name)

        quality_score = (completeness + freshness + reliability) / 3
        is_reliable = quality_score >= 0.6

        recommendations = self._generate_quality_recommendations(
            quality_score, completeness, freshness
        )

        quality = AIDataSourceQuality(
            source_name=source_name,
            quality_score=quality_score,
            reliability=reliability,
            freshness=freshness,
            completeness=completeness,
            recommendations=recommendations,
            is_reliable=is_reliable,
            last_evaluated=datetime.now().isoformat()
        )

        if source_name not in self.source_performance:
            self.source_performance[source_name] = {
                "success_count": 0,
                "failure_count": 0,
                "avg_quality": quality_score,
                "total_latency": 0,
            }

        return quality

    def _assess_completeness(self, data: Any) -> float:
        """评估数据完整性"""
        if data is None:
            return 0.0
        if isinstance(data, dict):
            filled = sum(1 for v in data.values() if v not in [None, "", [], {}])
            return filled / len(data) if data else 0.0
        if isinstance(data, list):
            return 0.8 if len(data) > 0 else 0.0
        return 1.0 if data else 0.0

    def _assess_freshness(self, context: Optional[Dict]) -> float:
        """评估数据新鲜度"""
        if not context:
            return 0.7
        if "timestamp" in context:
            try:
                data_time = datetime.fromisoformat(context["timestamp"])
                age_hours = (datetime.now() - data_time).total_seconds() / 3600
                return max(0.0, 1.0 - age_hours / 24)
            except Exception:
                pass
        return 0.7

    def _get_reliability_score(self, source_name: str) -> float:
        """获取源可靠性评分"""
        if source_name not in self.source_performance:
            return 0.7
        perf = self.source_performance[source_name]
        total = perf["success_count"] + perf["failure_count"]
        if total == 0:
            return 0.7
        return float(perf["success_count"] / total)

    def _generate_quality_recommendations(
        self,
        score: float,
        completeness: float,
        freshness: float
    ) -> List[str]:
        """生成质量改进建议 (L5)"""
        recs = []
        if score < 0.5:
            recs.append("考虑替换该数据源")
        if completeness < 0.7:
            recs.append("需要补充缺失字段")
        if freshness < 0.5:
            recs.append("数据已过时，需要更新")
        if not recs:
            recs.append("数据质量良好")
        return recs

    def ai_select_best_source(
        self,
        available_sources: List[str],
        priority: str = "quality"
    ) -> AISourceSelection:
        """AI智能选择最佳数据源 (L5完全AI原生)"""
        if not available_sources:
            return AISourceSelection(
                best_source="",
                all_scores={},
                selection_reasoning="无可用数据源",
                fallback_sources=[]
            )

        scores = {}
        for source in available_sources:
            if source in self.source_performance:
                perf = self.source_performance[source]
                if priority == "quality":
                    scores[source] = perf.get("avg_quality", 0.5)
                elif priority == "reliability":
                    total = perf["success_count"] + perf["failure_count"]
                    scores[source] = perf["success_count"] / total if total > 0 else 0.5
                else:
                    scores[source] = perf.get("avg_quality", 0.5)
            else:
                scores[source] = 0.5

        best_source = max(scores.items(), key=lambda x: x[1])[0]
        fallback_sources = [s for s in sorted(scores.keys(), key=lambda k: scores[k], reverse=True) if s != best_source][:2]

        reasoning = self._generate_selection_reasoning(best_source, scores, priority)

        return AISourceSelection(
            best_source=best_source,
            all_scores=scores,
            selection_reasoning=reasoning,
            fallback_sources=fallback_sources
        )

    def _generate_selection_reasoning(
        self,
        best_source: str,
        scores: Dict[str, float],
        priority: str
    ) -> str:
        """生成选择推理 (L5)"""
        best_score = scores[best_source]
        priority_desc = "质量" if priority == "quality" else "可靠性"
        return f"基于{priority_desc}选择，{best_source}评分{best_score:.1%}最高"

    def record_source_call(
        self,
        source_name: str,
        success: bool,
        latency: float,
        quality_score: Optional[float] = None
    ) -> None:
        """记录源调用性能"""
        if source_name not in self.source_performance:
            self.source_performance[source_name] = {
                "success_count": 0,
                "failure_count": 0,
                "avg_quality": 0.7,
                "total_latency": 0.0,
            }

        perf = self.source_performance[source_name]
        if success:
            perf["success_count"] += 1
        else:
            perf["failure_count"] += 1
        perf["total_latency"] += latency

        if quality_score is not None:
            total = perf["success_count"] + perf["failure_count"]
            perf["avg_quality"] = (perf["avg_quality"] * (total - 1) + quality_score) / total

        self._save_performance()

    def get_cached_data(self, key: str, max_age: Optional[int] = None) -> Optional[Any]:
        """获取缓存数据"""
        return self.cache.get(key, max_age)

    def set_cached_data(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """设置缓存数据"""
        self.cache.set(key, data, ttl)


DATA_SOURCE_MANAGER = DataSourceManager()

