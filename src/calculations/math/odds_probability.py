"""
OddsProbability - 赔率概率计算
将赔率转换为概率
"""

class OddsProbability:
    """赔率概率计算器"""
    
    def __init__(self, margin: float = 0.05):
        self.margin = margin  # 抽水比例
    
    def odds_to_probability(self, odds: float) -> float:
        """将赔率转换为概率"""
        if odds <= 1.0:
            return 0.0
        return 1 / odds
    
    def calculate_overround(self, odds_home: float, odds_draw: float, odds_away: float) -> float:
        """计算返还率(overround)"""
        prob_home = self.odds_to_probability(odds_home)
        prob_draw = self.odds_to_probability(odds_draw)
        prob_away = self.odds_to_probability(odds_away)
        return prob_home + prob_draw + prob_away
    
    def normalize_probabilities(
        self,
        odds_home: float,
        odds_draw: float,
        odds_away: float
    ) -> dict:
        """标准化概率（移除抽水）"""
        prob_home = self.odds_to_probability(odds_home)
        prob_draw = self.odds_to_probability(odds_draw)
        prob_away = self.odds_to_probability(odds_away)
        
        overround = prob_home + prob_draw + prob_away
        
        if overround == 0:
            return {"home": 0.333, "draw": 0.334, "away": 0.333}
        
        return {
            "home": prob_home / overround,
            "draw": prob_draw / overround,
            "away": prob_away / overround
        }
    
    def calculate_value(self, estimated_prob: float, odds: float) -> float:
        """计算价值分数"""
        if odds <= 1.0:
            return 0.0
        implied_prob = self.odds_to_probability(odds)
        edge = estimated_prob - implied_prob
        return edge * 100  # 转换为百分比
    
    def find_value_bets(
        self,
        estimated_probs: dict,
        odds: dict
    ) -> dict:
        """寻找价值投注"""
        normalized_probs = self.normalize_probabilities(
            odds.get("home", 2.0),
            odds.get("draw", 3.0),
            odds.get("away", 3.0)
        )
        
        value_bets = {}
        
        for outcome in ["home", "draw", "away"]:
            estimated = estimated_probs.get(outcome, 0.0)
            implied = normalized_probs.get(outcome, 0.0)
            edge = estimated - implied
            
            if edge > 0.02:  # 超过2%的优势
                value_bets[outcome] = {
                    "estimated_prob": round(estimated, 4),
                    "implied_prob": round(implied, 4),
                    "edge": round(edge * 100, 2),
                    "odds": odds.get(outcome, 0.0)
                }
        
        return value_bets
