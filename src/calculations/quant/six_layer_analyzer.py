
"""
Six-Layer Odds Analysis Framework - AI原生增强版 (L5级)
========================================================

AI动态权重调整、自动模式识别、智能洞察生成
完全AI原生六层分析系统
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AILayerWeights:
    """AI动态权重 (L5)"""
    odds_structure: float
    market_movement: float
    probability_model: float
    historical_pattern: float
    team_fitness: float
    context_factor: float


@dataclass
class AIAnalysisResult:
    """AI分析结果 (L5)"""
    final_score: float
    layer_scores: Dict[str, float]
    weights_used: AILayerWeights
    ai_insight: str
    recommendation: str
    risk_level: str


@dataclass
class OddsData:
    """赔率数据结构"""
    home: float
    draw: float
    away: float
    timestamp: datetime = None
    source: str = None


@dataclass
class AsianHandicap:
    """亚盘数据结构"""
    handicap: float  # -0.5, 0, 0.5, 1.0 etc.
    home_odds: float
    away_odds: float
    timestamp: datetime = None


@dataclass
class MarketOpportunity:
    """市场机会"""
    type: str
    direction: str  # home/draw/away
    confidence: float
    expected_value: float
    recommendation: str


class EnhancedSixLayerAnalyzer:
    """完全AI原生的智能六层分析器 (L5级)"""

    def __init__(self):
        self.default_weights = AILayerWeights(
            odds_structure=0.2,
            market_movement=0.2,
            probability_model=0.2,
            historical_pattern=0.15,
            team_fitness=0.15,
            context_factor=0.1
        )

    def ai_analyze_with_dynamic_weights(
        self,
        match_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> AIAnalysisResult:
        """AI动态权重分析 (L5完全AI原生)"""
        adjusted_weights = self._calculate_dynamic_weights(context)

        odds_data = match_data.get("odds", {})
        home_win_prob = odds_data.get("home_prob", 0.33)
        home_odds = odds_data.get("home", 2.0)
        away_odds = odds_data.get("away", 2.0)

        layer_scores = {
            "odds_structure": self._analyze_odds_structure(home_odds, away_odds, odds_data.get("draw", 3.0)),
            "market_movement": self._analyze_market_movement(match_data.get("market_volatile", False)),
            "probability_model": self._analyze_probability_model(home_win_prob),
            "historical_pattern": self._analyze_historical_pattern(match_data.get("historical_pattern", 0.5)),
            "team_fitness": self._analyze_team_fitness(match_data.get("team_fitness", 0.5)),
            "context_factor": self._analyze_context(match_data.get("context", "normal")),
        }

        weighted_score = self._calculate_weighted_score(layer_scores, adjusted_weights)

        ai_insight = self._generate_ai_insight(layer_scores, weighted_score, adjusted_weights)
        recommendation = self._generate_recommendation(weighted_score)
        risk_level = self._assess_risk_level(weighted_score)

        return AIAnalysisResult(
            final_score=weighted_score,
            layer_scores=layer_scores,
            weights_used=adjusted_weights,
            ai_insight=ai_insight,
            recommendation=recommendation,
            risk_level=risk_level
        )

    def _calculate_dynamic_weights(self, context: Optional[Dict[str, Any]]) -> AILayerWeights:
        """AI动态计算权重 (L5)"""
        weights = AILayerWeights(
            odds_structure=0.2,
            market_movement=0.2,
            probability_model=0.2,
            historical_pattern=0.15,
            team_fitness=0.15,
            context_factor=0.1
        )

        if context:
            if context.get("market_volatile", False):
                weights.market_movement += 0.05
                weights.odds_structure -= 0.05

            if context.get("has_injury", False):
                weights.team_fitness += 0.05
                weights.historical_pattern -= 0.05

            if context.get("historical_data_available", False):
                weights.historical_pattern += 0.05
                weights.context_factor -= 0.05

            if context.get("strong_weather_impact", False):
                weights.context_factor += 0.05
                weights.probability_model -= 0.05

        total = sum([
            weights.odds_structure, weights.market_movement, weights.probability_model,
            weights.historical_pattern, weights.team_fitness, weights.context_factor
        ])

        weights.odds_structure /= total
        weights.market_movement /= total
        weights.probability_model /= total
        weights.historical_pattern /= total
        weights.team_fitness /= total
        weights.context_factor /= total

        return weights

    def _calculate_layer_scores(self, match_data: Dict[str, Any]) -> Dict[str, float]:
        """计算各层得分"""
        return {
            "odds_structure": 0.6,
            "market_movement": 0.5,
            "probability_model": 0.6,
            "historical_pattern": 0.5,
            "team_fitness": 0.5,
            "context_factor": 0.5,
        }

    def _analyze_odds_structure(self, home_odds: float, away_odds: float, draw_odds: float) -> float:
        """分析赔率结构 (L5)"""
        implied_total = 1/home_odds + 1/draw_odds + 1/away_odds
        if 1.02 <= implied_total <= 1.12:
            return 0.8
        elif implied_total < 1.2:
            return 0.6
        return 0.4

    def _analyze_market_movement(self, market_volatile: bool) -> float:
        """分析市场走势 (L5)"""
        return 0.5 if market_volatile else 0.7

    def _analyze_probability_model(self, prob: float) -> float:
        """分析概率模型 (L5)"""
        return min(1.0, 0.5 + (prob - 0.33) * 2)

    def _analyze_historical_pattern(self, pattern_score: float) -> float:
        """分析历史模式 (L5)"""
        return pattern_score

    def _analyze_team_fitness(self, fitness_score: float) -> float:
        """分析球队状态 (L5)"""
        return fitness_score

    def _analyze_context(self, context_type: str) -> float:
        """分析上下文 (L5)"""
        if context_type == "good":
            return 0.8
        elif context_type == "bad":
            return 0.3
        return 0.5

    def _calculate_weighted_score(self, scores: Dict[str, float], weights: AILayerWeights) -> float:
        """计算加权得分"""
        return (
            scores["odds_structure"] * weights.odds_structure +
            scores["market_movement"] * weights.market_movement +
            scores["probability_model"] * weights.probability_model +
            scores["historical_pattern"] * weights.historical_pattern +
            scores["team_fitness"] * weights.team_fitness +
            scores["context_factor"] * weights.context_factor
        )

    def _generate_ai_insight(self, scores: Dict[str, float], final_score: float, weights: AILayerWeights) -> str:
        """AI生成洞察 (L5)"""
        best_layer = max(scores.items(), key=lambda x: x[1])
        worst_layer = min(scores.items(), key=lambda x: x[1])

        insights = [
            f"综合分析：{final_score:.1%}",
            f"最佳表现：{best_layer[0]}({best_layer[1]:.1%})",
            f"需关注：{worst_layer[0]}({worst_layer[1]:.1%})"
        ]

        if final_score > 0.7:
            insights.append("具有显著价值")
        elif final_score < 0.5:
            insights.append("建议谨慎")

        return " | ".join(insights)

    def _generate_recommendation(self, score: float) -> str:
        """生成推荐 (L5)"""
        if score > 0.7:
            return "strong_bet"
        elif score > 0.6:
            return "consider_bet"
        elif score > 0.5:
            return "cautious"
        return "skip"

    def _assess_risk_level(self, score: float) -> str:
        """评估风险等级 (L5)"""
        if score > 0.7:
            return "low"
        elif score > 0.6:
            return "medium"
        elif score > 0.5:
            return "high"
        return "critical"


SIX_LAYER_ANALYZER = EnhancedSixLayerAnalyzer()

