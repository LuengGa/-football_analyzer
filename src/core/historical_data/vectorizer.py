"""
历史数据向量化
================

将历史比赛数据向量化并存储到向量数据库
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..vector_store import get_default_store, embed_text
from .loader import HistoricalDataLoader, MatchRecord

logger = logging.getLogger(__name__)


class HistoricalVectorizer:
    """
    历史数据向量化器

    将历史比赛数据转换为向量并存储

    使用方式:
        vectorizer = HistoricalVectorizer()
        vectorizer.vectorize_all(batch_size=1000)
    """

    def __init__(
        self,
        loader: Optional[HistoricalDataLoader] = None,
        store=None
    ):
        self.loader = loader or HistoricalDataLoader()

        if store is None:
            from ..vector_store import SimpleVectorStore
            self.store = SimpleVectorStore("historical_matches")
        else:
            self.store = store

        self.vectorized_count = 0

    def _match_to_text(self, match: MatchRecord) -> str:
        """将比赛转换为文本用于向量化"""
        parts = [
            f"{match.home_team} vs {match.away_team}",
            f"League: {match.league_name} ({match.season})",
            f"Date: {match.date}",
        ]

        if match.home_odds:
            parts.append(f"Odds - Home: {match.home_odds}, Draw: {match.draw_odds}, Away: {match.away_odds}")

        if match.home_goals is not None:
            parts.append(f"Result: {match.home_goals}-{match.away_goals} ({match.result})")

        if match.home_shots:
            parts.append(f"Shots: {match.home_shots}-{match.away_shots}")

        if match.home_corners:
            parts.append(f"Corners: {match.home_corners}-{match.away_corners}")

        if match.over_line:
            parts.append(f"Over/Under {match.over_line}: O:{match.over_odds} U:{match.under_odds}")

        return " | ".join(parts)

    def vectorize_match(self, match: MatchRecord) -> None:
        """向量化单场比赛"""
        text = self._match_to_text(match)
        vector = embed_text(text)

        metadata = {
            "match_id": match.match_id,
            "league": match.league,
            "league_name": match.league_name,
            "home_team": match.home_team,
            "away_team": match.away_team,
            "date": match.date,
            "year": match.year,
            "result": match.result,
            "home_goals": match.home_goals,
            "away_goals": match.away_goals,
            "home_odds": match.home_odds,
            "draw_odds": match.draw_odds,
            "away_odds": match.away_odds,
        }

        self.store.add(match.match_id, vector, metadata)
        self.vectorized_count += 1

    def vectorize_batch(self, matches: List[MatchRecord]) -> int:
        """批量向量化"""
        count = 0
        for match in matches:
            try:
                self.vectorize_match(match)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to vectorize {match.match_id}: {e}")

        return count

    def vectorize_all(self, batch_size: int = 1000, limit: Optional[int] = None) -> int:
        """
        向量化所有历史数据

        Args:
            batch_size: 每批处理数量
            limit: 最大处理数量（用于测试）
        """
        logger.info("Starting historical data vectorization...")

        matches = self.loader.load_all()

        if limit:
            matches = matches[:limit]

        total = len(matches)
        logger.info(f"Total matches to vectorize: {total}")

        self.vectorized_count = 0

        for i in range(0, total, batch_size):
            batch = matches[i:i + batch_size]
            count = self.vectorize_batch(batch)
            self.vectorized_count += count

            if (i + batch_size) % 10000 == 0 or i + batch_size >= total:
                logger.info(f"Progress: {min(i + batch_size, total)}/{total} ({self.vectorized_count} vectorized)")

        logger.info(f"Vectorization complete! Total: {self.vectorized_count}")
        return self.vectorized_count

    def search_similar_matches(
        self,
        query: str,
        top_k: int = 5,
        league_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相似比赛

        Args:
            query: 搜索查询
            top_k: 返回数量
            league_filter: 联赛过滤
        """
        query_vector = embed_text(query)
        results = self.store.search(query_vector, top_k=top_k * 2 if league_filter else top_k)

        if league_filter:
            results = [
                r for r in results
                if r.get("metadata", {}).get("league") == league_filter
            ][:top_k]

        return results

    def get_vectorization_stats(self) -> Dict[str, Any]:
        """获取向量化统计"""
        return {
            "total_in_database": self.store.count(),
            "vectorized_count": self.vectorized_count,
        }


HISTORICAL_VECTORIZER = HistoricalVectorizer()
