"""
Dixon-Coles Predictive Model
足球预测黄金标准模型 - 对低比分结果专门优化

Reference: Dixon, M.J. and Coles, S.G. (1997)
Modelling Association Football Scores and Inefficiencies in the Football Betting Market.
"""

import math
import sys
import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
from scipy.optimize import minimize
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class TeamStrengthDC:
    """Dixon-Coles 球队实力"""
    attack: float
    defense: float
    name: str


@dataclass
class DCPrediction:
    """Dixon-Coles 预测结果"""
    home_goals_mean: float
    away_goals_mean: float
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    score_probabilities: Dict[Tuple[int, int], float]
    most_likely_score: Tuple[int, int]
    over_2_5_prob: float
    under_2_5_prob: float
    rho: float  # 相关性参数


class DixonColesModel:
    """
    Dixon-Coles 预测模型
    
    核心改进：
    - 考虑球队间的相关性参数 rho
    - 对低比分结果（0-0, 1-0, 0-1, 1-1）专门优化
    - 更精确的平局概率预测
    """
    
    def __init__(self):
        self.team_strengths: Dict[str, TeamStrengthDC] = {}
        self.home_advantage: float = 0.0
        self.rho: float = 0.0  # 相关性参数
        self.mean_goals_home: float = 1.5
        self.mean_goals_away: float = 1.2
        self.is_trained: bool = False
        self.max_goals = 10
    
    def _poisson_prob(self, k: int, lambda_val: float) -> float:
        """泊松概率"""
        if lambda_val <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.pow(lambda_val, k) * math.exp(-lambda_val)) / math.factorial(k)
    
    def _dc_adjusted_prob(
        self,
        x: int,
        y: int,
        lambda_home: float,
        lambda_away: float,
        rho: float
    ) -> float:
        """
        Dixon-Coles 调整后的比分概率
        
        对低比分结果应用相关性调整：
        - 0-0, 0-1, 1-0, 1-1
        
        tau(x,y) = 1 + rho * ... if x,y <=1
        else 1
        """
        poisson_product = self._poisson_prob(x, lambda_home) * self._poisson_prob(y, lambda_away)
        
        if x <= 1 and y <= 1:
            # 应用 Dixon-Coles 调整
            if x == 0 and y == 0:
                tau = 1 - (lambda_home * lambda_away * rho)
            elif x == 0 and y == 1:
                tau = 1 + (lambda_home * rho)
            elif x == 1 and y == 0:
                tau = 1 + (lambda_away * rho)
            else:  # x=1, y=1
                tau = 1 - rho
            return poisson_product * tau
        else:
            return poisson_product
    
    def _log_likelihood(self, params, matches_data) -> float:
        """
        对数似然函数（用于训练）
        
        params: [rho, home_adv, attack1, defense1, attack2, defense2, ...]
        """
        rho = params[0]
        home_adv = params[1]
        
        # 重建球队实力
        n_teams = len(self.team_strengths)
        team_indices = {name: i for i, name in enumerate(self.team_strengths.keys())}
        
        total_log_likelihood: float = 0.0
        
        for match in matches_data:
            home_team = match['home_team']
            away_team = match['away_team']
            
            if home_team not in team_indices or away_team not in team_indices:
                continue
                
            home_idx = team_indices[home_team]
            away_idx = team_indices[away_team]
            
            # 从参数中获取攻防实力
            attack_home = params[2 + home_idx * 2]
            defense_home = params[3 + home_idx * 2]
            attack_away = params[2 + away_idx * 2]
            defense_away = params[3 + away_idx * 2]
            
            lambda_home = attack_home * defense_away * self.mean_goals_home * math.exp(home_adv)
            lambda_away = attack_away * defense_home * self.mean_goals_away
            
            x = match['home_goals']
            y = match['away_goals']
            
            prob = self._dc_adjusted_prob(x, y, lambda_home, lambda_away, rho)
            if prob > 0:
                total_log_likelihood -= math.log(prob)
        
        return total_log_likelihood
    
    def fit(self, matches: List) -> None:
        """
        训练 Dixon-Coles 模型
        
        使用最大似然估计优化参数
        """
        print("🎯 训练 Dixon-Coles 模型 (使用 MLE)...")
        
        # 收集球队数据
        team_goals_scored: Dict[str, List[int]] = defaultdict(list)
        team_goals_conceded: Dict[str, List[int]] = defaultdict(list)
        matches_data = []
        
        total_home_goals = 0
        total_away_goals = 0
        valid_matches = 0
        
        for match in matches:
            if not hasattr(match, 'home_goals') or match.home_goals is None:
                continue
            if not hasattr(match, 'away_goals') or match.away_goals is None:
                continue
                
            home_goals = int(match.home_goals)
            away_goals = int(match.away_goals)
            
            matches_data.append({
                'home_team': match.home_team,
                'away_team': match.away_team,
                'home_goals': home_goals,
                'away_goals': away_goals
            })
            
            total_home_goals += home_goals
            total_away_goals += away_goals
            valid_matches += 1
            
            team_goals_scored[match.home_team].append(home_goals)
            team_goals_scored[match.away_team].append(away_goals)
            team_goals_conceded[match.home_team].append(away_goals)
            team_goals_conceded[match.away_team].append(home_goals)
        
        if valid_matches == 0:
            print("❌ 没有训练数据!")
            return
            
        self.mean_goals_home = total_home_goals / valid_matches
        self.mean_goals_away = total_away_goals / valid_matches
        print(f"  平均进球 - 主场: {self.mean_goals_home:.2f}, 客场: {self.mean_goals_away:.2f}")
        
        # 初始参数
        n_teams = len(team_goals_scored)
        self.team_strengths = {}
        for team_name in team_goals_scored:
            scored = sum(team_goals_scored[team_name])
            conceded = sum(team_goals_conceded[team_name])
            n_games = len(team_goals_scored[team_name])
            if n_games > 0:
                attack = (scored / n_games) / self.mean_goals_home if n_games > 0 else 1.0
                defense = (conceded / n_games) / self.mean_goals_away if n_games > 0 else 1.0
                self.team_strengths[team_name] = TeamStrengthDC(
                    attack=attack,
                    defense=defense,
                    name=team_name
                )
        
        # 准备优化参数
        initial_params: list[float] = [0.0, 0.1]  # rho, home_adv
        team_names = list(self.team_strengths.keys())
        for i in range(len(team_names)):
            team_obj: TeamStrengthDC = self.team_strengths[team_names[i]]
            initial_params.append(team_obj.attack)
            initial_params.append(team_obj.defense)
        
        print(f"  优化参数数量: {len(initial_params)}")
        
        # 边界：rho 在 [-0.2, 0.2]
        bounds = [(-0.3, 0.3), (-0.5, 0.5)] + [(0.1, 3.0), (0.1, 3.0)] * len(self.team_strengths)
        
        # 优化
        result = minimize(
            self._log_likelihood,
            initial_params,
            args=(matches_data),
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 1000}
        )
        
        # 更新训练后的参数
        self.rho = result.x[0]
        self.home_advantage = result.x[1]
        
        idx = 2
        for j in range(len(team_names)):
            team_data: TeamStrengthDC = self.team_strengths[team_names[j]]
            team_data.attack = result.x[idx]
            team_data.defense = result.x[idx + 1]
            idx += 2
        
        self.is_trained = True
        
        print(f"✅ Dixon-Coles 训练完成!")
        print(f"   Rho (相关性): {self.rho:.4f}")
        print(f"   主场优势参数: {self.home_advantage:.4f}")
        print(f"   覆盖球队: {len(self.team_strengths)}")
    
    def predict(self, home_team: str, away_team: str) -> Optional[DCPrediction]:
        """
        用 Dixon-Coles 模型预测比赛
        """
        if not self.is_trained:
            return None
        
        home_strength = self.team_strengths.get(home_team)
        away_strength = self.team_strengths.get(away_team)
        
        attack_home = home_strength.attack if home_strength else 1.0
        defense_home = home_strength.defense if home_strength else 1.0
        attack_away = away_strength.attack if away_strength else 1.0
        defense_away = away_strength.defense if away_strength else 1.0
        
        lambda_home = attack_home * defense_away * self.mean_goals_home * math.exp(self.home_advantage)
        lambda_away = attack_away * defense_home * self.mean_goals_away
        
        # 计算所有比分概率
        score_probs = {}
        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0
        over_2_5 = 0.0
        
        for x in range(self.max_goals + 1):
            for y in range(self.max_goals + 1):
                prob = self._dc_adjusted_prob(x, y, lambda_home, lambda_away, self.rho)
                score_probs[(x, y)] = prob
                
                if x > y:
                    home_win_prob += prob
                elif x == y:
                    draw_prob += prob
                else:
                    away_win_prob += prob
                
                if x + y > 2.5:
                    over_2_5 += prob
        
        total = home_win_prob + draw_prob + away_win_prob
        if total > 0:
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
        
        under_2_5 = 1.0 - over_2_5
        most_likely = max(score_probs.items(), key=lambda x: x[1])[0]
        
        return DCPrediction(
            home_goals_mean=lambda_home,
            away_goals_mean=lambda_away,
            home_win_prob=home_win_prob,
            draw_prob=draw_prob,
            away_win_prob=away_win_prob,
            score_probabilities=score_probs,
            most_likely_score=most_likely,
            over_2_5_prob=over_2_5,
            under_2_5_prob=under_2_5,
            rho=self.rho
        )
    
    def compare_with_poisson(self, home_team: str, away_team: str):
        """对比 Dixon-Coles 和 Poisson 的预测差异"""
        if not self.is_trained:
            return None
        
        prediction = self.predict(home_team, away_team)
        
        # 纯泊松概率（无调整）
        home_strength = self.team_strengths.get(home_team)
        away_strength = self.team_strengths.get(away_team)
        
        attack_home = home_strength.attack if home_strength else 1.0
        defense_home = home_strength.defense if home_strength else 1.0
        attack_away = away_strength.attack if away_strength else 1.0
        defense_away = away_strength.defense if away_strength else 1.0
        
        lambda_home = attack_home * defense_away * self.mean_goals_home * math.exp(self.home_advantage)
        lambda_away = attack_away * defense_home * self.mean_goals_away
        
        print("\n📊 Dixon-Coles vs 泊松对比:")
        print("  低比分调整对比:")
        
        low_scores = [(0,0), (0,1), (1,0), (1,1)]
        for x, y in low_scores:
            poisson_prob = self._poisson_prob(x, lambda_home) * self._poisson_prob(y, lambda_away)
            dc_prob = self._dc_adjusted_prob(x, y, lambda_home, lambda_away, self.rho)
            
            print(f"    {x}-{y}: Poisson {poisson_prob:.3%} | DC {dc_prob:.3%} | Δ {dc_prob - poisson_prob:.3%}")
        
        return prediction
