"""AFA MCP Server — 将足球分析核心暴露为 MCP 工具"""
import sys, os, math, statistics
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("afa-football-analyzer", port=18900)


# ─── Elo 评分系统 ───
@mcp.tool()
def elo_calculate(home_elo: float, away_elo: float, home_goals: int = None,
                  away_goals: int = None, k_factor: int = 20) -> dict:
    """计算 ELO 评分更新
    
    Args:
        home_elo: 主队当前 Elo
        away_elo: 客队当前 Elo
        home_goals: 主队进球（可选，用于赛后更新）
        away_goals: 客队进球（可选，用于赛后更新）
        k_factor: K 因子，控制 Elo 变动幅度
    
    Returns:
        包含预期胜率和新 Elo 的字典
    """
    # 预期胜率计算
    expected_home = 1.0 / (1.0 + 10.0 ** ((away_elo - home_elo - 65.0) / 400.0))
    expected_away = 1.0 - expected_home
    
    result = {
        "expected_home_win_prob": round(expected_home, 4),
        "expected_away_win_prob": round(expected_away, 4),
        "expected_draw_prob": round(1 - expected_home - expected_away, 4)
    }
    
    # 如果有比赛结果，更新 Elo
    if home_goals is not None and away_goals is not None:
        if home_goals > away_goals:
            actual_home, actual_away = 1.0, 0.0
        elif home_goals == away_goals:
            actual_home, actual_away = 0.5, 0.5
        else:
            actual_home, actual_away = 0.0, 1.0
        
        new_home = home_elo + k_factor * (actual_home - expected_home)
        new_away = away_elo + k_factor * (actual_away - expected_away)
        
        result.update({
            "new_home_elo": round(new_home, 1),
            "new_away_elo": round(new_away, 1),
            "elo_change_home": round(new_home - home_elo, 1),
            "elo_change_away": round(new_away - away_elo, 1)
        })
    
    return result


# ─── Dixon-Coles 泊松计算（简化版）───
@mcp.tool()
def dixon_coles_predict(home_attack: float, home_defense: float,
                         away_attack: float, away_defense: float,
                         home_advantage: float = 0.3) -> dict:
    """Dixon-Coles 泊松比分预测
    
    Args:
        home_attack: 主队攻击强度
        home_defense: 主队防守强度
        away_attack: 客队攻击强度
        away_defense: 客队防守强度
        home_advantage: 主场优势
    
    Returns:
        包含预期进球和胜负概率的字典
    """
    lam_h = math.exp(home_attack + away_defense + home_advantage)
    lam_a = math.exp(away_attack + home_defense)
    
    max_goals = 8
    home_win = draw = away_win = 0.0
    
    # 简单泊松概率计算
    for h in range(max_goals + 1):
        prob_h = (lam_h ** h) * math.exp(-lam_h) / math.factorial(h)
        for a in range(max_goals + 1):
            prob_a = (lam_a ** a) * math.exp(-lam_a) / math.factorial(a)
            prob = prob_h * prob_a
            
            if h > a:
                home_win += prob
            elif h == a:
                draw += prob
            else:
                away_win += prob
    
    return {
        "expected_home_goals": round(lam_h, 3),
        "expected_away_goals": round(lam_a, 3),
        "home_win_prob": round(home_win, 4),
        "draw_prob": round(draw, 4),
        "away_win_prob": round(away_win, 4)
    }


# ─── Kelly 准则投注分析 ───
@mcp.tool()
def kelly_analyze(true_probability: float, odds: float, bankroll: float = 10000) -> dict:
    """Kelly 公式投注分析
    
    Args:
        true_probability: 你认为的真实胜率 (0-1)
        odds: 博彩公司赔率（十进制，如 1.85）
        bankroll: 当前本金
    
    Returns:
        包含建议投注比例和金额的字典
    """
    if odds <= 1.0:
        return {"error": "赔率必须大于 1.0"}
    
    implied_prob = 1.0 / odds
    edge = true_probability - implied_prob
    
    # 全 Kelly
    if edge > 0 and odds > 1:
        kelly_fraction = (true_probability * odds - 1) / (odds - 1)
    else:
        kelly_fraction = 0.0
    
    # 保守版本（1/4 Kelly）
    quarter_kelly = kelly_fraction * 0.25
    
    return {
        "implied_probability": round(implied_prob, 4),
        "true_probability": round(true_probability, 4),
        "edge": round(edge, 4),
        "has_positive_edge": edge > 0,
        "kelly_fraction": round(kelly_fraction, 6),
        "kelly_bet_amount": round(kelly_fraction * bankroll, 2),
        "quarter_kelly_amount": round(quarter_kelly * bankroll, 2),
        "suggested_stake_pct": round(quarter_kelly * 100, 2)
    }


# ─── 赔率隐含概率 ───
@mcp.tool()
def odds_implied_probabilities(odds_home: float, odds_draw: float, odds_away: float) -> dict:
    """从赔率计算隐含概率（包含抽水）
    
    Args:
        odds_home: 主胜赔率
        odds_draw: 平局赔率
        odds_away: 客胜赔率
    
    Returns:
        包含各结果隐含概率和抽水的字典
    """
    inv_home = 1.0 / odds_home
    inv_draw = 1.0 / odds_draw
    inv_away = 1.0 / odds_away
    
    total = inv_home + inv_draw + inv_away
    vig = total - 1.0
    
    return {
        "implied_home": round(inv_home / total, 4),
        "implied_draw": round(inv_draw / total, 4),
        "implied_away": round(inv_away / total, 4),
        "market_margin": round(vig, 4),
        "fair_odds_home": round(1.0 / (inv_home / total), 2),
        "fair_odds_draw": round(1.0 / (inv_draw / total), 2),
        "fair_odds_away": round(1.0 / (inv_away / total), 2)
    }


# ─── 综合分析 ───
@mcp.tool()
def comprehensive_match_analysis(
    home_team: str,
    away_team: str,
    home_elo: float,
    away_elo: float,
    odds_home: float,
    odds_draw: float,
    odds_away: float,
    home_attack: float = 0.0,
    away_attack: float = 0.0,
    home_defense: float = 0.0,
    away_defense: float = 0.0
) -> dict:
    """综合比赛分析：ELO + 赔率 + 价值判断
    
    Args:
        home_team: 主队名称
        away_team: 客队名称
        home_elo: 主队 Elo
        away_elo: 客队 Elo
        odds_home: 主胜赔率
        odds_draw: 平局赔率
        odds_away: 客胜赔率
        home_attack: 主队攻击强度（可选）
        away_attack: 客队攻击强度（可选）
        home_defense: 主队防守强度（可选）
        away_defense: 客队防守强度（可选）
    
    Returns:
        完整的综合分析报告
    """
    result = {
        "match": {
            "home_team": home_team,
            "away_team": away_team
        }
    }
    
    # 1. ELO 概率
    elo_result = elo_calculate(home_elo, away_elo)
    result["elo"] = elo_result
    
    # 2. 市场隐含概率
    odds_result = odds_implied_probabilities(odds_home, odds_draw, odds_away)
    result["market"] = odds_result
    
    # 3. Dixon-Coles（如果有参数）
    if all(v != 0.0 for v in [home_attack, away_attack, home_defense, away_defense]):
        dc_result = dixon_coles_predict(home_attack, home_defense, away_attack, away_defense)
        result["dixon_coles"] = dc_result
    
    # 4. 集成预测（平均多个模型）
    home_probs = [elo_result["expected_home_win_prob"], odds_result["implied_home"]]
    away_probs = [elo_result["expected_away_win_prob"], odds_result["implied_away"]]
    
    if "dixon_coles" in result:
        home_probs.append(result["dixon_coles"]["home_win_prob"])
        away_probs.append(result["dixon_coles"]["away_win_prob"])
    
    avg_home = sum(home_probs) / len(home_probs)
    avg_away = sum(away_probs) / len(away_probs)
    avg_draw = 1 - avg_home - avg_away
    
    result["ensemble"] = {
        "avg_home_win_prob": round(avg_home, 4),
        "avg_draw_prob": round(avg_draw, 4),
        "avg_away_win_prob": round(avg_away, 4)
    }
    
    # 5. 价值判断（找价值投注）
    result["value_bets"] = []
    
    # 主胜价值
    home_value = avg_home * odds_home - 1
    if home_value > 0:
        result["value_bets"].append({
            "selection": f"{home_team} 胜",
            "value": round(home_value, 4),
            "ev": round(home_value * 100, 2),
            "recommendation": "考虑"
        })
    
    # 客胜价值
    away_value = avg_away * odds_away - 1
    if away_value > 0:
        result["value_bets"].append({
            "selection": f"{away_team} 胜",
            "value": round(away_value, 4),
            "ev": round(away_value * 100, 2),
            "recommendation": "考虑"
        })
    
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")