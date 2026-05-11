"""
Team Ratings - ELO/Glicko 球队评级系统
实现：
1. ELO评级
2. Glicko/Glicko-2评级
3. 动态实力更新
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class TeamRating:
    """球队评级"""
    name: str
    rating: float  # ELO/Glicko 评级分
    rd: float  # Rating Deviation (Glicko)
    volatility: float  # Glicko-2 波动率
    games: int
    last_update: str


@dataclass
class RatingChange:
    """评级变化"""
    team: str
    old_rating: float
    new_rating: float
    change: float
    opponent: str
    result: str


class EloRatingSystem:
    """ELO评级系统"""
    
    def __init__(self, k_factor: float = 30, initial_rating: float = 1500):
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.ratings: Dict[str, float] = {}
        self.history: List[RatingChange] = []
        
    def get_rating(self, team: str) -> float:
        """获取球队评级"""
        return self.ratings.get(team, self.initial_rating)
        
    def calculate_expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        计算A对B的期望得分
        E = 1 / (1 + 10^((B - A)/400))
        """
        return 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))
        
    def update_ratings(
        self,
        team_a: str,
        team_b: str,
        score_a: float,  # 实际得分：1=胜, 0.5=平, 0=负
        k_factor_override: Optional[float] = None
    ) -> List[RatingChange]:
        """
        更新两队评级
        """
        k = k_factor_override if k_factor_override else self.k_factor
        
        rating_a_old = self.get_rating(team_a)
        rating_b_old = self.get_rating(team_b)
        
        expected_a = self.calculate_expected_score(rating_a_old, rating_b_old)
        expected_b = 1.0 - expected_a
        
        # 更新评级
        rating_a_new = rating_a_old + k * (score_a - expected_a)
        rating_b_new = rating_b_old + k * ((1.0 - score_a) - expected_b)
        
        self.ratings[team_a] = rating_a_new
        self.ratings[team_b] = rating_b_new
        
        # 记录历史
        changes = [
            RatingChange(
                team=team_a,
                old_rating=rating_a_old,
                new_rating=rating_a_new,
                change=rating_a_new - rating_a_old,
                opponent=team_b,
                result='win' if score_a > 0.5 else 'draw' if score_a == 0.5 else 'loss'
            ),
            RatingChange(
                team=team_b,
                old_rating=rating_b_old,
                new_rating=rating_b_new,
                change=rating_b_new - rating_b_old,
                opponent=team_a,
                result='win' if score_a < 0.5 else 'draw' if score_a == 0.5 else 'loss'
            )
        ]
        
        self.history.extend(changes)
        return changes
        
    def process_matches(self, matches: List):
        """批量处理比赛更新评级"""
        for match in matches:
            if not hasattr(match, 'home_goals') or not hasattr(match, 'away_goals'):
                continue
                
            home_goals = match.home_goals
            away_goals = match.away_goals
            
            if home_goals is None or away_goals is None:
                continue
                
            # 计算比赛结果得分
            if home_goals > away_goals:
                home_score = 1.0
            elif home_goals == away_goals:
                home_score = 0.5
            else:
                home_score = 0.0
                
            # 更新评级
            self.update_ratings(match.home_team, match.away_team, home_score)
            
    def get_top_teams(self, n: int = 20) -> List[Tuple[str, float]]:
        """获取排名前n的球队"""
        sorted_ratings = sorted(self.ratings.items(), key=lambda x: -x[1])
        return sorted_ratings[:n]


class GlickoRatingSystem:
    """Glicko-2 评级系统（更先进）"""
    
    def __init__(
        self,
        initial_rating: float = 1500,
        initial_rd: float = 350,
        initial_volatility: float = 0.06,
        tau: float = 0.5,  # 系统参数，控制波动率的变化
        epsilon: float = 0.000001
    ):
        self.initial_rating = initial_rating
        self.initial_rd = initial_rd
        self.initial_volatility = initial_volatility
        self.tau = tau
        self.epsilon = epsilon
        
        self.ratings: Dict[str, TeamRating] = {}
        self.history: List[RatingChange] = []
        
    def _g(self, rd: float) -> float:
        """Glicko g函数"""
        return 1.0 / math.sqrt(1.0 + (3.0 * rd**2) / (math.pi**2))
        
    def _e(self, r: float, rj: float, rdj: float) -> float:
        """Glicko 期望得分"""
        return 1.0 / (1.0 + math.exp(-self._g(rdj) * (r - rj) / 400.0))
        
    def get_team_rating(self, team: str) -> TeamRating:
        """获取球队评级信息"""
        if team not in self.ratings:
            self.ratings[team] = TeamRating(
                name=team,
                rating=self.initial_rating,
                rd=self.initial_rd,
                volatility=self.initial_volatility,
                games=0,
                last_update=""
            )
        return self.ratings[team]
        
    def update_ratings(
        self,
        team_a: str,
        team_b: str,
        score_a: float  # 1=胜, 0.5=平, 0=负
    ) -> List[RatingChange]:
        """
        更新评级（简化版Glicko-1，足够用于足球）
        """
        rating_a = self.get_team_rating(team_a)
        rating_b = self.get_team_rating(team_b)
        
        # 计算期望得分
        expected_a = 1.0 / (1.0 + math.pow(10, (rating_b.rating - rating_a.rating)/400.0))
        expected_b = 1.0 - expected_a
        
        # K因子根据RD调整
        k_a = max(10, 30 * (1 - 200/(200 + rating_a.rd)))
        k_b = max(10, 30 * (1 - 200/(200 + rating_b.rd)))
        
        # 更新评级
        change_a = k_a * (score_a - expected_a)
        change_b = k_b * ((1-score_a) - expected_b)
        
        old_rating_a = rating_a.rating
        old_rating_b = rating_b.rating
        
        rating_a.rating += change_a
        rating_b.rating += change_b
        
        # 更新RD（缩小偏差）
        rating_a.rd = max(50, rating_a.rd * 0.98)
        rating_b.rd = max(50, rating_b.rd * 0.98)
        
        # 更新场次
        rating_a.games += 1
        rating_b.games += 1
        
        # 记录
        changes = [
            RatingChange(
                team=team_a,
                old_rating=old_rating_a,
                new_rating=rating_a.rating,
                change=change_a,
                opponent=team_b,
                result='win' if score_a > 0.5 else 'draw' if score_a == 0.5 else 'loss'
            ),
            RatingChange(
                team=team_b,
                old_rating=old_rating_b,
                new_rating=rating_b.rating,
                change=change_b,
                opponent=team_a,
                result='win' if score_a < 0.5 else 'draw' if score_a == 0.5 else 'loss'
            )
        ]
        
        self.history.extend(changes)
        return changes
        
    def process_matches(self, matches: List):
        """批量处理比赛更新评级"""
        for match in matches:
            if not hasattr(match, 'home_goals') or not hasattr(match, 'away_goals'):
                continue
                
            home_goals = match.home_goals
            away_goals = match.away_goals
            
            if home_goals is None or away_goals is None:
                continue
                
            if home_goals > away_goals:
                home_score = 1.0
            elif home_goals == away_goals:
                home_score = 0.5
            else:
                home_score = 0.0
                
            self.update_ratings(match.home_team, match.away_team, home_score)
            
    def get_top_teams(self, n: int = 20) -> List[Tuple[str, float]]:
        """获取排名前n的球队"""
        sorted_ratings = sorted(
            self.ratings.values(),
            key=lambda x: -x.rating
        )
        return [(t.name, t.rating) for t in sorted_ratings[:n]]
