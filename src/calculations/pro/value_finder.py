"""
Value Bet Finder - 专业价值投注发现器
"""

from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .domain_models import BetType

@dataclass
class ValueBet:
    """价值投注"""
    bet_type: BetType
    odds: float
    predicted_prob: float
    implied_prob: float
    value_score: float
    confidence: float
    expected_value: float
    edge: float

class ValueBetFinder:
    """专业价值投注发现器"""
    
    def __init__(self):
        self.min_value_threshold = 0.03  # 最小价值阈值
        self.min_edge = 0.02      # 最小优势
        self.confidence_weight = 0.5
    
    def calculate_implied_probability(self, odds: float) -> float:
        """计算隐含概率"""
        if odds <= 1.0:
            return 0.0
        return 1.0 / odds
    
    def calculate_expected_value(self, predicted_prob: float, odds: float) -> float:
        """计算期望价值"""
        implied_prob = self.calculate_implied_probability(odds)
        # EV = (p*(odds-1) - (1-p)*1
        return predicted_prob * (odds - 1) - (1 - predicted_prob)
    
    def find_value_bets(
        self,
        odds_dict: Dict[str, float],
        predicted_probs: Dict[str, float],
        min_value_threshold: Optional[float] = None
    ) -> List[ValueBet]:
        """
        发现价值投注
        
        Args:
            odds_dict: 赔率字典
            predicted_probs: 预测概率字典
        
        Returns:
            价值投注列表
        """
        threshold = min_value_threshold if min_value_threshold else self.min_value_threshold
        value_bets = []
        
        # 胜平负
        for outcome in ['home', 'draw', 'away']:
            odds = odds_dict.get(outcome, 0.0)
            if odds <= 1.0:
                continue
            
            pred_prob = predicted_probs.get(outcome, 0.0)
            implied_prob = self.calculate_implied_probability(odds)
            edge = pred_prob - implied_prob
            ev = self.calculate_expected_value(pred_prob, odds)
            value_score = edge * 100
            
            if edge > threshold:
                bet_type_map = {
                    'home': BetType.HOME,
                    'draw': BetType.DRAW,
                    'away': BetType.AWAY
                }
                
                value_bets.append(ValueBet(
                    bet_type=bet_type_map[outcome],
                    odds=odds,
                    predicted_prob=pred_prob,
                    implied_prob=implied_prob,
                    value_score=value_score,
                    confidence=min(1.0, edge * 5),
                    expected_value=ev,
                    edge=edge
                ))
        
        # 按价值排序
        value_bets.sort(key=lambda x: x.value_score, reverse=True)
        return value_bets
    
    def find_over_under_value(
        self,
        over_odds: float,
        under_odds: float,
        predicted_over_prob: float,
        predicted_under_prob: float
    ) -> Optional[ValueBet]:
        """
        发现大小球价值投注
        
        Args:
            over_odds: 大球赔率
            under_odds: 小球赔率
            predicted_over_prob: 预测大球概率
            predicted_under_prob: 预测小球概率
        
        Returns:
            最佳价值投注
        """
        best_bet = None
        
        # 检查大球
        if over_odds > 1.0:
            over_implied = self.calculate_implied_probability(over_odds)
            over_edge = predicted_over_prob - over_implied
            if over_edge > self.min_value_threshold:
                over_ev = self.calculate_expected_value(predicted_over_prob, over_odds)
                best_bet = ValueBet(
                    bet_type=BetType.OVER_2_5,
                    odds=over_odds,
                    predicted_prob=predicted_over_prob,
                    implied_prob=over_implied,
                    value_score=over_edge * 100,
                    confidence=min(1.0, over_edge * 5),
                    expected_value=over_ev,
                    edge=over_edge
                )
        
        # 检查小球
        if under_odds > 1.0:
            under_implied = self.calculate_implied_probability(under_odds)
            under_edge = predicted_under_prob - under_implied
            if under_edge > self.min_value_threshold:
                under_ev = self.calculate_expected_value(predicted_under_prob, under_odds)
                
                if best_bet is None or under_edge > best_bet.edge:
                    best_bet = ValueBet(
                        bet_type=BetType.UNDER_2_5,
                        odds=under_odds,
                        predicted_prob=predicted_under_prob,
                        implied_prob=under_implied,
                        value_score=under_edge * 100,
                        confidence=min(1.0, under_edge * 5),
                        expected_value=under_ev,
                        edge=under_edge
                    )
        
        return best_bet
    
    def get_best_value_bet(self, value_bets: List[ValueBet]) -> Optional[ValueBet]:
        """获取最佳价值投注"""
        if not value_bets:
            return None
        return value_bets[0]
    
    def print_value_bet(self, vb: ValueBet):
        """打印价值投注"""
        print(f"\n🎯 发现价值投注: {vb.bet_type.value}")
        print(f"   赔率: {vb.odds:.2f}")
        print(f"   预测概率: {vb.predicted_prob:.1%}")
        print(f"   隐含概率: {vb.implied_prob:.1%}")
        print(f"   优势: {vb.edge:.2%}")
        print(f"   期望价值: {vb.expected_value:.3f}")
        print(f"   信心: {vb.confidence:.1%}")
