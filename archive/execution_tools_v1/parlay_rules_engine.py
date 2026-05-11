import logging

logger = logging.getLogger(__name__)

class ParlayRulesEngine:
    """
    官方规则守护者：严格校验竞彩与北京单场的 M串1、M串N 及自由过关组合数学规则。
    """
    
    def __init__(self):
        self.JINGCAI_MAX_LEGS = {
            "WDL": 8,
            "HANDICAP": 8,
            "GOALS": 6,
            "CS": 4,
            "HTFT": 4
        }
        
        self.BEIDAN_MAX_LEGS = {
            "WDL": 15,
            "UP_DOWN_ODD_EVEN": 15,
            "HANDICAP": 15,
            "SFGG": 15,
            "GOALS": 15,
            "HTFT": 15,
            "CS": 3
        }
        
        self.JINGCAI_M_N_COMBOS = {
            "3_3": [2], "3_4": [2, 3],
            "4_4": [3], "4_5": [3, 4], "4_6": [2], "4_11": [2, 3, 4],
            "5_5": [4], "5_6": [4, 5], "5_10": [2], "5_16": [3, 4, 5], "5_20": [2, 3], "5_26": [2, 3, 4, 5],
            "6_6": [5], "6_7": [5, 6], "6_15": [2], "6_20": [3], "6_22": [4, 5, 6], "6_35": [2, 3], "6_42": [3, 4, 5, 6], "6_50": [2, 3, 4], "6_57": [2, 3, 4, 5, 6],
            "7_7": [6], "7_8": [6, 7], "7_21": [5], "7_35": [4], "7_120": [2, 3, 4, 5, 6, 7],
            "8_8": [7], "8_9": [7, 8], "8_28": [6], "8_56": [5], "8_70": [4], "8_247": [2, 3, 4, 5, 6, 7, 8], "8_255": [2, 3, 4, 5, 6, 7, 8]
        }

    def validate_ticket_legs(self, lottery_type: str, ticket_legs: list) -> dict:
        max_legs_dict = self.JINGCAI_MAX_LEGS if lottery_type == "竞彩足球" else self.BEIDAN_MAX_LEGS
        
        strictest_limit = 15
        for leg in ticket_legs:
            play_type = leg.get("play_type", "WDL")
            limit = max_legs_dict.get(play_type, 4)
            if limit < strictest_limit:
                strictest_limit = limit
                
        num_legs = len(ticket_legs)
        if num_legs > strictest_limit:
            msg = f"违规：{lottery_type} 包含 {ticket_legs[0].get('play_type')} 玩法时，最多允许 {strictest_limit} 串 1，当前票包含 {num_legs} 场。"
            logger.error(msg)
            return {"is_valid": False, "reason": msg, "max_allowed": strictest_limit}
            
        return {"is_valid": True, "reason": "合法"}

    def decompose_m_n(self, lottery_type: str, m: int, n: int) -> list:
        if lottery_type == "竞彩足球":
            combo_key = f"{m}_{n}"
            if combo_key not in self.JINGCAI_M_N_COMBOS:
                raise ValueError(f"竞彩足球不支持 {m}串{n} 的固定组合。")
            return self.JINGCAI_M_N_COMBOS[combo_key]
        elif lottery_type == "北京单场":
            if n > m or m > 15:
                raise ValueError(f"北京单场不支持 {m}场过{n}关。")
            return [n]
        else:
            raise ValueError(f"未知的彩票类型: {lottery_type}")

    def get_m_n_ticket_combinations(self, ticket_legs: list, m: int, n: int) -> list:
        import itertools
        m_n_map = {
            "3_3": [2], "3_4": [2, 3],
            "4_4": [3], "4_5": [3, 4], "4_6": [2], "4_11": [2, 3, 4],
            "5_5": [4], "5_6": [4, 5], "5_10": [2], "5_16": [3, 4, 5], "5_20": [2, 3], "5_26": [2, 3, 4, 5],
            "6_6": [5], "6_7": [5, 6], "6_15": [2], "6_20": [3], "6_22": [4, 5, 6], "6_35": [2, 3], "6_42": [3, 4, 5, 6], "6_50": [2, 3, 4], "6_57": [2, 3, 4, 5, 6],
            "7_7": [6], "7_8": [6, 7], "7_21": [5], "7_35": [4], "7_120": [2, 3, 4, 5, 6, 7],
            "8_8": [7], "8_9": [7, 8], "8_28": [6], "8_56": [5], "8_70": [4], "8_247": [2, 3, 4, 5, 6, 7, 8]
        }
        
        key = f"{m}_{n}"
        if key not in m_n_map:
            raise ValueError(f"Unsupported M_N combination: {key}")
            
        target_sizes = m_n_map[key]
        combinations = []
        
        for size in target_sizes:
            combos = list(itertools.combinations(ticket_legs, size))
            combinations.extend([list(c) for c in combos])
            
        return combinations

    def generate_free_parlay_combinations(self, match_selections: list, target_parlays: list) -> int:
        import itertools
        import math
        
        total_tickets = 0
        num_matches = len(match_selections)
        
        for k in target_parlays:
            if k <= num_matches:
                for combo in itertools.combinations(match_selections, k):
                    tickets_for_combo = math.prod(combo)
                    total_tickets += tickets_for_combo
                    
        return total_tickets

    def calculate_chuantong_combinations(self, match_selections: list, play_type: str = "renjiu") -> int:
        import itertools
        import math
        
        num_matches = len(match_selections)
        
        if sum(match_selections) > 50:
             raise ValueError("⚠️ 物理风控拦截：单票总选择项超过 50 个，属于严重越界或组合爆炸攻击，已拒绝出票。")
             
        if play_type == "14_match":
            if num_matches != 14:
                raise ValueError("14场胜负彩必须且只能选择14场比赛")
            return math.prod(match_selections)
            
        elif play_type == "renjiu":
            if num_matches < 9 or num_matches > 14:
                raise ValueError("任选九场必须选择 9 至 14 场比赛")
            total_tickets = 0
            for combo in itertools.combinations(match_selections, 9):
                total_tickets += math.prod(combo)
            return total_tickets
            
        elif play_type == "6_htft":
            if num_matches != 6:
                raise ValueError("6场半全场必须选择6场比赛")
            return math.prod(match_selections)
            
        elif play_type == "4_goals":
            if num_matches != 4:
                raise ValueError("4场进球彩必须选择4场比赛")
            return math.prod(match_selections)
            
        else:
            raise ValueError(f"未知的传统足彩玩法: {play_type}")

    def calculate_fuzzy_banker_combinations(self, banker_selections: list, tuo_selections: list, parlay_size: int, min_bankers: int = None) -> int:
        import itertools
        import math
        
        num_bankers = len(banker_selections)
        num_tuo = len(tuo_selections)
        total_matches = num_bankers + num_tuo
        
        if min_bankers is None:
            min_bankers = num_bankers
            
        if num_bankers > total_matches:
            raise ValueError("胆码数量不能超过总选取场次")
        if min_bankers > num_bankers:
            raise ValueError("最少命中胆码数不能超过设定的胆码总数")
        if parlay_size > total_matches:
            raise ValueError("过关场次不能大于总场次")
            
        total_tickets = 0
        
        max_possible_bankers_in_ticket = min(num_bankers, parlay_size)
        for k in range(min_bankers, max_possible_bankers_in_ticket + 1):
            tuo_needed = parlay_size - k
            
            if 0 <= tuo_needed <= num_tuo:
                banker_combinations_sum = 0
                for b_combo in itertools.combinations(banker_selections, k):
                    banker_combinations_sum += math.prod(b_combo)
                    
                tuo_combinations_sum = 0
                if tuo_needed == 0:
                    tuo_combinations_sum = 1
                else:
                    for t_combo in itertools.combinations(tuo_selections, tuo_needed):
                        tuo_combinations_sum += math.prod(t_combo)
                        
                total_tickets += banker_combinations_sum * tuo_combinations_sum
                
        return total_tickets
