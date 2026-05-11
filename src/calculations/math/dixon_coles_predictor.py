"""
DixonColesPredictor - Dixon-Coles预测器
使用Dixon-Coles模型进行比赛结果预测
"""
import numpy as np
from scipy.stats import poisson

class DixonColesPredictor:
    """Dixon-Coles预测模型"""
    
    def __init__(self):
        self.params = {
            'attack': {},
            'defense': {},
            'home_advantage': 0.25
        }
    
    def fit(self, matches: list):
        """拟合模型参数"""
        teams = set()
        for match in matches:
            teams.add(match['home_team'])
            teams.add(match['away_team'])
        
        n_teams = len(teams)
        team_list = list(teams)
        team_index = {t: i for i, t in enumerate(team_list)}
        
        # 初始化参数
        attack = np.ones(n_teams)
        defense = np.ones(n_teams)
        home_adv = 0.25
        
        # 简化版：基于平均进球数估计
        total_goals = sum(m.get('home_goals', 0) + m.get('away_goals', 0) for m in matches)
        avg_goals = total_goals / len(matches) if matches else 2.5
        
        for i, team in enumerate(team_list):
            home_goals = sum(m.get('home_goals', 0) for m in matches if m['home_team'] == team)
            away_goals = sum(m.get('away_goals', 0) for m in matches if m['away_team'] == team)
            home_games = sum(1 for m in matches if m['home_team'] == team)
            away_games = sum(1 for m in matches if m['away_team'] == team)
            
            attack[i] = ((home_goals + away_goals) / (home_games + away_games + 1)) / (avg_goals / 2)
        
        self.params['attack'] = {team: attack[i] for i, team in enumerate(team_list)}
        self.params['defense'] = {team: 1.0 for team in team_list}
        self.params['home_advantage'] = home_adv
    
    def predict(
        self,
        home_team: str,
        away_team: str,
        home_attack: float = None,
        away_attack: float = None,
        home_defense: float = None,
        away_defense: float = None,
        home_adv: float = 0.25
    ) -> dict:
        """预测比赛结果"""
        # 使用提供的参数或默认值
        home_att = home_attack if home_attack else 1.0
        away_att = away_attack if away_attack else 1.0
        home_def = home_defense if home_defense else 1.0
        away_def = away_defense if away_defense else 1.0
        
        # 计算预期进球数
        home_xg = home_att * away_def * (1 + home_adv)
        away_xg = away_att * home_def
        
        # 计算概率矩阵
        max_goals = 7
        probabilities = np.zeros((max_goals + 1, max_goals + 1))
        
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                probabilities[h, a] = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
        
        # 计算各项概率
        home_win = np.sum(probabilities[np.triu_indices(max_goals + 1, 1)])
        draw = np.sum(np.diag(probabilities))
        away_win = np.sum(probabilities[np.tril_indices(max_goals + 1, -1)])
        
        # 计算总进球概率
        total_goals = {}
        for tg in range(8):
            if tg < max_goals:
                total_goals[str(tg)] = np.sum(probabilities[probabilities.sum(axis=1) == tg])
            else:
                total_goals["7+"] = np.sum(probabilities[probabilities.sum(axis=1) >= 7])
        
        # 计算最可能比分
        max_prob = 0
        best_score = "0:0"
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                if probabilities[h, a] > max_prob:
                    max_prob = probabilities[h, a]
                    best_score = f"{h}:{a}"
        
        return {
            "success": True,
            "home_team": home_team,
            "away_team": away_team,
            "xg": {"home": round(home_xg, 3), "away": round(away_xg, 3)},
            "probabilities": {
                "home_win": round(float(home_win), 4),
                "draw": round(float(draw), 4),
                "away_win": round(float(away_win), 4)
            },
            "total_goals": {k: round(float(v), 4) for k, v in total_goals.items()},
            "most_likely_score": best_score,
            "score_probabilities": {
                f"{h}:{a}": round(float(probabilities[h, a]), 4)
                for h in range(4) for a in range(4)
                if probabilities[h, a] > 0.005
            }
        }
    
    def predict_with_history(
        self,
        home_team: str,
        away_team: str,
        home_history: list = None,
        away_history: list = None
    ) -> dict:
        """使用历史数据预测"""
        # 计算近期进攻/防守能力
        if home_history:
            home_goals_scored = sum(m.get('goals_scored', 0) for m in home_history[-5:]) / min(5, len(home_history))
            home_goals_conceded = sum(m.get('goals_conceded', 0) for m in home_history[-5:]) / min(5, len(home_history))
        else:
            home_goals_scored = 1.5
            home_goals_conceded = 1.2
        
        if away_history:
            away_goals_scored = sum(m.get('goals_scored', 0) for m in away_history[-5:]) / min(5, len(away_history))
            away_goals_conceded = sum(m.get('goals_conceded', 0) for m in away_history[-5:]) / min(5, len(away_history))
        else:
            away_goals_scored = 1.3
            away_goals_conceded = 1.4
        
        # 标准化为相对能力
        avg_goals = 1.4
        home_att = home_goals_scored / avg_goals
        home_def = avg_goals / home_goals_conceded
        away_att = away_goals_scored / avg_goals
        away_def = avg_goals / away_goals_conceded
        
        return self.predict(
            home_team, away_team,
            home_attack=home_att, away_attack=away_att,
            home_defense=home_def, away_defense=away_def
        )
