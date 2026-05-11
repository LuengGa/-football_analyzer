from typing import Dict, Any, List, Optional
from .state import AgentState
from .persistence import MemoryPersistence
import time
import json
from datetime import datetime


# 全局持久化对象
_persistence = None


def get_persistence() -> MemoryPersistence:
    """获取持久化对象（单例模式）"""
    global _persistence
    if _persistence is None:
        _persistence = MemoryPersistence()
    return _persistence


def auditor_node(state: AgentState) -> Dict:
    """
    Auditor Agent Node - 复盘节点（事后使用）
    
    回顾决策并生成改进建议
    """
    print("   -> 🔍 [Auditor] 复盘分析节点运行中...")
    
    # 获取决策信息
    trader_decision = state.get("trader_decision", {})
    approved = trader_decision.get("approved", False)
    final_bet = trader_decision.get("final_bet")
    
    # 模拟复盘（实际应该和比赛结果对比）
    feedback = {
        "review_id": f"REVIEW_{int(time.time())}",
        "match_id": state.get("match_id"),
        "decision_approved": approved,
        "final_bet": final_bet,
        "review_timestamp": datetime.now().isoformat(),
        "lessons_learned": [
            "Kelly准则计算正确",
            "风险评估合理",
            "建议更多关注球队伤病情况"
        ],
        "improvements": [
            "增强情报收集深度",
            "优化泊松分布参数",
            "增加市场情绪权重"
        ]
    }
    
    print("   -> ✅ [Auditor] 复盘分析完成")
    return {
        "auditor_feedback": feedback,
        "current_step": "audit_done"
    }


def save_to_memory(state: AgentState) -> Dict:
    """
    保存决策到记忆系统（内存+文件）
    """
    print("   -> 💾 [Memory] 保存决策到历史记录...")
    
    # 创建历史记录
    history_entry = {
        "decision_id": f"DECISION_{state.get('match_id')}_{int(time.time())}",
        "match_id": state.get("match_id"),
        "home_team": state.get("home_team"),
        "away_team": state.get("away_team"),
        "trader_decision": state.get("trader_decision"),
        "auditor_feedback": state.get("auditor_feedback"),
        "timestamp": datetime.now().isoformat()
    }
    
    # 更新历史记录列表（内存）
    history = state.get("historical_decisions", [])
    history.append(history_entry)
    
    # 持久化到文件
    persistence = get_persistence()
    persistence.save_decision(history_entry)
    
    print(f"   -> ✅ [Memory] 已保存决策到历史（共{len(history)}条）")
    return {
        "historical_decisions": history,
        "current_step": "memory_saved"
    }


def inject_memory_to_state(state: AgentState) -> Dict:
    """
    把历史经验注入到当前状态
    
    类似TradingAgents的Memory Injection模式
    同时从内存和文件加载历史
    """
    print("   -> 🧠 [Memory] 注入历史经验...")
    
    # 首先从持久化系统加载
    persistence = get_persistence()
    saved_history = persistence.load_recent_decisions(limit=5)
    
    # 合并内存和文件的历史
    memory_history = state.get("historical_decisions", [])
    all_history = memory_history + saved_history
    
    # 去重
    seen_ids = set()
    unique_history = []
    for entry in reversed(all_history):
        entry_id = entry.get("decision_id")
        if entry_id and entry_id not in seen_ids:
            seen_ids.add(entry_id)
            unique_history.append(entry)
    
    history = list(reversed(unique_history))[-5:]
    
    if not history:
        # 没有历史经验
        memory_summary = "无历史决策记录，这是第一次分析"
    else:
        # 简单总结最近几次决策
        recent = history[-3:]
        approved_count = sum(1 for h in recent if h.get("trader_decision", {}).get("approved", False))
        
        memory_summary = f"历史经验（最近{len(recent)}次）："
        memory_summary += f"批准投注{approved_count}次，拒绝{len(recent)-approved_count}次"
        
        # 收集改进建议
        all_improvements = []
        for h in recent:
            feedback = h.get("auditor_feedback", {})
            all_improvements.extend(feedback.get("improvements", []))
        
        if all_improvements:
            memory_summary += f" | 改进方向：{', '.join(set(all_improvements))}"
    
    # 更新memory_log
    memory_log = state.get("memory_log", [])
    memory_log.append({
        "step": "pre_match",
        "summary": memory_summary,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"   -> ✅ [Memory] 已注入历史经验（从内存+文件）")
    return {
        "historical_decisions": history,
        "memory_log": memory_log
    }
