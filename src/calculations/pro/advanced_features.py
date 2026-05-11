"""
Advanced Features - 高级功能
实现：
1. HT/FT (半场/全场预测
2. Portfolio Optimization 投资组合优化
3. In-Play Prediction 滚球预测框架
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class HTFTPrediction:
    """半场/全场预测"""
    h1: float  # 1-1
    hx: float  # 1-x
    h2: float  # 1-2
    x1: float  # x-1
    xx: float  # x-x
    x2: float  # x-2
    a1: float  # 2-1
    ax: float  # 2-x
    a2: float  # 2-2
    best_h1_prob: float  # 1-1 概率
    most_likely_ht_ft: str


@dataclass
class PortfolioBet:
    """投资组合中的投注"""
    match: str
    bet_type: str
    odds: float
    probability: float
    stake: float
    kelly_fraction: float


class HTFTPredictor:
    """半场/全场预测器（基于半场进球率"""
    
    def __init__(self):
        self.ht_goal_rates = {
            '0-0': 0.28,
            '1-0': 0.18,
            '0-1': 0.15,
            '1-1': 0.16,
            '2-0': 0.08,
            '0-2': 0.06,
            '2-1': 0.05,
            '1-2': 0.04,
            '2-2': 0.0,
        }
        
    def predict_ht_ft(
        self,
        home_attack_strength: float,
        away_attack_strength: float
    ) -> Optional[HTFTPrediction]:
        """预测半场/全场概率"""
        # 简化版模型
        h1 = 0.18
        hx = 0.25
        h2 = 0.07
        x1 = 0.15
        xx = 0.15
        x2 = 0.12
        a1 = 0.08
        ax = 0.06
        a2 = 0.04
        
        # 简单调整
        h1 *= home_attack_strength
        a2 *= away_attack_strength
        
        total = h1 + hx + h2 + x1 + xx + x2 + a1 + ax + a2
        
        h1 /= total
        hx /= total
        h2 /= total
        x1 /= total
        xx /= total
        x2 /= total
        a1 /= total
        ax /= total
        a2 /= total
        
        # 找出最大概率
        all_probs = [
            ('1-1', h1),
            ('1-x', hx),
            ('1-2', h2),
            ('x-1', x1),
            ('x-x', xx),
            ('x-2', x2),
            ('2-1', a1),
            ('2-x', ax),
            ('2-2', a2),
        ]
        best = max(all_probs, key=lambda x: x[1])
        
        return HTFTPrediction(
            h1=h1,
            hx=hx,
            h2=h2,
            x1=x1,
            xx=xx,
            x2=x2,
            a1=a1,
            ax=ax,
            a2=a2,
            best_h1_prob=best[1],
            most_likely_ht_ft=best[0]
        )


class PortfolioOptimizer:
    """投资组合优化器（基于Kelly）"""
    
    def __init__(self, max_portfolio_kelly: float = 0.5):
        self.max_total_kelly = max_portfolio_kelly
        
    def optimize_portfolio(
        self,
        bets: List[PortfolioBet],
        total_capital: float
    ) -> List[PortfolioBet]:
        """
        优化投资组合
        """
        # 排序按Edge
        # 1. 按Edge排序
        # 2. 分配资金，总凯利分数
        # 3. 限制最高
        # 实际项目中这会更复杂，包含协方差矩阵
        
        # 简化版
        sorted_bets = sorted(bets, key=lambda x: x.kelly_fraction, reverse=True)
        
        total_allocated = 0.0
        optimized = []
        
        for bet in sorted_bets:
            if total_allocated >= self.max_total_kelly:
                break
                
            allocate = min(bet.kelly_fraction, self.max_total_kelly - total_allocated)
            stake = allocate * total_capital
            
            optimized.append(PortfolioBet(
                match=bet.match,
                bet_type=bet.bet_type,
                odds=bet.odds,
                probability=bet.probability,
                stake=stake,
                kelly_fraction=allocate
            ))
            
            total_allocated += allocate
            
        return optimized
        
    def calculate_portfolio_stats(self, bets: List[PortfolioBet]) -> Dict:
        """计算投资组合统计"""
        total_stake = sum(b.stake for b in bets)
        
        # 预期收益
        expected_return = 0.0
        variance = 0.0
        
        for bet in bets:
            ev = bet.probability * (bet.odds - 1) - (1 - bet.probability)
            expected_return += ev * bet.stake
            variance += (bet.stake**2) * bet.probability * (1 - bet.probability)
        
        return {
            'total_stake': total_stake,
            'expected_value': expected_return,
            'expected_roi': (expected_return / total_stake * 100) if total_stake > 0 else 0,
            'variance': variance
        }


class InPlayPredictor:
    """滚球预测框架"""
    
    def __init__(self):
        self.time_decay_factor = 0.95
        self.minute_weights = [1.0 for _ in range(91)]  # 0-90分钟
        
        for i in range(75, 91):
            self.minute_weights[i] = 0.7 - (i - 75) * 0.03
        
    def predict_in_play(
        self,
        minute: int,
        home_goals: int,
        away_goals: int,
        home_attack: float,
        away_attack: float
    ) -> Dict:
        """实时预测"""
        
        minutes_remaining = max(0, 90 - minute)
        weight = self.minute_weights[min(minute, 90)]
        
        remaining_home_goals = home_attack * (minutes_remaining / 45)
        remaining_away_goals = away_attack * (minutes_remaining / 45)
        
        expected_final_home = home_goals + remaining_home_goals
        expected_final_away = away_goals + remaining_away_goals
        
        # 胜率概率（简化版）
        home_win = 0.0
        draw = 0.0
        away_win = 0.0
        
        # 简化版
        if expected_final_home > expected_final_away + 0.5:
            home_win = 0.6
            draw = 0.25
            away_win = 0.15
        elif expected_final_away > expected_final_home + 0.5:
            home_win = 0.15
            draw = 0.25
            away_win = 0.6
        else:
            home_win = 0.35
            draw = 0.3
            away_win = 0.35
            
        return {
            'current_score': f"{home_goals}-{away_goals}",
            'minute': minute,
            'remaining': minutes_remaining,
            'expected_home': expected_final_home,
            'expected_away': expected_final_away,
            'home_win_prob': home_win,
            'draw_prob': draw,
            'away_win_prob': away_win,
            'total_goals_remaining': remaining_home_goals + remaining_away_goals
        }
