import math
import numpy as np
from typing import Dict, List, Tuple, Any

class AdvancedLotteryMath:
    @staticmethod
    def dixon_coles_poisson_adjustment(xg_home: float, xg_away: float, rho: float = -0.05, zero_inflation: float = 1.05) -> dict:
        """
        [实战强化] Dixon-Coles 双变量泊松分布 + 零膨胀修正
        修复了纯泊松模型严重低估 0-0 平局发生率的致命缺陷。
        zero_inflation: 对 0-0 结果的额外放大系数 (默认放大 5%)
        """
        max_goals = 10
        prob_matrix = np.zeros((max_goals, max_goals))
        
        for x in range(max_goals):
            for y in range(max_goals):
                p_x = (math.exp(-xg_home) * (xg_home ** x)) / math.factorial(x)
                p_y = (math.exp(-xg_away) * (xg_away ** y)) / math.factorial(y)
                
                correction = 1.0
                if x == 0 and y == 0:
                    correction = (1 - xg_home * xg_away * rho) * zero_inflation
                elif x == 0 and y == 1:
                    correction = 1 + xg_home * rho
                elif x == 1 and y == 0:
                    correction = 1 + xg_away * rho
                elif x == 1 and y == 1:
                    correction = 1 - rho
                    
                prob_matrix[x, y] = max(0, p_x * p_y * correction)

        prob_matrix = prob_matrix / np.sum(prob_matrix)
        
        return {
            "home_win": round(float(np.sum(np.tril(prob_matrix, -1))), 4),
            "draw": round(float(np.sum(np.diag(prob_matrix))), 4),
            "away_win": round(float(np.sum(np.triu(prob_matrix, 1))), 4),
            "prob_0_0": round(float(prob_matrix[0, 0]), 4),
            "matrix": prob_matrix
        }

    @staticmethod
    def map_poisson_to_jingcai_scores(prob_matrix: np.ndarray) -> Dict[str, float]:
        """
        进化 1：分析策略 - 全玩法精确映射
        将泊松矩阵精准映射到竞彩官方的比分选项中，将长尾小概率事件收敛进"胜其他/平其他/负其他"。
        """
        if isinstance(prob_matrix, list):
            prob_matrix = np.array(prob_matrix)
        scores = {}
        
        home_win_scores = [(1,0), (2,0), (2,1), (3,0), (3,1), (3,2), (4,0), (4,1), (4,2), (5,0), (5,1), (5,2)]
        draw_scores = [(0,0), (1,1), (2,2), (3,3)]
        away_win_scores = [(0,1), (0,2), (1,2), (0,3), (1,3), (2,3), (0,4), (1,4), (2,4), (0,5), (1,5), (2,5)]
        
        win_other_prob = 0.0
        draw_other_prob = 0.0
        lose_other_prob = 0.0
        
        max_g = prob_matrix.shape[0]
        
        for i in range(max_g):
            for j in range(max_g):
                p = float(prob_matrix[i, j])
                score_str = f"{i}:{j}"
                
                if i > j:
                    if (i, j) in home_win_scores:
                        scores[score_str] = round(p, 4)
                    else:
                        win_other_prob += p
                elif i == j:
                    if (i, j) in draw_scores:
                        scores[score_str] = round(p, 4)
                    else:
                        draw_other_prob += p
                else:
                    if (i, j) in away_win_scores:
                        scores[score_str] = round(p, 4)
                    else:
                        lose_other_prob += p
                        
        scores["胜其他"] = round(win_other_prob, 4)
        scores["平其他"] = round(draw_other_prob, 4)
        scores["负其他"] = round(lose_other_prob, 4)
        
        return scores

    @staticmethod
    def calculate_beidan_sxds_matrix(prob_matrix: np.ndarray) -> Dict[str, float]:
        """
        进化补充：北京单场"上下单双"玩法概率映射
        上/下: 总进球 >=3 为上，<3 为下
        单/双: 总进球奇数为单，偶数为双
        """
        if isinstance(prob_matrix, list):
            prob_matrix = np.array(prob_matrix)
        res = {"上单": 0.0, "上双": 0.0, "下单": 0.0, "下双": 0.0}
        max_g = prob_matrix.shape[0]
        
        for i in range(max_g):
            for j in range(max_g):
                p = float(prob_matrix[i, j])
                total_goals = i + j
                
                is_shang = total_goals >= 3
                is_dan = (total_goals % 2) != 0
                
                if is_shang and is_dan: res["上单"] += p
                elif is_shang and not is_dan: res["上双"] += p
                elif not is_shang and is_dan: res["下单"] += p
                else: res["下双"] += p
                
        return {k: round(v, 4) for k, v in res.items()}

    @staticmethod
    def calculate_zucai_value_index(matches: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """
        进化 2：选场策略 - 足彩价值指数 (Value Index)
        计算真实概率与大众投注比例的偏差，找出防冷/爆冷节点。
        """
        result = []
        for m in matches:
            true_p = m.get("true_prob", 0.0)
            pub_p = m.get("public_prob", 0.0)
            val_idx = true_p / pub_p if pub_p > 0 else 1.0
            is_value = val_idx > 1.2 and true_p > 0.20
            
            m_copy = dict(m)
            m_copy["value_index"] = round(val_idx, 3)
            m_copy["is_value_pick"] = is_value
            result.append(m_copy)
            
        return result

    @staticmethod
    def optimize_jingcai_ticket(num_legs: int, combined_odds: float, target_investment: float) -> Dict[str, float]:
        """
        进化 3：投注策略 - 智能拆单避税器 (Smart Splitter)
        单注奖金超过 10,000 元扣 20% 税。
        根据 M串N 法定最高奖金封顶计算最优倍投拆票方案。
        """
        single_bet_bonus = 2.0 * combined_odds
        is_taxed = single_bet_bonus >= 10000.0
        
        post_tax_odds = combined_odds * 0.8 if is_taxed else combined_odds
        post_tax_single_bonus = 2.0 * post_tax_odds
        
        if num_legs <= 3: max_ticket_payout = 200_000.0
        elif num_legs <= 5: max_ticket_payout = 500_000.0
        else: max_ticket_payout = 1_000_000.0
        
        if post_tax_single_bonus > 0:
            max_bets_per_ticket = math.floor(max_ticket_payout / post_tax_single_bonus)
        else:
            max_bets_per_ticket = 0
            
        max_bets_per_ticket = min(max_bets_per_ticket, 50)
        
        total_bets_needed = target_investment / 2.0
        
        if max_bets_per_ticket > 0:
            suggested_tickets = math.ceil(total_bets_needed / max_bets_per_ticket)
        else:
            suggested_tickets = 0
            
        return {
            "is_taxed": is_taxed,
            "post_tax_odds": round(post_tax_odds, 2),
            "max_bets_per_ticket": max_bets_per_ticket,
            "suggested_tickets": suggested_tickets
        }

    @staticmethod
    def calculate_parlay_kelly(legs: List[Dict[str, float]], lottery_type: str = "JINGCAI") -> Dict[str, float]:
        """
        进化 4：串关策略 - Kelly 组合期望与仓位
        """
        combined_prob = 1.0
        combined_odds = 1.0
        
        for leg in legs:
            combined_prob *= leg.get("prob", 0.0)
            combined_odds *= leg.get("odds", 1.0)
            
        if lottery_type == "BEIDAN":
            combined_odds *= 0.65
            
        ev = (combined_prob * combined_odds) - 1.0
        
        b = combined_odds - 1.0
        if b > 0:
            kelly_fraction = (combined_prob * b - (1 - combined_prob)) / b
        else:
            kelly_fraction = 0.0
            
        return {
            "combined_prob": round(combined_prob, 4),
            "combined_odds": round(combined_odds, 2),
            "ev": round(ev, 4),
            "kelly_fraction": round(kelly_fraction, 4)
        }

    @staticmethod
    def calculate_last_leg_hedge(original_bet: float, potential_payout: float, hedge_odds: Dict[str, float]) -> Dict[str, Any]:
        """
        进化 4：串关策略 - 最后一关绝对防冷/对冲锁定 (Arbitrage Lock)
        """
        hedge_bets = {}
        total_hedge_cost = 0.0
        
        for outcome, odds in hedge_odds.items():
            if odds <= 0:
                continue
            bet_amount = potential_payout / odds
            hedge_bets[outcome] = round(bet_amount, 2)
            total_hedge_cost += bet_amount
            
        guaranteed_profit = potential_payout - original_bet - total_hedge_cost
        
        return {
            "hedge_bets": hedge_bets,
            "total_hedge_cost": round(total_hedge_cost, 2),
            "guaranteed_profit": round(guaranteed_profit, 2),
            "is_arbitrage_possible": guaranteed_profit > 0
        }
