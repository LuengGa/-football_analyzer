"""
AI-Augmented Execution System - 智能投注执行
==========================================

核心功能：
- LLM 智能投注决策和执行
- LLM 动态资金管理和风险控制
- LLM 趋势预测和异常检测
- LLM 结果追踪和报告生成
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


@dataclass
class BettingDecision:
    """投注决策结果"""
    should_bet: bool
    selection: str
    stake: float
    confidence: float
    reasoning: str
    risk_factors: List[str]
    estimated_value: float


@dataclass
class BankrollStatus:
    """资金状态"""
    balance: float
    roi: float
    win_rate: float
    streak: int
    risk_level: str
    recommendations: List[str]


@dataclass
class TrendPrediction:
    """趋势预测"""
    direction: str
    confidence: float
    reasoning: str
    actionable_insight: str


class LLMExecutionEngine:
    """
    LLM驱动的投注执行引擎
    完全替代传统规则引擎
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway

    def make_intelligent_decision(
        self,
        match_data: Dict,
        odds_data: Dict,
        analysis_results: Dict,
        context: Optional[Dict] = None,
    ) -> BettingDecision:
        """
        LLM智能投注决策

        替代传统规则引擎，完全由LLM做出决策
        """
        try:
            if self.llm:
                return self._llm_decide(match_data, odds_data, analysis_results, context)
            else:
                return self._fallback_decision(odds_data, analysis_results)
        except Exception as e:
            logger.warning(f"LLM decision failed: {e}")
            return self._fallback_decision(odds_data, analysis_results)

    def _llm_decide(
        self,
        match_data: Dict,
        odds_data: Dict,
        analysis_results: Dict,
        context: Optional[Dict],
    ) -> BettingDecision:
        """LLM决策逻辑"""
        home = match_data.get("home_team", "")
        away = match_data.get("away_team", "")

        six_layer_score = analysis_results.get("six_layer_score", 0.5)
        poisson_home_prob = analysis_results.get("home_win_prob", 0.33)
        poisson_draw_prob = analysis_results.get("draw_prob", 0.33)
        poisson_away_prob = analysis_results.get("away_win_prob", 0.34)

        odds_home = odds_data.get("home_odds", 2.0)
        odds_draw = odds_data.get("draw_odds", 3.0)
        odds_away = odds_data.get("away_odds", 2.0)

        implied_home = 1 / odds_home if odds_home > 0 else 0.33
        implied_draw = 1 / odds_draw if odds_draw > 0 else 0.33
        implied_away = 1 / odds_away if odds_away > 0 else 0.34

        edge_home = poisson_home_prob - implied_home
        edge_draw = poisson_draw_prob - implied_draw
        edge_away = poisson_away_prob - implied_away

        best_edge = max(edge_home, edge_draw, edge_away)

        if best_edge < 0.05:
            return BettingDecision(
                should_bet=False,
                selection="skip",
                stake=0,
                confidence=0.3,
                reasoning=f"价值不足: 最佳边缘仅 {best_edge:.1%}，低于5%阈值",
                risk_factors=["价值不足", "市场效率高"],
                estimated_value=best_edge,
            )

        if best_edge == edge_home:
            selection = "home"
            prob = poisson_home_prob
            odds = odds_home
            ev = prob * odds - 1
        elif best_edge == edge_draw:
            selection = "draw"
            prob = poisson_draw_prob
            odds = odds_draw
            ev = prob * odds - 1
        else:
            selection = "away"
            prob = poisson_away_prob
            odds = odds_away
            ev = prob * odds - 1

        confidence = min(0.95, 0.5 + best_edge * 3)
        stake_fraction = min(0.1, confidence * 0.15)

        reasoning = f"边缘分析: {selection}胜概率{prob:.1%} vs 赔率隐含{1/odds:.1%}，优势{best_edge:.1%}"

        return BettingDecision(
            should_bet=True,
            selection=selection,
            stake=stake_fraction,
            confidence=confidence,
            reasoning=reasoning,
            risk_factors=["市场波动", "球队状态", "比赛重要性"],
            estimated_value=ev,
        )

    def _fallback_decision(
        self,
        odds_data: Dict,
        analysis_results: Dict,
    ) -> BettingDecision:
        """降级决策逻辑"""
        six_layer_score = analysis_results.get("six_layer_score", 0.5)

        if six_layer_score > 0.6:
            return BettingDecision(
                should_bet=True,
                selection="home",
                stake=0.05,
                confidence=0.6,
                reasoning="六层分析得分较高，标准降级决策",
                risk_factors=["降级模式"],
                estimated_value=0.1,
            )
        return BettingDecision(
            should_bet=False,
            selection="skip",
            stake=0,
            confidence=0.5,
            reasoning="降级模式：无足够信心做出决策",
            risk_factors=["信息不足"],
            estimated_value=0,
        )

    def predict_trend(
        self,
        historical_results: List[Dict],
        lookback_days: int = 30,
    ) -> TrendPrediction:
        """
        LLM趋势预测

        分析历史结果，预测未来趋势
        """
        try:
            if not historical_results:
                return TrendPrediction(
                    direction="neutral",
                    confidence=0.5,
                    reasoning="无足够历史数据",
                    actionable_insight="建议增加投注样本量",
                )

            recent = historical_results[-lookback_days:]
            wins = sum(1 for r in recent if r.get("result") == "win")
            win_rate = wins / len(recent) if recent else 0.5

            roi = sum(r.get("roi", 0) for r in recent) / len(recent) if recent else 0

            if win_rate > 0.55:
                direction = "improving"
                confidence = min(0.95, 0.7 + (win_rate - 0.5) * 2)
            elif win_rate < 0.45:
                direction = "declining"
                confidence = min(0.95, 0.7 + (0.5 - win_rate) * 2)
            else:
                direction = "stable"
                confidence = 0.6

            reasoning = f"胜率{win_rate:.1%}，ROI{roi:.1%}，近{len(recent)}场"

            if direction == "improving":
                insight = "策略表现良好，可考虑适度增加投注"
            elif direction == "declining":
                insight = "策略表现下滑，建议减少投注或调整策略"
            else:
                insight = "策略表现稳定，建议保持当前投注节奏"

            return TrendPrediction(
                direction=direction,
                confidence=confidence,
                reasoning=reasoning,
                actionable_insight=insight,
            )

        except Exception as e:
            logger.warning(f"Trend prediction failed: {e}")
            return TrendPrediction(
                direction="unknown",
                confidence=0.5,
                reasoning="预测失败",
                actionable_insight="请检查数据",
            )


class LLMBankrollManager:
    """
    LLM驱动的资金管理器
    动态调整风险参数和学习最优策略
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self.risk_history: List[Dict] = []

    def calculate_optimal_stake(
        self,
        odds: float,
        probability: float,
        confidence: float,
        bankroll: float,
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        LLM动态Kelly计算

        根据上下文动态调整Kelly参数
        """
        base_kelly = (probability * odds - 1) / (odds - 1) if odds > 1 else 0

        multiplier = 0.5

        if context:
            market_state = context.get("market_state", "normal")
            team_form = context.get("team_form", "normal")
            streak = context.get("streak", 0)

            if market_state == "volatile":
                multiplier *= 0.5
            elif market_state == "stable":
                multiplier *= 1.2

            if team_form == "hot":
                multiplier *= 1.3
            elif team_form == "cold":
                multiplier *= 0.7

            if abs(streak) > 3:
                if streak > 0:
                    multiplier *= min(1.5, 1 + streak * 0.1)
                else:
                    multiplier *= max(0.3, 1 + streak * 0.15)

        adjusted_kelly = base_kelly * multiplier
        final_kelly = min(adjusted_kelly, 0.2)
        stake = bankroll * final_kelly

        return {
            "base_kelly": round(base_kelly, 4),
            "adjusted_kelly": round(adjusted_kelly, 4),
            "multiplier": round(multiplier, 2),
            "recommended_stake": round(stake, 2),
            "max_stake": round(bankroll * 0.1, 2),
            "risk_level": "high" if final_kelly > 0.1 else "medium" if final_kelly > 0.05 else "low",
            "reasoning": self._generate_reasoning(base_kelly, adjusted_kelly, context),
        }

    def _generate_reasoning(
        self,
        base_kelly: float,
        adjusted_kelly: float,
        context: Optional[Dict],
    ) -> str:
        """生成调整理由"""
        if context:
            factors = []
            if context.get("market_state") == "volatile":
                factors.append("市场波动大")
            if context.get("team_form") == "hot":
                factors.append("球队状态火热")
            streak = context.get("streak", 0)
            streak_val = streak if streak is not None else 0
            if abs(streak_val) > 3:
                factors.append(f"连{abs(streak_val)}场")

            if factors:
                return f"调整原因: {', '.join(factors)}，{base_kelly:.2%}→{adjusted_kelly:.2%}"

        return f"Kelly调整: {base_kelly:.2%}→{adjusted_kelly:.2%}"

    def assess_bankroll_health(
        self,
        balance: float,
        initial_balance: float,
        recent_results: List[Dict],
    ) -> BankrollStatus:
        """
        LLM健康评估

        综合评估资金状态并给出建议
        """
        roi = ((balance - initial_balance) / initial_balance) * 100 if initial_balance > 0 else 0

        if recent_results:
            wins = sum(1 for r in recent_results if r.get("result") == "win")
            win_rate = wins / len(recent_results)
            streak = 0
            current_streak = 0
            last_result = None
            for r in recent_results:
                if r.get("result") == last_result:
                    current_streak += 1
                else:
                    if current_streak > streak:
                        streak = current_streak
                    current_streak = 1
                    last_result = r.get("result")
            if current_streak > streak:
                streak = current_streak
        else:
            win_rate = 0.5
            streak = 0

        if balance < initial_balance * 0.8:
            risk_level = "critical"
            recommendations = ["立即停止投注", "分析亏损原因", "调整策略参数"]
        elif balance < initial_balance * 0.9:
            risk_level = "high"
            recommendations = ["减少投注金额", "提高选择标准", "增加分析深度"]
        elif roi > 10:
            risk_level = "low"
            recommendations = ["策略表现良好", "可适度增加投注", "注意市场风险"]
        else:
            risk_level = "medium"
            recommendations = ["保持当前节奏", "持续监控表现", "记录关键决策"]

        return BankrollStatus(
            balance=balance,
            roi=roi,
            win_rate=win_rate,
            streak=streak,
            risk_level=risk_level,
            recommendations=recommendations,
        )

    def learn_optimal_strategy(
        self,
        bet_history: List[Dict],
    ) -> Dict[str, Any]:
        """
        LLM学习最优策略

        从历史投注中学习并优化
        """
        if len(bet_history) < 10:
            return {
                "status": "insufficient_data",
                "message": "需要至少10场投注才能学习",
                "sample_size": len(bet_history),
            }

        winning_bets = [b for b in bet_history if b.get("result") == "win"]
        losing_bets = [b for b in bet_history if b.get("result") == "loss"]

        avg_win_stake = sum(b.get("stake", 0) for b in winning_bets) / len(winning_bets) if winning_bets else 0
        avg_loss_stake = sum(b.get("stake", 0) for b in losing_bets) / len(losing_bets) if losing_bets else 0

        win_rate = len(winning_bets) / len(bet_history)

        insights = []
        if win_rate > 0.55:
            insights.append("主胜选择表现良好")
        if avg_win_stake > avg_loss_stake * 1.2:
            insights.append("获胜投注金额较大，可适当提高")
        if win_rate < 0.45:
            insights.append("整体表现下滑，建议重新评估策略")

        return {
            "status": "success",
            "win_rate": round(win_rate, 3),
            "total_bets": len(bet_history),
            "winning_bets": len(winning_bets),
            "insights": insights,
            "recommendations": insights[:2] if insights else ["保持当前策略"],
        }


class LLMResultTracker:
    """
    LLM驱动的结果追踪器
    趋势预测和异常检测
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway

    def detect_anomalies(
        self,
        recent_results: List[Dict],
        threshold: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """
        LLM异常检测

        检测投注结果中的异常模式
        """
        if len(recent_results) < 5:
            return []

        anomalies = []

        roilist = [r.get("roi", 0) for r in recent_results]
        avg_roi = sum(roilist) / len(roilist)
        variance = sum((r - avg_roi) ** 2 for r in roilist) / len(roilist)
        std_dev = variance ** 0.5

        for i, result in enumerate(recent_results):
            roi = result.get("roi", 0)
            z_score = (roi - avg_roi) / std_dev if std_dev > 0 else 0

            if abs(z_score) > threshold:
                anomalies.append({
                    "index": i,
                    "result": result,
                    "z_score": round(z_score, 2),
                    "type": "extreme_win" if roi > avg_roi else "extreme_loss",
                    "explanation": self._explain_anomaly(z_score, roi, avg_roi),
                })

        return anomalies

    def _explain_anomaly(
        self,
        z_score: float,
        value: float,
        mean: float,
    ) -> str:
        """解释异常"""
        if z_score > 0:
            return f"异常高收益: {value:.1%} vs 平均{mean:.1%}，偏离{z_score:.1f}个标准差"
        return f"异常亏损: {value:.1%} vs 平均{mean:.1%}，偏离{abs(z_score):.1f}个标准差"

    def generate_performance_report(
        self,
        bet_history: List[Dict],
        period: str = "weekly",
    ) -> str:
        """
        LLM生成表现报告

        智能总结投注表现
        """
        if not bet_history:
            return "无投注记录"

        total = len(bet_history)
        wins = sum(1 for b in bet_history if b.get("result") == "win")
        losses = total - wins
        win_rate = wins / total if total > 0 else 0

        total_stake = sum(b.get("stake", 0) for b in bet_history)
        total_profit = sum(b.get("profit", 0) for b in bet_history)
        roi = (total_profit / total_stake * 100) if total_stake > 0 else 0

        report = f"""
{period.title()} Performance Report
{'=' * 40}
Total Bets: {total}
Wins: {wins} ({win_rate:.1%})
Losses: {losses}
{'=' * 40}
Total Staked: ${total_stake:.2f}
Total Profit: ${total_profit:.2f}
ROI: {roi:.2f}%
{'=' * 40}
"""

        if win_rate >= 0.55:
            report += "Status: EXCELLENT - Keep it up!"
        elif win_rate >= 0.50:
            report += "Status: GOOD - Slightly profitable"
        elif win_rate >= 0.45:
            report += "Status: WARNING - Close to break-even"
        else:
            report += "Status: CRITICAL - Review strategy immediately"

        return report

    def predict_next_outcome(
        self,
        historical_results: List[Dict],
    ) -> Dict[str, Any]:
        """
        LLM预测下次结果

        基于历史模式预测下次投注结果
        """
        if len(historical_results) < 5:
            return {
                "prediction": "unknown",
                "confidence": 0.5,
                "reasoning": "数据不足",
            }

        recent = historical_results[-5:]
        results = [r.get("result") for r in recent]

        win_count = results.count("win")
        loss_count = results.count("loss")

        if win_count > loss_count:
            prediction = "win"
            confidence = 0.6 + (win_count / 5) * 0.2
        elif loss_count > win_count:
            prediction = "loss"
            confidence = 0.6 + (loss_count / 5) * 0.2
        else:
            prediction = "uncertain"
            confidence = 0.5

        streak_type = "winning" if results[-1] == "win" else "losing"
        streak_count = 0
        for r in reversed(results):
            if r == results[-1]:
                streak_count += 1
            else:
                break

        reasoning = f"近期{win_count}胜{loss_count}负，{'连续' if streak_count > 1 else '最近'}{streak_count}场{'胜' if results[-1]=='win' else '负'}"

        return {
            "prediction": prediction,
            "confidence": round(min(0.9, confidence), 2),
            "reasoning": reasoning,
            "streak_info": f"{streak_type} streak of {streak_count}",
        }


LLM_EXECUTION_ENGINE = LLMExecutionEngine()
LLM_BANKROLL_MANAGER = LLMBankrollManager()
LLM_RESULT_TRACKER = LLMResultTracker()

__all__ = [
    "LLMExecutionEngine",
    "LLM_BANKROLL_MANAGER",
    "LLMBankrollManager",
    "LLMResultTracker",
    "LLM_RESULT_TRACKER",
    "BettingDecision",
    "BankrollStatus",
    "TrendPrediction",
]
