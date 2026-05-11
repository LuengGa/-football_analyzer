
"""
Kelly Criterion - AI原生增强版 (L4级)
==============================================

AI自适应调整、风险敏感度评估、组合凯利优化
高度AI原生的资金管理系统
"""

import math
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AIRiskProfile:
    """AI风险画像 (L4)"""
    risk_tolerance: str  # conservative, moderate, aggressive
    max_drawdown_tolerance: float
    confidence_weight: float
    recent_performance_weight: float
    portfolio_diversity: float


@dataclass
class AIEnhancedKellyBet:
    """AI增强凯利投注结果 (L4)"""
    bet_size: float
    kelly_fraction: float
    optimal_f: float
    win_probability: float
    odds_decimal: float
    ev_per_unit: float
    confidence: float
    ai_adjustment_reason: str
    risk_level: str


@dataclass
class KellyBet:
    """凯利投注计算结果"""
    bet_size: float  # 投注金额
    kelly_fraction: float  # 凯利比例 (0-1)
    optimal_f: float  # 理论最优 f*
    win_probability: float
    odds_decimal: float
    ev_per_unit: float  # 每单位期望价值
    confidence: float


class EnhancedKellyCriterion:
    """高度AI原生的增强版凯利准则 (L4级)"""

    def __init__(
        self,
        initial_capital: float = 10000,
        kelly_fraction: float = 0.25,
        min_bet: float = 10,
        max_bet_fraction: float = 0.1,
        bankroll_growth_target: float = 1.2
    ):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.kelly_fraction = kelly_fraction
        self.min_bet = min_bet
        self.max_bet_fraction = max_bet_fraction
        self.bankroll_growth_target = bankroll_growth_target
        self.bet_history: List[Dict] = []
        self.default_risk_profile = AIRiskProfile(
            risk_tolerance="moderate",
            max_drawdown_tolerance=0.2,
            confidence_weight=0.3,
            recent_performance_weight=0.2,
            portfolio_diversity=0.5
        )

    def ai_calculate_enhanced_kelly(
        self,
        win_prob: float,
        odds_decimal: float,
        confidence: float = 1.0,
        risk_profile: Optional[AIRiskProfile] = None,
        portfolio_context: Optional[Dict] = None
    ) -> AIEnhancedKellyBet:
        """AI增强凯利计算 (L4完全AI原生)"""
        risk_profile = risk_profile or self.default_risk_profile
        portfolio_context = portfolio_context or {}

        b = odds_decimal - 1.0
        p = win_prob
        q = 1 - p

        if b <= 0:
            optimal_f = 0.0
        else:
            optimal_f = max(0.0, (p * b - q) / b)

        adjusted_f = optimal_f * self.kelly_fraction
        adjustment_reason = []

        if confidence < 0.7:
            confidence_adjustment = confidence
            adjusted_f *= confidence_adjustment
            adjustment_reason.append(f"置信度调整: {confidence_adjustment:.1%}")

        recent_win_rate = self._calculate_recent_win_rate()
        if recent_win_rate < 0.5:
            recent_adjustment = 0.7
            adjusted_f *= recent_adjustment
            adjustment_reason.append(f"近期表现调整: {recent_adjustment:.1%}")

        if portfolio_context.get("concentration_risk", False):
            concentration_adjustment = 0.8
            adjusted_f *= concentration_adjustment
            adjustment_reason.append(f"集中度风险调整: {concentration_adjustment:.1%}")

        if portfolio_context.get("market_volatile", False):
            volatility_adjustment = 0.9
            adjusted_f *= volatility_adjustment
            adjustment_reason.append(f"市场波动调整: {volatility_adjustment:.1%}")

        if risk_profile.risk_tolerance == "conservative":
            adjusted_f *= 0.6
            adjustment_reason.append("保守型策略: 60%")
        elif risk_profile.risk_tolerance == "aggressive":
            adjusted_f *= 1.2
            adjustment_reason.append("激进型策略: 120%")

        max_f = self.max_bet_fraction
        if adjusted_f > max_f:
            adjusted_f = max_f
            adjustment_reason.append(f"超过最大投注比例: {max_f:.1%}")

        bet_size = max(self.min_bet, adjusted_f * self.current_capital)

        ev_per_unit = p * b - q

        risk_level = self._assess_risk_level(adjusted_f, confidence, win_prob)

        reason_str = " | ".join(adjustment_reason) if adjustment_reason else "标准凯利"

        return AIEnhancedKellyBet(
            bet_size=bet_size,
            kelly_fraction=adjusted_f,
            optimal_f=optimal_f,
            win_probability=win_prob,
            odds_decimal=odds_decimal,
            ev_per_unit=ev_per_unit,
            confidence=confidence,
            ai_adjustment_reason=reason_str,
            risk_level=risk_level
        )

    def _calculate_recent_win_rate(self) -> float:
        """计算近期胜率"""
        if not self.bet_history:
            return 0.5
        recent = self.bet_history[-10:]
        wins = sum(1 for bet in recent if bet.get("win", False))
        return wins / len(recent) if recent else 0.5

    def _assess_risk_level(self, fraction: float, confidence: float, win_prob: float) -> str:
        """评估风险等级 (L4)"""
        if fraction < 0.02:
            return "very_low"
        elif fraction < 0.05:
            return "low"
        elif fraction < 0.1:
            return "medium"
        elif fraction < 0.15:
            return "high"
        return "very_high"

    def calculate_kelly_bet(
        self,
        win_prob: float,
        odds_decimal: float,
        confidence: float = 1.0
    ) -> KellyBet:
        """基础凯利投注"""
        b = odds_decimal - 1.0
        p = win_prob
        q = 1 - p

        if b <= 0:
            optimal_f = 0.0
        else:
            optimal_f = max(0.0, (p * b - q) / b)

        adjusted_f = optimal_f * self.kelly_fraction

        if adjusted_f > self.max_bet_fraction:
            adjusted_f = self.max_bet_fraction

        bet_size = max(self.min_bet, adjusted_f * self.current_capital)

        ev_per_unit = p * b - q

        return KellyBet(
            bet_size=bet_size,
            kelly_fraction=adjusted_f,
            optimal_f=optimal_f,
            win_probability=win_prob,
            odds_decimal=odds_decimal,
            ev_per_unit=ev_per_unit,
            confidence=confidence
        )

    def update_capital(self, amount: float, is_win: bool = False) -> None:
        """更新资金"""
        self.current_capital += amount
        self.bet_history.append({
            "timestamp": datetime.now(),
            "amount": amount,
            "win": is_win
        })


KELLY_CRITERION = EnhancedKellyCriterion()

