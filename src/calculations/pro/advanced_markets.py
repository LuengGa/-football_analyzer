#!/usr/bin/env python3
"""
高级足球玩法预测模块 - 扩展版 (v8.1)
实现大小球、比分预测、角球预测等高级玩法
"""
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.calculations.pro.domain_models import BetType


@dataclass
class ScoreProbability:
    """比分概率"""
    home_goals: int
    away_goals: int
    probability: float


@dataclass
class AdvancedPredictionResult:
    """高级玩法预测结果"""
    model_name: str
    home_win_prob: float = 0.0
    draw_prob: float = 0.0
    away_win_prob: float = 0.0
    expected_home_goals: float = 0.0
    expected_away_goals: float = 0.0
    
    # 大小球概率
    over_under_probs: Dict[str, float] = field(default_factory=dict)
    
    # 双方进球
    btts_yes_prob: float = 0.0
    btts_no_prob: float = 0.0
    
    # 比分概率分布
    score_probs: List[ScoreProbability] = field(default_factory=list)
    
    # 总进球数分布
    total_goals_probs: Dict[int, float] = field(default_factory=dict)
    
    # 半全场
    htft_probs: Dict[str, float] = field(default_factory=dict)
    
    # 角球预测
    expected_corners_home: float = 0.0
    expected_corners_away: float = 0.0
    
    # 半场预测
    ht_home_prob: float = 0.0
    ht_draw_prob: float = 0.0
    ht_away_prob: float = 0.0
    expected_ht_home_goals: float = 0.0
    expected_ht_away_goals: float = 0.0


class AdvancedMarketPredictor:
    """高级玩法预测器"""
    
    def __init__(self, poisson_model=None):
        self.poisson_model = poisson_model
        self.max_goals = 10
        self.max_corners = 20
        
    def poisson_probability(self, lambda_val: float, k: int) -> float:
        """Poisson分布概率计算"""
        if lambda_val <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.exp(-lambda_val) * (lambda_val ** k)) / math.factorial(k)
        
    def predict_from_expected_goals(self, expected_home_goals: float, expected_away_goals: float) -> AdvancedPredictionResult:
        """
        基于预期进球计算所有高级玩法
        """
        result = AdvancedPredictionResult(
            model_name="AdvancedPoisson",
            expected_home_goals=expected_home_goals,
            expected_away_goals=expected_away_goals,
        )
        
        # 计算比分概率矩阵
        score_probs = []
        total_home_prob = 0.0
        total_draw_prob = 0.0
        total_away_prob = 0.0
        btts_yes = 0.0
        btts_no = 0.0
        
        total_goals_dist = {}
        
        for i in range(self.max_goals + 1):
            for j in range(self.max_goals + 1):
                prob = self.poisson_probability(expected_home_goals, i) * \
                      self.poisson_probability(expected_away_goals, j)
                
                score_probs.append(ScoreProbability(home_goals=i, away_goals=j, probability=prob))
                
                total = i + j
                if total not in total_goals_dist:
                    total_goals_dist[total] = 0.0
                total_goals_dist[total] += prob
                
                if i > j:
                    total_home_prob += prob
                elif i == j:
                    total_draw_prob += prob
                else:
                    total_away_prob += prob
                    
                if i > 0 and j > 0:
                    btts_yes += prob
                else:
                    btts_no += prob
        
        result.score_probs = sorted(score_probs, key=lambda x: -x.probability)
        result.home_win_prob = total_home_prob
        result.draw_prob = total_draw_prob
        result.away_win_prob = total_away_prob
        result.btts_yes_prob = btts_yes
        result.btts_no_prob = btts_no
        
        # 计算大小球概率
        result.over_under_probs = self._calculate_over_under(total_goals_dist)
        
        # 总进球数分布
        result.total_goals_probs = total_goals_dist
        
        # 半场预测 (假设半场进球是全场的一半)
        result = self._calculate_half_time_prediction(result, expected_home_goals, expected_away_goals)
        
        # 半全场预测
        result.htft_probs = self._calculate_htft_probs(expected_home_goals, expected_away_goals)
        
        # 角球预测 (基于简单模型)
        result.expected_corners_home = expected_home_goals * 2.5 + 3.0
        result.expected_corners_away = expected_away_goals * 2.5 + 2.5
        
        return result
        
    def _calculate_over_under(self, total_goals_dist: Dict[int, float]) -> Dict[str, float]:
        """计算各种球门线的大小球概率"""
        line_0_5_over = sum(p for g, p in total_goals_dist.items() if g >= 1)
        line_1_5_over = sum(p for g, p in total_goals_dist.items() if g >= 2)
        line_2_5_over = sum(p for g, p in total_goals_dist.items() if g >= 3)
        line_3_5_over = sum(p for g, p in total_goals_dist.items() if g >= 4)
        line_4_5_over = sum(p for g, p in total_goals_dist.items() if g >= 5)
        
        result = {
            'over_0_5': line_0_5_over,
            'under_0_5': 1 - line_0_5_over,
            'over_1_5': line_1_5_over,
            'under_1_5': 1 - line_1_5_over,
            'over_2_5': line_2_5_over,
            'under_2_5': 1 - line_2_5_over,
            'over_3_5': line_3_5_over,
            'under_3_5': 1 - line_3_5_over,
            'over_4_5': line_4_5_over,
            'under_4_5': 1 - line_4_5_over,
        }
        
        return result
        
    def _calculate_half_time_prediction(self, result: AdvancedPredictionResult, 
                                       full_home_goals: float, full_away_goals: float) -> AdvancedPredictionResult:
        """计算半场预测"""
        ht_home_goals = full_home_goals * 0.45
        ht_away_goals = full_away_goals * 0.45
        
        result.expected_ht_home_goals = ht_home_goals
        result.expected_ht_away_goals = ht_away_goals
        
        ht_home_prob = 0.0
        ht_draw_prob = 0.0
        ht_away_prob = 0.0
        
        for i in range(self.max_goals + 1):
            for j in range(self.max_goals + 1):
                prob = self.poisson_probability(ht_home_goals, i) * \
                      self.poisson_probability(ht_away_goals, j)
                if i > j:
                    ht_home_prob += prob
                elif i == j:
                    ht_draw_prob += prob
                else:
                    ht_away_prob += prob
        
        result.ht_home_prob = ht_home_prob
        result.ht_draw_prob = ht_draw_prob
        result.ht_away_prob = ht_away_prob
        
        return result
        
    def _calculate_htft_probs(self, full_home_goals: float, full_away_goals: float) -> Dict[str, float]:
        """计算半全场9种组合概率"""
        ht_home = full_home_goals * 0.45
        ht_away = full_away_goals * 0.45
        
        ft_home = full_home_goals * 0.55
        ft_away = full_away_goals * 0.55
        
        htft_names = ['htft_hh', 'htft_hd', 'htft_ha', 
                   'htft_dh', 'htft_dd', 'htft_da',
                   'htft_ah', 'htft_ad', 'htft_aa']
        htft = {name: 0.0 for name in htft_names}
        
        for i in range(self.max_goals + 1):
            for j in range(self.max_goals + 1):
                ht_prob = self.poisson_probability(ht_home, i) * \
                           self.poisson_probability(ht_away, j)
                
                for k in range(self.max_goals + 1):
                    for l in range(self.max_goals + 1):
                        ft_prob = self.poisson_probability(ft_home, k) * \
                                   self.poisson_probability(ft_away, l)
                        
                        full_home = i + k
                        full_away = j + l
                        
                        ht_result = self._get_result(i, j)
                        ft_result = self._get_result(full_home, full_away)
                        
                        key = f"htft_{ht_result}{ft_result}"
                        if key in htft:
                            htft[key] += ht_prob * ft_prob
        
        total = sum(htft.values())
        if total > 0:
            for key in htft:
                htft[key] /= total
                
        return htft
        
    def _get_result(self, home: int, away: int) -> str:
        if home > away:
            return 'h'
        elif home == away:
            return 'd'
        else:
            return 'a'
            
    def get_most_likely_scores(self, result: AdvancedPredictionResult, n: int = 5) -> List[ScoreProbability]:
        """获取最可能的比分"""
        return result.score_probs[:n]
        
    def get_correct_score_probability(self, result: AdvancedPredictionResult, home_goals: int, away_goals: int) -> float:
        """获取特定比分的概率"""
        score_prob = None
        for sp in result.score_probs:
            if sp.home_goals == home_goals and sp.away_goals == away_goals:
                score_prob = sp
                break
        return score_prob.probability if score_prob else 0.0
        
    def get_bet_type_probability(self, result: AdvancedPredictionResult, bet_type: BetType) -> float:
        """获取特定投注类型的概率"""
        if bet_type == BetType.BOTH_TEAMS_TO_SCORE_YES:
            return result.btts_yes_prob
        elif bet_type == BetType.BOTH_TEAMS_TO_SCORE_NO:
            return result.btts_no_prob
            
        key = bet_type.value
        if key in result.over_under_probs:
            return result.over_under_probs[key]
            
        if key in result.htft_probs:
            return result.htft_probs[key]
            
        if key.startswith('cs_'):
            parts = key.split('_')
            if len(parts) == 3 and parts[1] != 'other':
                hg = int(parts[1])
                ag = int(parts[2])
                return self.get_correct_score_probability(result, hg, ag)
            elif parts[1] == 'other':
                top_total = sum(sp.probability for sp in result.score_probs[:9])
                return 1.0 - top_total
                
        return 0.0


def demo_advanced_prediction():
    """演示高级玩法预测"""
    print("🎮 高级玩法预测演示")
    print("="*60)
    
    predictor = AdvancedMarketPredictor()
    
    test_cases = [
        ("强强对话 (2.1 vs 1.8)", 2.1, 1.8),
        ("主场优势 (1.8 vs 1.2)", 1.8, 1.2),
        ("进攻大战 (2.5 vs 2.2)", 2.5, 2.2),
    ]
    
    for desc, home_goals, away_goals in test_cases:
        print(f"\n📊 {desc}")
        print(f"  预期进球: 主场 {home_goals}, 客场 {away_goals}")
        
        result = predictor.predict_from_expected_goals(home_goals, away_goals)
        
        print(f"\n  🎯 胜平负: 主 {result.home_win_prob:.1%} / 平 {result.draw_prob:.1%} / 客 {result.away_win_prob:.1%}")
        
        print(f"\n  🎲 大小球:")
        print(f"    2.5球: 大 {result.over_under_probs['over_2_5']:.1%} / 小 {result.over_under_probs['under_2_5']:.1%}")
        print(f"    1.5球: 大 {result.over_under_probs['over_1_5']:.1%} / 小 {result.over_under_probs['under_1_5']:.1%}")
        print(f"    3.5球: 大 {result.over_under_probs['over_3_5']:.1%} / 小 {result.over_under_probs['under_3_5']:.1%}")
        
        print(f"\n  ⚽ 双方进球: 是 {result.btts_yes_prob:.1%} / 否 {result.btts_no_prob:.1%}")
        
        print(f"\n  🏆 最可能比分 (前5):")
        top_scores = predictor.get_most_likely_scores(result, 5)
        for i, sp in enumerate(top_scores, 1):
            print(f"    {i}. {sp.home_goals}-{sp.away_goals}: {sp.probability:.1%}")
            
        print(f"\n  🏟️  半场预测: 主 {result.ht_home_prob:.1%} / 平 {result.ht_draw_prob:.1%} / 客 {result.ht_away_prob:.1%}")
        
        print(f"\n  ⚽ 预期半场进球: 主 {result.expected_ht_home_goals:.2f} / 客 {result.expected_ht_away_goals:.2f}")
        
        print(f"\n  📐 角球预测: 主 {result.expected_corners_home:.1f} / 客 {result.expected_corners_away:.1f}")
        
        print()
        
    print("="*60)
    print("✅ 高级玩法预测演示完成!")


if __name__ == '__main__':
    demo_advanced_prediction()
