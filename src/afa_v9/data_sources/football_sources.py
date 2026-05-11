"""
AFA v9.0 数据源基类

统一的数据获取接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import time
import requests


class BaseDataSource(ABC):
    def __init__(self, name: str):
        self.name = name
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_delay = 1.0

    def _rate_limit(self) -> None:
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        self._rate_limit()
        self.request_count += 1

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "request_count": self.request_count,
            "last_request": datetime.fromtimestamp(self.last_request_time).isoformat()
                if self.last_request_time > 0 else None,
        }


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
        params = {}
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
        params = {"current": "true"}
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
        params = {}
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
