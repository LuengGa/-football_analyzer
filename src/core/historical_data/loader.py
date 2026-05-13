"""
历史数据加载器
================

加载 INTEGRATED_COMPLETE_DATA.json 并提供标准化接口
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Iterator
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MatchRecord:
    """比赛记录标准化格式"""
    match_id: str
    league: str
    league_name: str
    season: str
    date: str
    year: int
    month: int
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    result: str
    home_odds: Optional[float]
    draw_odds: Optional[float]
    away_odds: Optional[float]
    closing_home_odds: Optional[float]
    closing_draw_odds: Optional[float]
    closing_away_odds: Optional[float]
    asian_handicap_home: Optional[float]
    asian_handicap_away: Optional[float]
    over_line: Optional[float]
    over_odds: Optional[float]
    under_odds: Optional[float]
    home_shots: Optional[int]
    away_shots: Optional[int]
    home_corners: Optional[int]
    away_corners: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "match_id": self.match_id,
            "league": self.league,
            "league_name": self.league_name,
            "season": self.season,
            "date": self.date,
            "year": self.year,
            "month": self.month,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_goals": self.home_goals,
            "away_goals": self.away_goals,
            "result": self.result,
            "home_odds": self.home_odds,
            "draw_odds": self.draw_odds,
            "away_odds": self.away_odds,
            "closing_home_odds": self.closing_home_odds,
            "closing_draw_odds": self.closing_draw_odds,
            "closing_away_odds": self.closing_away_odds,
            "asian_handicap_home": self.asian_handicap_home,
            "asian_handicap_away": self.asian_handicap_away,
            "over_line": self.over_line,
            "over_odds": self.over_odds,
            "under_odds": self.under_odds,
            "home_shots": self.home_shots,
            "away_shots": self.away_shots,
            "home_corners": self.home_corners,
            "away_corners": self.away_corners,
        }

    def to_text(self) -> str:
        return f"{self.home_team} vs {self.away_team} | {self.league_name} | {self.date} | Score: {self.home_goals}-{self.away_goals} | Odds: H:{self.home_odds} D:{self.draw_odds} A:{self.away_odds}"


class HistoricalDataLoader:
    """
    历史数据加载器

    使用方式:
        loader = HistoricalDataLoader()
        matches = loader.load_all()

        # 按联赛查询
        epl_matches = loader.get_matches_by_league("E0")

        # 按球队查询
        city_matches = loader.get_matches_by_team("Manchester City")

        # 批量迭代
        for match in loader.iter_matches(batch_size=1000):
            process(match)
    """

    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            possible_paths = [
                str(project_root / "INTEGRATED_COMPLETE_DATA.json"),
                str(project_root / "data" / "archive" / "INTEGRATED_COMPLETE_DATA.json"),
                str(project_root / "data" / "INTEGRATED_COMPLETE_DATA.json"),
            ]
            for path in possible_paths:
                if Path(path).exists():
                    data_path = path
                    break
            else:
                data_path = possible_paths[0]

        self.data_path = Path(data_path)
        self._cache: Optional[List[MatchRecord]] = None
        self._metadata: Optional[Dict] = None

        if not self.data_path.exists():
            logger.warning(f"Data file not found at: {self.data_path}")

    def _generate_match_id(self, match: Dict) -> str:
        league = match.get("league", "")
        date = match.get("date", "")
        home = match.get("home_team", "")
        away = match.get("away_team", "")
        return f"{league}_{date}_{home}_{away}".replace(" ", "_")[:50]

    def _parse_match(self, match: Dict) -> Optional[MatchRecord]:
        try:
            three_way = match.get("three_way_odds", {}).get("opening", {})
            closing = match.get("three_way_odds", {}).get("closing", {})

            opening_odds = None
            closing_odds = None

            for bookmaker in ["Bet365", "WilliamHill", "Betway", "Average"]:
                if bookmaker in three_way:
                    opening_odds = three_way[bookmaker]
                    break

            for bookmaker in ["Bet365", "Betway", "Average"]:
                if bookmaker in closing:
                    closing_odds = closing[bookmaker]
                    break

            asian = match.get("asian_handicap", {}).get("opening", {})
            asian_home = asian.get("Ladbrokes", {}).get("home") if asian else None
            asian_away = asian.get("Ladbrokes", {}).get("away") if asian else None

            ou = match.get("over_under", {}).get("opening", {})
            over_line = None
            over_odds = None
            under_odds = None
            for bookmaker in ["Bet365", "Betway", "Average"]:
                if bookmaker in ou:
                    ou_data = ou[bookmaker]
                    if "line" in ou_data:
                        over_line = ou_data["line"]
                    if "over" in ou_data:
                        over_odds = ou_data["over"]
                    if "under" in ou_data:
                        under_odds = ou_data["under"]
                    break

            return MatchRecord(
                match_id=self._generate_match_id(match),
                league=match.get("league", ""),
                league_name=match.get("league_name", ""),
                season=match.get("season", ""),
                date=match.get("date", ""),
                year=match.get("year", 0),
                month=match.get("month", 0),
                home_team=match.get("home_team", ""),
                away_team=match.get("away_team", ""),
                home_goals=match.get("home_goals", 0),
                away_goals=match.get("away_goals", 0),
                result=match.get("result", ""),
                home_odds=opening_odds.get("home") if opening_odds else None,
                draw_odds=opening_odds.get("draw") if opening_odds else None,
                away_odds=opening_odds.get("away") if opening_odds else None,
                closing_home_odds=closing_odds.get("home") if closing_odds else None,
                closing_draw_odds=closing_odds.get("draw") if closing_odds else None,
                closing_away_odds=closing_odds.get("away") if closing_odds else None,
                asian_handicap_home=asian_home,
                asian_handicap_away=asian_away,
                over_line=over_line,
                over_odds=over_odds,
                under_odds=under_odds,
                home_shots=match.get("home_shots"),
                away_shots=match.get("away_shots"),
                home_corners=match.get("home_corners"),
                away_corners=match.get("away_corners"),
            )
        except Exception as e:
            logger.warning(f"Failed to parse match: {e}")
            return None

    def _load_json_data(self) -> Dict[str, Any]:
        """加载JSON数据并缓存"""
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Failed to load JSON data: {e}")
            return {}

    def load_metadata(self) -> Dict[str, Any]:
        """加载元数据"""
        if self._metadata is not None:
            return self._metadata

        if not self.data_path.exists():
            return {}

        data = self._load_json_data()
        self._metadata = data.get("metadata", {})
        return self._metadata  # type: ignore[no-any-return]

    def load_stats(self) -> Dict[str, Any]:
        """加载统计数据"""
        data = self._load_json_data()
        return data.get("stats", {})  # type: ignore[no-any-return]

    def load_all(self, force_reload: bool = False) -> List[MatchRecord]:
        """加载所有比赛记录"""
        if self._cache is not None and not force_reload:
            return self._cache

        if not self.data_path.exists():
            logger.error(f"Data file not found: {self.data_path}")
            return []

        logger.info(f"Loading historical data from {self.data_path}")

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            matches_data = data.get("matches", [])
            logger.info(f"Parsing {len(matches_data)} matches...")

            self._cache = []
            for match_data in matches_data:
                match = self._parse_match(match_data)
                if match:
                    self._cache.append(match)

            logger.info(f"Loaded {len(self._cache)} valid matches")
            return self._cache

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return []

    def iter_matches(self, batch_size: int = 1000) -> Iterator[List[MatchRecord]]:
        """批量迭代比赛记录"""
        matches = self.load_all()
        for i in range(0, len(matches), batch_size):
            yield matches[i:i + batch_size]

    def get_matches_by_league(self, league_code: str) -> List[MatchRecord]:
        """按联赛代码查询"""
        matches = self.load_all()
        return [m for m in matches if m.league == league_code]

    def get_matches_by_team(self, team_name: str) -> List[MatchRecord]:
        """按球队名称查询（模糊匹配）"""
        matches = self.load_all()
        team_lower = team_name.lower()
        return [
            m for m in matches
            if team_lower in m.home_team.lower() or team_lower in m.away_team.lower()
        ]

    def get_recent_matches(self, limit: int = 100) -> List[MatchRecord]:
        """获取最近的比赛"""
        matches = self.load_all()
        return sorted(matches, key=lambda x: x.date, reverse=True)[:limit]

    def get_leagues(self) -> List[str]:
        """获取所有联赛"""
        matches = self.load_all()
        return list(set(m.league for m in matches)) if matches else []

    def get_teams(self) -> List[str]:
        """获取所有球队"""
        matches = self.load_all()
        teams = set()
        for m in matches:
            teams.add(m.home_team)
            teams.add(m.away_team)
        return sorted(list(teams))

    def get_stats(self) -> Dict[str, Any]:
        """获取数据统计"""
        return self.load_stats()

HISTORICAL_LOADER = HistoricalDataLoader()
