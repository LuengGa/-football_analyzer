#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AFA v9.0 新功能演示 - 多Agent协作 + 自适应学习
==================================================
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.afa_v9.agents import (
    COLLABORATION_MANAGER,
    ADAPTIVE_LEARNING,
)


def demo_collective_decision():
    """演示集体决策"""
    print("\n" + "="*80)
    print("🤝 集体决策演示")
    print("="*80)
    
    decision = COLLABORATION_MANAGER.collective_decision(
        topic="是否调整投注策略",
        options=["保守策略", "激进策略"],
        participants=["Quant", "Risk", "Trader", "Auditor"],
    )
    
    print(f"\n🎯 最终决策: {decision.final_decision}")
    print(f"🤝 共识达成: {'✅ 是' if decision.consensus_reached else '❌ 否'}")
    print(f"💡 推理: {decision.reasoning}")


def demo_task_allocation():
    """演示任务分配"""
    print("\n" + "="*80)
    print("📋 任务分配演示")
    print("="*80)
    
    tasks = [
        ("intelligence_gathering", "收集伤病情报", 8),
        ("quantitative_analysis", "量化模型分析", 7),
        ("market_analysis", "市场情绪分析", 6),
        ("risk_management", "风险评估", 9),
        ("general_decision", "综合策略决策", 10),
    ]
    
    for task_type, desc, priority in tasks:
        assignment = COLLABORATION_MANAGER.assign_task(
            task_type=task_type,
            task_description=desc,
            priority=priority,
        )
        print(f"📋 任务 {assignment.task_id}: {desc}")
        print(f"   → 分配给: {assignment.assigned_agent} (优先级: {priority})")


def demo_adaptive_learning():
    """演示自适应学习"""
    print("\n" + "="*80)
    print("🧠 自适应学习回路演示")
    print("="*80)
    
    # 重置学习（方便演示）
    ADAPTIVE_LEARNING.reset_learning()
    
    # 记录一些示例投注结果
    print("\n📝 记录投注结果...")
    
    # 模拟15次投注
    results = [
        ("曼联 vs 阿森纳", "E0", "home_win", 1.85, 100, "home_win", 85),
        ("切尔西 vs 热刺", "E0", "away_win", 2.10, 100, "home_win", -100),
        ("利物浦 vs 埃弗顿", "E0", "home_win", 1.65, 100, "home_win", 65),
        ("曼城 vs 纽卡斯尔", "E0", "home_win", 1.45, 100, "home_win", 45),
        ("热刺 vs 西汉姆", "E0", "home_win", 1.75, 100, "draw", -100),
        ("阿森纳 vs 切尔西", "E0", "away_win", 2.20, 100, "away_win", 120),
        ("利物浦 vs 曼城", "E0", "draw", 3.50, 100, "home_win", -100),
        ("纽卡斯尔 vs 曼联", "E0", "home_win", 2.30, 100, "home_win", 130),
        ("埃弗顿 vs 热刺", "E0", "away_win", 2.00, 100, "away_win", 100),
        ("西汉姆 vs 阿森纳", "E0", "away_win", 1.95, 100, "home_win", -100),
        ("莱斯特 vs 维拉", "E0", "home_win", 1.80, 100, "home_win", 80),
        ("南安普顿 vs 水晶宫", "E0", "home_win", 1.90, 100, "away_win", -100),
        ("布莱顿 vs 伯恩利", "E0", "home_win", 1.70, 100, "home_win", 70),
        ("狼队 vs 谢菲联", "E0", "home_win", 1.60, 100, "home_win", 60),
        ("富勒姆 vs 卢顿", "E0", "home_win", 1.75, 100, "draw", -100),
    ]
    
    for i, (match, league, bet_type, odds, stake, actual, profit) in enumerate(results, 1):
        home, away = match.split(' vs ')
        result = ADAPTIVE_LEARNING.record_bet_result(
            bet_id=f"bet_202501{i:02d}",
            match_id=f"match_202501{i:02d}",
            home_team=home,
            away_team=away,
            league=league,
            bet_type=bet_type,
            odds=odds,
            stake=stake,
            actual_result=actual,
            profit=profit,
        )
    
    # 获取学习报告
    print("\n" + "="*80)
    print("📊 自适应学习报告")
    print("="*80)
    
    report = ADAPTIVE_LEARNING.get_learning_report()
    
    overview = report["overview"]
    print(f"🎯 总投注数: {overview['total_bets']}")
    print(f"📈 胜率: {overview['win_rate']:.1f}%")
    print(f"💰 总盈利: {overview['total_profit']:.2f} 元")
    print(f"📊 总ROI: {overview['overall_roi']:.1f}%")
    
    assessment = report["self_assessment"]
    print(f"\n🤖 自我评估: {assessment['overall_assessment']}")
    print(f"\n💡 改进建议:")
    for rec in assessment["recommendations"]:
        print(f"   • {rec}")
    
    print(f"\n⚙️ 当前优化参数:")
    for key, value in assessment["current_parameters"].items():
        print(f"   • {key}: {value}")
    
    print(f"\n📈 趋势分析: {report['trending']}")
    print(f"📚 学习洞察: {report['insights_count']} 条")


def demo_agent_communication():
    """演示Agent间通信"""
    print("\n" + "="*80)
    print("💬 Agent间通信演示")
    print("="*80)
    
    # Scout 发送消息给 Quant
    msg1 = COLLABORATION_MANAGER.send_message(
        sender="Scout",
        receiver="Quant",
        content="发现主队有2名主力后卫伤停",
        message_type="info",
        context={"injury_count": 2, "position": "defender"},
    )
    print(f"💬 {msg1.sender} → {msg1.receiver}: {msg1.content}")
    
    # Quant 发送消息给 Risk
    msg2 = COLLABORATION_MANAGER.send_message(
        sender="Quant",
        receiver="Risk",
        content="伤停信息影响较大，建议降低仓位",
        message_type="request",
        context={"confidence": -0.3, "action": "reduce_stake"},
    )
    print(f"💬 {msg2.sender} → {msg2.receiver}: {msg2.content}")
    
    # Trader 广播消息
    msgs = COLLABORATION_MANAGER.broadcast_message(
        sender="Trader",
        content="综合分析决定放弃本场比赛",
        receivers=["Quant", "Risk", "Auditor"],
        context={"decision": "skip", "reason": "risk_too_high"},
    )
    print(f"📢 {msgs[0].sender} 广播给所有人: {msgs[0].content}")
    
    # 获取协作统计
    stats = COLLABORATION_MANAGER.get_collaboration_stats()
    print(f"\n📊 协作统计:")
    print(f"   • 总消息数: {stats['total_messages']}")
    print(f"   • 等待任务: {stats['pending_tasks']}")
    print(f"   • 历史决策: {stats['total_decisions']}")
    print(f"   • 共识率: {stats['consensus_rate']:.1%}")


def main():
    """主演示"""
    print("\n" + "="*80)
    print("🚀 AFA v9.0 新功能演示")
    print("="*80)
    print("\n📋 新增功能:")
    print("   1. ✅ 多Agent协作框架")
    print("      • Agent间自然对话")
    print("      • 集体决策与共识达成")
    print("      • 智能任务分配")
    print("   2. ✅ 自适应学习回路")
    print("      • 投注结果反馈记录")
    print("      • 参数动态优化")
    print("      • 自我评估与改进")
    print("="*80)
    
    try:
        # 1. Agent间通信
        demo_agent_communication()
        
        # 2. 任务分配
        demo_task_allocation()
        
        # 3. 集体决策
        demo_collective_decision()
        
        # 4. 自适应学习
        demo_adaptive_learning()
        
        print("\n" + "="*80)
        print("✅ AFA v9.0 新功能演示完成!")
        print("="*80)
        print("\n📋 完整系统总览:")
        print("   1. ✅ 官方规则完整性验证 (SSOT)")
        print("   2. ✅ 规则驱动的AI决策系统")
        print("   3. ✅ MCP工具增强")
        print("   4. ✅ 多Agent协作框架 🆕")
        print("   5. ✅ 自适应学习回路 🆕")
        print("   6. ✅ 系统架构优化")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
