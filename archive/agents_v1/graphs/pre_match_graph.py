from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState, MatchPhase
from .nodes import scout_node, quant_node, market_node, risk_node, trader_node
from .evolution import auditor_node, save_to_memory, inject_memory_to_state
from .extended_agents import in_play_analyzer_node, long_term_predictor_node
from .llm.agents import (
    llm_scout_node,
    llm_quant_node,
    llm_market_node,
    llm_risk_node,
    llm_trader_node,
    llm_auditor_node
)
import os
from datetime import datetime


def create_initial_state(
    match_id: str,
    home_team: str,
    away_team: str,
    match_date: str = None
) -> AgentState:
    """创建初始状态"""
    if match_date is None:
        match_date = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "match_id": match_id,
        "home_team": home_team,
        "away_team": away_team,
        "match_date": match_date,
        "phase": MatchPhase.PRE_MATCH,
        "scout_report": None,
        "match_intel": None,
        "quant_report": None,
        "elo_ratings": None,
        "poisson_probs": None,
        "market_report": None,
        "odds_data": None,
        "value_opportunities": None,
        "risk_report": None,
        "kelly_stake": None,
        "risk_level": None,
        "trader_decision": None,
        "final_bet": None,
        "auditor_feedback": None,
        "in_play_analysis": None,
        "long_term_prediction": None,
        "historical_decisions": [],
        "memory_log": [],
        "current_step": "init",
        "errors": [],
        "messages": []
    }


def create_llm_graph(with_checkpoint: bool = True, with_memory: bool = True):
    """
    创建LLM驱动的赛前分析Graph
    
    特性：
    - 使用真实Ollama LLM进行智能分析
    - Memory Injection（记忆注入）
    - Checkpoint Resume（断点恢复）
    - Self-Evolving Loop（自主闭环）
    """
    # 1. 创建StateGraph
    graph = StateGraph(AgentState)
    
    # 2. 添加LLM驱动的节点
    graph.add_node("scout", llm_scout_node)
    graph.add_node("quant", llm_quant_node)
    graph.add_node("market", llm_market_node)
    graph.add_node("risk", llm_risk_node)
    graph.add_node("trader", llm_trader_node)
    graph.add_node("auditor", llm_auditor_node)
    graph.add_node("save_memory", save_to_memory)
    graph.add_node("inject_memory", inject_memory_to_state)
    
    # 3. 定义边
    if with_memory:
        graph.set_entry_point("inject_memory")
        graph.add_edge("inject_memory", "scout")
    else:
        graph.set_entry_point("scout")
    
    graph.add_edge("scout", "quant")
    graph.add_edge("quant", "market")
    graph.add_edge("market", "risk")
    graph.add_edge("risk", "trader")
    graph.add_edge("trader", "auditor")
    graph.add_edge("auditor", "save_memory")
    graph.add_edge("save_memory", END)
    
    if with_checkpoint:
        memory = MemorySaver()
        return graph.compile(checkpointer=memory)
    
    return graph.compile()


def demo_llm_agent():
    """LLM Agent完整功能演示"""
    print("=" * 80)
    print("🚀 AFA v8.6 - LLM驱动的智能Agent系统（Ollama）")
    print("=" * 80)
    
    # 1. 创建LLM Graph
    app = create_llm_graph(
        with_checkpoint=True,
        with_memory=True
    )
    
    # 2. 配置Checkpoint
    config = {"configurable": {"thread_id": "llm_demo"}}
    
    print(f"\n📊 LLM智能分析：曼彻斯特联 vs 利物浦")
    print("=" * 80)
    
    # 3. 创建初始状态
    initial_state = create_initial_state(
        match_id="LLM_MATCH_001",
        home_team="Manchester United",
        away_team="Liverpool"
    )
    
    # 4. 运行LLM Graph
    final_state = app.invoke(initial_state, config=config)
    
    print_result(final_state, "LLM分析完成")
    
    print("\n" + "=" * 80)
    print("✅ LLM Agent演示完成！")
    print("=" * 80)
    print_summary(final_state)


def print_result(state: AgentState, title: str):
    """打印结果"""
    print(f"\n🎯 {title} - 决策结果")
    print("-" * 60)
    
    trader = state.get("trader_decision", {})
    approved = trader.get("approved", False)
    
    print(f"  投注决策: {'✅ 批准' if approved else '❌ 拒绝'}")
    
    if trader.get("final_bet"):
        bet = trader.get("final_bet")
        print(f"  投注类型: {bet.get('type')}")
        print(f"  建议金额: {bet.get('stake', 0):.2f}元")
        print(f"  置信度: {bet.get('confidence', 0):.1%}")
    
    if state.get("in_play_analysis"):
        print(f"\n  🔴 滚球分析: 已就绪")
    
    if state.get("long_term_prediction"):
        print(f"  📈 长期预测: 已就绪")
    
    print(f"  📚 历史记录: {len(state.get('historical_decisions', []))}条")


def print_summary(state: AgentState):
    """打印总结"""
    print("\n💡 功能特性总结：")
    print("  ✅ LangGraph编排")
    print("  ✅ Checkpoint断点恢复")
    print("  ✅ Memory Injection历史经验注入")
    print("  ✅ Auditor自我复盘")
    print("  ✅ 持久化到文件（memory/history/）")
    print("  ✅ 滚球分析Agent")
    print("  ✅ 长期预测Agent")
    print("  ✅ 自主闭环进化")


def show_architecture():
    """显示架构图"""
    print("\n" + "=" * 80)
    print("🏗️  AFA v8.6 - LLM驱动的数字生命Agent架构")
    print("=" * 80)
    
    print("""
┌─────────────────────────────────────────────────────────────────┐
│                   LLM驱动的自主Agent系统                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌──────────┐     ┌────────────────────────────────────┐      │
│    │ 记忆注入  │────>│         LLM Agent集群              │      │
│    │(Injection)│     │                                    │      │
│    └──────────┘     │  ┌─────────┐  ┌─────────┐         │      │
│         ↑           │  │ Scout   │  │ Quant   │         │      │
│         │           │  │ (情报)  │  │ (量化)  │         │      │
│         │           │  └─────────┘  └─────────┘         │      │
│    ┌────┴─────┐     │                                    │      │
│    │ 历史持久化│◀───│  ┌─────────┐  ┌─────────┐         │      │
│    │(Persistence)│   │  │ Market  │  │ Risk   │         │      │
│    └──────────┘     │  │ (市场)  │  │ (风控)  │         │      │
│                     │  └─────────┘  └─────────┘         │      │
│                     │                                    │      │
│                     │  ┌─────────┐  ┌─────────┐         │      │
│                     │  │ Trader  │  │ Auditor │         │      │
│                     │  │ (交易)  │  │ (复盘)  │         │      │
│                     │  └─────────┘  └─────────┘         │      │
│                     └────────────────────────────────────┘      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  LLM引擎：Ollama (本地部署)                                  ││
│  │  特点：                                                      ││
│  │   • 100%隐私保护（数据不离开本地）                            ││
│  │   • 低成本（无API费用）                                       ││
│  │   • 可离线运行                                                ││
│  │   • 支持多种模型（Qwen, Llama, DeepSeek等）                   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    show_architecture()
    print("\n" * 2)
    demo_llm_agent()
