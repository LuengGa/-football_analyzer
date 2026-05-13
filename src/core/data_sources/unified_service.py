"""
AFA v9.0 统一数据获取服务
===========================

整合多种数据获取方式：
1. API数据源 (The Odds API, Football-Data, etc.)
2. 网页自动化 (VisualBrowser + browser-use)
3. MCP工具 (MCP服务器)
4. 搜索 (WebSearch)

使用策略:
- 优先使用API (快速)
- API失败时使用网页自动化
- 同时获取多源数据进行交叉验证
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DataSource:
    """数据源定义"""
    name: str
    source_type: str  # api, browser, mcp, search
    priority: int  # 优先级，越低越优先
    enabled: bool = True
    api_key_required: bool = False
    cost_per_call: float = 0.0  # 每调用成本


class UnifiedDataService:
    """
    统一数据获取服务

    支持多种数据源，按优先级自动选择
    """

    def __init__(self):
        self.sources: List[DataSource] = self._init_sources()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5分钟缓存

    def _init_sources(self) -> List[DataSource]:
        """初始化数据源"""
        return [
            DataSource(
                name="The_Odds_API",
                source_type="api",
                priority=1,
                api_key_required=True,
                cost_per_call=0.001
            ),
            DataSource(
                name="Football_Data_API",
                source_type="api",
                priority=2,
                api_key_required=True,
                cost_per_call=0.001
            ),
            DataSource(
                name="Sportmonks_API",
                source_type="api",
                priority=3,
                api_key_required=True,
                cost_per_call=0.01
            ),
            DataSource(
                name="Visual_Browser",
                source_type="browser",
                priority=10,
                api_key_required=True,  # 需要OpenAI API
            ),
            DataSource(
                name="MCP_Server",
                source_type="mcp",
                priority=5,
            ),
        ]

    async def get_live_odds(
        self,
        home_team: str,
        away_team: str,
        league: str = "EPL"
    ) -> Dict[str, Any]:
        """
        获取实时赔率

        策略:
        1. 尝试 The Odds API
        2. API失败时使用 VisualBrowser
        """
        cache_key = f"odds:{home_team}:{away_team}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result: Dict[str, Any] = {"source": [], "odds": {}}

        # 1. 尝试API
        api_result = await self._get_odds_from_api(home_team, away_team, league)
        if api_result and not api_result.get("error"):
            result["source"].append("api")
            result["odds"] = api_result
            self._cache[cache_key] = result
            return result

        # 2. API失败，使用浏览器
        browser_result = await self._get_odds_from_browser(home_team, away_team)
        if browser_result:
            result["source"].append("browser")
            result["odds"].update(browser_result)

        self._cache[cache_key] = result
        return result

    async def _get_odds_from_api(
        self,
        home_team: str,
        away_team: str,
        league: str
    ) -> Optional[Dict[str, Any]]:
        """从API获取赔率"""
        try:
            from src.tools.odds.global_odds_fetcher import get_global_arbitrage_data

            league_map = {
                "EPL": "英超", "西甲": "西甲", "意甲": "意甲",
                "德甲": "德甲", "法甲": "法甲"
            }
            league_cn = league_map.get(league, league)

            raw = get_global_arbitrage_data(league_cn, home_team, away_team)
            data: Dict[str, Any] = json.loads(raw)

            if "error" in data:
                logger.warning(f"API返回错误: {data['error']}")
                return None

            return data
        except Exception as e:
            logger.warning(f"API调用失败: {e}")
            return None

    async def _get_odds_from_browser(
        self,
        home_team: str,
        away_team: str
    ) -> Optional[Dict[str, Any]]:
        """使用VisualBrowser获取赔率"""
        try:
            from src.tools.odds.visual_browser import VisualBrowser

            browser = VisualBrowser()
            instruction = f"""
            访问以下博彩网站获取赔率信息:
            1. 搜索 '{home_team}' vs '{away_team}'
            2. 提取胜平负赔率 (H2H)
            3. 提取亚洲盘口和大小球赔率
            4. 返回JSON格式结果
            """
            result = await browser.extract_info(instruction)
            return {"browser_raw": result}
        except Exception as e:
            logger.warning(f"浏览器获取失败: {e}")
            return None

    async def get_match_info(
        self,
        home_team: str,
        away_team: str,
        league: str = "EPL"
    ) -> Dict[str, Any]:
        """
        获取比赛信息

        包含: 阵容、伤病、天气等
        """
        cache_key = f"match:{home_team}:{away_team}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result: Dict[str, Any] = {"source": [], "data": {}}

        # 1. 尝试API
        api_data = await self._get_match_info_from_api(home_team, away_team, league)
        if api_data:
            result["source"].append("api")
            result["data"].update(api_data)

        # 2. 尝试MCP
        mcp_data = await self._get_match_info_from_mcp(home_team, away_team)
        if mcp_data:
            result["source"].append("mcp")
            result["data"].update(mcp_data)

        # 3. 浏览器补充
        browser_data = await self._get_match_info_from_browser(home_team, away_team)
        if browser_data:
            result["source"].append("browser")
            result["data"].update(browser_data)

        self._cache[cache_key] = result
        return result

    async def _get_match_info_from_api(
        self,
        home_team: str,
        away_team: str,
        league: str
    ) -> Optional[Dict[str, Any]]:
        """从API获取比赛信息"""
        try:
            from src.afa_v9.data_sources.football_sources import APIFootballDataSource
            import os

            api_key = os.environ.get("FOOTBALL_API_KEY", "")
            base_url = os.environ.get("FOOTBALL_API_URL", "https://v3.football.api-sports.io")
            source = APIFootballDataSource(api_key=api_key, base_url=base_url)
            fixtures = source.get_fixtures()

            for f in fixtures.get("response", []):
                home_team_attr = f.get("teams", {}).get("home", {}).get("name", "")
                away_team_attr = f.get("teams", {}).get("away", {}).get("name", "")
                if home_team.lower() in str(home_team_attr).lower() and away_team.lower() in str(away_team_attr).lower():
                    return {
                        "date": f.get("fixture", {}).get("date", ""),
                        "venue": f.get("fixture", {}).get("venue", {}).get("name", "unknown"),
                        "league": league
                    }
        except Exception as e:
            logger.warning(f"API获取比赛信息失败: {e}")
        return None

    async def _get_match_info_from_mcp(
        self,
        home_team: str,
        away_team: str
    ) -> Optional[Dict[str, Any]]:
        """从MCP获取比赛信息"""
        try:
            from src.core.mcp.adapter import MCPServer

            server = MCPServer()
            result: Optional[Dict[str, Any]] = await server.call_tool("get_match_data", {
                "home_team": home_team,
                "away_team": away_team
            })
            return result
        except Exception as e:
            logger.warning(f"MCP获取失败: {e}")
        return None

    async def _get_match_info_from_browser(
        self,
        home_team: str,
        away_team: str
    ) -> Optional[Dict[str, Any]]:
        """使用VisualBrowser获取比赛信息"""
        try:
            from src.tools.odds.visual_browser import VisualBrowser

            browser = VisualBrowser()
            instruction = f"""
            访问足球信息网站获取以下比赛信息:
            1. {home_team} vs {away_team}
            2. 提取: 比赛时间、场地、天气预报
            3. 提取: 主队阵容、伤病情况
            4. 提取: 客队阵容、伤病情况
            5. 返回JSON格式
            """
            result = await browser.extract_info(instruction)
            return {"browser_raw": result}
        except Exception as e:
            logger.warning(f"浏览器获取失败: {e}")
        return None

    async def get_injury_news(
        self,
        team_name: str
    ) -> Dict[str, Any]:
        """获取伤病信息"""
        cache_key = f"injury:{team_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result: Dict[str, Any] = {"source": [], "injuries": []}

        # 尝试浏览器获取
        try:
            from src.tools.odds.visual_browser import VisualBrowser

            browser = VisualBrowser()
            instruction = f"""
            搜索 {team_name} 的伤病情况:
            1. 查找受伤球员名单
            2. 查找伤愈复出球员
            3. 返回球员名和伤情
            """
            result_text = await browser.extract_info(instruction)
            result["source"].append("browser")
            result["browser_raw"] = result_text
        except Exception as e:
            logger.warning(f"伤病信息获取失败: {e}")

        self._cache[cache_key] = result
        return result

    def get_weather(
        self,
        venue: str,
        match_date: str
    ) -> Dict[str, Any]:
        """获取天气信息"""
        try:
            from src.afa_v9.data_sources.weather_sources import OpenWeatherMapSource
            import os

            api_key = os.environ.get("WEATHER_API_KEY", "")
            base_url = os.environ.get("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5")
            source = OpenWeatherMapSource(api_key=api_key, base_url=base_url)
            weather = source.get_current_weather(city=venue)

            return {
                "venue": venue,
                "date": match_date,
                "weather": weather,
                "source": "api"
            }
        except Exception as e:
            logger.warning(f"天气获取失败: {e}")
            return {"error": str(e)}

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        logger.info("数据缓存已清除")


# 全局实例
UNIFIED_DATA_SERVICE = UnifiedDataService()


def get_data_service() -> UnifiedDataService:
    """获取数据服务实例"""
    return UNIFIED_DATA_SERVICE
