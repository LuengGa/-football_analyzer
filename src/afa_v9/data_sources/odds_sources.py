"""
AFA v9.0 赔率数据源连接器
"""

from typing import Any, Dict, Optional
from .base import BaseDataSource


class TheOddsAPISource(BaseDataSource):
    def __init__(self, api_key: str, base_url: str):
        super().__init__("TheOddsAPI")
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit_delay = 2.0

    def get_sports(self) -> Dict[str, Any]:
        url = f"{self.base_url}/sports"
        params = {"apiKey": self.api_key}
        return self._make_request("GET", url, params=params)

    def get_odds(
        self,
        sport: str = "soccer_epl",
        region: str = "uk",
        markets: str = "h2h",
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/sports/{sport}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": region,
            "markets": markets,
        }
        return self._make_request("GET", url, params=params)

    def get_historical_odds(
        self,
        sport: str = "soccer_epl",
        date: str = "",
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/sports/{sport}/odds-history"
        params = {
            "apiKey": self.api_key,
            "date": date,
        }
        return self._make_request("GET", url, params=params)


class OddsAPIioSource(BaseDataSource):
    def __init__(self, api_key: str, base_url: str):
        super().__init__("OddsAPIio")
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit_delay = 1.5

    def get_all_odds(self, sport: str = "soccer") -> Dict[str, Any]:
        url = f"{self.base_url}/odds"
        params = {
            "key": self.api_key,
            "sport": sport,
        }
        return self._make_request("GET", url, params=params)

    def get_event_odds(self, event_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/event"
        params = {
            "key": self.api_key,
            "event": event_id,
        }
        return self._make_request("GET", url, params=params)
