"""
历史数据Agent MixIn
==================

让Agent能够主动调用历史数据

使用方式:
    class ScoutAgent(Agent, HistoricalAgentMixin):
        def __init__(self):
            super().__init__(...)
            self._init_historical()

        def execute(self, state):
            # 查询球队历史
            history = self.query_team_history("Manchester City")
            odds = self.get_odds_statistics("E0")
            # ... 执行逻辑
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HistoricalAgentMixin:
    """
    历史数据查询能力Mixin

    为Agent提供便捷的历史数据访问方法
    """

    _shared_initialized: bool = False
    _shared_query_service: Optional[Any] = None
    _shared_analyzer: Optional[Any] = None
    _historical_initialized: bool = False
    _query_service: Optional[Any] = None
    _analyzer: Optional[Any] = None

    def _init_historical(self) -> None:
        """初始化历史数据服务"""
        if hasattr(self, '_historical_initialized') and self._historical_initialized:
            self._query_service = HistoricalAgentMixin._shared_query_service
            self._analyzer = HistoricalAgentMixin._shared_analyzer
            return

        try:
            from src.core.historical_data.query_service import HistoricalQueryService
            from src.core.historical_data.analytics import HistoricalDataAnalyzer

            query_service = HistoricalQueryService()
            analyzer = HistoricalDataAnalyzer()
            HistoricalAgentMixin._shared_query_service = query_service
            HistoricalAgentMixin._shared_analyzer = analyzer
            HistoricalAgentMixin._shared_initialized = True

            self._query_service = query_service
            self._analyzer = analyzer
            self._historical_initialized = True

            logger.info(f"历史数据服务已初始化")
        except Exception as e:
            logger.warning(f"历史数据服务初始化失败: {e}")
            self._query_service = None
            self._analyzer = None
            self._historical_initialized = False

    def query_team_history(
        self,
        team_name: str,
        limit: int = 20,
        home_only: bool = False,
        away_only: bool = False
    ) -> Dict[str, Any]:
        """
        查询球队历史比赛

        Args:
            team_name: 球队名称
            limit: 返回数量
            home_only: 只查主场比赛
            away_only: 只查客场比赛

        Returns:
            包含历史比赛记录的字典
        """
        self._init_historical()

        if not self._query_service:
            return {"error": "历史数据服务不可用"}

        try:
            matches = self._query_service.query_team_history(
                team_name=team_name,
                limit=limit,
                home_only=home_only,
                away_only=away_only
            )

            stats = self._query_service.get_team_statistics(team_name)

            return {
                "team": team_name,
                "total_matches": stats.get("total_matches", 0),
                "win_rate": stats.get("win_rate", 0),
                "recent_matches": matches
            }
        except Exception as e:
            logger.error(f"查询球队历史失败: {e}")
            return {"error": str(e)}

    def query_league_history(
        self,
        league_code: str,
        year: Optional[int] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        查询联赛历史比赛

        Args:
            league_code: 联赛代码 (E0=英超, D1=德甲, SP1=西甲等)
            year: 年份筛选
            limit: 返回数量

        Returns:
            联赛比赛记录
        """
        self._init_historical()

        if not self._query_service:
            return {"error": "历史数据服务不可用"}

        try:
            matches = self._query_service.query_league_matches(
                league_code=league_code,
                year=year,
                limit=limit
            )

            odds_stats = self._query_service.get_odds_statistics(league_code)

            return {
                "league": league_code,
                "total_matches": odds_stats.get("count", 0),
                "odds_stats": odds_stats,
                "recent_matches": matches
            }
        except Exception as e:
            logger.error(f"查询联赛历史失败: {e}")
            return {"error": str(e)}

    def get_league_odds_stats(self, league_code: str) -> Dict[str, Any]:
        """获取联赛赔率统计"""
        self._init_historical()

        if not self._query_service:
            return {"error": "历史数据服务不可用"}

        return self._query_service.get_odds_statistics(league_code)  # type: ignore[no-any-return]

    def get_team_stats(self, team_name: str) -> Dict[str, Any]:
        """获取球队详细统计"""
        self._init_historical()

        if not self._query_service:
            return {"error": "历史数据服务不可用"}

        return self._query_service.get_team_statistics(team_name)  # type: ignore[no-any-return]

    def search_similar_matches(
        self,
        query: str,
        top_k: int = 10,
        league: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        语义搜索相似比赛

        Args:
            query: 自然语言查询 (如 "高比分英超比赛")
            top_k: 返回数量
            league: 联赛筛选

        Returns:
            相似比赛列表
        """
        self._init_historical()

        if not self._query_service:
            return []

        try:
            return self._query_service.search_similar(  # type: ignore[no-any-return]
                query=query,
                top_k=top_k,
                league=league
            )
        except Exception as e:
            logger.error(f"搜索相似比赛失败: {e}")
            return []

    def analyze_league_value(self, league_code: str) -> Dict[str, Any]:
        """
        分析联赛价值

        Returns:
            包含赔率价值和发现机会的字典
        """
        self._init_historical()

        if not self._analyzer:
            return {"error": "分析器不可用"}

        try:
            matches = self._query_service.query_league_matches(
                league_code=league_code,
                limit=1000
            ) if self._query_service else []

            odds_stats = self._query_service.get_odds_statistics(league_code) if self._query_service else {}

            return {
                "league": league_code,
                "total_matches": len(matches),
                "odds_distribution": odds_stats,
                "recommendation": self._generate_value_recommendation(odds_stats)
            }
        except Exception as e:
            logger.error(f"分析联赛价值失败: {e}")
            return {"error": str(e)}

    def _generate_value_recommendation(self, odds_stats: Dict) -> str:
        """生成价值推荐建议"""
        if not odds_stats or odds_stats.get("count", 0) == 0:
            return "数据不足，无法分析"

        avg_home_odds = odds_stats.get("home_odds", {}).get("avg", 0)
        implied_home_prob = 1 / avg_home_odds if avg_home_odds > 0 else 0

        if implied_home_prob > 0.5:
            return f"主队胜赔率偏低({avg_home_odds:.2f})，存在一定主队价值"
        elif implied_home_prob < 0.4:
            return f"主队胜赔率偏高({avg_home_odds:.2f})，客队可能有机会"
        else:
            return "赔率分布均衡，无明显价值倾向"

    def get_data_overview(self) -> Dict[str, Any]:
        """获取数据库概览"""
        self._init_historical()

        if not self._query_service:
            return {"error": "历史数据服务不可用"}

        return self._query_service.get_data_overview()  # type: ignore[no-any-return]

    def get_asian_handicap_value(self) -> Dict[str, Any]:
        """分析亚洲盘价值"""
        self._init_historical()

        if not self._analyzer:
            return {"error": "分析器不可用"}

        try:
            result = self._analyzer.analyze_asian_handicap()
            return {
                "data_count": result.get("count", 0),
                "avg_margin": result.get("avg_margin", 0),
                "implied_prob": result.get("implied_home_prob", 0),
                "actual_rate": result.get("actual_home_win_rate", 0),
                "value": result.get("value", 0),
                "interpretation": "亚洲盘庄家抽水3.7%，实际主队胜率低于预期-8.6%"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_over_under_value(self, line: float = 2.5) -> Dict[str, Any]:
        """分析大小球价值"""
        self._init_historical()

        if not self._analyzer:
            return {"error": "分析器不可用"}

        try:
            result = self._analyzer.analyze_over_under(line=line)
            return {
                "line": line,
                "data_count": result.get("count", 0),
                "implied_prob": result.get("implied_over_prob", 0),
                "actual_rate": result.get("actual_over_rate", 0),
                "value": result.get("value", 0),
            }
        except Exception as e:
            return {"error": str(e)}

    def get_half_time_insights(self) -> Dict[str, Any]:
        """获取半场分析洞察"""
        self._init_historical()

        if not self._analyzer:
            return {"error": "分析器不可用"}

        try:
            result = self._analyzer.get_half_time_stats()
            ht_results = result.get("ht_results", {})

            insights = []
            for key, data in ht_results.items():
                pct = data.get("pct", 0) * 100
                if pct > 40:
                    insights.append(f"{key}情况占比{pct:.1f}%，值得关注")

            return {
                "total": result.get("total", 0),
                "ht_distribution": ht_results,
                "insights": insights
            }
        except Exception as e:
            return {"error": str(e)}

    def get_match_context(
        self,
        home_team: str,
        away_team: str,
        league: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取比赛上下文信息

        综合两队历史交锋和各自表现
        """
        self._init_historical()

        if not self._query_service:
            return {"error": "历史数据服务不可用"}

        try:
            home_stats = self._query_service.get_team_statistics(home_team)
            away_stats = self._query_service.get_team_statistics(away_team)

            home_history = self._query_service.query_team_history(home_team, limit=10)
            away_history = self._query_service.query_team_history(away_team, limit=10)

            head_to_head = [
                m for m in home_history
                if m.get("home_team") == home_team and m.get("away_team") == away_team
                or m.get("home_team") == away_team and m.get("away_team") == home_team
            ]

            return {
                "home_team": {
                    "name": home_team,
                    "stats": home_stats,
                    "recent": home_history[:5]
                },
                "away_team": {
                    "name": away_team,
                    "stats": away_stats,
                    "recent": away_history[:5]
                },
                "head_to_head": head_to_head,
                "summary": self._generate_match_summary(home_stats, away_stats, head_to_head)
            }
        except Exception as e:
            return {"error": str(e)}

    def _generate_match_summary(
        self,
        home_stats: Dict,
        away_stats: Dict,
        h2h: List
    ) -> str:
        """生成比赛摘要"""
        home_wr = home_stats.get("win_rate", 0) * 100
        away_wr = away_stats.get("win_rate", 0) * 100
        home_matches = home_stats.get("total_matches", 0)
        away_matches = away_stats.get("total_matches", 0)

        summary = f"{home_stats.get('team', 'Home')}历史{home_matches}场胜率{home_wr:.1f}%"
        summary += f"，{away_stats.get('team', 'Away')}历史{away_matches}场胜率{away_wr:.1f}%"

        if h2h:
            summary += f"，两队历史交锋{len(h2h)}场"

        return summary
