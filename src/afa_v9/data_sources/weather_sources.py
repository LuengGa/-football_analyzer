"""
AFA v9.0 天气数据源连接器
"""

from typing import Any, Dict, Optional
from .base import BaseDataSource


class OpenWeatherMapSource(BaseDataSource):
    def __init__(self, api_key: str, base_url: str):
        super().__init__("OpenWeatherMap")
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit_delay = 1.0

    def get_current_weather(self, city: str, units: str = "metric") -> Dict[str, Any]:
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
        }
        return self._make_request("GET", url, params=params)

    def get_forecast(
        self,
        city: str,
        units: str = "metric",
        cnt: int = 5,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
            "cnt": cnt,
        }
        return self._make_request("GET", url, params=params)

    def get_weather_by_coords(
        self,
        lat: float,
        lon: float,
        units: str = "metric",
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": units,
        }
        return self._make_request("GET", url, params=params)


class WeatherAPISource(BaseDataSource):
    def __init__(self, api_key: str, base_url: str):
        super().__init__("WeatherAPI")
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit_delay = 0.5

    def get_current(self, location: str) -> Dict[str, Any]:
        url = f"{self.base_url}/current.json"
        params = {
            "key": self.api_key,
            "q": location,
        }
        return self._make_request("GET", url, params=params)

    def get_forecast(
        self,
        location: str,
        days: int = 3,
        aqi: str = "no",
        alerts: str = "no",
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/forecast.json"
        params = {
            "key": self.api_key,
            "q": location,
            "days": days,
            "aqi": aqi,
            "alerts": alerts,
        }
        return self._make_request("GET", url, params=params)

    def get_sports(
        self,
        location: str,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/sports.json"
        params = {
            "key": self.api_key,
            "q": location,
        }
        return self._make_request("GET", url, params=params)
