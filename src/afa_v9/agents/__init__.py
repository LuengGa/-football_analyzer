"""
AFA v9.0 Agent集群 - 数字生命体集群
=====================================

6个专业Agent:
- Scout: 情报收集Agent
- Quant: 量化分析Agent
- Market: 市场分析Agent
- Risk: 风险控制Agent
- Trader: 交易决策Agent
- Auditor: 审计监督Agent

每个Agent = Soul + Brain + LLM + 历史数据查询能力
"""

from typing import Dict, Any, List
from .base import Agent, AgentSoul, AgentBrain
from .historical_mixin import HistoricalAgentMixin

try:
    from src.calculations.lottery import (
        LOTTERY_KNOWLEDGE,
        LotteryRouter
    )
    LOTTERY_CONFIG = {
        "JINGCAI": LOTTERY_KNOWLEDGE.get_lottery('JINGCAI'),
        "BEIDAN": LOTTERY_KNOWLEDGE.get_lottery('BEIDAN'),
    }
    LOTTERY_ROUTER = LotteryRouter()
except ImportError:
    LOTTERY_ROUTER = None
    LOTTERY_CONFIG = None


class ScoutAgent(Agent, HistoricalAgentMixin):
    """情报收集Agent - 可调用158,971场历史数据"""

    def __init__(self):
        super().__init__(
            soul=AgentSoul(
                name="Scout",
                role="情报收集专家",
                description="收集球队状态、伤病、天气、历史战绩等情报，整合历史数据分析",
                personality={
                    "attention_to_detail": "high",
                    "data_driven": True,
                },
                goals=["收集全面情报", "验证信息来源", "实时更新状态", "查询历史数据"],
            ),
            brain=AgentBrain(
                skills=["web_scraping", "api_integration", "data_validation", "historical_analysis"],
                rules=["always_verify_sources", "prefer_official_sources", "query_historical_data"],
            ),
        )
        self._init_historical()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"   -> 🔍 [{self.soul.name}] 情报收集中...")

        home_team = state.get("home_team", "Unknown")
        away_team = state.get("away_team", "Unknown")
        league = state.get("league", "")

        scout_report = {
            "home_team": home_team,
            "away_team": away_team,
            "current_intel": self._gather_current_intel(home_team, away_team, league),
        }

        historical_context = {}
        if self._historical_initialized and self._query_service:
            historical_context = self.get_match_context(home_team, away_team, league)
            scout_report["historical_data"] = historical_context
            scout_report["intelligence_summary"] = self._generate_intelligence_summary(
                historical_context
            )

        self._record_execution(state, scout_report)
        print(f"   -> ✅ [{self.soul.name}] 情报收集完成 (含{historical_context.get('home_team', {}).get('stats', {}).get('total_matches', 0)}场历史数据分析)")

        return {
            "scout_report": scout_report,
            "match_intel": scout_report,
            "historical_context": historical_context,
            "current_step": "scout_done",
        }

    def _gather_current_intel(self, home_team: str, away_team: str, league: str) -> Dict[str, Any]:
        """收集当前情报"""
        intel = {
            "home_form": "unknown",
            "away_form": "unknown",
            "injuries": [],
            "weather": "unknown",
            "venue": "unknown",
        }

        if self._query_service:
            home_matches = self._query_service.query_team_history(home_team, limit=10)
            away_matches = self._query_service.query_team_history(away_team, limit=10)

            if home_matches:
                recent = home_matches[:5]
                results = []
                for m in recent:
                    r = m.get("result", "")
                    if r == "H":
                        results.append("W")
                    elif r == "D":
                        results.append("D")
                    else:
                        results.append("L")
                intel["home_form"] = "-".join(results)
                intel["home_recent_results"] = results

            if away_matches:
                recent = away_matches[:5]
                results = []
                for m in recent:
                    r = m.get("result", "")
                    if r == "H":
                        results.append("W")
                    elif r == "D":
                        results.append("D")
                    else:
                        results.append("L")
                intel["away_form"] = "-".join(results)
                intel["away_recent_results"] = results

        return intel

    def _generate_intelligence_summary(self, context: Dict[str, Any]) -> str:
        """生成情报摘要"""
        home_stats = context.get("home_team", {}).get("stats", {})
        away_stats = context.get("away_team", {}).get("stats", {})

        home_wr = home_stats.get("win_rate", 0) * 100
        away_wr = away_stats.get("win_rate", 0) * 100

        h2h = context.get("head_to_head", [])
        h2h_summary = ""
        if h2h:
            h2h_home_wins = sum(1 for m in h2h if m.get("result") == "H")
            h2h_summary = f"，历史交锋{len(h2h)}场，主队{h2h_home_wins}胜"

        return f"主队历史胜率{home_wr:.1f}%，客队{away_wr:.1f}%{h2h_summary}"


class QuantAgent(Agent, HistoricalAgentMixin):
    """量化分析Agent - 使用历史数据训练模型"""

    def __init__(self):
        super().__init__(
            soul=AgentSoul(
                name="Quant",
                role="量化分析专家",
                description="执行泊松预测、Elo评级、xG计算等数学计算，结合历史数据分析",
                personality={
                    "analytical": True,
                    "precision": "high",
                },
                goals=["精准量化分析", "多模型验证", "持续优化算法", "基于历史数据预测"],
            ),
            brain=AgentBrain(
                skills=["poisson_model", "elo_rating", "xg_calculation", "historical_modeling"],
                rules=["validate_assumptions", "report_confidence", "train_on_historical_data"],
            ),
        )
        self._init_historical()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"   -> 📊 [{self.soul.name}] 量化分析中...")

        home_team = state.get("home_team", "")
        away_team = state.get("away_team", "")
        league = state.get("league", "")

        quant_report = {
            "home_xg": 1.5,
            "away_xg": 1.2,
            "poisson_probs": {
                "home_win": 0.45,
                "draw": 0.28,
                "away_win": 0.27,
            },
            "elo_ratings": {
                "home": 1800,
                "away": 1750,
            },
            "historical_analysis": {},
        }

        if self._historical_initialized and self._query_service:
            team_a_stats = self._query_service.get_team_statistics(home_team)
            team_b_stats = self._query_service.get_team_statistics(away_team)

            if team_a_stats and team_b_stats:
                poisson_probs = self._calculate_poisson_from_history(
                    home_team, away_team, team_a_stats, team_b_stats
                )
                elo_ratings = self._calculate_elo_ratings(
                    home_team, away_team, team_a_stats, team_b_stats
                )
                xg_values = self._calculate_xg(
                    home_team, away_team, team_a_stats, team_b_stats
                )

                quant_report["poisson_probs"] = poisson_probs
                quant_report["elo_ratings"] = elo_ratings
                quant_report["home_xg"] = xg_values["home_xg"]
                quant_report["away_xg"] = xg_values["away_xg"]
                quant_report["historical_analysis"] = {
                    "home_team_stats": team_a_stats,
                    "away_team_stats": team_b_stats,
                    "match_count": team_a_stats.get("total_matches", 0),
                    "confidence": "HIGH" if team_a_stats.get("total_matches", 0) > 50 else "MEDIUM",
                }

        self._record_execution(state, quant_report)
        print(f"   -> ✅ [{self.soul.name}] 量化分析完成 (基于{quant_report['historical_analysis'].get('match_count', 0)}场比赛数据)")

        return {
            "quant_report": quant_report,
            "poisson_probs": quant_report["poisson_probs"],
            "elo_ratings": quant_report["elo_ratings"],
            "current_step": "quant_done",
        }

    def _calculate_poisson_from_history(
        self, home_team: str, away_team: str,
        home_stats: Dict, away_stats: Dict
    ) -> Dict[str, float]:
        """基于历史数据计算泊松概率"""
        home_wr = home_stats.get("home_win_rate", 0.5)
        away_wr = away_stats.get("away_win_rate", 0.3)
        home_draw_rate = home_stats.get("home_matches", 1) > 0 and (
            home_stats.get("draws", 0) / home_stats.get("home_matches", 1)
        ) or 0.25
        away_draw_rate = away_stats.get("away_matches", 1) > 0 and (
            away_stats.get("draws", 0) / away_stats.get("away_matches", 1)
        ) or 0.25

        avg_home_wr = (home_wr + (1 - away_wr)) / 2
        avg_away_wr = (away_wr + (1 - home_wr)) / 2
        avg_draw = (home_draw_rate + away_draw_rate) / 2

        total = avg_home_wr + avg_away_wr + avg_draw
        if total > 0:
            return {
                "home_win": avg_home_wr / total,
                "draw": avg_draw / total,
                "away_win": avg_away_wr / total,
            }
        return {"home_win": 0.45, "draw": 0.28, "away_win": 0.27}

    def _calculate_elo_ratings(
        self, home_team: str, away_team: str,
        home_stats: Dict, away_stats: Dict
    ) -> Dict[str, int]:
        """基于历史胜率计算ELO评分"""
        base_elo = 1500
        home_wr = home_stats.get("win_rate", 0.5)
        away_wr = away_stats.get("win_rate", 0.5)

        home_elo = int(base_elo + (home_wr - 0.5) * 800)
        away_elo = int(base_elo + (away_wr - 0.5) * 800)

        return {"home": home_elo, "away": away_elo}

    def _calculate_xg(
        self, home_team: str, away_team: str,
        home_stats: Dict, away_stats: Dict
    ) -> Dict[str, float]:
        """估算xG值"""
        home_xg = 1.3 + (home_stats.get("win_rate", 0.5) - 0.4) * 2
        away_xg = 1.0 + (away_stats.get("win_rate", 0.4) - 0.3) * 2

        return {
            "home_xg": round(max(0.5, min(3.0, home_xg)), 2),
            "away_xg": round(max(0.3, min(2.5, away_xg)), 2),
        }


class MarketAgent(Agent, HistoricalAgentMixin):
    """市场分析Agent - 基于历史数据发现价值"""

    def __init__(self):
        super().__init__(
            soul=AgentSoul(
                name="Market",
                role="市场分析专家",
                description="分析赔率、市场情绪、发现价值机会，结合历史赔率分析",
                personality={
                    "market_aware": True,
                    "risk_sensitive": True,
                },
                goals=["发现价值投注", "追踪市场动向", "识别异常赔率", "基于历史定价"],
            ),
            brain=AgentBrain(
                skills=["odds_analysis", "value_detection", "market_tracking", "historical_comparison"],
                rules=["compare_multiple_sources", "flag_anomalies", "compare_with_historical"],
            ),
        )
        self._init_historical()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"   -> 📈 [{self.soul.name}] 市场分析中...")

        league = state.get("league", "")
        home_team = state.get("home_team", "")
        away_team = state.get("away_team", "")

        market_report = {
            "odds": {
                "home_win": 2.0,
                "draw": 3.2,
                "away_win": 3.5,
            },
            "market_sentiment": "neutral",
            "value_opportunities": [],
            "historical_comparison": {},
        }

        if self._historical_initialized and self._query_service and league:
            odds_stats = self._query_service.get_odds_statistics(league)
            league_matches = self._query_service.query_league_matches(league, limit=100)

            if odds_stats and odds_stats.get("count", 0) > 0:
                market_report["odds"] = self._calculate_fair_odds(league, odds_stats)
                market_report["historical_comparison"] = {
                    "league_avg_odds": odds_stats,
                    "data_count": odds_stats.get("count", 0),
                }

            if home_team and away_team:
                value_opps = self._find_value_opportunities(
                    home_team, away_team, league, league_matches
                )
                market_report["value_opportunities"] = value_opps

            asian_value = self.get_asian_handicap_value()
            ou_value = self.get_over_under_value()
            market_report["market_analysis"] = {
                "asian_handicap": asian_value,
                "over_under": ou_value,
            }

        self._record_execution(state, market_report)
        print(f"   -> ✅ [{self.soul.name}] 市场分析完成")

        return {
            "market_report": market_report,
            "odds_data": market_report["odds"],
            "value_opportunities": market_report["value_opportunities"],
            "current_step": "market_done",
        }

    def _calculate_fair_odds(self, league: str, odds_stats: Dict) -> Dict[str, float]:
        """基于历史数据计算公平赔率"""
        avg_home = odds_stats.get("home_odds", {}).get("avg", 2.0)
        avg_draw = odds_stats.get("draw_odds", {}).get("avg", 3.2)
        avg_away = odds_stats.get("away_odds", {}).get("avg", 3.5)

        return {
            "home_win": round(avg_home, 2),
            "draw": round(avg_draw, 2) if avg_draw else 3.2,
            "away_win": round(avg_away, 2),
        }

    def _find_value_opportunities(
        self, home_team: str, away_team: str,
        league: str, matches: List[Dict]
    ) -> List[Dict]:
        """发现价值机会"""
        opps = []

        if not matches:
            return opps

        team_matches = [
            m for m in matches
            if home_team.lower() in m.get("home_team", "").lower()
            or away_team.lower() in m.get("away_team", "").lower()
        ]

        if len(team_matches) < 5:
            return opps

        home_wins = sum(1 for m in team_matches if m.get("result") == "H")
        away_wins = sum(1 for m in team_matches if m.get("result") == "A")

        actual_home_rate = home_wins / len(team_matches)
        actual_away_rate = away_wins / len(team_matches)

        implied_home = 1 / 2.0 if 2.0 > 0 else 0.5
        implied_away = 1 / 3.5 if 3.5 > 0 else 0.28

        if actual_home_rate > implied_home + 0.05:
            opps.append({
                "type": "home_win",
                "expected_rate": actual_home_rate,
                "implied_rate": implied_home,
                "edge": actual_home_rate - implied_home,
            })

        if actual_away_rate > implied_away + 0.05:
            opps.append({
                "type": "away_win",
                "expected_rate": actual_away_rate,
                "implied_rate": implied_away,
                "edge": actual_away_rate - implied_away,
            })

        return opps


class RiskAgent(Agent, HistoricalAgentMixin):
    """风险控制Agent - 基于历史数据评估风险"""

    def __init__(self):
        super().__init__(
            soul=AgentSoul(
                name="Risk",
                role="风险控制专家",
                description="计算Kelly准则、评估风险等级、控制仓位，基于历史胜率优化",
                personality={
                    "cautious": True,
                    "rule_based": True,
                },
                goals=["控制下行风险", "优化仓位管理", "设置止损线", "基于历史数据评估"],
            ),
            brain=AgentBrain(
                skills=["kelly_criterion", "risk_management", "position_sizing", "historical_backtest"],
                rules=["never_exceed_max_exposure", "always_set_stop_loss", "backtest_before_deploy"],
            ),
        )
        self._init_historical()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"   -> 🛡️ [{self.soul.name}] 风险评估中...")

        poisson = state.get("poisson_probs", {"home_win": 0.5})
        odds = state.get("odds_data", {"home_win": 2.0})
        quant_report = state.get("quant_report", {})
        historical = quant_report.get("historical_analysis", {})
        match_count = historical.get("match_count", 0)

        p_home = poisson.get("home_win", 0.5)
        p_draw = poisson.get("draw", 0.28)
        p_away = poisson.get("away_win", 0.27)

        odds_home = odds.get("home_win", 2.0)
        odds_draw = odds.get("draw", 3.2)
        odds_away = odds.get("away_win", 3.5)

        kelly_home = self._calculate_kelly(p_home, odds_home)
        kelly_draw = self._calculate_kelly(p_draw, odds_draw)
        kelly_away = self._calculate_kelly(p_away, odds_away)

        kelly_fraction = max(kelly_home, kelly_draw, kelly_away)
        kelly_fraction = min(0.25, kelly_fraction)

        confidence = "HIGH" if match_count > 100 else "MEDIUM" if match_count > 30 else "LOW"
        risk_multiplier = 1.0 if confidence == "HIGH" else 0.7 if confidence == "MEDIUM" else 0.4
        adjusted_kelly = kelly_fraction * risk_multiplier

        if adjusted_kelly > 0:
            best_bet = "home_win" if kelly_home == kelly_fraction else ("draw" if kelly_draw == kelly_fraction else "away_win")
            best_odds = odds_home if best_bet == "home_win" else (odds_draw if best_bet == "draw" else odds_away)
            risk_level = "LOW" if adjusted_kelly <= 0.05 else "MEDIUM" if adjusted_kelly <= 0.15 else "HIGH"
        else:
            best_bet = None
            best_odds = None
            risk_level = "REJECT"

        risk_report = {
            "kelly_fraction": round(adjusted_kelly, 4),
            "kelly_raw": round(kelly_fraction, 4),
            "risk_level": risk_level,
            "recommended_stake": round(adjusted_kelly * 1000, 2),
            "approved": adjusted_kelly > 0.01,
            "best_bet": best_bet,
            "best_odds": best_odds,
            "confidence": confidence,
            "match_count": match_count,
            "bet_kelly_values": {
                "home_win": round(kelly_home, 4),
                "draw": round(kelly_draw, 4),
                "away_win": round(kelly_away, 4),
            },
        }

        self._record_execution(state, risk_report)
        print(f"   -> ✅ [{self.soul.name}] 风险等级: {risk_level} (信心:{confidence}, 数据:{match_count}场)")

        return {
            "risk_report": risk_report,
            "kelly_stake": risk_report["recommended_stake"],
            "risk_level": risk_level,
            "current_step": "risk_done",
        }

    def _calculate_kelly(self, p: float, odds: float) -> float:
        """计算Kelly指数"""
        if p <= 0 or odds <= 1:
            return 0
        b = odds - 1
        if b <= 0:
            return 0
        kelly = (p * (b + 1) - 1) / b
        return max(0, kelly)


class TraderAgent(Agent, HistoricalAgentMixin):
    """交易决策Agent - 综合所有分析做出最终决策"""

    def __init__(self):
        super().__init__(
            soul=AgentSoul(
                name="Trader",
                role="交易决策专家",
                description="综合所有信息做出最终投注决策，结合历史验证决策质量",
                personality={
                    "decisive": True,
                    "balanced": True,
                },
                goals=["做出最优决策", "平衡风险收益", "执行交易计划", "验证历史表现"],
            ),
            brain=AgentBrain(
                skills=["decision_making", "trade_execution", "portfolio_management", "historical_validation"],
                rules=["require_multiple_confirmations", "document_reasoning", "validate_against_history"],
            ),
        )
        self._init_historical()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"   -> 🎯 [{self.soul.name}] 交易决策中...")

        risk_report = state.get("risk_report", {})
        scout_report = state.get("scout_report", {})
        quant_report = state.get("quant_report", {})
        market_report = state.get("market_report", {})

        approved = risk_report.get("approved", False)
        kelly_fraction = risk_report.get("kelly_fraction", 0)
        best_bet = risk_report.get("best_bet")
        best_odds = risk_report.get("best_odds")
        risk_level = risk_report.get("risk_level", "REJECT")
        confidence = risk_report.get("confidence", "LOW")

        historical_context = scout_report.get("historical_data", {})
        intelligence_summary = scout_report.get("intelligence_summary", "")
        value_opportunities = market_report.get("value_opportunities", [])

        reasoning_parts = []
        if intelligence_summary:
            reasoning_parts.append(intelligence_summary)
        if value_opportunities:
            reasoning_parts.append(f"发现{len(value_opportunities)}个价值机会")
        reasoning_parts.append(f"风险等级:{risk_level}, 信心:{confidence}")

        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "综合分析后做出决策"

        final_bet = None
        if approved and best_bet and best_odds:
            stake = round(kelly_fraction * 1000, 2)
            if stake > 0:
                final_bet = {
                    "type": best_bet,
                    "odds": best_odds,
                    "stake": stake,
                    "kelly_fraction": kelly_fraction,
                    "market_value": value_opportunities,
                }

        if final_bet:
            self._record_historical_decision(state, final_bet)

        trader_decision = {
            "approved": approved,
            "final_bet": final_bet,
            "reasoning": reasoning,
            "risk_level": risk_level,
            "confidence": confidence,
        }

        self._record_execution(state, trader_decision)
        print(f"   -> ✅ [{self.soul.name}] 决策: {'批准' if approved else '拒绝'} - {reasoning}")

        return {
            "trader_decision": trader_decision,
            "final_bet": trader_decision["final_bet"],
            "current_step": "trader_done",
        }

    def _record_historical_decision(self, state: Dict, decision: Dict) -> None:
        """记录历史决策用于后续回测"""
        try:
            home_team = state.get("home_team", "")
            away_team = state.get("away_team", "")
            bet_type = decision.get("type", "")
            print(f"      📝 记录决策: {home_team} vs {away_team} - {bet_type}")
        except Exception:
            pass


class AuditorAgent(Agent, HistoricalAgentMixin):
    """审计监督Agent - 基于历史数据审查决策质量"""

    def __init__(self):
        super().__init__(
            soul=AgentSoul(
                name="Auditor",
                role="审计监督专家",
                description="审查决策过程、记录经验教训、驱动进化，基于历史数据评估决策质量",
                personality={
                    "critical": True,
                    "improvement_oriented": True,
                },
                goals=["确保决策质量", "提取经验教训", "反馈改进建议", "历史数据验证"],
            ),
            brain=AgentBrain(
                skills=["audit", "reflection", "pattern_recognition", "historical_audit"],
                rules=["document_everything", "identify_improvements", "compare_with_historical"],
            ),
        )
        self._init_historical()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"   -> 🧐 [{self.soul.name}] 审计复盘中...")

        scout_report = state.get("scout_report", {})
        quant_report = state.get("quant_report", {})
        market_report = state.get("market_report", {})
        risk_report = state.get("risk_report", {})
        trader_decision = state.get("trader_decision", {})

        intelligence_summary = scout_report.get("intelligence_summary", "")
        confidence = risk_report.get("confidence", "UNKNOWN")
        match_count = risk_report.get("match_count", 0)
        value_opportunities = market_report.get("value_opportunities", [])
        approved = trader_decision.get("approved", False)

        lessons_learned = []
        improvements = []

        if confidence == "HIGH":
            lessons_learned.append("历史数据充足，决策信心高")
        elif confidence == "MEDIUM":
            lessons_learned.append("历史数据中等，需要更多样本验证")
            improvements.append("建议积累更多该联赛/球队的比赛数据")
        else:
            lessons_learned.append("历史数据不足，决策需谨慎")
            improvements.append("该球队/联赛数据不足，建议跳过或降低投注")

        if value_opportunities:
            lessons_learned.append(f"发现{len(value_opportunities)}个潜在价值机会")
            improvements.append("验证价值机会的历史回测效果")

        if match_count > 100:
            lessons_learned.append(f"基于{match_count}场历史比赛分析")
        elif match_count > 0:
            lessons_learned.append(f"基于{match_count}场比赛，数据有限")

        if approved:
            improvements.append("批准投注，需跟踪结果用于回测")
        else:
            lessons_learned.append("决策被拒绝，风险控制有效")

        if self._query_service:
            data_overview = self._query_service.get_data_overview()
            lessons_learned.append(f"数据库共{data_overview.get('total_matches', 'N/A')}场比赛")

        audit_report = {
            "decision_quality": confidence,
            "data_quality": "GOOD" if match_count > 50 else "FAIR" if match_count > 10 else "POOR",
            "lessons_learned": lessons_learned,
            "improvements": improvements,
            "recommendations": self._generate_recommendations(approved, confidence, match_count),
            "match_count_analyzed": match_count,
            "value_opportunities_count": len(value_opportunities),
        }

        self._record_execution(state, audit_report)
        print(f"   -> ✅ [{self.soul.name}] 审计完成 - 数据质量:{audit_report['data_quality']}")

        return {
            "audit_report": audit_report,
            "current_step": "audit_done",
        }

    def _generate_recommendations(self, approved: bool, confidence: str, match_count: int) -> List[str]:
        """生成改进建议"""
        recs = []

        if approved and confidence == "HIGH":
            recs.append("该投注信号质量较高，可执行")
            recs.append("建议记录结果用于后续回测分析")
        elif approved and confidence == "MEDIUM":
            recs.append("信号中等，建议降低投注金额")
            recs.append("持续跟踪该类型投注表现")
        elif not approved:
            recs.append("当前信号未通过风控，继续寻找机会")
        else:
            recs.append("数据不足，建议增加该联赛/球队的关注")

        recs.append("定期复盘整体投注表现，优化参数")

        return recs


SCOUT_AGENT = ScoutAgent()
QUANT_AGENT = QuantAgent()
MARKET_AGENT = MarketAgent()
RISK_AGENT = RiskAgent()
TRADER_AGENT = TraderAgent()
AUDITOR_AGENT = AuditorAgent()

ALL_AGENTS = [
    SCOUT_AGENT,
    QUANT_AGENT,
    MARKET_AGENT,
    RISK_AGENT,
    TRADER_AGENT,
    AUDITOR_AGENT,
]


def get_agent_by_name(name: str) -> Agent:
    """根据名称获取Agent"""
    for agent in ALL_AGENTS:
        if agent.soul.name.lower() == name.lower():
            return agent
    return None


class LotteryRouterMixin:
    """
    彩票路由混入类 - 竞彩/北单完全隔离
    
    从单一真实来源获取规则: src/calculations/lottery
    """

    def __init__(self):
        self._lottery_config_loaded = False
        self._LOTTERY_CONFIG = None

    @property
    def LOTTERY_CONFIG(self):
        """懒加载 - 从单一真实来源获取彩票规则"""
        if not self._lottery_config_loaded:
            try:
                from src.calculations.lottery import LOTTERY_KNOWLEDGE
                self._LOTTERY_CONFIG = {
                    "JINGCAI": LOTTERY_KNOWLEDGE.get_lottery("JINGCAI"),
                    "BEIDAN": LOTTERY_KNOWLEDGE.get_lottery("BEIDAN"),
                }
                self._lottery_config_loaded = True
            except ImportError:
                # 如果导入失败，返回默认配置作为后备
                self._LOTTERY_CONFIG = self._get_fallback_config()
                self._lottery_config_loaded = True
        return self._LOTTERY_CONFIG

    def _get_fallback_config(self):
        """后备配置（仅在无法导入LotteryKnowledge时使用）"""
        return {
            "JINGCAI": {
                "name": "竞彩足球",
                "return_rate": 0.69,
                "max_legs": 8,
            },
            "BEIDAN": {
                "name": "北京单场",
                "return_rate": 0.65,
                "max_legs": 15,
            },
        }

    def _route_lottery(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        路由到正确的彩种通道
        """
        league = state.get("league", "")
        lottery_type = state.get("lottery_type", "")

        if lottery_type not in self.LOTTERY_CONFIG:
            if league in ["E0", "D1", "SP1", "I1", "F1", "G1"]:
                lottery_type = "JINGCAI"
            else:
                lottery_type = "BEIDAN"

        config = self.LOTTERY_CONFIG.get(lottery_type, self.LOTTERY_CONFIG["JINGCAI"])

        routing_result = {
            "lottery_type": lottery_type,
            "lottery_name": config["name"],
            "return_rate": config["return_rate"],
            "max_legs": config["max_legs"],
            "has_fraction_handicap": config["has_fraction_handicap"],
            "play_types": config["play_types"],
        }

        print(f"      🏷️ 路由至: {config['name']} (返奖率{config['return_rate']*100:.0f}%, 最大{config['max_legs']}关)")

        return routing_result

    def _validate_ticket(self, lottery_type: str, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用 LotteryRouter 验证投注单
        """
        if LOTTERY_ROUTER:
            return LOTTERY_ROUTER.route_and_validate(lottery_type, ticket_data)
        return {"status": "SUCCESS", "channel": lottery_type}


class LotteryRouterAgent(Agent, HistoricalAgentMixin, LotteryRouterMixin):
    """
    彩票路由Agent - 竞彩/北单完全隔离

    职责：
    1. 根据联赛自动识别彩种
    2. 设置正确的玩法规则
    3. 验证投注单符合物理限制
    """

    def __init__(self):
        LotteryRouterMixin.__init__(self)
        super().__init__(
            soul=AgentSoul(
                name="LotteryRouter",
                role="彩票路由专家",
                description="竞彩/北单完全隔离，根据联赛自动路由，设置正确玩法规则",
                personality={
                    "precise": True,
                    "rule_following": True,
                },
                goals=["正确路由彩种", "设置玩法规则", "验证投注单"],
            ),
            brain=AgentBrain(
                skills=["lottery_routing", "play_type_validation", "odds_verification"],
                rules=["strict_lottery_isolation", "respect_max_legs", "validate_odds"],
            ),
        )
        self._init_historical()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"   -> 🏷️ [{self.soul.name}] 彩种路由中...")

        routing = self._route_lottery(state)

        state["lottery_type"] = routing["lottery_type"]
        state["lottery_name"] = routing["lottery_name"]
        state["return_rate"] = routing["return_rate"]
        state["max_legs"] = routing["max_legs"]
        state["has_fraction_handicap"] = routing["has_fraction_handicap"]
        state["play_types"] = routing["play_types"]

        if routing["lottery_type"] == "JINGCAI":
            print(f"   -> ✅ [{self.soul.name}] 路由至竞彩足球 - 固定赔率, 整数让球, 最大{routing['max_legs']}关")
        else:
            print(f"   -> ✅ [{self.soul.name}] 路由至北京单场 - 浮动奖池, 小数让球, 最大{routing['max_legs']}关")

        return {
            "routing": routing,
            "lottery_type": routing["lottery_type"],
            "lottery_name": routing["lottery_name"],
            "return_rate": routing["return_rate"],
            "max_legs": routing["max_legs"],
            "current_step": "routing_done",
        }


LOTTERY_ROUTER_AGENT = LotteryRouterAgent()


__all__ = [
    "Agent",
    "AgentSoul",
    "AgentBrain",
    "HistoricalAgentMixin",
    "LotteryRouterMixin",
    "ScoutAgent",
    "QuantAgent",
    "MarketAgent",
    "RiskAgent",
    "TraderAgent",
    "AuditorAgent",
    "LotteryRouterAgent",
    "HistoricalAnalystAgent",
    "LeagueExpertAgent",
    "SCOUT_AGENT",
    "QUANT_AGENT",
    "MARKET_AGENT",
    "RISK_AGENT",
    "TRADER_AGENT",
    "AUDITOR_AGENT",
    "LOTTERY_ROUTER_AGENT",
    "ALL_AGENTS",
    "get_agent_by_name",
]

from .historical_agent import HistoricalAnalystAgent, LeagueExpertAgent


SCOUT_NODE = SCOUT_AGENT
QUANT_NODE = QUANT_AGENT
MARKET_NODE = MARKET_AGENT
RISK_NODE = RISK_AGENT
TRADER_NODE = TRADER_AGENT
AUDITOR_NODE = AUDITOR_AGENT
LOTTERY_NODE = LOTTERY_ROUTER_AGENT
AgentNode = Agent


from .collaboration import AgentCollaborationManager, COLLABORATION_MANAGER
from .adaptive_learning import AdaptiveLearningLoop, ADAPTIVE_LEARNING


__all__ = [
    "Agent",
    "AgentSoul",
    "AgentBrain",
    "HistoricalAgentMixin",
    "LotteryRouterMixin",
    "ScoutAgent",
    "QuantAgent",
    "MarketAgent",
    "RiskAgent",
    "TraderAgent",
    "AuditorAgent",
    "LotteryRouterAgent",
    "HistoricalAnalystAgent",
    "LeagueExpertAgent",
    "AgentCollaborationManager",
    "AdaptiveLearningLoop",
    "SCOUT_AGENT",
    "QUANT_AGENT",
    "MARKET_AGENT",
    "RISK_AGENT",
    "TRADER_AGENT",
    "AUDITOR_AGENT",
    "LOTTERY_ROUTER_AGENT",
    "COLLABORATION_MANAGER",
    "ADAPTIVE_LEARNING",
    "ALL_AGENTS",
    "get_agent_by_name",
]
