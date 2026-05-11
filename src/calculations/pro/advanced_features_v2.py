"""
Advanced Features v2.0 - 高级功能模块
包含：HT/FT 预测、实时预测框架、投资组合优化
"""

import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
from enum import Enum
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.calculations.pro.domain_models import HalfTimeScore, BetType


class GameState(Enum):
    """比赛状态"""
    NOT_STARTED = "not_started"
    FIRST_HALF = "first_half"
    HALF_TIME = "half_time"
    SECOND_HALF = "second_half"
    FINISHED = "finished"


@dataclass
class HTFTPrediction:
    """半场/全场预测结果"""
    home_home: float  # 半场主胜，全场主胜
    home_draw: float  # 半场主胜，全场平
    home_away: float  # 半场主胜，全场客胜
    draw_home: float  # 半场平，全场主胜
    draw_draw: float  # 半场平，全场平
    draw_away: float  # 半场平，全场客胜
    away_home: float  # 半场客胜，全场主胜
    away_draw: float  # 半场客胜，全场平
    away_away: float  # 半场客胜，全场客胜

    @property
    def most_likely(self) -> str:
        """最可能的 HT/FT 结果"""
        probs = [
            ('HH', self.home_home), ('HD', self.home_draw), ('HA', self.home_away),
            ('DH', self.draw_home), ('DD', self.draw_draw), ('DA', self.draw_away),
            ('AH', self.away_home), ('AD', self.away_draw), ('AA', self.away_away)
        ]
        return max(probs, key=lambda x: x[1])[0]


@dataclass
class LivePredictionUpdate:
    """实时预测更新"""
    minute: int
    home_goals: int
    away_goals: int
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    over_2_5_prob: float
    confidence: float


class HTFTPredictor:
    """半场/全场预测器"""

    def __init__(self):
        self.historical_htft_data: List[Dict] = []
        self.team_ht_performance: Dict[str, Dict] = defaultdict(lambda: {
            'home_ht_win': 0, 'home_ht_draw': 0, 'home_ht_loss': 0,
            'away_ht_win': 0, 'away_ht_draw': 0, 'away_ht_loss': 0,
            'total': 0
        })
        self.htft_transition_matrix: Dict[Tuple, Dict] = defaultdict(lambda: defaultdict(int))

    def fit(self, matches: List[Any]):
        """训练 HT/FT 预测器"""
        print("🎯 训练 HT/FT 预测器...")

        count = 0
        for match in matches:
            if not hasattr(match, 'half_time') or not match.half_time:
                continue
            if not hasattr(match, 'home_goals') or match.home_goals is None:
                continue
            if not hasattr(match, 'away_goals') or match.away_goals is None:
                continue

            ht_home = match.half_time.home if hasattr(match.half_time, 'home') else 0
            ht_away = match.half_time.away if hasattr(match.half_time, 'away') else 0
            ft_home = match.home_goals
            ft_away = match.away_goals

            if ht_home is None or ht_away is None:
                continue

            ht_result = self._get_result(ht_home, ht_away)
            ft_result = self._get_result(ft_home, ft_away)

            self.htft_transition_matrix[ht_result][ft_result] += 1

            self._update_team_performance(match.home_team, ht_home, ht_away, True)
            self._update_team_performance(match.away_team, ht_away, ht_home, False)

            count += 1

        print(f"      ✅ HT/FT 训练完成，使用 {count} 场比赛数据")

    def _get_result(self, home: int, away: int) -> str:
        if home > away:
            return 'H'
        elif home == away:
            return 'D'
        else:
            return 'A'

    def _update_team_performance(self, team: str, scored: int, conceded: int, is_home: bool):
        perf = self.team_ht_performance[team]
        result = self._get_result(scored, conceded)

        prefix = 'home_ht_' if is_home else 'away_ht_'
        if result == 'H':
            perf[prefix + 'win'] += 1
        elif result == 'D':
            perf[prefix + 'draw'] += 1
        else:
            perf[prefix + 'loss'] += 1
        perf['total'] += 1

    def predict(self, home_team: str, away_team: str, home_strength: float = 1.0,
                away_strength: float = 1.0) -> Optional[HTFTPrediction]:
        """预测 HT/FT 结果"""

        ht_probs = self._predict_half_time(home_team, away_team, home_strength, away_strength)

        result = HTFTPrediction(
            home_home=0.0, home_draw=0.0, home_away=0.0,
            draw_home=0.0, draw_draw=0.0, draw_away=0.0,
            away_home=0.0, away_draw=0.0, away_away=0.0
        )

        for ht_state in ['H', 'D', 'A']:
            ft_probs = self._predict_second_half(ht_state, home_strength, away_strength)

            if ht_state == 'H':
                result.home_home = ht_probs['H'] * ft_probs['H']
                result.home_draw = ht_probs['H'] * ft_probs['D']
                result.home_away = ht_probs['H'] * ft_probs['A']
            elif ht_state == 'D':
                result.draw_home = ht_probs['D'] * ft_probs['H']
                result.draw_draw = ht_probs['D'] * ft_probs['D']
                result.draw_away = ht_probs['D'] * ft_probs['A']
            else:
                result.away_home = ht_probs['A'] * ft_probs['H']
                result.away_draw = ht_probs['A'] * ft_probs['D']
                result.away_away = ht_probs['A'] * ft_probs['A']

        total = sum([
            result.home_home, result.home_draw, result.home_away,
            result.draw_home, result.draw_draw, result.draw_away,
            result.away_home, result.away_draw, result.away_away
        ])

        if total > 0:
            for attr in ['home_home', 'home_draw', 'home_away',
                        'draw_home', 'draw_draw', 'draw_away',
                        'away_home', 'away_draw', 'away_away']:
                setattr(result, attr, getattr(result, attr) / total)

        return result

    def _predict_half_time(self, home_team: str, away_team: str,
                          home_strength: float, away_strength: float) -> Dict[str, float]:
        home_p = 0.40 * home_strength / (home_strength + away_strength) + 0.15
        away_p = 0.40 * away_strength / (home_strength + away_strength) + 0.10
        draw_p = 1.0 - home_p - away_p
        return {'H': home_p, 'D': max(0.20, draw_p), 'A': away_p}

    def _predict_second_half(self, ht_state: str, home_strength: float,
                            away_strength: float) -> Dict[str, float]:
        if ht_state == 'H':
            return {'H': 0.60, 'D': 0.25, 'A': 0.15}
        elif ht_state == 'D':
            home_p = 0.45 * home_strength / (home_strength + away_strength)
            away_p = 0.45 * away_strength / (home_strength + away_strength)
            return {'H': home_p, 'D': 0.35, 'A': away_p}
        else:
            return {'H': 0.15, 'D': 0.25, 'A': 0.60}


class LivePredictor:
    """实时比赛预测器 - 滚球预测框架"""

    def __init__(self):
        self.goal_rate_home = 1.4
        self.goal_rate_away = 1.1
        self.red_card_impact = 0.3

    def predict_in_game(self, current_home_goals: int, current_away_goals: int,
                       minute: int, home_strength: float = 1.0,
                       away_strength: float = 1.0,
                       home_red_cards: int = 0, away_red_cards: int = 0) -> LivePredictionUpdate:
        """实时预测比赛结果"""
        remaining_minutes = max(0, 90 - minute)
        minutes_ratio = remaining_minutes / 90.0

        home_rate = self.goal_rate_home * home_strength * minutes_ratio
        away_rate = self.goal_rate_away * away_strength * minutes_ratio

        if home_red_cards > 0:
            home_rate *= (1.0 - self.red_card_impact * home_red_cards)
        if away_red_cards > 0:
            away_rate *= (1.0 - self.red_card_impact * away_red_cards)

        home_win_prob, draw_prob, away_win_prob = self._calculate_result_probs(
            current_home_goals, current_away_goals, home_rate, away_rate
        )

        total_goals = current_home_goals + current_away_goals
        expected_remaining = home_rate + away_rate
        over_2_5_prob = self._calculate_over_2_5(total_goals, expected_remaining)

        confidence = max(home_win_prob, draw_prob, away_win_prob)

        return LivePredictionUpdate(
            minute=minute,
            home_goals=current_home_goals,
            away_goals=current_away_goals,
            home_win_prob=home_win_prob,
            draw_prob=draw_prob,
            away_win_prob=away_win_prob,
            over_2_5_prob=over_2_5_prob,
            confidence=confidence
        )

    def _calculate_result_probs(self, current_home: int, current_away: int,
                                lambda_home: float, lambda_away: float) -> Tuple[float, float, float]:
        home_win = 0.0
        draw = 0.0
        away_win = 0.0

        max_goals = 5
        for i in range(max_goals):
            for j in range(max_goals):
                prob = self._poisson_prob(i, lambda_home) * self._poisson_prob(j, lambda_away)
                final_home = current_home + i
                final_away = current_away + j

                if final_home > final_away:
                    home_win += prob
                elif final_home == final_away:
                    draw += prob
                else:
                    away_win += prob

        total = home_win + draw + away_win
        if total > 0:
            return home_win / total, draw / total, away_win / total
        return 0.33, 0.34, 0.33

    def _calculate_over_2_5(self, current_goals: int, expected_remaining: float) -> float:
        if current_goals > 2:
            return 1.0

        needed = 3 - current_goals
        prob_under = 0.0

        for i in range(needed):
            prob_under += self._poisson_prob(i, expected_remaining)

        return 1.0 - prob_under

    def _poisson_prob(self, k: int, lambda_val: float) -> float:
        if lambda_val <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.pow(lambda_val, k) * math.exp(-lambda_val)) / math.factorial(k)


class PortfolioOptimizer:
    """投注投资组合优化器 - 使用现代投资组合理论"""

    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate

    def optimize_portfolio(self, bets: List[Dict], max_allocations: int = 5,
                          risk_tolerance: float = 0.5) -> List[Dict]:
        """优化投资组合"""
        if not bets:
            return []

        scored_bets = []
        for bet in bets:
            edge = bet.get('edge', 0.0)
            ev = bet.get('expected_value', 0.0)
            odds = bet.get('odds', 2.0)
            prob = bet.get('predicted_prob', 0.5)

            score = edge * 0.6 + ev * 0.3 + (prob * (odds - 1)) * 0.1
            risk = self._calculate_bet_risk(bet)

            scored_bets.append({**bet, 'score': score, 'risk': risk})

        scored_bets.sort(key=lambda x: x['score'], reverse=True)
        selected = scored_bets[:max_allocations]

        total_score = sum(b['score'] for b in selected)
        for bet in selected:
            bet['allocation'] = bet['score'] / total_score if total_score > 0 else 1.0 / len(selected)

        return selected

    def _calculate_bet_risk(self, bet: Dict) -> float:
        odds = bet.get('odds', 2.0)
        prob = bet.get('predicted_prob', 0.5)

        variance = prob * (1 - prob) * (odds - 1) ** 2 + prob * (1 - prob) * 1
        return math.sqrt(variance)
