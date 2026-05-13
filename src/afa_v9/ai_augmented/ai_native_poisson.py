"""
AFA v9.0 AI原生Poisson预测模型
=================================

完全整合158,971场历史数据的AI预测模型

特点：
1. 历史ELO驱动
2. 动态调整参数
3. AI洞察生成
4. 语义匹配历史比赛
5. 球队画像计算
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from collections import defaultdict
import math

from src.afa_v9.ai_augmented.ai_native_historical import (
    AI_NATIVE_SYSTEM,
    CompleteAINativeSystem,
)

logger = logging.getLogger(__name__)


@dataclass
class AIPredictionContext:
    """AI预测上下文"""
    has_injury: bool = False
    weather_impact: str = "normal"
    recent_form: List[bool] = None  # type: ignore[assignment]
    home_advantage_active: bool = True
    historical_data_available: bool = True
    team_morale: str = "normal"
    league_phase: str = "regular"


@dataclass
class AIPredictionResult:
    """AI预测结果"""
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    expected_home_goals: float
    expected_away_goals: float
    confidence_score: float
    ai_insights: List[str]
    historical_matches: List[Dict[str, Any]]
    risk_level: str
    value_opportunity: Optional[float]


class AINativePoissonModel:
    """
    完全AI原生的Poisson预测模型
    
    特点：
    1. 使用158,971场历史数据训练
    2. 动态计算球队攻防强度
    3. ELO调整权重
    4. AI洞察生成
    5. 风险评估
    """
    
    def __init__(self, ai_system: Optional[CompleteAINativeSystem] = None):
        self.ai_system = ai_system or AI_NATIVE_SYSTEM
        self._initialized = False
    
    def initialize(self):
        """初始化AI系统"""
        if self._initialized:
            return
        self.ai_system.initialize()
        self._initialized = True
    
    def _poisson_prob(self, lambda_: float, k: int) -> float:
        """Poisson概率"""
        return math.exp(-lambda_) * (lambda_ ** k) / math.factorial(k)
    
    def _compute_match_probabilities(self, home_lambda: float, away_lambda: float) -> Tuple[float, float, float]:
        """计算胜负平概率"""
        max_goals = 10
        
        home_win = 0.0
        draw = 0.0
        away_win = 0.0
        
        for hg in range(max_goals + 1):
            for ag in range(max_goals + 1):
                prob = self._poisson_prob(home_lambda, hg) * self._poisson_prob(away_lambda, ag)
                
                if hg > ag:
                    home_win += prob
                elif hg == ag:
                    draw += prob
                else:
                    away_win += prob
        
        total = home_win + draw + away_win
        if total > 0:
            home_win /= total
            draw /= total
            away_win /= total
        
        return home_win, draw, away_win
    
    def ai_predict_with_adjustments(
        self,
        home_team: str,
        away_team: str,
        context: Optional[AIPredictionContext] = None
    ) -> AIPredictionResult:
        """
        AI增强的预测
        
        使用历史数据、ELO、模式发现进行预测
        """
        self.initialize()
        context = context or AIPredictionContext()
        
        analysis = self.ai_system.get_complete_analysis(home_team, away_team, "E0")
        stats = analysis.get("historical_statistics", {})
        
        home_att = stats.get("home_attack_strength", 1.0)
        home_def = stats.get("home_defense_strength", 1.0)
        away_att = stats.get("away_attack_strength", 1.0)
        away_def = stats.get("away_defense_strength", 1.0)
        
        home_elo = stats.get("home_elo", 1500.0)
        away_elo = stats.get("away_elo", 1500.0)
        
        elo_diff = (home_elo - away_elo) / 400.0
        
        league_avg_goals = stats.get("league_avg_goals", 2.7)
        avg_home_goals = league_avg_goals * 0.55
        avg_away_goals = league_avg_goals * 0.45
        
        expected_home_goals = avg_home_goals * home_att * away_def
        expected_away_goals = avg_away_goals * away_att * home_def
        
        elo_factor = 1.0 + elo_diff * 0.2
        expected_home_goals *= elo_factor
        expected_away_goals /= elo_factor
        
        factors = analysis.get("ai_insight", {}).get("factors", {})
        home_bonus = factors.get("home_advantage", 0) + factors.get("h2h_advantage_home", 0)
        away_bonus = factors.get("away_strong", 0) + factors.get("h2h_advantage_away", 0)
        
        expected_home_goals *= (1 + home_bonus * 0.5)
        expected_away_goals *= (1 + away_bonus * 0.5)
        
        if context.weather_impact == "rain":
            expected_home_goals *= 0.9
            expected_away_goals *= 0.9
        
        if context.recent_form:
            win_rate = sum(1 for f in context.recent_form if f) / len(context.recent_form)
            form_factor = 0.8 + win_rate * 0.4
            expected_home_goals *= form_factor
        
        expected_home_goals = max(0.3, min(4.0, expected_home_goals))
        expected_away_goals = max(0.3, min(4.0, expected_away_goals))
        
        home_win_prob, draw_prob, away_win_prob = self._compute_match_probabilities(expected_home_goals, expected_away_goals)
        
        confidence_score = self._calculate_confidence(stats, factors, context)
        
        risk_level = self._assess_risk(confidence_score, home_win_prob, draw_prob, away_win_prob)
        
        ai_insights = analysis.get("ai_insight", {}).get("insights", [])
        
        historical_matches = []
        try:
            recent_home = self.ai_system.db.get_team_matches(home_team, limit=5)
            historical_matches.extend([{
                "date": m.date, "opponent": m.away_team, "result": m.result,
                "score": f"{m.home_goals}-{m.away_goals}"
            } for m in recent_home])
        except:
            pass
        
        return AIPredictionResult(
            home_win_prob=home_win_prob,
            draw_prob=draw_prob,
            away_win_prob=away_win_prob,
            expected_home_goals=expected_home_goals,
            expected_away_goals=expected_away_goals,
            confidence_score=confidence_score,
            ai_insights=ai_insights,
            historical_matches=historical_matches,
            risk_level=risk_level,
            value_opportunity=None,
        )
    
    def _calculate_confidence(
        self,
        stats: Dict[str, Any],
        factors: Dict[str, float],
        context: AIPredictionContext
    ) -> float:
        """计算信心分数"""
        confidence: float = 0.5
        
        factor_strength = sum(abs(v) for v in factors.values())
        confidence += factor_strength * 0.3
        
        home_elo = stats.get("home_elo", 1500)
        away_elo = stats.get("away_elo", 1500)
        elo_gap = abs(home_elo - away_elo) / 400.0
        confidence += min(0.2, elo_gap * 0.2)
        
        if context.historical_data_available:
            confidence += 0.1
        
        if context.recent_form and len(context.recent_form) >= 5:
            confidence += 0.05
        
        return float(min(0.95, max(0.3, confidence)))
    
    def _assess_risk(self, confidence: float, home: float, draw: float, away: float) -> str:
        """评估风险等级"""
        max_prob = max(home, draw, away)
        
        if confidence > 0.8 and max_prob > 0.6:
            return "low"
        elif confidence > 0.6 and max_prob > 0.5:
            return "medium"
        else:
            return "high"
    
    def predict_with_ai_insights(
        self,
        home_team: str,
        away_team: str,
        home_odds: float,
        draw_odds: float,
        away_odds: float
    ) -> Dict[str, Any]:
        """带AI洞察和价值计算的预测"""
        result = self.ai_predict_with_adjustments(home_team, away_team)
        
        implied_home = 1.0 / home_odds if home_odds > 0 else 0.33
        implied_draw = 1.0 / draw_odds if draw_odds > 0 else 0.33
        implied_away = 1.0 / away_odds if away_odds > 0 else 0.33
        
        value_home = result.home_win_prob - implied_home
        value_draw = result.draw_prob - implied_draw
        value_away = result.away_win_prob - implied_away
        
        best_value = max(value_home, value_draw, value_away)
        best_outcome = "home" if best_value == value_home else ("draw" if best_value == value_draw else "away")
        
        return {
            "prediction": {
                "home_win_prob": result.home_win_prob,
                "draw_prob": result.draw_prob,
                "away_win_prob": result.away_win_prob,
                "expected_home_goals": result.expected_home_goals,
                "expected_away_goals": result.expected_away_goals,
            },
            "implied_probabilities": {
                "home": implied_home,
                "draw": implied_draw,
                "away": implied_away,
            },
            "value_opportunity": {
                "home": value_home,
                "draw": value_draw,
                "away": value_away,
                "best": best_outcome,
                "best_value": best_value,
            },
            "ai_insights": result.ai_insights,
            "historical_matches": result.historical_matches,
            "confidence": result.confidence_score,
            "risk_level": result.risk_level,
        }


AI_NATIVE_POISSON_MODEL = AINativePoissonModel()

__all__ = [
    "AINativePoissonModel",
    "AIPredictionContext",
    "AIPredictionResult",
    "AI_NATIVE_POISSON_MODEL",
]
