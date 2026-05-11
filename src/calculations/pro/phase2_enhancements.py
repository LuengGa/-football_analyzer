#!/usr/bin/env python3
"""
AFA v8.2 - Phase 2 增强功能模块
实现：
 1. 亚洲让球深度支持 (多种让球数)
 2. 角球玩法深度预测
 3. 精确总进球数赔率
 4. 简单串关组合支持
"""
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.calculations.pro.domain_models import BetType


# =============================================================================
# 1. 亚洲让球支持增强
# =============================================================================

class AsianHandicap(Enum):
    """亚洲让球类型"""
    AH_0_0 = "0.0"
    AH_0_25 = "0.25"
    AH_0_5 = "0.5"
    AH_0_75 = "0.75"
    AH_1_0 = "1.0"
    AH_1_25 = "1.25"
    AH_1_5 = "1.5"
    AH_1_75 = "1.75"
    AH_2_0 = "2.0"
    AH_2_25 = "2.25"
    AH_2_5 = "2.5"
    AH_2_75 = "2.75"
    AH_3_0 = "3.0"
    AH_MINUS_0_25 = "-0.25"
    AH_MINUS_0_5 = "-0.5"
    AH_MINUS_0_75 = "-0.75"
    AH_MINUS_1_0 = "-1.0"


@dataclass
class AsianHandicapResult:
    """亚洲让球结果"""
    handicap: float
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    return_rate: float


class AsianHandicapCalculator:
    """亚洲让球计算引擎"""
    
    def __init__(self):
        self.max_goals = 10
    
    def poisson_prob(self, lambda_h: float, lambda_a: float, h: int, a: int) -> float:
        prob_h = (math.exp(-lambda_h) * (lambda_h ** h)) / math.factorial(h)
        prob_a = (math.exp(-lambda_a) * (lambda_a ** a)) / math.factorial(a)
        return prob_h * prob_a
    
    def calculate_handicap(self, expected_home: float, expected_away: float, handicap: float) -> AsianHandicapResult:
        home_total = 0.0
        draw_total = 0.0
        away_total = 0.0
        
        for h in range(self.max_goals + 1):
            for a in range(self.max_goals + 1):
                prob = self.poisson_prob(expected_home, expected_away, h, a)
                effective_diff = h - a + handicap
                
                if effective_diff > 0.01:
                    home_total += prob
                elif effective_diff < -0.01:
                    away_total += prob
                else:
                    draw_total += prob
        
        if abs(handicap % 0.5 - 0.25) < 0.01 or abs(handicap % 0.5 - 0.75) < 0.01:
            half_handicap_1 = math.floor(handicap * 2) / 2
            half_handicap_2 = half_handicap_1 + 0.5
            
            result_1 = self._calculate_simple_handicap(expected_home, expected_away, half_handicap_1)
            result_2 = self._calculate_simple_handicap(expected_home, expected_away, half_handicap_2)
            
            return AsianHandicapResult(
                handicap=handicap,
                home_win_prob=(result_1.home_win_prob + result_2.home_win_prob) / 2,
                draw_prob=(result_1.draw_prob + result_2.draw_prob) / 2,
                away_win_prob=(result_1.away_win_prob + result_2.away_win_prob) / 2,
                return_rate=0.0
            )
        
        return AsianHandicapResult(
            handicap=handicap,
            home_win_prob=home_total,
            draw_prob=draw_total,
            away_win_prob=away_total,
            return_rate=0.0
        )
    
    def _calculate_simple_handicap(self, expected_home: float, expected_away: float, handicap: float) -> AsianHandicapResult:
        home_total = 0.0
        draw_total = 0.0
        away_total = 0.0
        
        for h in range(self.max_goals + 1):
            for a in range(self.max_goals + 1):
                prob = self.poisson_prob(expected_home, expected_away, h, a)
                diff = h - a + handicap
                
                if diff > 0.01:
                    home_total += prob
                elif diff < -0.01:
                    away_total += prob
                else:
                    draw_total += prob
        
        return AsianHandicapResult(
            handicap=handicap,
            home_win_prob=home_total,
            draw_prob=draw_total,
            away_win_prob=away_total,
            return_rate=0.0
        )
    
    def get_all_handicaps(self, expected_home: float, expected_away: float) -> Dict[float, AsianHandicapResult]:
        results = {}
        common_handicaps = [-2.0, -1.75, -1.5, -1.25, -1.0, -0.75, -0.5, -0.25,
                            0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0,
                            2.25, 2.5, 2.75, 3.0]
        
        for hc in common_handicaps:
            results[hc] = self.calculate_handicap(expected_home, expected_away, hc)
        
        return results


# =============================================================================
# 2. 角球玩法深度预测
# =============================================================================

@dataclass
class CornersPrediction:
    expected_home_corners: float
    expected_away_corners: float
    expected_total_corners: float
    over_under_probs: Dict[str, float]
    corner_handicap_probs: Dict[float, AsianHandicapResult]
    exact_corner_probs: Dict[int, float]


class CornersPredictor:
    """角球预测引擎"""
    
    def __init__(self):
        self.max_corners = 25
        self.corner_ratio_home = 3.0
        self.corner_ratio_away = 2.8
        self.corner_intercept = 4.0
    
    def predict_from_goals(self, expected_home_goals: float, expected_away_goals: float, league_multiplier: float = 1.0) -> CornersPrediction:
        exp_home = (expected_home_goals * self.corner_ratio_home + expected_away_goals * 0.5 + self.corner_intercept / 2) * league_multiplier
        exp_away = (expected_away_goals * self.corner_ratio_away + expected_home_goals * 0.5 + self.corner_intercept / 2) * league_multiplier
        exp_total = exp_home + exp_away
        
        exact_probs = self._calculate_corner_distribution(exp_home, exp_away)
        ou_probs = self._calculate_over_under(exact_probs)
        
        ah_calc = AsianHandicapCalculator()
        handicap_probs = {}
        for hc in [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]:
            handicap_probs[hc] = ah_calc.calculate_handicap(exp_home, exp_away, hc)
        
        return CornersPrediction(
            expected_home_corners=exp_home,
            expected_away_corners=exp_away,
            expected_total_corners=exp_total,
            over_under_probs=ou_probs,
            corner_handicap_probs=handicap_probs,
            exact_corner_probs=exact_probs
        )
    
    def _calculate_corner_distribution(self, lambda_h: float, lambda_a: float) -> Dict[int, float]:
        total_dist = defaultdict(float)
        for h in range(self.max_corners + 1):
            for a in range(self.max_corners + 1):
                prob_h = self._poisson(lambda_h, h)
                prob_a = self._poisson(lambda_a, a)
                total = h + a
                total_dist[total] += prob_h * prob_a
        return dict(total_dist)
    
    def _calculate_over_under(self, corner_dist: Dict[int, float]) -> Dict[str, float]:
        result = {}
        lines = [6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5]
        for line in lines:
            over_prob = sum(p for c, p in corner_dist.items() if c > int(line))
            under_prob = 1.0 - over_prob
            result[f"over_{line:.1f}".replace('.', '_')] = over_prob
            result[f"under_{line:.1f}".replace('.', '_')] = under_prob
        return result
    
    def _poisson(self, lam: float, k: int) -> float:
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam ** k)) / math.factorial(k)


# =============================================================================
# 3. 精确总进球数赔率
# =============================================================================

@dataclass
class ExactGoalsOdds:
    goal_count: int
    probability: float
    fair_odds: float
    implied_prob_from_odds: Optional[float] = None


class ExactGoalsCalculator:
    def __init__(self):
        self.max_goals = 15
    
    def calculate(self, expected_home: float, expected_away: float) -> List[ExactGoalsOdds]:
        results = []
        for total_goals in range(self.max_goals + 1):
            prob = self._calculate_total_goals_prob(expected_home, expected_away, total_goals)
            if prob > 0.0001:
                fair_odds = 1.0 / prob if prob > 0 else float('inf')
                results.append(ExactGoalsOdds(
                    goal_count=total_goals,
                    probability=prob,
                    fair_odds=fair_odds
                ))
        if self.max_goals >= 5:
            prob_5_plus = sum(r.probability for r in results if r.goal_count >= 5)
            if prob_5_plus > 0.0001:
                results.append(ExactGoalsOdds(
                    goal_count=-1,
                    probability=prob_5_plus,
                    fair_odds=1.0 / prob_5_plus
                ))
        return sorted(results, key=lambda x: x.goal_count)
    
    def _calculate_total_goals_prob(self, lambda_h: float, lambda_a: float, total: int) -> float:
        total_prob = 0.0
        for h in range(0, total + 1):
            a = total - h
            if a >= 0:
                prob_h = self._poisson(lambda_h, h)
                prob_a = self._poisson(lambda_a, a)
                total_prob += prob_h * prob_a
        return total_prob
    
    def _poisson(self, lam: float, k: int) -> float:
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam ** k)) / math.factorial(k)


# =============================================================================
# 4. 简单串关组合支持
# =============================================================================

@dataclass
class BetLeg:
    match_id: str
    home_team: str
    away_team: str
    bet_type: BetType
    odds: float
    predicted_prob: float
    is_winner: Optional[bool] = None


@dataclass
class AccumulatorBet:
    legs: List[BetLeg]
    combined_odds: float
    total_stake: float
    potential_return: float
    win_probability: float
    expected_value: float


class AccumulatorEngine:
    def __init__(self):
        self.max_legs = 8
    
    def create_accumulator(self, legs: List[BetLeg], stake: float = 10.0) -> AccumulatorBet:
        if len(legs) > self.max_legs:
            raise ValueError(f"串关最多支持{self.max_legs}注")
        
        combined_odds = 1.0
        win_prob = 1.0
        for leg in legs:
            combined_odds *= leg.odds
            win_prob *= leg.predicted_prob
        
        potential_return = stake * combined_odds
        expected_value = (win_prob * potential_return) - stake
        
        return AccumulatorBet(
            legs=legs,
            combined_odds=combined_odds,
            total_stake=stake,
            potential_return=potential_return,
            win_probability=win_prob,
            expected_value=expected_value
        )
    
    def calculate_optimal_stakes(self, legs: List[BetLeg], total_budget: float = 100.0) -> List[Tuple[BetLeg, float]]:
        stakes = []
        for leg in legs:
            kelly_fraction = (leg.predicted_prob * leg.odds - 1.0) / (leg.odds - 1.0)
            kelly_fraction = max(0.0, min(kelly_fraction, 0.25))
            stake = total_budget * kelly_fraction
            stakes.append((leg, stake))
        return stakes
    
    def analyze_risk(self, accumulator: AccumulatorBet) -> Dict[str, Any]:
        num_legs = len(accumulator.legs)
        avg_odds = accumulator.combined_odds ** (1.0 / num_legs)
        avg_prob = accumulator.win_probability ** (1.0 / num_legs)
        return {
            "number_of_legs": num_legs,
            "average_odds_per_leg": avg_odds,
            "average_prob_per_leg": avg_prob,
            "variance_index": accumulator.combined_odds * num_legs,
            "risk_level": "Low" if num_legs <= 2 else "Medium" if num_legs <= 4 else "High"
        }


# =============================================================================
# 综合演示
# =============================================================================

def demo_phase2_enhancements():
    print("="*80)
    print("🚀 AFA v8.2 - Phase 2 增强功能演示")
    print("="*80)
    
    home_exp, away_exp = 1.8, 1.2
    print(f"\n📊 测试场景: 主队预期进球 {home_exp}, 客队预期进球 {away_exp}")
    
    print("\n" + "="*60)
    print("1️⃣  亚洲让球深度支持")
    print("="*60)
    ah_calc = AsianHandicapCalculator()
    all_ah = ah_calc.get_all_handicaps(home_exp, away_exp)
    
    print("  让球  | 主胜概率  | 走水概率  | 客胜概率")
    print("-"*55)
    for hc in [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
        if hc in all_ah:
            res = all_ah[hc]
            sign = "+" if hc > 0 else ""
            print(f"  {sign}{hc:4.2f} | {res.home_win_prob*100:8.1f}% | {res.draw_prob*100:8.1f}% | {res.away_win_prob*100:8.1f}%")
    
    print("\n" + "="*60)
    print("2️⃣  角球玩法深度预测")
    print("="*60)
    corner_pred = CornersPredictor()
    corner_res = corner_pred.predict_from_goals(home_exp, away_exp)
    
    print(f"  预期角球: 主 {corner_res.expected_home_corners:.1f}, 客 {corner_res.expected_away_corners:.1f}, 总计 {corner_res.expected_total_corners:.1f}")
    print("\n  角球大小球:")
    for line in ['over_9_5', 'under_9_5', 'over_10_5', 'under_10_5']:
        if line in corner_res.over_under_probs:
            line_name = line.replace('_', '.').replace('over', '大').replace('under', '小')
            print(f"    {line_name}: {corner_res.over_under_probs[line]*100:.1f}%")
    
    print("\n" + "="*60)
    print("3️⃣  精确总进球数赔率")
    print("="*60)
    goals_calc = ExactGoalsCalculator()
    goals_odds = goals_calc.calculate(home_exp, away_exp)
    
    print("  进球数 | 概率     | 公平赔率")
    print("-"*35)
    for odd in goals_odds:
        if odd.goal_count == -1:
            print(f"    5+  | {odd.probability*100:6.1f}% | {odd.fair_odds:7.2f}")
        elif odd.goal_count <= 7:
            print(f"    {odd.goal_count:2d}  | {odd.probability*100:6.1f}% | {odd.fair_odds:7.2f}")
    
    print("\n" + "="*60)
    print("4️⃣  简单串关组合支持")
    print("="*60)
    acc_engine = AccumulatorEngine()
    
    legs = [
        BetLeg("match_1", "Bayern", "Dortmund", BetType.HOME, 1.85, 0.52),
        BetLeg("match_2", "Man City", "Arsenal", BetType.OVER_2_5, 1.75, 0.58),
        BetLeg("match_3", "Real Madrid", "Barca", BetType.BOTH_TEAMS_TO_SCORE_YES, 1.90, 0.55),
    ]
    
    acc = acc_engine.create_accumulator(legs, stake=100.0)
    print(f"  串关注数: {len(acc.legs)}")
    print(f"  组合赔率: {acc.combined_odds:.2f}")
    print(f"  投入本金: {acc.total_stake:.0f}元")
    print(f"  潜在奖金: {acc.potential_return:.0f}元")
    print(f"  胜率: {acc.win_probability*100:.1f}%")
    print(f"  期望值: {acc.expected_value:.1f}元")
    
    risk = acc_engine.analyze_risk(acc)
    print(f"  风险等级: {risk['risk_level']}")
    
    print("\n" + "="*80)
    print("✅ Phase 2 演示完成！")
    print("="*80)


if __name__ == '__main__':
    demo_phase2_enhancements()
