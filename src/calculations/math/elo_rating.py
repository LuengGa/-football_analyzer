"""
EloRating - ELO评分系统
用于计算和更新球队的ELO评分
"""

class EloRating:
    """ELO评分系统"""
    
    def __init__(self, initial_rating: int = 1800, k_factor: int = 32):
        self.initial_rating = initial_rating
        self.k_factor = k_factor
    
    def calculate_expectation(self, rating1: float, rating2: float) -> float:
        """计算期望胜率"""
        return 1 / (1 + 10 ** ((rating2 - rating1) / 400))
    
    def calculate_elo_after_match(
        self,
        rating: float,
        expected: float,
        actual: float
    ) -> float:
        """计算比赛后的ELO评分"""
        return rating + self.k_factor * (actual - expected)
    
    def update_ratings(
        self,
        home_rating: float,
        away_rating: float,
        result: str = None
    ) -> dict:
        """更新两队的ELO评分"""
        expected_home = self.calculate_expectation(home_rating, away_rating)
        expected_away = 1 - expected_home
        
        if result == "home":
            actual_home, actual_away = 1.0, 0.0
        elif result == "draw":
            actual_home, actual_away = 0.5, 0.5
        elif result == "away":
            actual_home, actual_away = 0.0, 1.0
        else:
            # 如果没有结果，返回预期评分变化
            return {
                "home": home_rating,
                "away": away_rating,
                "expected_home": expected_home,
                "expected_away": expected_away
            }
        
        new_home = self.calculate_elo_after_match(home_rating, expected_home, actual_home)
        new_away = self.calculate_elo_after_match(away_rating, expected_away, actual_away)
        
        return {
            "home": round(new_home, 1),
            "away": round(new_away, 1),
            "expected_home": round(expected_home, 4),
            "expected_away": round(expected_away, 4)
        }
    
    def predict_match(self, home_rating: float, away_rating: float) -> dict:
        """预测比赛结果"""
        expected_home = self.calculate_expectation(home_rating, away_rating)
        expected_draw = 0.25  # 平局概率估算
        
        return {
            "home_win_prob": round(expected_home * (1 - expected_draw), 4),
            "draw_prob": round(expected_draw, 4),
            "away_win_prob": round((1 - expected_home) * (1 - expected_draw), 4)
        }
