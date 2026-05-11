from typing import Dict, Any
from .state import AgentState
import time
import random


def scout_node(state: AgentState) -> Dict:
    """
    Scout Agent Node - 情报收集节点
    
    遵循TradingAgents最佳实践：
    - 输入：基础比赛信息
    - 输出：scout_report
    """
    print("   -> 🔍 [Scout] 情报收集节点运行中...")
    
    # 模拟情报收集（实际会调用sportsipy等工具）
    home_team = state["home_team"]
    away_team = state["away_team"]
    
    scout_report = {
        "home_team": home_team,
        "away_team": away_team,
        "home_form": "W-W-W-L-W",
        "away_form": "L-W-W-D-W",
        "injuries": ["Home Player A"],
        "weather": "clear",
        "venue": "Home Stadium",
        "timestamp": time.time()
    }
    
    print(f"   -> ✅ [Scout] 情报收集完成：{home_team} vs {away_team}")
    
    # 只返回修改的key，避免并行冲突
    return {
        "scout_report": scout_report,
        "match_intel": scout_report,
        "current_step": "scout_done"
    }


def quant_node(state: AgentState) -> Dict:
    """
    Quant Agent Node - 量化分析节点
    
    调用我们现有的数学计算模块！
    """
    print("   -> 📊 [Quant] 量化分析节点运行中...")
    
    from src.calculations.pro.phase2_enhancements import (
        AsianHandicapCalculator,
        CornersPredictor,
        ExactGoalsCalculator
    )
    
    # 模拟预期进球
    home_xg = 1.8
    away_xg = 1.2
    
    # 计算泊松概率
    ah_calc = AsianHandicapCalculator()
    ah_results = ah_calc.calculate_handicap(home_xg, away_xg, 0.0)
    
    # 计算角球
    corner_pred = CornersPredictor()
    corners = corner_pred.predict_from_goals(home_xg, away_xg)
    
    # 计算精确进球
    goals_calc = ExactGoalsCalculator()
    goal_probs = goals_calc.calculate(home_xg, away_xg)
    
    quant_report = {
        "home_xg": home_xg,
        "away_xg": away_xg,
        "asian_handicap": ah_results,
        "corners": corners,
        "exact_goals": goal_probs,
        "poisson_probs": {
            "home_win": 0.514,
            "draw": 0.231,
            "away_win": 0.255
        },
        "elo_ratings": {
            "home": 1850.0,
            "away": 1780.0
        }
    }
    
    print("   -> ✅ [Quant] 量化分析完成")
    
    # 只返回修改的key，避免并行冲突
    return {
        "quant_report": quant_report,
        "poisson_probs": quant_report["poisson_probs"],
        "elo_ratings": quant_report["elo_ratings"],
        "current_step": "quant_done"
    }


def market_node(state: AgentState) -> Dict:
    """
    Market Agent Node - 市场分析节点
    
    分析赔率、市场情绪
    """
    print("   -> 📈 [Market] 市场分析节点运行中...")
    
    market_report = {
        "odds": {
            "home_win": 1.85,
            "draw": 3.40,
            "away_win": 4.20,
            "over_2_5": 1.80,
            "under_2_5": 1.95
        },
        "market_sentiment": "neutral",
        "smart_money_movement": "inactive",
        "value_opportunities": [
            {
                "type": "home_win",
                "fair_odds": 1.95,
                "market_odds": 1.85,
                "value": -0.05
            }
        ]
    }
    
    print("   -> ✅ [Market] 市场分析完成")
    
    # 只返回修改的key，避免并行冲突
    return {
        "market_report": market_report,
        "odds_data": market_report["odds"],
        "value_opportunities": market_report["value_opportunities"],
        "current_step": "market_done"
    }


def risk_node(state: AgentState) -> Dict:
    """
    Risk Agent Node - 风控节点
    
    计算Kelly准则、风险评估
    """
    print("   -> 🛡️ [Risk] 风控节点运行中...")
    
    # 从quant_report获取概率
    poisson_probs = state.get("poisson_probs", {
        "home_win": 0.514,
        "draw": 0.231,
        "away_win": 0.255
    })
    
    # 从market_report获取赔率
    odds_data = state.get("odds_data", {
        "home_win": 1.85,
        "draw": 3.40,
        "away_win": 4.20
    })
    
    # 计算Kelly比例（简化版）
    p = poisson_probs["home_win"]
    b = odds_data["home_win"] - 1
    
    # Kelly formula: f* = (p*(b+1) - 1) / b
    if b > 0:
        kelly_fraction = (p * (b + 1) - 1) / b
    else:
        kelly_fraction = 0.0
    
    # 限制范围
    kelly_fraction = max(0, min(0.25, kelly_fraction))
    
    # 风险评级
    if kelly_fraction <= 0:
        risk_level = "REJECT"
    elif kelly_fraction <= 0.10:
        risk_level = "LOW"
    elif kelly_fraction <= 0.20:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    risk_report = {
        "kelly_fraction": kelly_fraction,
        "risk_level": risk_level,
        "recommended_stake": kelly_fraction * 1000,  # 假设总资金1000
        "risk_factors": ["market_volatility", "team_injuries"],
        "approved": kelly_fraction > 0
    }
    
    print(f"   -> ✅ [Risk] 风控完成：风险等级 {risk_level}")
    
    # 只返回修改的key
    return {
        "risk_report": risk_report,
        "kelly_stake": risk_report["recommended_stake"],
        "risk_level": risk_level,
        "current_step": "risk_done"
    }


def trader_node(state: AgentState) -> Dict:
    """
    Trader Agent Node - 交易决策节点
    
    综合所有信息，做出最终决策
    """
    print("   -> 🎯 [Trader] 交易决策节点运行中...")
    
    risk_report = state.get("risk_report", {})
    quant_report = state.get("quant_report", {})
    market_report = state.get("market_report", {})
    
    # 最终决策
    approved = risk_report.get("approved", False)
    stake = risk_report.get("recommended_stake", 0)
    
    if approved and stake > 0:
        final_bet = {
            "match_id": state["match_id"],
            "type": "home_win",
            "odds": market_report.get("odds", {}).get("home_win", 0),
            "stake": stake,
            "confidence": quant_report.get("poisson_probs", {}).get("home_win", 0),
            "timestamp": time.time()
        }
    else:
        final_bet = None
    
    trader_decision = {
        "approved": approved,
        "final_bet": final_bet,
        "reasoning": "综合情报、量化、市场、风控后做出决策"
    }
    
    print(f"   -> ✅ [Trader] 决策完成：{'批准投注' if approved else '拒绝投注'}")
    
    # 只返回修改的key
    return {
        "trader_decision": trader_decision,
        "final_bet": final_bet,
        "current_step": "trader_done"
    }
