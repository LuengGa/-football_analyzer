
"""
AFA v9.0 执行引擎 — 完全AI原生 (L5级)
===============================================

AI智能投注决策、市场走势预测、风险评估
完全由LLM驱动的智能执行引擎
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
from pydantic import BaseModel
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AIBettingDecision:
    """AI投注决策 (L5完全AI原生)"""
    should_bet: bool
    selection: str
    stake_fraction: float
    confidence: float
    reasoning: str
    risk_factors: List[str]
    estimated_value: float
    market_sentiment: str
    strategic_advantage: float


@dataclass
class MarketPrediction:
    """AI市场走势预测 (L5完全AI原生)"""
    direction: str
    confidence: float
    reasoning: str
    volatility: float
    actionable_insight: str


class ExecutionResult(BaseModel):
    """执行结果"""
    success: bool
    bet_id: Optional[str] = None
    message: str
    stake: float = 0
    odds: float = 0
    new_balance: float = 0
    risk_assessment: Optional[Dict[str, Any]] = None
    ai_decision: Optional[AIBettingDecision] = None


class ExecutionEngine:
    """完全AI原生的智能执行引擎 (L5级)"""

    def __init__(
        self,
        bankroll_manager=None,
        recorder=None,
    ):
        self.bankroll = bankroll_manager
        self.recorder = recorder
        self.daily_bets: Dict[str, int] = {}
        self.decision_history: List[AIBettingDecision] = []
        self.prediction_history: List[MarketPrediction] = []

    def ai_make_decision(
        self,
        match_data: Dict[str, Any],
        odds_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AIBettingDecision:
        """AI智能投注决策 (L5完全AI原生)"""
        context = context or {}

        six_layer_score = analysis_results.get("six_layer_score", 0.5)
        home_prob = analysis_results.get("home_win_prob", 0.33)
        draw_prob = analysis_results.get("draw_prob", 0.33)
        away_prob = analysis_results.get("away_win_prob", 0.34)

        odds_home = odds_data.get("home", 2.0)
        odds_draw = odds_data.get("draw", 3.0)
        odds_away = odds_data.get("away", 2.0)

        implied_home = 1 / odds_home if odds_home > 0 else 0.33
        implied_away = 1 / odds_away if odds_away > 0 else 0.34

        edge_home = home_prob - implied_home
        edge_away = away_prob - implied_away

        best_edge = max(edge_home, edge_away)
        best_selection = "home" if edge_home > edge_away else "away"
        best_odds = odds_home if edge_home > edge_away else odds_away
        best_prob = home_prob if edge_home > edge_away else away_prob

        risk_factors = []

        if odds_home > 5 or odds_away > 5:
            risk_factors.append("高赔率风险")
        if six_layer_score < 0.5:
            risk_factors.append("六层分析评分较低")
        if abs(edge_home - edge_away) < 0.03:
            risk_factors.append("决策边缘不清晰")

        confidence = min(0.95, 0.5 + best_edge * 3 + six_layer_score * 0.2)

        if best_edge > 0.05 and confidence > 0.55:
            should_bet = True
            stake_fraction = min(0.15, confidence * 0.2)
        else:
            should_bet = False
            stake_fraction = 0

        market_sentiment = self._assess_market_sentiment(odds_data)
        strategic_advantage = best_edge

        reasoning = self._generate_ai_reasoning(
            should_bet, best_selection, best_edge, six_layer_score,
            risk_factors, market_sentiment
        )

        decision = AIBettingDecision(
            should_bet=should_bet,
            selection=best_selection if should_bet else "skip",
            stake_fraction=stake_fraction,
            confidence=confidence,
            reasoning=reasoning,
            risk_factors=risk_factors,
            estimated_value=best_edge,
            market_sentiment=market_sentiment,
            strategic_advantage=strategic_advantage
        )

        self.decision_history.append(decision)
        if len(self.decision_history) > 100:
            self.decision_history.pop(0)

        return decision

    def _assess_market_sentiment(self, odds_data: Dict[str, Any]) -> str:
        """AI评估市场情绪 (L5)"""
        home = odds_data.get("home", 2.0)
        away = odds_data.get("away", 2.0)
        draw = odds_data.get("draw", 3.0)

        if home < 1.5:
            return "强烈倾向主队"
        elif away < 1.5:
            return "强烈倾向客队"
        elif abs(home - away) < 0.5:
            return "市场均衡"
        elif home < away:
            return "略微倾向主队"
        else:
            return "略微倾向客队"

    def _generate_ai_reasoning(
        self, should_bet: bool, selection: str, edge: float,
        six_layer_score: float, risk_factors: List[str],
        market_sentiment: str
    ) -> str:
        """AI生成决策推理 (L5)"""
        if not should_bet:
            reasons = [
                f"价值边缘不足: {edge:.2%}",
                f"市场情绪: {market_sentiment}",
                f"六层分析: {six_layer_score:.1%}"
            ]
            if risk_factors:
                reasons.extend([f"风险: {f}" for f in risk_factors])
            return " | ".join(reasons)

        reasons = [
            f"选择: {selection}",
            f"价值边缘: {edge:.2%}",
            f"六层分析: {six_layer_score:.1%}",
            f"市场情绪: {market_sentiment}"
        ]
        if risk_factors:
            reasons.extend([f"风险: {f}" for f in risk_factors])
        return " | ".join(reasons)

    def ai_predict_market_trend(
        self,
        historical_odds: List[Dict[str, Any]],
        recent_results: Optional[List[Dict[str, Any]]] = None
    ) -> MarketPrediction:
        """AI预测市场走势 (L5完全AI原生)"""
        if len(historical_odds) < 3:
            return MarketPrediction(
                direction="unknown",
                confidence=0.5,
                reasoning="历史数据不足",
                volatility=0.1,
                actionable_insight="建议收集更多数据"
            )

        changes = []
        for i in range(1, len(historical_odds)):
            prev = historical_odds[i-1]
            curr = historical_odds[i]
            home_change = curr.get("home", 2.0) - prev.get("home", 2.0)
            away_change = curr.get("away", 2.0) - prev.get("away", 2.0)
            changes.append(home_change + away_change)

        avg_change = sum(changes) / len(changes)
        volatility = max(0.05, abs(avg_change))

        if avg_change > 0.08:
            direction = "rising"
            confidence = min(0.85, 0.6 + abs(avg_change) * 2)
            insight = "赔率上升趋势，考虑降低仓位"
        elif avg_change < -0.08:
            direction = "falling"
            confidence = min(0.85, 0.6 + abs(avg_change) * 2)
            insight = "赔率下降趋势，考虑把握机会"
        else:
            direction = "stable"
            confidence = 0.7
            insight = "市场稳定，维持现有策略"

        prediction = MarketPrediction(
            direction=direction,
            confidence=confidence,
            reasoning=f"近{len(historical_odds)}次赔率平均变化: {avg_change:.3f}",
            volatility=volatility,
            actionable_insight=insight
        )

        self.prediction_history.append(prediction)
        if len(self.prediction_history) > 50:
            self.prediction_history.pop(0)

        return prediction

    def can_execute(
        self,
        odds: float,
        kelly_fraction: float,
        confidence: float,
        match_id: str,
    ) -> Dict[str, Any]:
        """AI驱动的执行检查 (L5)"""
        date_str = datetime.now().strftime("%Y-%m-%d")

        daily_limit = self.bankroll.config.max_daily_bets if self.bankroll else 10
        today_count = self.daily_bets.get(date_str, 0)
        if today_count >= daily_limit:
            return {
                "can_execute": False,
                "reason": f"已达到每日投注上限 ({daily_limit})",
                "ai_assessment": "AI建议: 今日投注已达上限，避免疲劳决策"
            }

        if kelly_fraction <= 0:
            return {
                "can_execute": False,
                "reason": "Kelly值为负或零",
                "ai_assessment": "AI建议: 无正向价值，跳过"
            }

        if odds < 1.01:
            return {
                "can_execute": False,
                "reason": "赔率过低",
                "ai_assessment": "AI建议: 赔率不足，无投注价值"
            }

        if confidence < 0.4:
            return {
                "can_execute": False,
                "reason": "置信度过低",
                "ai_assessment": "AI建议: 信心不足，等待更明确的信号"
            }

        risk_warnings = []
        if kelly_fraction > 0.1:
            risk_warnings.append("Kelly值较高，建议适当降低")
        if odds > 6:
            risk_warnings.append("高赔率，风险较大")

        return {
            "can_execute": True,
            "reason": "所有检查通过",
            "ai_assessment": "AI建议: 可以执行，注意风险控制" if not risk_warnings else
                           f"AI建议: 可以执行，{'; '.join(risk_warnings)}",
            "risk_warnings": risk_warnings
        }

    def execute_bet(
        self,
        match_id: str,
        odds: float,
        kelly_fraction: float,
        confidence: float,
        selection: str,
        ai_decision: Optional[AIBettingDecision] = None
    ) -> ExecutionResult:
        """AI驱动的投注执行 (L5完全AI原生)"""
        date_str = datetime.now().strftime("%Y-%m-%d")

        check = self.can_execute(odds, kelly_fraction, confidence, match_id)
        if not check["can_execute"]:
            return ExecutionResult(
                success=False,
                message=check["reason"],
                risk_assessment=check
            )

        if self.bankroll:
            stake = self.bankroll.calculate_stake(kelly_fraction, confidence)
        else:
            stake = kelly_fraction * 10000

        self._increment_daily(date_str)

        new_balance = self.bankroll.balance - stake if self.bankroll else 10000 - stake

        bet_id = f"bet_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return ExecutionResult(
            success=True,
            bet_id=bet_id,
            message=f"投注执行成功 (AI决策: {'是' if ai_decision and ai_decision.should_bet else '否'})",
            stake=stake,
            odds=odds,
            new_balance=new_balance,
            risk_assessment=check,
            ai_decision=ai_decision
        )

    def _check_daily_limit(self, date_str: str) -> bool:
        if self.bankroll:
            today_count = self.daily_bets.get(date_str, 0)
            return today_count < self.bankroll.config.max_daily_bets
        return True

    def _increment_daily(self, date_str: str) -> None:
        self.daily_bets[date_str] = self.daily_bets.get(date_str, 0) + 1

    def get_ai_decision_summary(self, limit: int = 20) -> Dict[str, Any]:
        """获取AI决策历史总结 (L5)"""
        if not self.decision_history:
            return {
                "total_decisions": 0,
                "success_rate": 0,
                "average_confidence": 0,
                "recommendations": ["数据不足"]
            }

        decisions = self.decision_history[-limit:]
        total = len(decisions)
        bets_made = sum(1 for d in decisions if d.should_bet)
        avg_confidence = sum(d.confidence for d in decisions) / total

        recommendations = []
        if avg_confidence < 0.5:
            recommendations.append("建议提高决策阈值")
        if bets_made / total < 0.3:
            recommendations.append("可以尝试提高决策频率")
        elif bets_made / total > 0.7:
            recommendations.append("建议降低决策频率")

        return {
            "total_decisions": total,
            "bets_made": bets_made,
            "bet_rate": bets_made / total,
            "average_confidence": avg_confidence,
            "recommendations": recommendations or ["策略表现稳定"]
        }


_EXECUTION_ENGINE = None


def get_execution_engine(bankroll_manager=None, recorder=None) -> ExecutionEngine:
    """获取执行引擎单例"""
    global _EXECUTION_ENGINE
    if _EXECUTION_ENGINE is None:
        _EXECUTION_ENGINE = ExecutionEngine(bankroll_manager, recorder)
    return _EXECUTION_ENGINE


EXECUTION_ENGINE = get_execution_engine()

