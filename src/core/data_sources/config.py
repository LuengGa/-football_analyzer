"""
AFA 数据源配置
===============

免费API限制:
- API-Football: 100次/天
- Football-data.org: 10次/分钟, 50次/天
- Odds-API.io: 1000次/月
"""

import os


class DataSourceConfig:
    ODDS_API_KEY = os.getenv("ODDS_API_KEY", "fb47ab523dd9db967003590d76ec9074")
    API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "ac143a21c2fa6ffdfe8716b7424fc4f8")
    FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY", "3a0228c6a55d49a9959b6161cdfca252")
    ODDS_API_IO_KEY = os.getenv(
        "ODDS_API_IO_KEY",
        "9316d729a44c240aa8243660323eda654efdba2db8d961e991fd491516a6b30e",
    )
    THESPORTSDB_KEY = os.getenv("THESPORTSDB_KEY", "1")

    BASE_URLS = {
        "api_football": "https://v3.football.api-sports.io",
        "football_data": "https://api.football-data.org/v4",
        "odds_api": "https://api.odds-api.io/v1",
        "the_sports_db": "https://www.thesportsdb.com/api/v1/json/3",
    }

    RATE_LIMITS = {
        "api_football": {"requests": 100, "period": "day"},
        "football_data": {"requests": 10, "period": "minute"},
        "odds_api": {"requests": 1000, "period": "month"},
        "the_sports_db": {"requests": float("inf"), "period": "unlimited"},
    }


CONFIG = DataSourceConfig()
