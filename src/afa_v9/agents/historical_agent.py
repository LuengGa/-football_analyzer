"""
历史数据分析Agent
================

专门使用历史数据进行足球分析的Agent

使用方式:
    agent = HistoricalAnalystAgent()
    result = agent.execute({
        "task": "分析曼城 vs 利物浦的历史交锋",
        "home_team": "Manchester City",
        "away_team": "Liverpool",
        "league": "E0"
    })
"""

from typing import Dict, Any
from dataclasses import dataclass

from .base import Agent, AgentSoul, AgentBrain
from .historical_mixin import HistoricalAgentMixin


@dataclass
class HistoricalAnalystSoul:
    """历史分析师的灵魂"""
    name: str = "历史分析师"
    role: str = "历史数据分析专家"
    description: str = """
    专精于利用158,971场历史比赛数据进行分析。

    核心能力:
    1. 球队历史表现分析
    2. 联赛特征识别
    3. 赔率价值发现
    4. 相似比赛匹配
    5. 半场全场模式识别

    分析原则:
    - 一切分析基于数据
    - 量化而非直觉
    - 历史规律指导预测
    """


class HistoricalAnalystAgent(Agent, HistoricalAgentMixin):
    """
    历史数据分析Agent

    继承 Agent 的执行框架 + HistoricalAgentMixin 的数据查询能力
    """

    def __init__(self):
        soul = AgentSoul(
            name="历史分析师",
            role="历史数据分析专家",
            description=HistoricalAnalystSoul().description,
            personality={
                "style": "数据驱动",
                "confidence": "高",
                "verbosity": "详细"
            },
            goals=[
                "提供数据支撑的分析",
                "发现历史规律",
                "量化价值机会"
            ],
            values={
                "accuracy": "高精度",
                "transparency": "透明方法论"
            }
        )

        brain = AgentBrain(
            skills=[
                "league_analysis",      # 联赛分析
                "team_profiling",       # 球队画像
                "odds_evaluation",      # 赔率评估
                "pattern_recognition",  # 模式识别
                "value_detection"       # 价值发现
            ],
            rules=[
                "always_query_historical_data",
                "quantify_uncertainty",
                "cite_data_sources"
            ]
        )

        super().__init__(soul=soul, brain=brain)
        self._init_historical()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行分析任务

        Args:
            state: {
                "task": str,           # 分析任务
                "home_team": str,      # 主队
                "away_team": str,      # 客队
                "league": str,         # 联赛代码
                "analysis_type": str   # 分析类型
            }

        Returns:
            分析结果
        """
        task = state.get("task", "")
        home_team = state.get("home_team", "")
        away_team = state.get("away_team", "")
        league = state.get("league", "")
        analysis_type = state.get("analysis_type", "full")

        result = {
            "agent": self.soul.name,
            "task": task,
            "data_source": "158,971场历史比赛"
        }

        if analysis_type == "full" or analysis_type == "match_context":
            match_context = self.get_match_context(home_team, away_team, league)
            result["match_context"] = match_context

        if analysis_type == "full" or analysis_type == "league_analysis":
            if league:
                league_analysis = self.analyze_league_value(league)
                result["league_analysis"] = league_analysis

        if analysis_type == "full" or analysis_type == "value_analysis":
            asian_value = self.get_asian_handicap_value()
            ou_value = self.get_over_under_value()
            result["market_analysis"] = {
                "asian_handicap": asian_value,
                "over_under": ou_value
            }

        if analysis_type == "full" or analysis_type == "half_time":
            half_time = self.get_half_time_insights()
            result["half_time_pattern"] = half_time

        result["recommendation"] = self._generate_recommendation(result)

        return result

    def analyze_team(self, team_name: str) -> Dict[str, Any]:
        """
        分析单只球队

        Args:
            team_name: 球队名称

        Returns:
            球队分析报告
        """
        team_stats = self.get_team_stats(team_name)
        recent_matches = self.query_team_history(team_name, limit=10)

        home_history = self.query_team_history(team_name, limit=50, home_only=True)
        away_history = self.query_team_history(team_name, limit=50, away_only=True)

        home_form_data = home_history.get("recent_matches", []) if isinstance(home_history, dict) else []
        away_form_data = away_history.get("recent_matches", []) if isinstance(away_history, dict) else []

        return {
            "team": team_name,
            "overview": team_stats,
            "home_form": self._analyze_form(home_form_data),
            "away_form": self._analyze_form(away_form_data),
            "recent_matches": recent_matches
        }

    def compare_teams(self, team_a: str, team_b: str) -> Dict[str, Any]:
        """
        对比两只球队

        Args:
            team_a: 球队A
            team_b: 球队B

        Returns:
            对比分析报告
        """
        stats_a = self.get_team_stats(team_a)
        stats_b = self.get_team_stats(team_b)

        matches_a = self.query_team_history(team_a, limit=20)
        matches_b = self.query_team_history(team_b, limit=20)

        matches_a_data = matches_a.get("recent_matches", []) if isinstance(matches_a, dict) else []
        h2h = [
            m for m in matches_a_data
            if (isinstance(m, dict) and m.get("home_team") in [team_a, team_b]
                and m.get("away_team") in [team_a, team_b])
        ]

        return {
            "team_a": {"name": team_a, "stats": stats_a},
            "team_b": {"name": team_b, "stats": stats_b},
            "head_to_head": h2h,
            "comparison": self._compare_stats(stats_a, stats_b)
        }

    def find_similar_matches(
        self,
        description: str,
        league: str = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        查找相似比赛

        Args:
            description: 自然语言描述 (如 "高比分逆转")
            league: 联赛筛选
            limit: 返回数量

        Returns:
            相似比赛列表
        """
        matches = self.search_similar_matches(description, top_k=limit, league=league)

        return {
            "query": description,
            "league_filter": league,
            "matches_found": len(matches),
            "matches": matches
        }

    def _analyze_form(self, matches: list) -> Dict[str, Any]:
        """分析近期状态"""
        if not matches:
            return {"error": "无数据"}

        results = [m.get("result", "D") for m in matches]
        wins = results.count("H") + results.count("A") if matches else 0

        if isinstance(matches[0], dict):
            home_wins = sum(1 for m in matches if m.get("result") == "H")
            away_wins = sum(1 for m in matches if m.get("result") == "A")
        else:
            home_wins = sum(1 for m in matches if m.result == "H")
            away_wins = sum(1 for m in matches if m.result == "A")

        return {
            "matches_analyzed": len(matches),
            "home_wins": home_wins,
            "away_wins": away_wins,
            "draws": len(matches) - home_wins - away_wins,
            "win_rate": (home_wins + away_wins) / len(matches) if matches else 0
        }

    def _compare_stats(self, stats_a: Dict, stats_b: Dict) -> str:
        """生成对比摘要"""
        wr_a = stats_a.get("win_rate", 0) * 100
        wr_b = stats_b.get("win_rate", 0) * 100

        diff = wr_a - wr_b
        if abs(diff) < 2:
            return f"{stats_a['team']} vs {stats_b['team']} 胜率相近"
        elif diff > 0:
            return f"{stats_a['team']} 胜率更高 ({wr_a:.1f}% vs {wr_b:.1f}%)"
        else:
            return f"{stats_b['team']} 胜率更高 ({wr_b:.1f}% vs {wr_a:.1f}%)"

    def _generate_recommendation(self, analysis: Dict) -> str:
        """生成推荐建议"""
        recommendations = []

        if "market_analysis" in analysis:
            m = analysis["market_analysis"]
            if "asian_handicap" in m:
                ah = m["asian_handicap"]
                if ah.get("value", 0) < -0.05:
                    recommendations.append("⚠️ 亚洲盘主队价值偏低")
                elif ah.get("value", 0) > 0.02:
                    recommendations.append("✅ 亚洲盘主队存在价值机会")

            if "over_under" in m:
                ou = m["over_under"]
                if ou.get("value", 0) > 0.02:
                    recommendations.append(f"✅ 大球({ou.get('line', 2.5)})存在价值")

        if "match_context" in analysis:
            mc = analysis["match_context"]
            if "home_team" in mc and "away_team" in mc:
                home_wr = mc["home_team"]["stats"].get("win_rate", 0) * 100
                away_wr = mc["away_team"]["stats"].get("win_rate", 0) * 100
                recommendations.append(
                    f"📊 主队胜率{home_wr:.1f}% vs 客队胜率{away_wr:.1f}%"
                )

        return "\n".join(recommendations) if recommendations else "数据不足，无法生成建议"


class LeagueExpertAgent(Agent, HistoricalAgentMixin):
    """
    联赛专家Agent

    专门分析特定联赛的特征和价值
    """

    LEAGUE_NAMES = {
        "E0": "英格兰超级联赛",
        "SP1": "西班牙甲级联赛",
        "I1": "意大利甲级联赛",
        "D1": "德国甲级联赛",
        "F1": "法国甲级联赛",
        "N1": "荷兰甲级联赛",
        "T1": "土耳其超级联赛",
        "P1": "葡萄牙超级联赛",
    }

    def __init__(self, league_code: str = "E0"):
        self.league_code = league_code
        self.league_name = self.LEAGUE_NAMES.get(league_code, league_code)

        soul = AgentSoul(
            name=f"{self.league_name}专家",
            role=f"{self.league_name}数据分析",
            description=f"专精于分析{self.league_name}的历史数据和规律",
            personality={"style": "专业", "confidence": "高"},
            goals=[f"分析{self.league_name}特征", "发现联赛价值"],
            values={"accuracy": "高精度"}
        )

        brain = AgentBrain(
            skills=["league_analysis", "historical_patterns", "odds_evaluation"],
            rules=["基于数据", "量化分析"]
        )

        super().__init__(soul=soul, brain=brain)
        self._init_historical()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """分析联赛"""
        year = state.get("year")
        analysis_type = state.get("type", "full")

        result: Dict[str, Any] = {
            "agent": self.soul.name,
            "league": self.league_code,
            "league_name": self.league_name
        }

        league_data = self.query_league_history(self.league_code, year=year, limit=100)
        result["league_data"] = league_data

        value_analysis = self.analyze_league_value(self.league_code)
        result["value_analysis"] = value_analysis

        odds_stats = self.get_league_odds_stats(self.league_code)
        result["odds_distribution"] = odds_stats

        result["recommendation"] = self._generate_league_recommendation(odds_stats, value_analysis)

        return result

    def _generate_league_recommendation(self, odds: Dict, value: Dict) -> str:
        """生成联赛推荐"""
        if not odds or odds.get("count", 0) == 0:
            return "数据不足"

        avg_home = odds.get("home_odds", {}).get("avg", 0)
        implied = 1 / avg_home if avg_home > 0 else 0

        recommendations = []
        recommendations.append(f"主队隐含胜率: {implied:.1%}")
        recommendations.append(f"分析样本: {odds.get('count', 0)}场")

        return "\n".join(recommendations)
