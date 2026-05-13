"""
AFA v9.0 足球数据源连接器
"""

from typing import Any, Dict, Optional
from .base import BaseDataSource


class FootballDataSource(BaseDataSource):
    def __init__(self, api_key: str, base_url: str):
        super().__init__("FootballData")
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"X-Auth-Token": api_key}

    def get_competitions(self) -> Dict[str, Any]:
        url = f"{self.base_url}/competitions"
        return self._make_request("GET", url, headers=self.headers)

    def get_team(self, team_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/teams/{team_id}"
        return self._make_request("GET", url, headers=self.headers)

    def get_matches(
        self,
        competition_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/matches"
        params: Dict[str, Any] = {}
        if competition_id:
            params["competitions"] = competition_id
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        return self._make_request("GET", url, headers=self.headers, params=params)

    def get_match_odds(self, match_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/matches/{match_id}/odds"
        return self._make_request("GET", url, headers=self.headers)

    def get_match_head2head(self, match_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/matches/{match_id}/head2head"
        return self._make_request("GET", url, headers=self.headers)


class APIFootballDataSource(BaseDataSource):
    def __init__(self, api_key: str, base_url: str):
        super().__init__("APIFootball")
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"x-apisports-key": api_key}
        self.rate_limit_delay = 0.5

    def get_leagues(self, country: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/leagues"
        params: Dict[str, Any] = {"current": "true"}
        if country:
            params["country"] = country
        return self._make_request("GET", url, headers=self.headers, params=params)

    def get_fixtures(
        self,
        league_id: Optional[int] = None,
        date: Optional[str] = None,
        live: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/fixtures"
        params: Dict[str, Any] = {}
        if league_id:
            params["league"] = league_id
        if date:
            params["date"] = date
        if live:
            params["live"] = "all"
        return self._make_request("GET", url, headers=self.headers, params=params)

    def get_fixture_odds(self, fixture_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/odds"
        params = {"fixture": fixture_id}
        return self._make_request("GET", url, headers=self.headers, params=params)

    def get_teams(self, league_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/teams"
        params = {"league": league_id}
        return self._make_request("GET", url, headers=self.headers, params=params)

    def get_player_statistics(self, fixture_id: int, team_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/players"
        params = {"fixture": fixture_id, "team": team_id}
        return self._make_request("GET", url, headers=self.headers, params=params)


class SportmonksDataSource(BaseDataSource):
    def __init__(self, api_key: str, base_url: str):
        super().__init__("Sportmonks")
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit_delay = 1.5

    def get_livescores(self) -> Dict[str, Any]:
        url = f"{self.base_url}/football/livescores"
        params = {"api_token": self.api_key}
        return self._make_request("GET", url, params=params)

    def get_upcoming_matches(self, date: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/football/fixtures/multi/{date}" if date else f"{self.base_url}/football/fixtures/date"
        params = {"api_token": self.api_key}
        return self._make_request("GET", url, params=params)

    def get_team(self, team_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/football/teams/{team_id}"
        params = {"api_token": self.api_key}
        return self._make_request("GET", url, params=params)

    def get_standings(self, season_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/football/standings/{season_id}"
        params = {"api_token": self.api_key}
        return self._make_request("GET", url, params=params)
