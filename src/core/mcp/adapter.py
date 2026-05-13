"""
MCP工具适配器
==============

Model Context Protocol (MCP) 标准化工具调用
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from ..data_sources.manager import DATA_SOURCE_MANAGER

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    usage_count: int = 0
    success_count: int = 0
    last_used: Optional[datetime] = None


class MCPServer:
    """
    MCP服务器 - 标准化工具注册和调用

    使用方式:
        server = MCPServer()

        @server.tool(name="get_match_info", description="获取比赛信息")
        def get_match_info(match_id: str) -> dict:
            ...

        result = await server.call_tool("get_match_info", {"match_id": "123"})
    """

    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        self.register_tool(MCPTool(
            name="get_match_data",
            description="获取比赛详细信息（包含球队、联赛、时间等）",
            input_schema={
                "type": "object",
                "properties": {
                    "match_id": {
                        "type": "string",
                        "description": "比赛ID"
                    },
                    "include_live": {
                        "type": "boolean",
                        "description": "包含直播数据",
                        "default": False
                    },
                },
                "required": ["match_id"],
            },
            handler=self._get_match_data,
            category="football",
            tags=["match", "data", "api"],
        ))

        self.register_tool(MCPTool(
            name="get_odds",
            description="获取比赛赔率（支持多个博彩公司）",
            input_schema={
                "type": "object",
                "properties": {
                    "match_id": {
                        "type": "string",
                        "description": "比赛ID"
                    },
                    "bookmaker": {
                        "type": "string",
                        "description": "博彩公司名称",
                        "default": "all"
                    },
                },
                "required": ["match_id"],
            },
            handler=self._get_odds,
            category="odds",
            tags=["odds", "betting", "api"],
        ))

        self.register_tool(MCPTool(
            name="get_team_stats",
            description="获取球队统计数据（进球、积分、主客场等）",
            input_schema={
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "球队ID"
                    },
                    "season": {
                        "type": "integer",
                        "description": "赛季年份",
                        "default": 2025
                    },
                },
                "required": ["team_id"],
            },
            handler=self._get_team_stats,
            category="football",
            tags=["team", "stats", "api"],
        ))

        self.register_tool(MCPTool(
            name="search_memory",
            description="搜索AFA记忆系统中的历史数据",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 5
                    },
                },
                "required": ["query"],
            },
            handler=self._search_memory,
            category="memory",
            tags=["search", "memory", "history"],
        ))

        self.register_tool(MCPTool(
            name="get_cache_status",
            description="获取数据源缓存和限流状态",
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=self._get_cache_status,
            category="system",
            tags=["cache", "status", "system"],
        ))

        self.register_tool(MCPTool(
            name="query_team_history",
            description="查询球队历史比赛记录（来自158,971场比赛数据库）",
            input_schema={
                "type": "object",
                "properties": {
                    "team_name": {
                        "type": "string",
                        "description": "球队名称（如 Manchester City）"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回比赛数量",
                        "default": 20
                    },
                },
                "required": ["team_name"],
            },
            handler=self._query_team_history,
            category="historical",
            tags=["historical", "team", "history"],
        ))

        self.register_tool(MCPTool(
            name="query_league_matches",
            description="查询联赛历史比赛",
            input_schema={
                "type": "object",
                "properties": {
                    "league_code": {
                        "type": "string",
                        "description": "联赛代码（如 E0=英超, D1=德甲, SP1=西甲）"
                    },
                    "year": {
                        "type": "integer",
                        "description": "年份",
                        "default": 2024
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回数量",
                        "default": 50
                    },
                },
                "required": ["league_code"],
            },
            handler=self._query_league_matches,
            category="historical",
            tags=["historical", "league", "matches"],
        ))

        self.register_tool(MCPTool(
            name="get_team_statistics",
            description="获取球队统计（胜率、主客场表现等）",
            input_schema={
                "type": "object",
                "properties": {
                    "team_name": {
                        "type": "string",
                        "description": "球队名称"
                    },
                },
                "required": ["team_name"],
            },
            handler=self._get_team_statistics,
            category="historical",
            tags=["historical", "team", "stats"],
        ))

        self.register_tool(MCPTool(
            name="get_odds_statistics",
            description="获取联赛赔率统计（赔率范围、平均值等）",
            input_schema={
                "type": "object",
                "properties": {
                    "league_code": {
                        "type": "string",
                        "description": "联赛代码"
                    },
                },
                "required": ["league_code"],
            },
            handler=self._get_odds_statistics,
            category="historical",
            tags=["historical", "odds", "stats"],
        ))

        self.register_tool(MCPTool(
            name="get_data_overview",
            description="获取历史数据库概览（比赛总数、联赛数等）",
            input_schema={
                "type": "object",
                "properties": {},
            },
            handler=self._get_data_overview,
            category="historical",
            tags=["historical", "overview", "stats"],
        ))

        # ========== 浏览器自动化工具 ==========

        self.register_tool(MCPTool(
            name="browser_scrape",
            description="使用浏览器自动化抓取网页数据（赔率、伤病、阵容等）",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "目标网页URL"
                    },
                    "instruction": {
                        "type": "string",
                        "description": "提取数据的具体指令"
                    },
                },
                "required": ["url", "instruction"],
            },
            handler=self._browser_scrape,
            category="browser",
            tags=["browser", "scraping", "automation"],
        ))

        self.register_tool(MCPTool(
            name="search_web",
            description="搜索互联网获取比赛相关信息",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "source": {
                        "type": "string",
                        "description": "数据来源类型 (odds, injuries, news, general)",
                        "default": "general"
                    },
                },
                "required": ["query"],
            },
            handler=self._search_web,
            category="search",
            tags=["search", "web", "news"],
        ))

        self.register_tool(MCPTool(
            name="get_injury_report",
            description="获取球队伤病报告和阵容信息",
            input_schema={
                "type": "object",
                "properties": {
                    "team_name": {
                        "type": "string",
                        "description": "球队名称"
                    },
                    "use_browser": {
                        "type": "boolean",
                        "description": "是否使用浏览器获取",
                        "default": True
                    },
                },
                "required": ["team_name"],
            },
            handler=self._get_injury_report,
            category="browser",
            tags=["injury", "team", "browser"],
        ))

        self.register_tool(MCPTool(
            name="get_live_odds",
            description="获取实时赔率（使用浏览器或API）",
            input_schema={
                "type": "object",
                "properties": {
                    "home_team": {
                        "type": "string",
                        "description": "主队名称"
                    },
                    "away_team": {
                        "type": "string",
                        "description": "客队名称"
                    },
                    "source": {
                        "type": "string",
                        "description": "数据来源 (api, browser, auto)",
                        "default": "auto"
                    },
                },
                "required": ["home_team", "away_team"],
            },
            handler=self._get_live_odds,
            category="odds",
            tags=["odds", "live", "browser"],
        ))

        self.register_tool(MCPTool(
            name="get_live_match_data",
            description="获取比赛实时数据（阵容、伤病、天气、进球等）",
            input_schema={
                "type": "object",
                "properties": {
                    "home_team": {
                        "type": "string",
                        "description": "主队名称"
                    },
                    "away_team": {
                        "type": "string",
                        "description": "客队名称"
                    },
                    "league": {
                        "type": "string",
                        "description": "联赛名称",
                        "default": "EPL"
                    },
                },
                "required": ["home_team", "away_team"],
            },
            handler=self._get_live_match_data,
            category="live",
            tags=["live", "match", "data"],
        ))

        self.register_tool(MCPTool(
            name="get_weather",
            description="获取比赛场地天气信息",
            input_schema={
                "type": "object",
                "properties": {
                    "venue": {
                        "type": "string",
                        "description": "比赛场地名称"
                    },
                    "date": {
                        "type": "string",
                        "description": "比赛日期 (YYYY-MM-DD)",
                        "default": ""
                    },
                },
                "required": ["venue"],
            },
            handler=self._get_weather,
            category="weather",
            tags=["weather", "venue", "data"],
        ))

        self.register_tool(MCPTool(
            name="get_bet_status",
            description="获取投注状态和追踪信息",
            input_schema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "统计周期 (daily, weekly, monthly, overall)",
                        "default": "daily"
                    },
                },
            },
            handler=self._get_bet_status,
            category="tracking",
            tags=["bet", "tracking", "status"],
        ))

        self.register_tool(MCPTool(
            name="calculate_stake",
            description="计算投注金额（基于Kelly公式）",
            input_schema={
                "type": "object",
                "properties": {
                    "odds": {
                        "type": "number",
                        "description": "赔率"
                    },
                    "probability": {
                        "type": "number",
                        "description": "预测概率 (0-1)"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "置信度 (0-1)",
                        "default": 1.0
                    },
                },
                "required": ["odds", "probability"],
            },
            handler=self._calculate_stake,
            category="bankroll",
            tags=["stake", "kelly", "bankroll"],
        ))

        self.register_tool(MCPTool(
            name="record_bet",
            description="记录投注到系统",
            input_schema={
                "type": "object",
                "properties": {
                    "match_id": {
                        "type": "string",
                        "description": "比赛ID"
                    },
                    "home_team": {
                        "type": "string",
                        "description": "主队名称"
                    },
                    "away_team": {
                        "type": "string",
                        "description": "客队名称"
                    },
                    "selection": {
                        "type": "string",
                        "description": "投注选择 (home, draw, away)"
                    },
                    "odds": {
                        "type": "number",
                        "description": "赔率"
                    },
                    "stake": {
                        "type": "number",
                        "description": "投注金额"
                    },
                    "kelly_fraction": {
                        "type": "number",
                        "description": "Kelly值",
                        "default": 0.1
                    },
                    "confidence": {
                        "type": "number",
                        "description": "置信度",
                        "default": 0.8
                    },
                },
                "required": ["match_id", "home_team", "away_team", "selection", "odds", "stake"],
            },
            handler=self._record_bet,
            category="bankroll",
            tags=["bet", "record", "tracking"],
        ))

        self.register_tool(MCPTool(
            name="settle_bet",
            description="结算投注（标记为赢或输）",
            input_schema={
                "type": "object",
                "properties": {
                    "bet_id": {
                        "type": "string",
                        "description": "投注ID"
                    },
                    "won": {
                        "type": "boolean",
                        "description": "是否获胜"
                    },
                },
                "required": ["bet_id", "won"],
            },
            handler=self._settle_bet,
            category="bankroll",
            tags=["bet", "settle", "result"],
        ))

        self.register_tool(MCPTool(
            name="get_bet_history",
            description="获取投注历史记录",
            input_schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回数量",
                        "default": 20
                    },
                    "status": {
                        "type": "string",
                        "description": "投注状态 (pending, won, lost, all)",
                        "default": "all"
                    },
                },
            },
            handler=self._get_bet_history,
            category="tracking",
            tags=["bet", "history", "records"],
        ))

        self.register_tool(MCPTool(
            name="backtest_strategy",
            description="使用历史数据回测投注策略",
            input_schema={
                "type": "object",
                "properties": {
                    "strategy_name": {
                        "type": "string",
                        "description": "策略名称 (poisson_value, six_layer, simple_favorite)",
                        "default": "poisson_value"
                    },
                    "league_code": {
                        "type": "string",
                        "description": "联赛代码 (如 E0=英超, D1=德甲)",
                        "default": "all"
                    },
                    "year": {
                        "type": "integer",
                        "description": "回测年份",
                        "default": 2024
                    },
                    "use_kelly": {
                        "type": "boolean",
                        "description": "是否使用Kelly投注",
                        "default": True
                    },
                    "value_threshold": {
                        "type": "number",
                        "description": "价值阈值",
                        "default": 0.03
                    },
                },
            },
            handler=self._backtest_strategy,
            category="backtest",
            tags=["backtest", "strategy", "historical"],
        ))

        self.register_tool(MCPTool(
            name="compare_strategies",
            description="比较多个策略的回测表现",
            input_schema={
                "type": "object",
                "properties": {
                    "league_code": {
                        "type": "string",
                        "description": "联赛代码",
                        "default": "all"
                    },
                    "year": {
                        "type": "integer",
                        "description": "回测年份",
                        "default": 2024
                    },
                },
            },
            handler=self._compare_strategies,
            category="backtest",
            tags=["backtest", "compare", "strategy"],
        ))

        self.register_tool(MCPTool(
            name="llm_full_analysis",
            description="AI完整分析 - 综合所有AI能力对比赛进行全面分析",
            input_schema={
                "type": "object",
                "properties": {
                    "home_team": {"type": "string", "description": "主队名称"},
                    "away_team": {"type": "string", "description": "客队名称"},
                    "odds_home": {"type": "number", "description": "主队赔率"},
                    "odds_draw": {"type": "number", "description": "平局赔率"},
                    "odds_away": {"type": "number", "description": "客队赔率"},
                    "league": {"type": "string", "description": "联赛代码", "default": "EPL"},
                },
                "required": ["home_team", "away_team", "odds_home", "odds_draw", "odds_away"],
            },
            handler=self._llm_full_analysis,
            category="ai_decision",
            tags=["ai", "llm", "full_analysis", "decision"],
        ))

        self.register_tool(MCPTool(
            name="llm_betting_decision",
            description="LLM投注决策 - 由AI综合分析后做出投注决策",
            input_schema={
                "type": "object",
                "properties": {
                    "home_team": {"type": "string", "description": "主队名称"},
                    "away_team": {"type": "string", "description": "客队名称"},
                    "odds_home": {"type": "number", "description": "主队赔率"},
                    "odds_draw": {"type": "number", "description": "平局赔率"},
                    "odds_away": {"type": "number", "description": "客队赔率"},
                    "market_sentiment": {"type": "string", "description": "市场情绪", "default": ""},
                    "news_impact": {"type": "string", "description": "新闻影响", "default": ""},
                },
                "required": ["home_team", "away_team", "odds_home", "odds_draw", "odds_away"],
            },
            handler=self._llm_betting_decision,
            category="ai_decision",
            tags=["ai", "llm", "betting", "decision"],
        ))

        self.register_tool(MCPTool(
            name="llm_dynamic_kelly",
            description="LLM动态Kelly - 根据上下文动态调整Kelly参数",
            input_schema={
                "type": "object",
                "properties": {
                    "odds": {"type": "number", "description": "赔率"},
                    "probability": {"type": "number", "description": "预测概率 (0-1)"},
                    "confidence": {"type": "number", "description": "置信度", "default": 0.8},
                },
                "required": ["odds", "probability"],
            },
            handler=self._llm_dynamic_kelly,
            category="ai_bankroll",
            tags=["ai", "llm", "kelly", "stake"],
        ))

        self.register_tool(MCPTool(
            name="llm_dynamic_six_layer",
            description="LLM动态六层分析 - 根据比赛上下文动态调整各层权重",
            input_schema={
                "type": "object",
                "properties": {
                    "home_team": {"type": "string", "description": "主队名称"},
                    "away_team": {"type": "string", "description": "客队名称"},
                    "odds_home": {"type": "number", "description": "主队赔率"},
                    "odds_draw": {"type": "number", "description": "平局赔率"},
                    "odds_away": {"type": "number", "description": "客队赔率"},
                },
                "required": ["home_team", "away_team", "odds_home", "odds_draw", "odds_away"],
            },
            handler=self._llm_dynamic_six_layer,
            category="ai_analysis",
            tags=["ai", "llm", "six_layer", "analysis"],
        ))

        self.register_tool(MCPTool(
            name="llm_generate_strategy",
            description="LLM自动生成策略 - 分析历史数据自动发现模式并生成策略",
            input_schema={
                "type": "object",
                "properties": {
                    "league": {"type": "string", "description": "联赛代码", "default": "E0"},
                    "matches_count": {"type": "integer", "description": "分析比赛数量", "default": 100},
                    "target_roi": {"type": "number", "description": "目标ROI%", "default": 5.0},
                },
            },
            handler=self._llm_generate_strategy,
            category="ai_strategy",
            tags=["ai", "llm", "strategy", "generate"],
        ))

    def register_tool(self, tool: MCPTool) -> None:
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool: {tool.name}")

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")

        tool.usage_count += 1
        tool.last_used = datetime.now()

        try:
            import asyncio
            import inspect

            handler = tool.handler
            if inspect.iscoroutinefunction(handler):
                result = await handler(**arguments)
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: handler(**arguments)
                )
            tool.success_count += 1
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Tool '{name}' failed: {e}")
            return {"success": False, "error": str(e)}

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "category": tool.category,
                "tags": tool.tags,
            }
            for tool in self.tools.values()
        ]

    def get_tool_stats(self) -> Dict[str, Any]:
        return {
            "total_tools": len(self.tools),
            "total_usage": sum(t.usage_count for t in self.tools.values()),
            "categories": list(set(t.category for t in self.tools.values())),
            "tools": [
                {
                    "name": t.name,
                    "usage_count": t.usage_count,
                    "success_rate": (
                        t.success_count / t.usage_count
                        if t.usage_count > 0
                        else 0
                    ),
                    "last_used": (
                        t.last_used.isoformat() if t.last_used else None
                    ),
                }
                for t in self.tools.values()
            ],
        }

    def _get_match_data(
        self, match_id: str, include_live: bool = False
    ) -> Dict:
        return DATA_SOURCE_MANAGER.fetch_match_data(match_id)  # type: ignore[attr-defined,no-any-return]

    def _get_odds(self, match_id: str, bookmaker: str = "all") -> Dict:
        return DATA_SOURCE_MANAGER.fetch_odds(match_id)  # type: ignore[attr-defined,no-any-return]

    def _get_team_stats(self, team_id: str, season: int = 2025) -> Dict:
        cache_key = f"team_{team_id}_{season}"
        cached = DATA_SOURCE_MANAGER.cache.get(cache_key)
        if cached:
            return cached  # type: ignore[no-any-return]

        return {"team_id": team_id, "season": season, "stats": {}}

    def _search_memory(self, query: str, limit: int = 5) -> Dict:
        from ...afa_v9.memory import MEMORY_INSTANCE
        results = MEMORY_INSTANCE.search_memory(query)
        return {"query": query, "results": results[:limit]}

    def _get_cache_status(self) -> Dict:
        return DATA_SOURCE_MANAGER.get_stats()  # type: ignore[attr-defined,no-any-return]

    def _query_team_history(self, team_name: str, limit: int = 20) -> Dict:
        from ..historical_data import HISTORICAL_QUERY_SERVICE
        return {
            "team": team_name,
            "matches": HISTORICAL_QUERY_SERVICE.query_team_history(team_name, limit=limit)
        }

    def _query_league_matches(
        self, league_code: str, year: int = 2024, limit: int = 50
    ) -> Dict:
        from ..historical_data import HISTORICAL_QUERY_SERVICE
        return {
            "league": league_code,
            "year": year,
            "matches": HISTORICAL_QUERY_SERVICE.query_league_matches(
                league_code, year=year, limit=limit
            )
        }

    def _get_team_statistics(self, team_name: str) -> Dict:
        from ..historical_data import HISTORICAL_QUERY_SERVICE
        return HISTORICAL_QUERY_SERVICE.get_team_statistics(team_name)

    def _get_odds_statistics(self, league_code: str) -> Dict:
        from ..historical_data import HISTORICAL_QUERY_SERVICE
        return HISTORICAL_QUERY_SERVICE.get_odds_statistics(league_code)

    def _get_data_overview(self) -> Dict:
        from ..historical_data import HISTORICAL_QUERY_SERVICE
        return HISTORICAL_QUERY_SERVICE.get_data_overview()

    async def _browser_scrape(self, url: str, instruction: str) -> Dict:
        """
        使用浏览器自动化抓取网页数据

        支持:
        - 赔率网站 (500.com, Bet365, etc.)
        - 伤病报告
        - 阵容信息
        - 天气数据
        """
        try:
            from ...tools.odds.visual_browser import VisualBrowser
            import asyncio

            browser = VisualBrowser()

            full_instruction = f"""
            请执行以下任务:
            {instruction}

            目标URL: {url}

            请仔细浏览页面，提取相关信息，并以结构化方式返回结果。
            """

            result = await browser.extract_info(full_instruction)

            return {
                "url": url,
                "instruction": instruction,
                "result": result,
                "source": "visual_browser"
            }
        except Exception as e:
            logger.error(f"浏览器抓取失败: {e}")
            return {
                "url": url,
                "instruction": instruction,
                "error": str(e),
                "source": "fallback"
            }

    async def _search_web(self, query: str, source: str = "general") -> Dict:
        """
        搜索互联网获取比赛相关信息

        source类型:
        - odds: 赔率信息
        - injuries: 伤病情况
        - news: 球队新闻
        - general: 通用搜索
        """
        try:
            import requests
            from urllib.parse import quote

            search_urls = {
                "odds": [
                    "https://www.oddschecker.com/football",
                    "https://www.bet365.com",
                ],
                "injuries": [
                    "https://www.transfermarkt.com",
                    "https://www.bbc.com/sport/football",
                ],
                "news": [
                    "https://www.bbc.com/sport/football",
                    "https://www.skysports.com/football",
                ],
                "general": [
                    "https://www.google.com/search?q={}",
                ]
            }

            encoded_query = quote(query)
            urls_to_scrape = search_urls.get(source, search_urls["general"])[:1]

            results = []
            for base_url in urls_to_scrape:
                url = base_url.format(encoded_query) if "{}" in base_url else base_url

                try:
                    from ...tools.odds.visual_browser import VisualBrowser

                    browser = VisualBrowser()
                    instruction = f"搜索并提取关于 '{query}' 的相关信息，返回关键数据点"

                    result = await browser.extract_info(instruction)

                    results.append({
                        "url": url,
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "url": url,
                        "error": str(e)
                    })

            return {
                "query": query,
                "source_type": source,
                "results": results
            }
        except Exception as e:
            logger.error(f"网络搜索失败: {e}")
            return {
                "query": query,
                "source_type": source,
                "error": str(e)
            }

    async def _get_injury_report(self, team_name: str, use_browser: bool = True) -> Dict:
        """
        获取球队伤病报告和阵容信息

        数据来源优先级:
        1. Transfermarkt (最权威)
        2. 浏览器自动化搜索
        3. API数据
        """
        try:
            cache_key = f"injury:{team_name}"
            cached = DATA_SOURCE_MANAGER.cache.get(cache_key)
            if cached:
                return cached  # type: ignore[no-any-return]

            result: Dict[str, Any] = {
                "team": team_name,
                "injuries": [],
                "suspended": [],
                "doubtful": [],
                "source": []
            }

            if use_browser:
                try:
                    from ...tools.odds.visual_browser import VisualBrowser
                    import asyncio

                    browser = VisualBrowser()
                    instruction = f"""
                    访问 Transfermarkt 或其他足球网站，查找 {team_name} 的最新伤病情况。

                    请提取:
                    1. 受伤球员名单及伤情
                    2. 伤愈复出球员
                    3. 停赛球员
                    4. 存疑球员(上场存疑)

                    返回格式: 球员名 | 位置 | 伤情 | 预计复出时间
                    """

                    injury_text = await browser.extract_info(instruction)

                    result["injury_report_text"] = injury_text
                    result["source"].append("browser")  # type: ignore[attr-defined]

                    if injury_text and "Error" not in injury_text:
                        lines = injury_text.split('\n')
                        for line in lines:
                            if '|' in line:
                                parts = [p.strip() for p in line.split('|')]
                                if len(parts) >= 2:
                                    player_info = {
                                        "player": parts[0],
                                        "position": parts[1] if len(parts) > 1 else "Unknown",
                                        "status": parts[2] if len(parts) > 2 else "Unknown",
                                        "return_date": parts[3] if len(parts) > 3 else "Unknown"
                                    }

                                    if "out" in parts[2].lower() or "injured" in parts[2].lower():
                                        result["injuries"].append(player_info)  # type: ignore[attr-defined]
                                    elif "suspended" in parts[2].lower():
                                        result["suspended"].append(player_info)  # type: ignore[attr-defined]
                                    elif "doubtful" in parts[2].lower():
                                        result["doubtful"].append(player_info)  # type: ignore[attr-defined]

                except Exception as e:
                    logger.warning(f"浏览器获取伤病失败: {e}")
                    result["browser_error"] = str(e)

            result["timestamp"] = datetime.now().isoformat()
            DATA_SOURCE_MANAGER.cache.set(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"伤病报告获取失败: {e}")
            return {
                "team": team_name,
                "error": str(e)
            }

    async def _get_live_odds(
        self,
        home_team: str,
        away_team: str,
        source: str = "auto"
    ) -> Dict:
        """
        获取实时赔率

        source选项:
        - api: 优先使用API
        - browser: 优先使用浏览器
        - auto: 自动选择（推荐）

        返回数据包含:
        - 胜平负赔率 (H2H)
        - 亚洲盘口
        - 大小球
        - 多个博彩公司对比
        """
        try:
            cache_key = f"live_odds:{home_team}:{away_team}:{source}"
            cached = DATA_SOURCE_MANAGER.cache.get(cache_key)
            if cached:
                return cached  # type: ignore[no-any-return]

            result: Dict[str, Any] = {
                "match": f"{home_team} vs {away_team}",
                "h2h": {},      # 胜平负
                "asian_handicap": {},  # 亚洲盘口
                "over_under": {},      # 大小球
                "bookmakers": [],
                "source": [],
                "timestamp": datetime.now().isoformat()
            }

            if source in ["api", "auto"]:
                api_odds = self._fetch_odds_from_api(home_team, away_team)
                if api_odds and not api_odds.get("error"):
                    result["h2h"] = api_odds.get("h2h", {})
                    result["bookmakers"] = api_odds.get("bookmakers", [])
                    result["source"].append("api")  # type: ignore[attr-defined]
                    if source == "api":
                        DATA_SOURCE_MANAGER.cache.set(cache_key, result)
                        return result

            if source in ["browser", "auto"]:
                browser_odds = await self._fetch_odds_from_browser(home_team, away_team)
                if browser_odds and not browser_odds.get("error"):
                    result["h2h"].update(browser_odds.get("h2h", {}))  # type: ignore[attr-defined]
                    result["asian_handicap"] = browser_odds.get("asian_handicap", {})
                    result["over_under"] = browser_odds.get("over_under", {})
                    result["source"].append("browser")  # type: ignore[attr-defined]

            if not result["source"]:
                result["error"] = "所有数据源均不可用"
                result["source"] = ["none"]

            DATA_SOURCE_MANAGER.cache.set(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"实时赔率获取失败: {e}")
            return {
                "match": f"{home_team} vs {away_team}",
                "error": str(e)
            }

    def _fetch_odds_from_api(self, home_team: str, away_team: str) -> Optional[Dict]:
        """从API获取赔率"""
        try:
            from ...tools.odds.global_odds_fetcher import get_global_arbitrage_data

            league_map = {
                "EPL": "英超", "Premier League": "英超",
                "La Liga": "西甲", "西甲": "西甲",
                "Serie A": "意甲", "意甲": "意甲",
                "Bundesliga": "德甲", "德甲": "德甲",
                "Ligue 1": "法甲", "法甲": "法甲",
            }

            league = "EPL"
            for key, value in league_map.items():
                if key.lower() in home_team.lower() or key.lower() in away_team.lower():
                    league = value
                    break

            raw_result = get_global_arbitrage_data(league, home_team, away_team)

            import json
            data = json.loads(raw_result) if isinstance(raw_result, str) else raw_result

            if "error" in data:
                return data  # type: ignore[no-any-return]

            pinnacle = data.get("pinnacle_home_odds")
            betfair = data.get("betfair_home_odds")
            bookmaker_count = data.get("bookmaker_count", 0)

            return {
                "h2h": {
                    "pinnacle": pinnacle,
                    "betfair": betfair,
                    "bookmaker_count": bookmaker_count
                },
                "bookmakers": data.get("global_bookmaker_odds_list", [])
            }

        except Exception as e:
            logger.warning(f"API赔率获取失败: {e}")
            return None

    async def _fetch_odds_from_browser(self, home_team: str, away_team: str) -> Optional[Dict]:
        """使用浏览器获取赔率"""
        try:
            from ...tools.odds.visual_browser import VisualBrowser

            browser = VisualBrowser()

            instruction = f"""
            请访问多个博彩网站（如Bet365, 888sport, William Hill等），
            搜索并提取以下比赛的赔率信息:

            比赛: {home_team} vs {away_team}

            请提取以下数据并以结构化JSON格式返回:

            1. 胜平负赔率 (H2H):
               - 主队胜 (Home)
               - 平局 (Draw)
               - 客队胜 (Away)

            2. 亚洲盘口 (Asian Handicap):
               - 盘口类型 (如 -0.5, -1, +0.5 等)
               - 主队盘口赔率
               - 客队盘口赔率

            3. 大小球 (Over/Under):
               - 盘口类型 (如 2.5, 3, 3.5 等)
               - 大球赔率
               - 小球赔率

            如果某个博彩公司没有特定盘口，请标注为null。
            """

            result_text = await browser.extract_info(instruction)

            parsed = self._parse_odds_text(result_text)
            return parsed

        except Exception as e:
            logger.warning(f"浏览器赔率获取失败: {e}")
            return None

    def _parse_odds_text(self, text: str) -> Dict:
        """解析赔率文本为结构化数据"""
        result = {
            "h2h": {},
            "asian_handicap": {},
            "over_under": {},
            "raw_text": text
        }

        lines = text.split('\n')
        current_section = None

        for line in lines:
            line_lower = line.lower().strip()

            if 'h2h' in line_lower or '胜平负' in line or '1x2' in line_lower:
                current_section = 'h2h'
                continue
            elif 'asian' in line_lower or '盘口' in line or 'handicap' in line_lower:
                current_section = 'asian_handicap'
                continue
            elif 'over' in line_lower or 'under' in line_lower or '大小球' in line:
                current_section = 'over_under'
                continue

            if current_section and line.strip():
                parts = line.split()
                for part in parts:
                    try:
                        val = float(part)
                        if 1.0 < val < 20.0:
                            if current_section == 'h2h':
                                if 'home' not in result[current_section]:
                                    result[current_section]['home'] = val  # type: ignore[index]
                                elif 'draw' not in result[current_section]:
                                    result[current_section]['draw'] = val  # type: ignore[index]
                                elif 'away' not in result[current_section]:
                                    result[current_section]['away'] = val  # type: ignore[index]
                            else:
                                key = f"odds_{len(result[current_section])}"
                                result[current_section][key] = val  # type: ignore[index]
                    except ValueError:
                        continue

        return result

    async def _get_live_match_data(
        self,
        home_team: str,
        away_team: str,
        league: str = "EPL"
    ) -> Dict:
        """
        获取比赛实时数据（阵容、伤病、天气、进球等）

        使用浏览器自动化 + API 组合获取
        """
        try:
            cache_key = f"live_match:{home_team}:{away_team}:{league}"
            cached = DATA_SOURCE_MANAGER.cache.get(cache_key, max_age=300)
            if cached:
                return cached  # type: ignore[no-any-return]

            result = {
                "match": f"{home_team} vs {away_team}",
                "league": league,
                "lineups": {"home": {}, "away": {}},
                "injuries": {"home": [], "away": []},
                "weather": {},
                "score": {},
                "source": []
            }

            try:
                from ...tools.odds.visual_browser import VisualBrowser
                import asyncio

                browser = VisualBrowser()
                instruction = f"""
                请访问足球数据网站（如WhoScored, Transfermarkt, SofaScore等），
                获取以下比赛的详细实时数据:

                比赛: {home_team} vs {away_team}
                联赛: {league}

                请提取以下信息并以结构化方式返回:

                1. 比赛比分 (如 2-1)
                2. 比赛状态 (进行中/已结束/未开始)
                3. 主队阵容 (首发11人)
                4. 客队阵容 (首发11人)
                5. 主队伤病名单
                6. 客队伤病名单
                7. 进球球员和时间
                8. 黄红牌信息
                9. 比赛场地天气

                返回格式尽量使用结构化数据。
                """

                match_data = await browser.extract_info(instruction)

                result["raw_data"] = match_data
                result["source"].append("browser")  # type: ignore[attr-defined]

            except Exception as e:
                logger.warning(f"浏览器获取比赛数据失败: {e}")
                result["browser_error"] = str(e)

            DATA_SOURCE_MANAGER.cache.set(cache_key, result, ttl=300)
            return result

        except Exception as e:
            logger.error(f"获取比赛实时数据失败: {e}")
            return {
                "match": f"{home_team} vs {away_team}",
                "error": str(e)
            }

    async def _get_weather(self, venue: str, date: str = "") -> Dict:
        """
        获取比赛场地天气信息

        使用天气API或浏览器自动化
        """
        try:
            cache_key = f"weather:{venue}:{date}"
            cached = DATA_SOURCE_MANAGER.cache.get(cache_key, max_age=3600)
            if cached:
                return cached  # type: ignore[no-any-return]

            result: Dict[str, Any] = {
                "venue": venue,
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "temperature": None,
                "condition": None,
                "humidity": None,
                "wind": None,
                "source": []
            }

            try:
                from ...afa_v9.data_sources.weather_sources import OpenWeatherMapSource
                from ...afa_v9.data_sources.config import DATA_SOURCE_CONFIG

                venue_to_city = {
                    "Emirates": "London",
                    "Anfield": "Liverpool",
                    "Old": "Manchester",
                    "Stamford": "London",
                    "Etihad": "Manchester",
                    "Old Trafford": "Manchester",
                    "Tottenham": "London",
                    "Wembley": "London",
                    "Stamford Bridge": "London",
                    "Camp Nou": "Barcelona",
                    "Santiago": "Madrid",
                    "Allianz": "Munich",
                    "Juventus": "Turin",
                    "Parc": "Paris",
                    "San": "Milan",
                    "Warner": "London",
                    "Stadium": "London",
                    "Villa": "Birmingham",
                    "Goodison": "Liverpool",
                    "King": "London",
                    "Molineux": "Wolverhampton",
                    "Elland": "Leeds",
                    "Vicarage": "Watford",
                    "St Mary's": "Southampton",
                    "Vitality": "Bournemouth",
                }

                city = venue_to_city.get(venue.split()[0], venue.split(',')[0])
                weather_source = OpenWeatherMapSource(
                    api_key=DATA_SOURCE_CONFIG.OPENWEATHERMAP_API_KEY,
                    base_url=DATA_SOURCE_CONFIG.OPENWEATHERMAP_BASE_URL
                )

                weather = weather_source.get_current_weather(city)
                if weather and isinstance(weather, dict) and "main" in weather:
                    result["temperature"] = weather.get("main", {}).get("temp")
                    result["humidity"] = weather.get("main", {}).get("humidity")
                    result["condition"] = weather.get("weather", [{}])[0].get("description") if weather.get("weather") else None
                    result["wind"] = weather.get("wind", {})
                    result["source"].append("api")  # type: ignore[union-attr]

            except Exception as e:
                logger.warning(f"API天气获取失败: {e}")

            if not result["source"]:
                try:
                    from ...tools.odds.visual_browser import VisualBrowser
                    import asyncio

                    browser = VisualBrowser()
                    instruction = f"搜索并获取 {venue} 的当前天气情况，包括温度、天气状况、湿度、风速等"

                    weather_text = await browser.extract_info(instruction)

                    result["raw_weather"] = weather_text
                    result["source"].append("browser")  # type: ignore[union-attr]

                except Exception as e:
                    logger.warning(f"浏览器天气获取失败: {e}")

            DATA_SOURCE_MANAGER.cache.set(cache_key, result, ttl=3600)
            return result

        except Exception as e:
            logger.error(f"获取天气信息失败: {e}")
            return {
                "venue": venue,
                "error": str(e)
            }

    def _get_bet_status(self, period: str = "daily") -> Dict:
        """
        获取投注状态和追踪信息
        """
        try:
            from ...afa_v9.execution import RESULT_TRACKER, BANKROLL_MANAGER

            tracker = RESULT_TRACKER

            if period == "daily":
                summary = tracker.get_daily_summary()
            elif period == "weekly":
                summary = tracker.get_weekly_summary()
            elif period == "monthly":
                summary = tracker.get_monthly_summary()  # type: ignore[attr-defined]
            else:
                summary = tracker.get_overall_performance()  # type: ignore[attr-defined]

            bankroll_stats = BANKROLL_MANAGER.get_stats()  # type: ignore[attr-defined]

            return {
                "period": period,
                "bet_summary": summary,
                "bankroll": {
                    "balance": bankroll_stats["balance"],
                    "total_profit": bankroll_stats["total_profit"],
                    "roi": bankroll_stats["roi"],
                    "win_rate": bankroll_stats["win_rate"],
                },
                "pending_bets": len(tracker.recorder.get_pending_bets()),
            }

        except Exception as e:
            logger.error(f"获取投注状态失败: {e}")
            return {
                "period": period,
                "error": str(e)
            }

    def _calculate_stake(
        self,
        odds: float,
        probability: float,
        confidence: float = 1.0
    ) -> Dict:
        """
        计算投注金额（基于Kelly公式）

        参数:
        - odds: 赔率
        - probability: 预测概率 (0-1)
        - confidence: 置信度 (0-1)
        """
        try:
            from ...afa_v9.execution import BANKROLL_MANAGER
            from ...calculations.pro.kelly_criterion import EnhancedKellyCriterion as KellyCriterion  # type: ignore[attr-defined]

            if odds < 1.01:
                return {
                    "odds": odds,
                    "probability": probability,
                    "error": "赔率过低"
                }

            implied_prob = 1 / odds
            value_edge = probability - implied_prob

            if value_edge <= 0:
                return {
                    "odds": odds,
                    "probability": probability,
                    "implied_probability": implied_prob,
                    "value_edge": value_edge,
                    "recommendation": "不建议投注",
                    "reason": "预测概率 <= 隐含概率，无价值"
                }

            kelly = KellyCriterion(initial_capital=BANKROLL_MANAGER.balance)
            kelly_bet = kelly.calculate_kelly_bet(probability, odds, confidence)

            adjusted_fraction = kelly_bet.kelly_fraction * BANKROLL_MANAGER.config.kelly_multiplier
            stake = BANKROLL_MANAGER.balance * adjusted_fraction
            stake = min(stake, BANKROLL_MANAGER.balance * BANKROLL_MANAGER.config.max_stake_percentage)
            stake = max(stake, BANKROLL_MANAGER.config.min_stake)

            expected_value = (probability * (odds - 1)) - ((1 - probability) * 1)
            roi = expected_value * 100

            return {
                "odds": odds,
                "probability": probability,
                "implied_probability": round(implied_prob, 4),
                "value_edge": round(value_edge, 4),
                "kelly_fraction": round(kelly_bet.kelly_fraction, 4),
                "adjusted_fraction": round(adjusted_fraction, 4),
                "recommended_stake": round(stake, 2),
                "expected_value": round(expected_value, 4),
                "expected_roi": round(roi, 2),
                "confidence": confidence,
                "recommendation": "可以投注" if value_edge > 0.02 else "谨慎投注",
                "current_balance": BANKROLL_MANAGER.balance
            }

        except Exception as e:
            logger.error(f"计算投注金额失败: {e}")
            return {
                "odds": odds,
                "probability": probability,
                "error": str(e)
            }

    def _record_bet(
        self,
        match_id: str,
        home_team: str,
        away_team: str,
        selection: str,
        odds: float,
        stake: float,
        kelly_fraction: float = 0.1,
        confidence: float = 0.8
    ) -> Dict:
        """
        记录投注到系统

        包含风险检查和资金验证
        """
        try:
            from ...afa_v9.execution import EXECUTION_ENGINE

            result = EXECUTION_ENGINE.execute_bet(  # type: ignore[call-arg]
                match_id=match_id,
                home_team=home_team,
                away_team=away_team,
                market="h2h",
                selection=selection,
                odds=odds,
                kelly_fraction=kelly_fraction,
                confidence=confidence,
            )

            return {
                "success": result.success,
                "bet_id": result.bet_id,
                "message": result.message,
                "stake": result.stake,
                "odds": result.odds,
                "new_balance": result.new_balance,
                "risk_assessment": result.risk_assessment
            }

        except Exception as e:
            logger.error(f"记录投注失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _settle_bet(self, bet_id: str, won: bool) -> Dict:
        """
        结算投注（标记为赢或输）

        会自动更新资金和统计
        """
        try:
            from ...afa_v9.execution import EXECUTION_ENGINE

            result = EXECUTION_ENGINE.settle_bet(bet_id, won)  # type: ignore[attr-defined]

            return result  # type: ignore[no-any-return]

        except Exception as e:
            logger.error(f"结算投注失败: {e}")
            return {
                "success": False,
                "bet_id": bet_id,
                "error": str(e)
            }

    def _get_bet_history(
        self,
        limit: int = 20,
        status: str = "all"
    ) -> Dict:
        """
        获取投注历史记录

        status: pending, won, lost, all
        """
        try:
            from ...afa_v9.execution import BET_RECORDER, BetStatus

            records = BET_RECORDER.get_recent_bets(count=limit * 2)

            if status != "all":
                status_map = {
                    "pending": BetStatus.PENDING,
                    "won": BetStatus.WON,
                    "lost": BetStatus.LOST,
                }
                target_status = status_map.get(status)
                if target_status:
                    records = [r for r in records if r.status == target_status]

            records = records[:limit]

            return {
                "total": len(records),
                "bets": [
                    {
                        "bet_id": r.bet_id,
                        "match": f"{r.home_team} vs {r.away_team}",
                        "selection": r.selection,
                        "odds": r.odds,
                        "stake": r.stake,
                        "profit": r.profit,
                        "status": r.status.value,
                        "created_at": r.created_at.isoformat(),
                        "settled_at": r.settled_at.isoformat() if r.settled_at else None,
                    }
                    for r in records
                ]
            }

        except Exception as e:
            logger.error(f"获取投注历史失败: {e}")
            return {
                "total": 0,
                "bets": [],
                "error": str(e)
            }

    def _backtest_strategy(
        self,
        strategy_name: str = "poisson_value",
        league_code: str = "all",
        year: int = 2024,
        use_kelly: bool = True,
        value_threshold: float = 0.03
    ) -> Dict:
        """
        使用历史数据回测投注策略

        支持的策略:
        - poisson_value: Poisson模型价值投注
        - six_layer: 六层分析策略
        - simple_favorite: 简单热门策略
        """
        try:
            from ...calculations.pro.strategy_backtest import StrategyTester
            from ...core.historical_data import HISTORICAL_QUERY_SERVICE

            league_map = {
                "all": None,
                "E0": "E0", "英超": "E0", "Premier League": "E0",
                "D1": "D1", "德甲": "D1", "Bundesliga": "D1",
                "SP1": "SP1", "西甲": "SP1", "La Liga": "SP1",
                "I1": "I1", "意甲": "I1", "Serie A": "I1",
                "F1": "F1", "法甲": "F1", "Ligue 1": "F1",
            }
            query_league = league_map.get(league_code, None)

            matches = HISTORICAL_QUERY_SERVICE.query_league_matches(
                query_league or "E0", year=year, limit=500
            )

            if not matches:
                return {
                    "strategy": strategy_name,
                    "error": f"未找到{league_code} {year}年的比赛数据"
                }

            from ...calculations.pro.poisson_model import EnhancedPoissonGoalModel as PoissonGoalModel  # type: ignore[attr-defined]
            poisson_model = PoissonGoalModel()

            for m in matches[:50]:
                if hasattr(m, 'home_team') and hasattr(m, 'away_team'):
                    poisson_model.update_team_stats(m.home_team, m.away_team, m.home_goals, m.away_goals)  # type: ignore[attr-defined]

            tester = StrategyTester(initial_capital=10000)
            result = tester.backtest_strategy(
                strategy_name=strategy_name,
                matches=matches,
                poisson_model=poisson_model,
                use_kelly=use_kelly,
                value_threshold=value_threshold
            )

            return {
                "strategy": result.strategy_name,
                "total_bets": result.total_bets,
                "wins": result.wins,
                "losses": result.losses,
                "win_rate": f"{result.win_rate:.2f}%",
                "total_stake": result.total_stake,
                "net_profit": result.net_profit,
                "roi": f"{result.roi:.2f}%",
                "max_drawdown": f"{result.max_drawdown:.2f}%",
                "sharpe_ratio": f"{result.sharpe_ratio:.3f}",
                "profit_factor": f"{result.profit_factor:.2f}" if result.profit_factor != float('inf') else "∞",
                "league_performance": result.league_performance,
            }

        except Exception as e:
            logger.error(f"策略回测失败: {e}")
            return {
                "strategy": strategy_name,
                "error": str(e)
            }

    def _compare_strategies(
        self,
        league_code: str = "all",
        year: int = 2024
    ) -> Dict:
        """
        比较多个策略的回测表现
        """
        try:
            from ...calculations.pro.strategy_backtest import StrategyTester
            from ...calculations.pro.poisson_model import PoissonGoalModel
            from ...core.historical_data import HISTORICAL_QUERY_SERVICE

            league_map = {
                "all": "E0",
                "E0": "E0", "英超": "E0",
                "D1": "D1", "德甲": "D1",
                "SP1": "SP1", "西甲": "SP1",
                "I1": "I1", "意甲": "I1",
                "F1": "F1", "法甲": "F1",
            }
            query_league = league_map.get(league_code, "E0")

            matches = HISTORICAL_QUERY_SERVICE.query_league_matches(
                query_league, year=year, limit=500
            )

            if not matches:
                return {
                    "error": f"未找到{league_code} {year}年的比赛数据"
                }

            poisson_model = PoissonGoalModel()
            for m in matches[:50]:
                if hasattr(m, 'home_team') and hasattr(m, 'away_team'):
                    poisson_model.update_team_stats(m.home_team, m.away_team, m.home_goals, m.away_goals)  # type: ignore[attr-defined]

            tester = StrategyTester(initial_capital=10000)
            results = tester.compare_strategies(matches, poisson_model)

            comparison = {
                "league": query_league,
                "year": year,
                "total_matches_tested": len(matches),
                "strategies": {}
            }

            for name, result in results.items():
                comparison["strategies"][name] = {
                    "total_bets": result.total_bets,
                    "win_rate": f"{result.win_rate:.2f}%",
                    "roi": f"{result.roi:.2f}%",
                    "net_profit": result.net_profit,
                    "max_drawdown": f"{result.max_drawdown:.2f}%",
                    "sharpe_ratio": f"{result.sharpe_ratio:.3f}",
                }

            best_strategy = max(
                results.keys(),
                key=lambda x: results[x].roi
            )
            comparison["recommendation"] = {
                "best_strategy": best_strategy,
                "best_roi": f"{results[best_strategy].roi:.2f}%"
            }

            return comparison

        except Exception as e:
            logger.error(f"策略比较失败: {e}")
            return {
                "error": str(e)
            }

    def _llm_full_analysis(
        self,
        home_team: str,
        away_team: str,
        odds_home: float,
        odds_draw: float,
        odds_away: float,
        league: str = "EPL"
    ) -> Dict:
        """AI完整分析"""
        try:
            from ...afa_v9.ai_augmented.mcp_tools import llm_full_analysis

            return llm_full_analysis(
                home_team=home_team,
                away_team=away_team,
                odds_home=odds_home,
                odds_draw=odds_draw,
                odds_away=odds_away,
                league=league,
            )

        except Exception as e:
            logger.error(f"AI完整分析失败: {e}")
            return {"success": False, "error": str(e)}

    def _llm_betting_decision(
        self,
        home_team: str,
        away_team: str,
        odds_home: float,
        odds_draw: float,
        odds_away: float,
        market_sentiment: str = "",
        news_impact: str = ""
    ) -> Dict:
        """LLM投注决策"""
        try:
            from ...afa_v9.ai_augmented import LLMBettingDecider
            from ...afa_v9.ai_augmented.augmented_modules import LLMDecisionContext

            decider = LLMBettingDecider()

            context = LLMDecisionContext(
                match_info={"home_team": home_team, "away_team": away_team},
                odds_data={"home_odds": odds_home, "draw_odds": odds_draw, "away_odds": odds_away},
                analysis_results={},
                bankroll_status={},
                market_sentiment=market_sentiment,
                news_impact=news_impact,
            )

            result = decider.decide(context)
            return {"success": True, "decision": result}

        except Exception as e:
            logger.error(f"LLM投注决策失败: {e}")
            return {"success": False, "error": str(e)}

    def _llm_dynamic_kelly(
        self,
        odds: float,
        probability: float,
        confidence: float = 0.8
    ) -> Dict:
        """LLM动态Kelly计算"""
        try:
            from ...afa_v9.ai_augmented import LLM_DYNAMIC_KELLY

            result = LLM_DYNAMIC_KELLY.calculate(
                odds=odds,
                predicted_prob=probability,
                confidence=confidence,
                context=None,
            )

            return {"success": True, **result}

        except Exception as e:
            logger.error(f"LLM动态Kelly失败: {e}")
            return {"success": False, "error": str(e)}

    def _llm_dynamic_six_layer(
        self,
        home_team: str,
        away_team: str,
        odds_home: float,
        odds_draw: float,
        odds_away: float
    ) -> Dict:
        """LLM动态六层分析"""
        try:
            from ...afa_v9.ai_augmented import LLM_SIX_LAYER

            match_data = {
                "home_team": home_team,
                "away_team": away_team,
                "odds": {"home": odds_home, "draw": odds_draw, "away": odds_away}
            }

            result = LLM_SIX_LAYER.analyze(match_data, None)
            return {"success": True, **result}

        except Exception as e:
            logger.error(f"LLM动态六层分析失败: {e}")
            return {"success": False, "error": str(e)}

    def _llm_generate_strategy(
        self,
        league: str = "E0",
        matches_count: int = 100,
        target_roi: float = 5.0
    ) -> Dict:
        """LLM自动生成策略"""
        try:
            from ...afa_v9.ai_augmented import LLMStrategyGenerator

            generator = LLMStrategyGenerator()

            result = generator.generate_strategy(
                historical_data=[],
                target_league=league,
                constraints={"target_roi": target_roi}
            )

            return {"success": True, **result}

        except Exception as e:
            logger.error(f"LLM策略生成失败: {e}")
            return {"success": False, "error": str(e)}


MCP_SERVER = MCPServer()
