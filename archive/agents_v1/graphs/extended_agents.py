from typing import Dict, Any
from .state import AgentState
import time
import random


def in_play_analyzer_node(state: AgentState) -> Dict:
    """
    滚球分析Agent节点
    
    实时比赛分析（Live Betting）
    """
    print("   -> 🔴 [In-Play] 滚球分析节点运行中...")
    
    match_status = state.get("match_status", "not_started")
    minute = state.get("current_minute", 0)
    current_score = state.get("current_score", {"home": 0, "away": 0})
    
    # 模拟滚球分析
    momentum = calculate_momentum(current_score, minute)
    
    analysis = {
        "analysis_type": "in_play",
        "current_minute": minute,
        "score": current_score,
        "momentum": momentum,
        "recommended_bet": get_recommendation(current_score, minute),
        "confidence": random.uniform(0.55, 0.85),
        "timestamp": time.time()
    }
    
    print(f"   -> ✅ [In-Play] 滚球分析完成：第{minute}分钟 {current_score.get('home')}-{current_score.get('away')}")
    
    return {
        "in_play_analysis": analysis,
        "current_step": "in_play_done"
    }


def long_term_predictor_node(state: AgentState) -> Dict:
    """
    长期预测Agent节点
    
    联赛排名预测、冠军争夺等
    """
    print("   -> 📈 [Long-Term] 长期预测节点运行中...")
    
    # 模拟长期预测
    home_team = state.get("home_team")
    away_team = state.get("away_team")
    
    prediction = {
        "prediction_type": "long_term",
        "teams": [home_team, away_team],
        "league_standing_projection": {
            home_team: random.randint(1, 6),
            away_team: random.randint(1, 6)
        },
        "title_chance": {
            home_team: round(random.uniform(0.05, 0.35), 2),
            away_team: round(random.uniform(0.05, 0.35), 2)
        },
        "relegation_risk": {
            home_team: round(random.uniform(0, 0.25), 2),
            away_team: round(random.uniform(0, 0.25), 2)
        },
        "timestamp": time.time()
    }
    
    print(f"   -> ✅ [Long-Term] 长期预测完成：{home_team} 和 {away_team}")
    
    return {
        "long_term_prediction": prediction,
        "current_step": "long_term_done"
    }


def calculate_momentum(score: Dict, minute: int) -> str:
    """计算场上动量"""
    home_goals = score.get("home", 0)
    away_goals = score.get("away", 0)
    
    if home_goals > away_goals:
        return "home_advantage"
    elif away_goals > home_goals:
        return "away_advantage"
    else:
        return "balanced"


def get_recommendation(score: Dict, minute: int) -> Dict:
    """获取滚球推荐"""
    home = score.get("home", 0)
    away = score.get("away", 0)
    goal_diff = abs(home - away)
    
    if minute < 30 and goal_diff == 0:
        return {"type": "over_2_5", "confidence": "medium"}
    elif minute > 75 and goal_diff == 1:
        return {"type": "next_goal", "confidence": "high"}
    else:
        return {"type": "wait", "confidence": "low"}
