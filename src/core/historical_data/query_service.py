"""
历史数据查询服务
=================

为Agent提供历史数据查询接口
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .loader import HistoricalDataLoader, HISTORICAL_LOADER, MatchRecord
from .vectorizer import HistoricalVectorizer, HISTORICAL_VECTORIZER

logger = logging.getLogger(__name__)


class HistoricalQueryService:
    """
    历史数据查询服务

    为Agent提供便捷的历史数据访问接口

    使用方式:
        service = HistoricalQueryService()

        # 查询球队历史
        results = service.query_team_history("Manchester City", limit=20)

        # 查询联赛比赛
        results = service.query_league_matches("E0", year=2024)

        # 搜索相似比赛
        results = service.search_similar(
            "Premier League high scoring matches",
            top_k=10
        )

        # 获取赔率统计
        stats = service.get_odds_statistics("E0")
    """

    def __init__(
        self,
        loader: Optional[HistoricalDataLoader] = None,
        vectorizer: Optional[HistoricalVectorizer] = None
    ):
        self.loader = loader or HISTORICAL_LOADER
        self.vectorizer = vectorizer or HISTORICAL_VECTORIZER

    def query_team_history(
        self,
        team_name: str,
        limit: int = 20,
        home_only: bool = False,
        away_only: bool = False
    ) -> List[Dict[str, Any]]:
        """查询球队历史比赛"""
        matches = self.loader.get_matches_by_team(team_name)

        if home_only:
            matches = [m for m in matches if m.home_team.lower() == team_name.lower()]
        elif away_only:
            matches = [m for m in matches if m.away_team.lower() == team_name.lower()]

        matches = sorted(matches, key=lambda x: x.date, reverse=True)[:limit]

        return [m.to_dict() for m in matches]

    def query_league_matches(
        self,
        league_code: str,
        year: Optional[int] = None,
        season: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """查询联赛比赛"""
        matches = self.loader.get_matches_by_league(league_code)

        if year:
            matches = [m for m in matches if m.year == year]
        elif season:
            matches = [m for m in matches if m.season == season]

        matches = sorted(matches, key=lambda x: x.date, reverse=True)[:limit]

        return [m.to_dict() for m in matches]

    def query_recent_matches(
        self,
        days: int = 30,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """查询最近的比赛"""
        cutoff = datetime.now() - timedelta(days=days)
        matches = self.loader.load_all()

        recent = []
        for m in matches:
            try:
                match_date = datetime.strptime(m.date, "%Y-%m-%d")
                if match_date >= cutoff:
                    recent.append(m)
            except:
                continue

        recent = sorted(recent, key=lambda x: x.date, reverse=True)[:limit]
        return [m.to_dict() for m in recent]

    def search_similar(
        self,
        query: str,
        top_k: int = 10,
        league: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """语义搜索相似比赛"""
        return self.vectorizer.search_similar_matches(
            query=query,
            top_k=top_k,
            league_filter=league
        )

    def get_odds_statistics(self, league_code: str) -> Dict[str, Any]:
        """获取联赛赔率统计"""
        matches = self.loader.get_matches_by_league(league_code)

        valid_odds = [m for m in matches if m.home_odds is not None]

        if not valid_odds:
            return {"count": 0}

        home_odds: List[float] = [m.home_odds for m in valid_odds if m.home_odds is not None]
        draw_odds: List[float] = [m.draw_odds for m in valid_odds if m.draw_odds is not None]
        away_odds: List[float] = [m.away_odds for m in valid_odds if m.away_odds is not None]

        return {
            "count": len(valid_odds),
            "home_odds": {
                "min": min(home_odds) if home_odds else None,
                "max": max(home_odds) if home_odds else None,
                "avg": sum(home_odds) / len(home_odds) if home_odds else None,
            },
            "draw_odds": {
                "min": min(draw_odds) if draw_odds else None,
                "max": max(draw_odds) if draw_odds else None,
                "avg": sum(draw_odds) / len(draw_odds) if draw_odds else None,
            },
            "away_odds": {
                "min": min(away_odds) if away_odds else None,
                "max": max(away_odds) if away_odds else None,
                "avg": sum(away_odds) / len(away_odds) if away_odds else None,
            },
        }

    def get_team_statistics(self, team_name: str) -> Dict[str, Any]:
        """获取球队统计"""
        matches = self.loader.get_matches_by_team(team_name)

        if not matches:
            return {"count": 0}

        home_matches = [m for m in matches if m.home_team.lower() == team_name.lower()]
        away_matches = [m for m in matches if m.away_team.lower() == team_name.lower()]

        home_wins = sum(1 for m in home_matches if m.result == "H")
        away_wins = sum(1 for m in away_matches if m.result == "A")
        draws_home = sum(1 for m in home_matches if m.result == "D")
        draws_away = sum(1 for m in away_matches if m.result == "D")

        total_wins = home_wins + away_wins
        total_draws = draws_home + draws_away
        total_losses = len(matches) - total_wins - total_draws

        return {
            "team": team_name,
            "total_matches": len(matches),
            "home_matches": len(home_matches),
            "away_matches": len(away_matches),
            "wins": total_wins,
            "draws": total_draws,
            "losses": total_losses,
            "win_rate": total_wins / len(matches) if matches else 0,
            "home_win_rate": home_wins / len(home_matches) if home_matches else 0,
            "away_win_rate": away_wins / len(away_matches) if away_matches else 0,
        }

    def get_data_overview(self) -> Dict[str, Any]:
        """获取数据概览"""
        stats = self.loader.get_stats()
        vector_stats = self.vectorizer.get_vectorization_stats()

        return {
            "total_matches": stats.get("total_matches", 0),
            "date_range": f"{self.loader.load_metadata().get('date_range', 'N/A')}",
            "leagues": len(stats.get("by_league", {})),
            "vectorized": vector_stats.get("total_in_database", 0),
        }


HISTORICAL_QUERY_SERVICE = HistoricalQueryService()
