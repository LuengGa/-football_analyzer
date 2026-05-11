"""
数据清洗器 - 标准化数据格式
=============================
"""

import re
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataCleaner:
    """通用数据清洗器"""

    @staticmethod
    def clean_string(value: Any, max_length: int = 100) -> str:
        if value is None:
            return ""

        text = str(value).strip()

        text = re.sub(r'\s+', ' ', text)

        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        return text[:max_length]

    @staticmethod
    def clean_team_name(name: str) -> str:
        if not name:
            return "Unknown"

        name = DataCleaner.clean_string(name)

        team_aliases = {
            "manchester city": "Manchester City",
            "man city": "Manchester City",
            "mci": "Manchester City",
            "arsenal": "Arsenal",
            "ars": "Arsenal",
            "liverpool": "Liverpool",
            "liv": "Liverpool",
            "chelsea": "Chelsea",
            "che": "Chelsea",
            "manchester united": "Manchester United",
            "man utd": "Manchester United",
            "mun": "Manchester United",
            "tottenham": "Tottenham Hotspur",
            "spurs": "Tottenham Hotspur",
            "tot": "Tottenham Hotspur",
            "real madrid": "Real Madrid",
            "rm": "Real Madrid",
            "barcelona": "FC Barcelona",
            "barca": "FC Barcelona",
            "fcb": "FC Barcelona",
            "bayern": "Bayern Munich",
            "fcbayern": "Bayern Munich",
            "psg": "Paris Saint-Germain",
            "paris sg": "Paris Saint-Germain",
            "juventus": "Juventus",
            "juv": "Juventus",
            "inter": "Inter Milan",
            "milan": "AC Milan",
        }

        name_lower = name.lower()
        if name_lower in team_aliases:
            return team_aliases[name_lower]

        return name

    @staticmethod
    def clean_league_name(league: str) -> str:
        if not league:
            return "Unknown League"

        league = DataCleaner.clean_string(league)

        league_normalizations = {
            "premier league": "Premier League",
            "epl": "Premier League",
            "english premier": "Premier League",
            "english premier league": "Premier League",
            "la liga": "La Liga",
            "laliga": "La Liga",
            "spanish league": "La Liga",
            "serie a": "Serie A",
            "serie": "Serie A",
            "italian league": "Serie A",
            "bundesliga": "Bundesliga",
            "german league": "Bundesliga",
            "ligue 1": "Ligue 1",
            "ligue1": "Ligue 1",
            "french league": "Ligue 1",
            "champions league": "Champions League",
            "ucl": "Champions League",
            "uefa champions": "Champions League",
            "champions": "Champions League",
            "europa league": "Europa League",
            "uel": "Europa League",
            "uefa europa": "Europa League",
        }

        league_lower = league.lower()
        if league_lower in league_normalizations:
            return league_normalizations[league_lower]

        return league

    @staticmethod
    def clean_odds(odds: Any) -> Optional[float]:
        if odds is None:
            return None

        if isinstance(odds, (int, float)):
            value = float(odds)
            if 1.0 <= value <= 100.0:
                return round(value, 2)
            return None

        if isinstance(odds, str):
            try:
                value = float(odds.replace(",", "."))
                if 1.0 <= value <= 100.0:
                    return round(value, 2)
            except ValueError:
                pass

        return None

    @staticmethod
    def clean_score(score: Any) -> Optional[Dict[str, int]]:
        if score is None:
            return None

        if isinstance(score, dict):
            home = score.get("home")
            away = score.get("away")

            if isinstance(home, int) and isinstance(away, int):
                return {"home": home, "away": away}

        if isinstance(score, str):
            parts = re.split(r'[-:]', score)
            if len(parts) == 2:
                try:
                    home = int(parts[0].strip())
                    away = int(parts[1].strip())
                    return {"home": home, "away": away}
                except ValueError:
                    pass

        return None

    @staticmethod
    def clean_date(date_str: Any) -> Optional[str]:
        if not date_str:
            return None

        if isinstance(date_str, datetime):
            return date_str.strftime("%Y-%m-%d %H:%M:%S")

        if isinstance(date_str, str):
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue

        return str(date_str)


class MatchDataCleaner:
    """比赛数据专用清洗器"""

    def __init__(self):
        self.cleaner = DataCleaner()

    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = {}

        if "home_team" in data or "home" in data:
            home = data.get("home_team") or data.get("home")
            cleaned["home_team"] = self.cleaner.clean_team_name(str(home)) if home else "Unknown"

        if "away_team" in data or "away" in data:
            away = data.get("away_team") or data.get("away")
            cleaned["away_team"] = self.cleaner.clean_team_name(str(away)) if away else "Unknown"

        if "league" in data:
            cleaned["league"] = self.cleaner.clean_league_name(data["league"])

        if "odds" in data:
            odds = data["odds"]
            if isinstance(odds, dict):
                cleaned["odds"] = {
                    k: self.cleaner.clean_odds(v)
                    for k, v in odds.items()
                    if self.cleaner.clean_odds(v) is not None
                }
            else:
                cleaned_odds = self.cleaner.clean_odds(odds)
                if cleaned_odds:
                    cleaned["odds"] = {"default": cleaned_odds}

        if "score" in data:
            cleaned["score"] = self.cleaner.clean_score(data["score"])

        if "match_date" in data or "date" in data:
            date = data.get("match_date") or data.get("date")
            cleaned["match_date"] = self.cleaner.clean_date(date)

        if "match_id" in data or "id" in data:
            match_id = data.get("match_id") or data.get("id")
            cleaned["match_id"] = self.cleaner.clean_string(str(match_id), max_length=50)

        for key, value in data.items():
            if key not in cleaned:
                cleaned[key] = value

        return cleaned
