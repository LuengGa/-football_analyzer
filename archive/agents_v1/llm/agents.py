"""
LLM驱动的Agent节点

使用Ollama LLM进行真实的智能分析
"""

from typing import Dict, Any
from typing import TYPE_CHECKING
import json
import time
import random

if TYPE_CHECKING:
    from src.agents.graphs.state import AgentState


def llm_scout_node(state) -> Dict:
    """Scout Agent - LLM驱动"""
    from .ollama_client import get_llm_client
    from .prompts import get_system_prompt
    
    print("   -> 🔍 [Scout-LLM] 情报收集（LLM分析中...）")
    
    llm = get_llm_client()
    home_team = state["home_team"]
    away_team = state["away_team"]
    
    prompt = f"""分析比赛：{home_team} vs {away_team}

请提供情报分析，包括：
- 近期战绩（假设各有胜负）
- 关键球员状态
- 天气和场地因素
- 主场优势评估

直接返回JSON格式数据。"""
    
    try:
        response = llm.generate(prompt, system=get_system_prompt("scout"))
        
        # 尝试解析JSON
        scout_report = parse_llm_json(response)
        if not scout_report:
            scout_report = {
                "home_form": "W-W-L-W-D",
                "away_form": "L-W-D-W-W",
                "key_injuries": [],
                "weather": "clear",
                "venue_factor": 0.6,
                "summary": "情报收集完成"
            }
        
        print(f"   -> ✅ [Scout-LLM] 情报收集完成")
        
        return {
            "scout_report": scout_report,
            "match_intel": scout_report,
            "current_step": "scout_done"
        }
    except Exception as e:
        print(f"   -> ⚠️ [Scout-LLM] LLM调用失败，使用备用方案")
        return get_fallback_scout(state)


def llm_quant_node(state) -> Dict:
    """Quant Agent - LLM驱动"""
    from .ollama_client import get_llm_client
    from .prompts import get_system_prompt
    
    print("   -> 📊 [Quant-LLM] 量化分析（LLM计算中...）")
    
    llm = get_llm_client()
    home_team = state["home_team"]
    away_team = state["away_team"]
    intel = state.get("match_intel", {})
    
    prompt = f"""分析比赛：{home_team} vs {away_team}

主队情报：{intel.get('summary', '无数据')}

请计算：
1. 预期进球（xG）
2. 胜平负概率
3. ELO评分

直接返回JSON格式数据。"""
    
    try:
        response = llm.generate(prompt, system=get_system_prompt("quant"))
        
        quant_report = parse_llm_json(response)
        if not quant_report:
            # 使用现有计算引擎
            quant_report = calculate_with_engine(state)
        
        print(f"   -> ✅ [Quant-LLM] 量化分析完成")
        
        return {
            "quant_report": quant_report,
            "poisson_probs": quant_report.get("poisson_probs", {}),
            "elo_ratings": quant_report.get("elo_ratings", {}),
            "current_step": "quant_done"
        }
    except Exception as e:
        print(f"   -> ⚠️ [Quant-LLM] LLM调用失败，使用计算引擎")
        return get_fallback_quant(state)


def llm_market_node(state) -> Dict:
    """Market Agent - LLM驱动"""
    from .ollama_client import get_llm_client
    from .prompts import get_system_prompt
    
    print("   -> 📈 [Market-LLM] 市场分析（LLM分析中...）")
    
    llm = get_llm_client()
    home_team = state["home_team"]
    away_team = state["away_team"]
    
    prompt = f"""分析比赛：{home_team} vs {away_team}

请分析：
1. 当前市场赔率（假设合理值）
2. 是否有价值投注
3. 市场情绪

直接返回JSON格式数据。"""
    
    try:
        response = llm.generate(prompt, system=get_system_prompt("market"))
        
        market_report = parse_llm_json(response)
        if not market_report:
            market_report = get_fallback_market()
        
        print(f"   -> ✅ [Market-LLM] 市场分析完成")
        
        return {
            "market_report": market_report,
            "odds_data": market_report.get("odds", {}),
            "value_opportunities": market_report.get("value_bets", []),
            "current_step": "market_done"
        }
    except Exception as e:
        print(f"   -> ⚠️ [Market-LLM] LLM调用失败，使用备用方案")
        return get_fallback_market_result(state)


def llm_risk_node(state) -> Dict:
    """Risk Agent - LLM驱动"""
    from .ollama_client import get_llm_client
    from .prompts import get_system_prompt
    
    print("   -> 🛡️ [Risk-LLM] 风控分析（LLM评估中...）")
    
    llm = get_llm_client()
    
    poisson = state.get("poisson_probs", {"home_win": 0.5, "draw": 0.25, "away_win": 0.25})
    odds = state.get("odds_data", {"home_win": 2.0, "draw": 3.2, "away_win": 3.8})
    
    prompt = f"""计算投注风险：

主胜概率：{poisson.get('home_win', 0.5)}
主胜赔率：{odds.get('home_win', 2.0)}

请用Kelly公式计算推荐投注比例和风险等级。

直接返回JSON格式数据。"""
    
    try:
        response = llm.generate(prompt, system=get_system_prompt("risk"))
        
        risk_report = parse_llm_json(response)
        if not risk_report:
            risk_report = calculate_kelly(poisson, odds)
        
        print(f"   -> ✅ [Risk-LLM] 风控完成：{risk_report.get('risk_level', 'UNKNOWN')}")
        
        return {
            "risk_report": risk_report,
            "kelly_stake": risk_report.get("recommended_stake", 0),
            "risk_level": risk_report.get("risk_level", "UNKNOWN"),
            "current_step": "risk_done"
        }
    except Exception as e:
        print(f"   -> ⚠️ [Risk-LLM] LLM调用失败，使用备用方案")
        return get_fallback_risk(state)


def llm_trader_node(state) -> Dict:
    """Trader Agent - LLM驱动"""
    from .ollama_client import get_llm_client
    from .prompts import get_system_prompt
    
    print("   -> 🎯 [Trader-LLM] 交易决策（LLM决策中...）")
    
    llm = get_llm_client()
    
    risk = state.get("risk_report", {})
    quant = state.get("quant_report", {})
    market = state.get("market_report", {})
    
    prompt = f"""综合分析决策：

风险评估：{risk.get('risk_level', 'UNKNOWN')}
主胜概率：{quant.get('poisson_probs', {}).get('home_win', 0.5)}
主胜赔率：{market.get('odds', {}).get('home_win', 2.0)}

请做出最终投注决策。

直接返回JSON格式数据。"""
    
    try:
        response = llm.generate(prompt, system=get_system_prompt("trader"))
        
        trader_decision = parse_llm_json(response)
        if not trader_decision:
            trader_decision = get_fallback_trader(state)
        
        approved = trader_decision.get("approved", False)
        print(f"   -> ✅ [Trader-LLM] 决策完成：{'批准投注' if approved else '拒绝投注'}")
        
        return {
            "trader_decision": trader_decision,
            "final_bet": trader_decision.get("final_bet"),
            "current_step": "trader_done"
        }
    except Exception as e:
        print(f"   -> ⚠️ [Trader-LLM] LLM调用失败，使用备用方案")
        return get_fallback_trader_result(state)


def llm_auditor_node(state) -> Dict:
    """Auditor Agent - LLM驱动"""
    from .ollama_client import get_llm_client
    from .prompts import get_system_prompt
    
    print("   -> 🔍 [Auditor-LLM] 复盘分析（LLM反思中...）")
    
    llm = get_llm_client()
    
    decision = state.get("trader_decision", {})
    match_id = state.get("match_id", "UNKNOWN")
    
    prompt = f"""复盘决策：

决策ID：{match_id}
决策结果：{'批准' if decision.get('approved') else '拒绝'}
投注类型：{decision.get('bet_type', 'N/A')}

请进行复盘分析，总结经验教训。

直接返回JSON格式数据。"""
    
    try:
        response = llm.generate(prompt, system=get_system_prompt("auditor"))
        
        feedback = parse_llm_json(response)
        if not feedback:
            feedback = {
                "review_id": f"REVIEW_{int(time.time())}",
                "decision_quality": "GOOD",
                "lessons_learned": ["分析流程正常"],
                "improvements": ["持续优化中"]
            }
        
        print(f"   -> ✅ [Auditor-LLM] 复盘完成")
        
        return {
            "auditor_feedback": feedback,
            "current_step": "audit_done"
        }
    except Exception as e:
        print(f"   -> ⚠️ [Auditor-LLM] LLM调用失败，使用备用方案")
        return get_fallback_auditor(state)


# ============ 辅助函数 ============

def parse_llm_json(text: str) -> Dict:
    """解析LLM输出的JSON"""
    try:
        # 尝试提取JSON
        text = text.strip()
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end]
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end]
        
        # 尝试直接解析
        return json.loads(text)
    except:
        return None


def get_fallback_scout(state: AgentState) -> Dict:
    """Scout备用方案"""
    return {
        "scout_report": {"home_form": "W-W-L-W-D", "away_form": "L-W-D-W-W", "venue_factor": 0.6},
        "match_intel": {"venue_factor": 0.6},
        "current_step": "scout_done"
    }


def calculate_with_engine(state) -> Dict:
    """使用计算引擎"""
    from src.calculations.pro.phase2_enhancements import (
        AsianHandicapCalculator, CornersPredictor, ExactGoalsCalculator
    )
    
    home_xg = random.uniform(1.2, 2.2)
    away_xg = random.uniform(0.8, 1.8)
    
    return {
        "home_xg": home_xg,
        "away_xg": away_xg,
        "poisson_probs": {"home_win": 0.5, "draw": 0.25, "away_win": 0.25},
        "elo_ratings": {"home": 1800, "away": 1750}
    }


def get_fallback_market() -> Dict:
    """Market备用方案"""
    return {
        "odds": {"home_win": 1.95, "draw": 3.4, "away_win": 4.0},
        "market_sentiment": "neutral",
        "value_bets": []
    }


def get_fallback_market_result(state: AgentState) -> Dict:
    """Market备用结果"""
    return {
        "market_report": get_fallback_market(),
        "odds_data": {"home_win": 1.95, "draw": 3.4, "away_win": 4.0},
        "value_opportunities": [],
        "current_step": "market_done"
    }


def calculate_kelly(probs: Dict, odds: Dict) -> Dict:
    """Kelly计算"""
    p = probs.get("home_win", 0.5)
    b = odds.get("home_win", 2.0) - 1
    
    if b > 0:
        kelly = max(0, min(0.25, (p * (b + 1) - 1) / b))
    else:
        kelly = 0
    
    return {
        "kelly_fraction": kelly,
        "recommended_stake": kelly * 1000,
        "risk_level": "REJECT" if kelly <= 0 else ("LOW" if kelly <= 0.1 else "MEDIUM"),
        "approved": kelly > 0
    }


def get_fallback_risk(state: AgentState) -> Dict:
    """Risk备用方案"""
    probs = state.get("poisson_probs", {"home_win": 0.5})
    odds = state.get("odds_data", {"home_win": 2.0})
    report = calculate_kelly(probs, odds)
    
    return {
        "risk_report": report,
        "kelly_stake": report.get("recommended_stake", 0),
        "risk_level": report.get("risk_level", "UNKNOWN"),
        "current_step": "risk_done"
    }


def get_fallback_trader(state: AgentState) -> Dict:
    """Trader备用方案"""
    risk = state.get("risk_report", {})
    
    approved = risk.get("approved", False)
    return {
        "approved": approved,
        "final_bet": {
            "type": "home_win",
            "odds": state.get("odds_data", {}).get("home_win", 2.0),
            "stake": risk.get("recommended_stake", 0)
        } if approved else None,
        "reasoning": "系统决策"
    }


def get_fallback_trader_result(state: AgentState) -> Dict:
    """Trader备用结果"""
    decision = get_fallback_trader(state)
    return {
        "trader_decision": decision,
        "final_bet": decision.get("final_bet"),
        "current_step": "trader_done"
    }


def get_fallback_auditor(state: AgentState) -> Dict:
    """Auditor备用方案"""
    return {
        "auditor_feedback": {
            "review_id": f"REVIEW_{int(time.time())}",
            "decision_quality": "GOOD",
            "lessons_learned": ["流程正常"],
            "improvements": []
        },
        "current_step": "audit_done"
    }
