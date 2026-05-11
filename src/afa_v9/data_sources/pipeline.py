"""
AFA v9.0 统一数据管道

整合所有数据源，提供统一的接口
"""

from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from .config import DATA_SOURCE_CONFIG
from .football_sources import (
    FootballDataSource,
    APIFootballDataSource,
    SportmonksDataSource,
)
from .odds_sources import TheOddsAPISource, OddsAPIioSource
from .weather_sources import OpenWeatherMapSource, WeatherAPISource


class DataPipeline:
    def __init__(self):
        self._init_sources()

    def _init_sources(self) -> None:
        config = DATA_SOURCE_CONFIG

        self.football_data = FootballDataSource(
            api_key=config.FOOTBALL_DATA_API_KEY,
            base_url=config.FOOTBALL_DATA_BASE_URL,
        )

        self.api_football = APIFootballDataSource(
            api_key=config.API_FOOTBALL_KEY,
            base_url=config.API_FOOTBALL_BASE_URL,
        )

        self.sportmonks = SportmonksDataSource(
            api_key=config.SPORTMONKS_API_KEY,
            base_url=config.SPORTMONKS_BASE_URL,
        )

        self.the_odds_api = TheOddsAPISource(
            api_key=config.ODDS_API_KEY,
            base_url=config.ODDS_API_BASE_URL,
        )

        self.odds_api_io = OddsAPIioSource(
            api_key=config.ODDS_API_IO_KEY,
            base_url=config.ODDS_API_IO_BASE_URL,
        )

        self.openweathermap = OpenWeatherMapSource(
            api_key=config.OPENWEATHERMAP_API_KEY,
            base_url=config.OPENWEATHERMAP_BASE_URL,
        )

        self.weather_api = WeatherAPISource(
            api_key=config.WEATHERAPI_KEY,
            base_url=config.WEATHERAPI_BASE_URL,
        )

    def get_match_intel(
        self,
        home_team: str,
        away_team: str,
        match_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取比赛情报"""
        intel = {
            "home_team": home_team,
            "away_team": away_team,
            "match_date": match_date or datetime.now().isoformat(),
            "fetched_at": datetime.now().isoformat(),
        }

        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        football_matches = self.api_football.get_fixtures(date=today)
        if "response" in football_matches:
            for match in football_matches["response"][:3]:
                teams = match.get("teams", {})
                home = teams.get("home", {}).get("name", "")
                away = teams.get("away", {}).get("name", "")
                if home.lower() in home_team.lower() or away.lower() in away_team.lower():
                    intel["fixture"] = {
                        "id": match.get("fixture", {}).get("id"),
                        "date": match.get("fixture", {}).get("date"),
                        "venue": match.get("fixture", {}).get("venue", {}).get("name"),
                        "league": match.get("league", {}).get("name"),
                        "status": match.get("fixture", {}).get("status", {}).get("short"),
                    }

        return intel

    def get_team_form(
        self,
        team_name: str,
        league_id: Optional[int] = None,
        matches_count: int = 5,
    ) -> Dict[str, Any]:
        """获取球队近期状态"""
        form_data = {
            "team": team_name,
            "recent_matches": [],
            "form_string": "",
            "win_rate": 0.0,
        }

        if league_id:
            fixtures = self.api_football.get_fixtures(league_id=league_id)
            if "response" in fixtures:
                team_matches = []
                for match in fixtures["response"]:
                    teams = match.get("teams", {})
                    if team_name.lower() in [teams.get("home", {}).get("name", "").lower(),
                                            teams.get("away", {}).get("name", "").lower()]:
                        team_matches.append(match)

                team_matches.sort(key=lambda x: x.get("fixture", {}).get("timestamp", 0), reverse=True)

                results = []
                for match in team_matches[:matches_count]:
                    teams = match.get("teams", {})
                    goals = match.get("goals", {})

                    if teams.get("home", {}).get("name", "").lower() == team_name.lower():
                        team_goals = goals.get("home", 0)
                        opp_goals = goals.get("away", 0)
                    else:
                        team_goals = goals.get("away", 0)
                        opp_goals = goals.get("home", 0)

                    if team_goals > opp_goals:
                        result = "W"
                    elif team_goals < opp_goals:
                        result = "L"
                    else:
                        result = "D"
                    results.append(result)

                form_data["recent_matches"] = team_matches[:matches_count]
                form_data["form_string"] = "-".join(results) if results else ""
                if results:
                    wins = results.count("W")
                    form_data["win_rate"] = wins / len(results)

        return form_data

    def get_odds_data(
        self,
        sport: str = "soccer_epl",
        region: str = "uk",
    ) -> Dict[str, Any]:
        """获取赔率数据"""
        odds_data = {
            "sport": sport,
            "region": region,
            "bookmakers": [],
            "timestamp": datetime.now().isoformat(),
        }

        try:
            odds_response = self.the_odds_api.get_odds(sport=sport, region=region)
            if "data" in odds_response:
                odds_data["bookmakers"] = odds_response["data"][:5]
            elif "response" in odds_response:
                odds_data["bookmakers"] = odds_response["response"][:5]
        except Exception:
            odds_data["error"] = "Failed to fetch odds data"

        return odds_data

    def get_weather(self, city: str) -> Dict[str, Any]:
        """获取天气数据"""
        weather_data = {
            "city": city,
            "weather": None,
            "forecast": [],
            "timestamp": datetime.now().isoformat(),
        }

        try:
            current = self.weather_api.get_current(city)
            if "current" in current:
                weather_data["weather"] = {
                    "temp": current["current"].get("temp_c"),
                    "condition": current["current"].get("condition", {}).get("text"),
                    "wind": current["current"].get("wind_kph"),
                    "humidity": current["current"].get("humidity"),
                }

            forecast = self.weather_api.get_forecast(city=city, days=1)
            if "forecast" in forecast:
                weather_data["forecast"] = forecast["forecast"].get("forecastday", [])
        except Exception:
            weather_data["error"] = "Failed to fetch weather data"

        return weather_data

    def get_comprehensive_match_data(
        self,
        home_team: str,
        away_team: str,
        venue_city: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取综合比赛数据"""
        data = {
            "home_team": home_team,
            "away_team": away_team,
            "timestamp": datetime.now().isoformat(),
        }

        data["match_intel"] = self.get_match_intel(home_team, away_team)

        data["home_form"] = self.get_team_form(home_team)
        data["away_form"] = self.get_team_form(away_team)

        if venue_city:
            data["weather"] = self.get_weather(venue_city)

        data["odds"] = self.get_odds_data()

        return data

    def get_all_sources_status(self) -> Dict[str, Any]:
        """获取所有数据源状态"""
        return {
            "FootballData": self.football_data.get_status(),
            "APIFootball": self.api_football.get_status(),
            "Sportmonks": self.sportmonks.get_status(),
            "TheOddsAPI": self.the_odds_api.get_status(),
            "OddsAPIio": self.odds_api_io.get_status(),
            "OpenWeatherMap": self.openweathermap.get_status(),
            "WeatherAPI": self.weather_api.get_status(),
        }


DATA_PIPELINE = DataPipeline()
