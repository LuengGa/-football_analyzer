"""
GameTypeManager - 玩法类型管理器
统一管理竞彩、北单、传统足彩的所有玩法
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import math
from itertools import combinations
import numpy as np
from scipy.stats import poisson


@dataclass
class GameType:
    """玩法类型定义"""
    id: str
    name: str
    category: str  # jingcai, beidan, traditional
    description: str
    options: List[str]


class GameTypeManager:
    """玩法类型管理器"""
    
    def __init__(self):
        self.game_types = self._initialize_game_types()
        
    def _initialize_game_types(self) -> Dict[str, GameType]:
        """初始化所有玩法类型"""
        return {
            # ========== 竞彩足球 (Jingcai) ==========
            "jingcai_wdl": GameType(
                id="jingcai_wdl",
                name="竞彩胜平负",
                category="jingcai",
                description="竞彩标准胜平负玩法",
                options=["胜", "平", "负"]
            ),
            "jingcai_handicap": GameType(
                id="jingcai_handicap",
                name="竞彩让球胜平负",
                category="jingcai",
                description="竞彩让球胜平负玩法",
                options=["胜", "平", "负"]
            ),
            "jingcai_score": GameType(
                id="jingcai_score",
                name="竞彩比分",
                category="jingcai",
                description="竞彩比分玩法",
                options=["0:0", "1:0", "0:1", "2:0", "1:1", "0:2", "2:1", "1:2", "3:0", "3:1", "3:2", "其他"]
            ),
            "jingcai_total": GameType(
                id="jingcai_total",
                name="竞彩总进球数",
                category="jingcai",
                description="竞彩总进球数玩法",
                options=["0", "1", "2", "3", "4", "5", "6", "7+"]
            ),
            "jingcai_htft": GameType(
                id="jingcai_htft",
                name="竞彩半全场",
                category="jingcai",
                description="竞彩半全场玩法",
                options=["胜胜", "胜平", "胜负", "平胜", "平平", "平负", "负胜", "负平", "负负"]
            ),
            # ========== 北京单场 (Beidan) ==========
            "beidan_wdl": GameType(
                id="beidan_wdl",
                name="北单胜平负",
                category="beidan",
                description="北京单场胜平负玩法",
                options=["胜", "平", "负"]
            ),
            "beidan_handicap": GameType(
                id="beidan_handicap",
                name="北单让球胜平负",
                category="beidan",
                description="北京单场让球胜平负玩法",
                options=["胜", "平", "负"]
            ),
            "beidan_total": GameType(
                id="beidan_total",
                name="北单总进球数",
                category="beidan",
                description="北京单场总进球数玩法",
                options=["0", "1", "2", "3", "4", "5", "6", "7+"]
            ),
            "beidan_bonus": GameType(
                id="beidan_bonus",
                name="北单上下单双",
                category="beidan",
                description="北京单场上下单双玩法",
                options=["上单", "上双", "下单", "下双"]
            ),
            "beidan_score": GameType(
                id="beidan_score",
                name="北单比分",
                category="beidan",
                description="北京单场比分玩法",
                options=["0:0", "1:0", "0:1", "2:0", "1:1", "0:2", "2:1", "1:2", "3:0", "3:1", "3:2", "其他"]
            ),
            "beidan_htft": GameType(
                id="beidan_htft",
                name="北单半全场",
                category="beidan",
                description="北京单场半全场玩法",
                options=["胜胜", "胜平", "胜负", "平胜", "平平", "平负", "负胜", "负平", "负负"]
            ),
            # ========== 传统足彩 (Traditional) ==========
            "traditional_14": GameType(
                id="traditional_14",
                name="足彩14场",
                category="traditional",
                description="传统足彩14场胜负玩法",
                options=["3", "1", "0"]  # 胜平负
            ),
            "traditional_9": GameType(
                id="traditional_9",
                name="足彩任选9场",
                category="traditional",
                description="传统足彩任选9场玩法",
                options=["3", "1", "0"]
            ),
            # ========== 串关玩法 (Parlay) ==========
            "parlay_mix": GameType(
                id="parlay_mix",
                name="混合过关",
                category="parlay",
                description="竞彩混合过关玩法，支持不同玩法混合串关",
                options=["2串1", "3串1", "4串1", "5串1", "6串1", "M串N"]
            ),
            "beidan_parlay": GameType(
                id="beidan_parlay",
                name="北单胜负过关",
                category="parlay",
                description="北京单场胜负过关玩法",
                options=["2串1", "3串1", "4串1", "5串1", "6串1", "7串1", "8串1"]
            ),
            # ========== 国际玩法 (International) ==========
            "asian_handicap": GameType(
                id="asian_handicap",
                name="亚洲盘",
                category="international",
                description="亚洲让球盘玩法",
                options=["上盘", "下盘"]
            ),
            "european_odds": GameType(
                id="european_odds",
                name="欧洲盘",
                category="international",
                description="欧洲标准盘玩法",
                options=["胜", "平", "负"]
            ),
            "over_under": GameType(
                id="over_under",
                name="大小球",
                category="international",
                description="总进球大小玩法",
                options=["大", "小"]
            ),
            "correct_score": GameType(
                id="correct_score",
                name="波胆",
                category="international",
                description="精确比分玩法",
                options=["0:0", "1:0", "0:1", "2:0", "1:1", "0:2", "2:1", "1:2", "其他"]
            ),
            "both_teams_score": GameType(
                id="both_teams_score",
                name="双方进球",
                category="international",
                description="双方是否都进球",
                options=["是", "否"]
            ),
            "double_chance": GameType(
                id="double_chance",
                name="双重机会",
                category="international",
                description="双重结果玩法",
                options=["胜/平", "胜/负", "平/负"]
            ),
            "first_half_winner": GameType(
                id="first_half_winner",
                name="半场结果",
                category="international",
                description="半场胜负",
                options=["胜", "平", "负"]
            ),
            "draw_no_bet": GameType(
                id="draw_no_bet",
                name="无平局",
                category="international",
                description="平局返还本金",
                options=["胜", "负"]
            ),
            "total_corners": GameType(
                id="total_corners",
                name="角球数",
                category="international",
                description="总角球数大小",
                options=["大", "小"]
            ),
            "card_count": GameType(
                id="card_count",
                name="黄牌数",
                category="international",
                description="黄牌数量",
                options=["大", "小"]
            ),
            "first_goal_scorer": GameType(
                id="first_goal_scorer",
                name="首名进球者",
                category="international",
                description="谁先进球",
                options=["主队球员", "客队球员", "无进球"]
            ),
            "anytime_goal_scorer": GameType(
                id="anytime_goal_scorer",
                name="任意进球者",
                category="international",
                description="任意时间进球",
                options=["主队球员", "客队球员", "不进球"]
            ),
            "over_under_half": GameType(
                id="over_under_half",
                name="半场大小球",
                category="international",
                description="半场总进球",
                options=["大", "小"]
            ),
            "handicap_half": GameType(
                id="handicap_half",
                name="半场让球",
                category="international",
                description="半场让球玩法",
                options=["上盘", "下盘"]
            ),
        }
    
    def get_game_type(self, game_type_id: str) -> Optional[GameType]:
        """获取玩法类型"""
        return self.game_types.get(game_type_id)
    
    def get_by_category(self, category: str) -> List[GameType]:
        """按类别获取玩法"""
        return [gt for gt in self.game_types.values() if gt.category == category]
    
    def get_all_categories(self) -> List[str]:
        """获取所有类别"""
        return list(set(gt.category for gt in self.game_types.values()))
    
    def get_jingcai_games(self) -> List[GameType]:
        """获取竞彩玩法"""
        return self.get_by_category("jingcai")
    
    def get_beidan_games(self) -> List[GameType]:
        """获取北单玩法"""
        return self.get_by_category("beidan")
    
    def get_traditional_games(self) -> List[GameType]:
        """获取传统足彩玩法"""
        return self.get_by_category("traditional")
    
    def get_international_games(self) -> List[GameType]:
        """获取国际玩法"""
        return self.get_by_category("international")
    
    def get_parlay_games(self) -> List[GameType]:
        """获取串关玩法"""
        return self.get_by_category("parlay")
    
    def get_all_games(self) -> List[GameType]:
        """获取所有玩法"""
        return list(self.game_types.values())
    
    def count_by_category(self) -> Dict[str, int]:
        """按类别统计玩法数量"""
        counts = {}
        for gt in self.game_types.values():
            counts[gt.category] = counts.get(gt.category, 0) + 1
        return counts


class ParlayCalculator:
    """串关计算器"""
    
    @staticmethod
    def calculate_mn_combinations(matches_count: int, pass_type: int) -> int:
        """计算M串N组合数"""
        if pass_type > matches_count:
            return 0
        return math.comb(matches_count, pass_type)
    
    @staticmethod
    def calculate_jingcai_max_bonus(selected_odds: List[float], pass_type: int, bet_amount: float = 2.0) -> float:
        """计算竞彩最大奖金（含官方封顶）"""
        if len(selected_odds) < pass_type:
            return 0.0
        
        combos = list(combinations(selected_odds, pass_type))
        
        # 官方封顶规则
        if pass_type <= 3:
            max_limit = 200_000.0
        elif pass_type <= 5:
            max_limit = 500_000.0
        else:
            max_limit = 1_000_000.0
        
        total_max_bonus = 0.0
        for combo in combos:
            combo_bonus = bet_amount * np.prod(combo)
            combo_bonus = min(combo_bonus, max_limit)
            if combo_bonus >= 10000.0:
                combo_bonus *= 0.80
            total_max_bonus += combo_bonus
        
        return round(total_max_bonus, 2)
    
    @staticmethod
    def calculate_beidan_real_sp(estimated_sp_list: List[float]) -> float:
        """计算北单真实SP奖金（官方规则：65%返奖率）
        
        官方公式：单注奖金 = 单注本金 × 所选场次的单场SP值连乘 × 65%
        来源：中国体彩网官方规则
        """
        # 本金2元 × SP值连乘 × 65%返奖率
        raw_bonus = 2.0 * np.prod(estimated_sp_list) * 0.65
        # 保底2元
        real_bonus = max(raw_bonus, 2.0)
        # 1万元以上扣20%税
        if real_bonus >= 10000.0:
            real_bonus *= 0.80
        return round(real_bonus, 2)
    
    @staticmethod
    def calculate_traditional_bonus(total_sales: float, winners: int, is_14game: bool = True) -> Dict[str, float]:
        """计算传统足彩奖金（官方规则）
        
        官方规则：
        - 14场胜负：一等奖占当期奖金70%，二等奖占30%
        - 任选9场：只设一等奖，占当期奖金100%
        - 返奖率：65%
        - 奖池：上期未中出奖金 + 超出封顶部分
        
        Args:
            total_sales: 当期销售额
            winners: 中奖注数
            is_14game: True=14场, False=任选9场
            
        Returns:
            奖金分配字典
        """
        # 返奖奖金 = 销售额 × 65%
        prize_pool = total_sales * 0.65
        
        if is_14game:
            # 14场：一等奖70%，二等奖30%
            first_prize = prize_pool * 0.70
            second_prize = prize_pool * 0.30
            
            return {
                "first_prize_per_winner": round(first_prize / winners if winners > 0 else 0, 2),
                "second_prize_per_winner": round(second_prize / winners if winners > 0 else 0, 2),
                "total_first_prize": round(first_prize, 2),
                "total_second_prize": round(second_prize, 2),
                "description": "14场胜负：一等奖70%，二等奖30%"
            }
        else:
            # 任选9场：只设一等奖
            return {
                "first_prize_per_winner": round(prize_pool / winners if winners > 0 else 0, 2),
                "total_first_prize": round(prize_pool, 2),
                "description": "任选9场：一等奖100%"
            }
    
    @staticmethod
    def calculate_mixed_parlay(
        selections: List[Dict[str, Any]],
        pass_type: int,
        bet_type: str = "jingcai"  # "jingcai" or "beidan"
    ) -> Dict[str, Any]:
        """
        计算混合过关奖金
        
        Args:
            selections: 选中的比赛和玩法 [{"game_type": "jingcai_wdl", "odds": 1.85}, ...]
            pass_type: N串1
            bet_type: 竞彩或北单
            
        Returns:
            奖金计算结果
        """
        odds_list = [s["odds"] for s in selections]
        
        if len(odds_list) < pass_type:
            return {"success": False, "error": "比赛数量不足"}
        
        if bet_type == "jingcai":
            bonus = ParlayCalculator.calculate_jingcai_max_bonus(odds_list, pass_type)
            return {
                "success": True,
                "type": "jingcai_mixed_parlay",
                "pass_type": f"{pass_type}串1",
                "total_odds": round(np.prod(odds_list), 2),
                "max_bonus": bonus,
                "selections": selections
            }
        else:
            bonus = ParlayCalculator.calculate_beidan_real_sp(odds_list)
            return {
                "success": True,
                "type": "beidan_parlay",
                "pass_type": f"{pass_type}串1",
                "total_sp": round(np.prod(odds_list), 2),
                "real_bonus": bonus,
                "selections": selections
            }
    
    @staticmethod
    def calculate_mixed_mn(
        selections: List[Dict[str, Any]],
        min_pass: int,
        max_pass: int,
        bet_type: str = "jingcai"
    ) -> Dict[str, Any]:
        """
        计算M串N奖金（多串组合）
        
        Args:
            selections: 选中的比赛
            min_pass: 最小串关数
            max_pass: 最大串关数
            
        Returns:
            奖金计算结果
        """
        total_bonus = 0.0
        breakdown = []
        
        for pass_type in range(min_pass, max_pass + 1):
            count = ParlayCalculator.calculate_mn_combinations(len(selections), pass_type)
            odds_list = [s["odds"] for s in selections]
            
            if bet_type == "jingcai":
                bonus = ParlayCalculator.calculate_jingcai_max_bonus(odds_list, pass_type)
            else:
                bonus = ParlayCalculator.calculate_beidan_real_sp(odds_list)
            
            total_bonus += bonus * count
            breakdown.append({
                "pass_type": f"{pass_type}串1",
                "combinations": count,
                "bonus_per_combo": bonus,
                "total": bonus * count
            })
        
        return {
            "success": True,
            "type": f"{len(selections)}串{sum(b['combinations'] for b in breakdown)}",
            "min_pass": min_pass,
            "max_pass": max_pass,
            "total_bonus": round(total_bonus, 2),
            "breakdown": breakdown
        }


class GameProbabilityEngine:
    """玩法概率引擎"""
    
    def __init__(self, max_goals: int = 7):
        self.max_goals = max_goals
    
    def calculate_all_markets(self, home_xg: float, away_xg: float, handicap: float = 0.0) -> Dict[str, Any]:
        """计算所有玩法概率"""
        if home_xg < 0 or away_xg < 0:
            raise ValueError("xG 必须大于等于 0")
        
        dynamic_max_goals = max(self.max_goals, int(max(home_xg, away_xg) * 2 + 5))
        
        # 构建泊松概率矩阵
        matrix = [[0.0 for _ in range(dynamic_max_goals)] for _ in range(dynamic_max_goals)]
        for h in range(dynamic_max_goals):
            for a in range(dynamic_max_goals):
                matrix[h][a] = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
        
        # 胜平负
        w, d, l = 0.0, 0.0, 0.0
        # 让球胜平负
        hw, hd, hl = 0.0, 0.0, 0.0
        # 总进球
        total_goals = {str(i): 0.0 for i in range(8)}
        total_goals["7+"] = 0.0
        # 上下单双
        shang_dan, shang_shuang, xia_dan, xia_shuang = 0.0, 0.0, 0.0, 0.0
        # 比分分布
        score_probs = {}
        
        for h in range(dynamic_max_goals):
            for a in range(dynamic_max_goals):
                prob = matrix[h][a]
                
                # W/D/L
                if h > a: w += prob
                elif h == a: d += prob
                else: l += prob
                
                # Handicap
                adjusted_h = h + handicap
                if adjusted_h > a: hw += prob
                elif adjusted_h == a: hd += prob
                else: hl += prob
                
                # Total Goals
                tg = h + a
                if tg >= 7:
                    total_goals["7+"] += prob
                else:
                    total_goals[str(tg)] += prob
                
                # 上下单双
                is_shang = (tg >= 3)
                is_shuang = (tg % 2 == 0)
                if is_shang and not is_shuang: shang_dan += prob
                elif is_shang and is_shuang: shang_shuang += prob
                elif not is_shang and not is_shuang: xia_dan += prob
                elif not is_shang and is_shuang: xia_shuang += prob
                
                # 比分
                if h <= 3 and a <= 3:
                    score_probs[f"{h}:{a}"] = prob
        
        # 半全场
        ht_home_xg, ht_away_xg = home_xg * 0.45, away_xg * 0.45
        sh_home_xg, sh_away_xg = home_xg * 0.55, away_xg * 0.55
        
        htft = {
            "胜胜": 0.0, "胜平": 0.0, "胜负": 0.0,
            "平胜": 0.0, "平平": 0.0, "平负": 0.0,
            "负胜": 0.0, "负平": 0.0, "负负": 0.0,
        }
        
        ht_max = max(self.max_goals, int(max(ht_home_xg, ht_away_xg) * 2 + 5))
        sh_max = max(self.max_goals, int(max(sh_home_xg, sh_away_xg) * 2 + 5))
        
        for h1 in range(ht_max):
            for a1 in range(ht_max):
                p_ht = poisson.pmf(h1, ht_home_xg) * poisson.pmf(a1, ht_away_xg)
                if p_ht < 1e-6: continue
                
                ht_res = "胜" if h1 > a1 else "平" if h1 == a1 else "负"
                
                for h2 in range(sh_max):
                    for a2 in range(sh_max):
                        p_sh = poisson.pmf(h2, sh_home_xg) * poisson.pmf(a2, sh_away_xg)
                        ft_h = h1 + h2
                        ft_a = a1 + a2
                        ft_res = "胜" if ft_h > ft_a else "平" if ft_h == ft_a else "负"
                        htft[f"{ht_res}{ft_res}"] += p_ht * p_sh
        
        htft_sum = sum(htft.values())
        if htft_sum > 0:
            htft = {k: v / htft_sum for k, v in htft.items()}
        
        return {
            "wdl": {"胜": round(float(w), 4), "平": round(float(d), 4), "负": round(float(l), 4)},
            "handicap": {"胜": round(float(hw), 4), "平": round(float(hd), 4), "负": round(float(hl), 4)},
            "total_goals": {k: round(float(v), 4) for k, v in total_goals.items()},
            "bd_up_down": {"上单": round(float(shang_dan), 4), "上双": round(float(shang_shuang), 4), "下单": round(float(xia_dan), 4), "下双": round(float(shang_shuang), 4)},
            "htft": {k: round(float(v), 4) for k, v in htft.items()},
            "score": {k: round(float(v), 4) for k, v in score_probs.items()}
        }
    
    def calculate_asian_handicap(self, home_xg: float, away_xg: float, handicap_line: float) -> Dict[str, float]:
        """计算亚洲盘概率"""
        dynamic_max_goals = max(self.max_goals, int(max(home_xg, away_xg) * 2 + 5))
        
        over_prob = 0.0
        under_prob = 0.0
        
        for h in range(dynamic_max_goals):
            for a in range(dynamic_max_goals):
                prob = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                adjusted_h = h + handicap_line
                if adjusted_h > a:
                    over_prob += prob
                else:
                    under_prob += prob
        
        return {"上盘": round(over_prob, 4), "下盘": round(under_prob, 4)}
    
    def calculate_over_under(self, home_xg: float, away_xg: float, line: float = 2.5) -> Dict[str, float]:
        """计算大小球概率"""
        dynamic_max_goals = max(self.max_goals, int(max(home_xg, away_xg) * 2 + 5))
        
        over_prob = 0.0
        under_prob = 0.0
        
        for h in range(dynamic_max_goals):
            for a in range(dynamic_max_goals):
                prob = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                if h + a > line:
                    over_prob += prob
                else:
                    under_prob += prob
        
        return {"大": round(over_prob, 4), "小": round(under_prob, 4)}
    
    def calculate_both_teams_score(self, home_xg: float, away_xg: float) -> Dict[str, float]:
        """计算双方进球概率"""
        dynamic_max_goals = max(self.max_goals, int(max(home_xg, away_xg) * 2 + 5))
        
        both_score = 0.0
        no_both = 0.0
        
        for h in range(dynamic_max_goals):
            for a in range(dynamic_max_goals):
                prob = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                if h > 0 and a > 0:
                    both_score += prob
                else:
                    no_both += prob
        
        return {"是": round(both_score, 4), "否": round(no_both, 4)}


# 全局实例
_game_type_manager = None
_parlay_calculator = None
_probability_engine = None

def get_game_type_manager() -> GameTypeManager:
    """获取玩法类型管理器实例"""
    global _game_type_manager
    if _game_type_manager is None:
        _game_type_manager = GameTypeManager()
    return _game_type_manager

def get_parlay_calculator() -> ParlayCalculator:
    """获取串关计算器实例"""
    global _parlay_calculator
    if _parlay_calculator is None:
        _parlay_calculator = ParlayCalculator()
    return _parlay_calculator

def get_probability_engine() -> GameProbabilityEngine:
    """获取概率引擎实例"""
    global _probability_engine
    if _probability_engine is None:
        _probability_engine = GameProbabilityEngine()
    return _probability_engine


if __name__ == "__main__":
    print("=" * 60)
    print("🎮 玩法类型管理器测试")
    print("=" * 60)
    
    # 测试玩法类型管理器
    manager = get_game_type_manager()
    
    print("\n📊 各类玩法数量统计:")
    counts = manager.count_by_category()
    for category, count in counts.items():
        print(f"  {category}: {count} 种")
    
    print("\n⚽ 竞彩玩法:")
    for game in manager.get_jingcai_games():
        print(f"  - {game.name}")
    
    print("\n🎟️ 北单玩法:")
    for game in manager.get_beidan_games():
        print(f"  - {game.name}")
    
    print("\n🌍 国际玩法:")
    for game in manager.get_international_games():
        print(f"  - {game.name}")
    
    # 测试串关计算器
    print("\n" + "=" * 60)
    print("🔗 串关计算器测试")
    print("=" * 60)
    
    parlay = get_parlay_calculator()
    
    # 测试混合过关
    selections = [
        {"game_type": "jingcai_wdl", "odds": 1.85},
        {"game_type": "jingcai_handicap", "odds": 2.10},
        {"game_type": "jingcai_total", "odds": 1.90}
    ]
    
    result = parlay.calculate_mixed_parlay(selections, 3)
    print(f"\n混合过关 3串1:")
    print(f"  总赔率: {result['total_odds']}")
    print(f"  最大奖金: {result['max_bonus']}元")
    
    # 测试M串N
    result_mn = parlay.calculate_mixed_mn(selections, 2, 3)
    print(f"\n3串6 (2串1+3串1):")
    for b in result_mn["breakdown"]:
        print(f"  {b['pass_type']}: {b['combinations']}注, 每注{b['bonus_per_combo']}元, 合计{b['total']}元")
    print(f"  总奖金: {result_mn['total_bonus']}元")
    
    # 测试概率引擎
    print("\n" + "=" * 60)
    print("📈 概率引擎测试")
    print("=" * 60)
    
    engine = get_probability_engine()
    
    probs = engine.calculate_all_markets(1.8, 1.2)
    print(f"\n胜平负概率: {probs['wdl']}")
    print(f"总进球概率: {probs['total_goals']}")
    print(f"半全场概率: {probs['htft']}")
    
    # 测试亚洲盘
    asian = engine.calculate_asian_handicap(1.8, 1.2, -0.5)
    print(f"\n亚洲盘(-0.5)概率: {asian}")
    
    # 测试大小球
    ou = engine.calculate_over_under(1.8, 1.2, 2.5)
    print(f"大小球(2.5)概率: {ou}")
