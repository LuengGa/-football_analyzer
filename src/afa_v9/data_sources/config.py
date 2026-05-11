"""
AFA v9.0 数据源配置

数据源类型：
1. 赛事数据: Football-Data.org, API-Football, Sportmonks
2. 赔率数据: The Odds API, Odds-API.io
3. 天气数据: OpenWeatherMap, WeatherAPI

配置方式：
1. 直接使用环境变量
2. 或修改此文件
"""

import os


class DataSourceConfig:
    FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "")
    FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"

    API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
    API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"

    SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY", "")
    SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3"

    ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
    ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"

    ODDS_API_IO_KEY = os.getenv("ODDS_API_IO_KEY", "")
    ODDS_API_IO_BASE_URL = "https://api.odds-api.io/api/v1"

    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
    OPENWEATHERMAP_BASE_URL = "https://api.openweathermap.org/data/2.5"

    WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY", "")
    WEATHERAPI_BASE_URL = "https://api.weatherapi.com/v1"


DATA_SOURCE_CONFIG = DataSourceConfig()
