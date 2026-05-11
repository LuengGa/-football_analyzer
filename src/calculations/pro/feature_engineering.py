"""
Feature Engineering Module
特征工程模块 - 为机器学习预测模型提取专业特征

包含:
- 球队历史表现特征
- 攻防统计特征
- 交锋历史特征
- 历史赔率特征
- 比赛统计特征（射门/角球/犯规）
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class MatchFeatures:
    """比赛特征向量"""
    # 主队特征
    home_recent_form: float  # 近期状态（近6场积分/18）
    home_goals_scored_avg: float
    home_goals_conceded_avg: float
    home_attack_strength: float
    home_defense_strength: float
    home_wins_pct: float
    home_draws_pct: float
    home_losses_pct: float
    
    # 客队特征
    away_recent_form: float
    away_goals_scored_avg: float
    away_goals_conceded_avg: float
    away_attack_strength: float
    away_defense_strength: float
    away_wins_pct: float
    away_draws_pct: float
    away_losses_pct: float
    
    # 交锋特征
    h2h_home_wins: int
    h2h_draws: int
    h2h_away_wins: int
    h2h_home_goals_avg: float
    h2h_away_goals_avg: float
    
    # 高级统计特征
    home_shots_avg: Optional[float]
    away_shots_avg: Optional[float]
    home_corners_avg: Optional[float]
    away_corners_avg: Optional[float]
    
    # 联赛级别特征
    league_strength: float
    
    # 衍生特征
    goal_diff_expectation: float
    form_diff: float
    
    def to_array(self) -> np.ndarray:
        """转换为 NumPy 数组"""
        features = [
            self.home_recent_form,
            self.home_goals_scored_avg,
            self.home_goals_conceded_avg,
            self.home_attack_strength,
            self.home_defense_strength,
            self.home_wins_pct,
            self.home_draws_pct,
            self.home_losses_pct,
            self.away_recent_form,
            self.away_goals_scored_avg,
            self.away_goals_conceded_avg,
            self.away_attack_strength,
            self.away_defense_strength,
            self.away_wins_pct,
            self.away_draws_pct,
            self.away_losses_pct,
            self.h2h_home_wins,
            self.h2h_draws,
            self.h2h_away_wins,
            self.h2h_home_goals_avg,
            self.h2h_away_goals_avg,
            self.goal_diff_expectation,
            self.form_diff,
            self.league_strength
        ]
        return np.array([f if f is not None else 0.0 for f in features])


class FeatureExtractor:
    """专业特征提取器"""
    
    def __init__(self, matches: List):
        self.matches = matches
        self.team_history: Dict[str, List] = defaultdict(list)
        self.h2h_history: Dict[Tuple[str, str], List] = defaultdict(list)
        self.league_avg_goals: Dict[str, float] = {}
        self._build_team_history()
    
    def _build_team_history(self):
        """构建球队历史数据库"""
        print("🔧 构建球队历史数据库...")
        
        # 按日期排序
        sorted_matches = sorted(self.matches, key=lambda m: m.date if hasattr(m, 'date') else '0')
        
        for match in sorted_matches:
            if not hasattr(match, 'home_goals') or match.home_goals is None:
                continue
            if not hasattr(match, 'away_goals') or match.away_goals is None:
                continue
                
            # 存储球队比赛记录
            self.team_history[match.home_team].append(match)
            self.team_history[match.away_team].append(match)
            
            # 交锋历史
            key = tuple(sorted([match.home_team, match.away_team]))
            self.h2h_history[key].append(match)
        
        # 计算联赛平均进球
        league_goals: Dict[str, List] = defaultdict(list)
        for match in sorted_matches:
            if hasattr(match, 'home_goals') and hasattr(match, 'away_goals'):
                if match.home_goals is not None and match.away_goals is not None:
                    league = match.league_name if hasattr(match, 'league_name') else 'Unknown'
                    league_goals[league].append(match.home_goals + match.away_goals)
        
        for league, goals in league_goals.items():
            if goals:
                self.league_avg_goals[league] = sum(goals) / len(goals)
        
        print(f"✅ 历史数据构建完成: {len(self.team_history)} 支球队")
    
    def _calculate_form(self, team: str, num_games: int = 6) -> float:
        """计算球队近期状态（3分制积分）"""
        if team not in self.team_history:
            return 0.5
        
        matches = self.team_history[team][-num_games:]
        total_points = 0
        
        for match in matches:
            is_home = match.home_team == team
            
            if is_home:
                home_goals = match.home_goals
                away_goals = match.away_goals
            else:
                home_goals = match.away_goals
                away_goals = match.home_goals
            
            if home_goals > away_goals:
                total_points += 3
            elif home_goals == away_goals:
                total_points += 1
        
        max_points = len(matches) * 3 if matches else 18
        return total_points / max_points if max_points > 0 else 0.5
    
    def _get_team_stats(self, team: str, is_home: bool) -> Dict:
        """获取球队统计数据"""
        if team not in self.team_history:
            return {
                'goals_scored_avg': 1.5,
                'goals_conceded_avg': 1.2,
                'attack_strength': 1.0,
                'defense_strength': 1.0,
                'wins_pct': 0.33,
                'draws_pct': 0.33,
                'losses_pct': 0.33,
                'shots_avg': None,
                'corners_avg': None
            }
        
        matches = self.team_history[team]
        if not matches:
            return self._get_team_stats(team, is_home)
        
        goals_scored = []
        goals_conceded = []
        shots = []
        corners = []
        wins = 0
        draws = 0
        losses = 0
        
        for match in matches:
            team_home = match.home_team == team
            
            if team_home:
                scored = match.home_goals
                conceded = match.away_goals
            else:
                scored = match.away_goals
                conceded = match.home_goals
            
            if scored is not None and conceded is not None:
                goals_scored.append(scored)
                goals_conceded.append(conceded)
                
                if scored > conceded:
                    wins += 1
                elif scored == conceded:
                    draws += 1
                else:
                    losses += 1
            
            # 比赛统计数据
            if hasattr(match, 'match_stats') and match.match_stats:
                stats = match.match_stats
                if team_home:
                    if 'shots' in stats and stats['shots'] and isinstance(stats['shots'], dict):
                        shots.append(stats['shots'].get('home', 0))
                    if 'corners' in stats and stats['corners'] and isinstance(stats['corners'], dict):
                        corners.append(stats['corners'].get('home', 0))
                else:
                    if 'shots' in stats and stats['shots'] and isinstance(stats['shots'], dict):
                        shots.append(stats['shots'].get('away', 0))
                    if 'corners' in stats and stats['corners'] and isinstance(stats['corners'], dict):
                        corners.append(stats['corners'].get('away', 0))
        
        total = wins + draws + losses
        if total == 0:
            total = 1
        
        league = matches[0].league_name if hasattr(matches[0], 'league_name') else 'Unknown'
        league_avg = self.league_avg_goals.get(league, 2.7)
        
        return {
            'goals_scored_avg': sum(goals_scored) / len(goals_scored) if goals_scored else 1.5,
            'goals_conceded_avg': sum(goals_conceded) / len(goals_conceded) if goals_conceded else 1.2,
            'attack_strength': (sum(goals_scored) / len(goals_scored)) / (league_avg / 2) if goals_scored else 1.0,
            'defense_strength': (sum(goals_conceded) / len(goals_conceded)) / (league_avg / 2) if goals_conceded else 1.0,
            'wins_pct': wins / total,
            'draws_pct': draws / total,
            'losses_pct': losses / total,
            'shots_avg': sum(shots) / len(shots) if shots else None,
            'corners_avg': sum(corners) / len(corners) if corners else None
        }
    
    def _get_h2h_stats(self, home_team: str, away_team: str) -> Dict:
        """获取交锋历史统计"""
        key = tuple(sorted([home_team, away_team]))
        matches = self.h2h_history.get(key, [])
        
        h2h_home_wins = 0
        h2h_draws = 0
        h2h_away_wins = 0
        home_goals = []
        away_goals = []
        
        for match in matches:
            if not hasattr(match, 'home_goals') or match.home_goals is None:
                continue
            if not hasattr(match, 'away_goals') or match.away_goals is None:
                continue
                
            is_home_order = match.home_team == home_team
            
            hg = match.home_goals if is_home_order else match.away_goals
            ag = match.away_goals if is_home_order else match.home_goals
            
            home_goals.append(hg)
            away_goals.append(ag)
            
            if hg > ag:
                h2h_home_wins += 1
            elif hg == ag:
                h2h_draws += 1
            else:
                h2h_away_wins += 1
        
        return {
            'h2h_home_wins': h2h_home_wins,
            'h2h_draws': h2h_draws,
            'h2h_away_wins': h2h_away_wins,
            'h2h_home_goals_avg': sum(home_goals) / len(home_goals) if home_goals else 1.5,
            'h2h_away_goals_avg': sum(away_goals) / len(away_goals) if away_goals else 1.2
        }
    
    def extract_features(self, home_team: str, away_team: str, league: Optional[str] = None) -> MatchFeatures:
        """提取完整比赛特征"""
        home_stats = self._get_team_stats(home_team, True)
        away_stats = self._get_team_stats(away_team, False)
        h2h_stats = self._get_h2h_stats(home_team, away_team)
        
        home_form = self._calculate_form(home_team, 6)
        away_form = self._calculate_form(away_team, 6)
        
        league_strength = self._get_league_strength(league)
        
        goal_diff_exp = (home_stats['attack_strength'] - away_stats['defense_strength']) - \
                      (away_stats['attack_strength'] - home_stats['defense_strength'])
        
        return MatchFeatures(
            home_recent_form=home_form,
            home_goals_scored_avg=home_stats['goals_scored_avg'],
            home_goals_conceded_avg=home_stats['goals_conceded_avg'],
            home_attack_strength=home_stats['attack_strength'],
            home_defense_strength=home_stats['defense_strength'],
            home_wins_pct=home_stats['wins_pct'],
            home_draws_pct=home_stats['draws_pct'],
            home_losses_pct=home_stats['losses_pct'],
            
            away_recent_form=away_form,
            away_goals_scored_avg=away_stats['goals_scored_avg'],
            away_goals_conceded_avg=away_stats['goals_conceded_avg'],
            away_attack_strength=away_stats['attack_strength'],
            away_defense_strength=away_stats['defense_strength'],
            away_wins_pct=away_stats['wins_pct'],
            away_draws_pct=away_stats['draws_pct'],
            away_losses_pct=away_stats['losses_pct'],
            
            h2h_home_wins=h2h_stats['h2h_home_wins'],
            h2h_draws=h2h_stats['h2h_draws'],
            h2h_away_wins=h2h_stats['h2h_away_wins'],
            h2h_home_goals_avg=h2h_stats['h2h_home_goals_avg'],
            h2h_away_goals_avg=h2h_stats['h2h_away_goals_avg'],
            
            home_shots_avg=home_stats['shots_avg'],
            away_shots_avg=away_stats['shots_avg'],
            home_corners_avg=home_stats['corners_avg'],
            away_corners_avg=away_stats['corners_avg'],
            
            league_strength=league_strength,
            
            goal_diff_expectation=goal_diff_exp,
            form_diff=home_form - away_form
        )
    
    def _get_league_strength(self, league: Optional[str]) -> float:
        """获取联赛强度评分"""
        league_ranks = {
            '英格兰超级联赛': 1.0,
            '西班牙超级联赛': 0.95,
            '德国超级联赛': 0.9,
            '意大利超级联赛': 0.88,
            '法国超级联赛': 0.85,
            '英格兰冠军联赛': 0.7,
            '西班牙乙级联赛': 0.65,
            '意大利乙级联赛': 0.63,
            '德国乙级联赛': 0.62
        }
        return league_ranks.get(league, 0.6) if league else 0.6
    
    def prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray, List]:
        """准备完整训练数据集"""
        print("🔧 准备训练数据集...")
        
        X = []
        y = []  # 0=客胜, 1=平局, 2=主胜
        match_info = []
        
        # 按时间顺序
        sorted_matches = sorted(
            [m for m in self.matches if hasattr(m, 'date')],
            key=lambda m: m.date
        )
        
        for i, match in enumerate(sorted_matches):
            if i % 1000 == 0:
                print(f"  处理进度: {i}/{len(sorted_matches)}")
                
            if not hasattr(match, 'home_goals') or match.home_goals is None:
                continue
            if not hasattr(match, 'away_goals') or match.away_goals is None:
                continue
                
            # 提取特征（只使用此比赛之前的数据）
            past_extractor = FeatureExtractor(sorted_matches[:i])
            features = past_extractor.extract_features(
                match.home_team, 
                match.away_team,
                match.league_name if hasattr(match, 'league_name') else None
            )
            
            # 确定标签
            if match.home_goals > match.away_goals:
                label = 2
            elif match.home_goals == match.away_goals:
                label = 1
            else:
                label = 0
            
            X.append(features.to_array())
            y.append(label)
            match_info.append((match.home_team, match.away_team, match.date))
        
        print(f"✅ 训练数据准备完成: {len(X)} 样本")
        return np.array(X), np.array(y), match_info
