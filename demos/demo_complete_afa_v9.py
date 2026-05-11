#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AFA v9.0 完整演示 - 多Agent协作 + 自适应学习
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
    LOTTERY_ROUTER_AGENT,
    SCOUT_AGENT,
    QUANT_AGENT,
    MARKET_AGENT,
    RISK_AGENT,
    TRADER_AGENT,
    AUDITOR_AGENT,
)


def demo_collaborative_analysis():
    """演示多Agent协作分析"""
    print("\n" + "="*80)
    print("🏆 AFA v9.0 完整演示 - 多Agent协作 + 自适应学习")
    print("="*80)
    
    # 示例比赛数据
    match_data = {
        "match_id": "20250101_001",
        "home_team": "曼城",
        "away_team": "利物浦",
        "league": "E0",
        "date": "2025-01-01",
    }
    
    print(f"\n📊 分析比赛: {match_data['home_team']} vs {match_data['away_team']}")
    
    # 使用协作管理器进行完整分析
    result = COLLABORATION_MANAGER.collaborative_analysis(match_data)
    
    # 显示结果
    print("\n" + "="*80)
    print("📋 协作分析结果")
    print("="*80)
    
    final_decision = result.get("trader_decision", {})
    if final_decision.get("approved"):
        bet = final_decision.get("final_bet")
        print(f"✅ 批准投注: {bet['type']} @ {bet['odds']}")
        print(f"💰 建议投注: {bet['stake']} 元 (Kelly倍数: {bet['kelly_fraction']:.4f})")
    else:
        print("❌ 未批准投注")
    
    print(f"📝 决策理由: {final_decision.get('reasoning')}")
    
    return result


def demo_collective_decision():
    """演示集体决策"""
    print("\n" + "="*80)
    print("🤝 集体决策演示")
    print("="*80)
    
    decision = COLLABORATION_MANAGER.collective_decision(
        topic="是否投注策略调整",
        options=["保守策略", "激进策略"],
        participants=["Quant", "Risk", "Trader", "Auditor"],
    )
    
    print(f"\n🎯 决策: {decision.final_decision}")
    print(f"🤝 共识达成: {'✅' if decision.consensus_reached else '❌'}")


def demo_adaptive_learning():
    """演示自适应学习"""
    print("\n" + "="*80)
    print("🧠 自适应学习回路演示")
    print("="*80)
    
    # 记录一些示例投注结果
    print("\n📝 记录投注结果...")
    
    # 模拟10次投注
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
    ]
    
    for i, (match, league, bet_type, odds, stake, actual, profit) in enumerate(results, 1):
        home, away = match.split(' vs ')
        ADAPTIVE_LEARNING.record_bet_result(
            bet_id=f"bet_2025010{i}",
            match_id=f"match_2025010{i}",
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
    print(f"\n💡 建议:")
    for rec in assessment["recommendations"]:
        print(f"   • {rec}")
    
    print(f"\n⚙️ 当前参数:")
    for key, value in assessment["current_parameters"].items():
        print(f"   • {key}: {value}")


def demo_task_allocation():
    """演示任务分配"""
    print("\n" + "="*80)
    print("📋 任务分配演示")
    print("="*80)
    
    tasks = [
        ("intelligence_gathering", "收集伤病情报", 8),
        ("quantitative_analysis", "量化模型分析", 7),
        ("market_analysis", "市场分析", 6),
        ("general_decision", "综合决策", 9),
    ]
    
    for task_type, desc, priority in tasks:
        assignment = COLLABORATION_MANAGER.assign_task(
            task_type=task_type,
            task_description=desc,
            priority=priority,
        )
        print(f"📋 任务 {assignment.task_id}: {desc}")
        print(f"   → 分配给: {assignment.assigned_agent} (优先级: {priority})")


def main():
    """主演示"""
    print("\n" + "="*80)
    print("🚀 开始 AFA v9.0 完整系统演示")
    print("="*80)
    
    try:
        # 1. 协作分析
        demo_collaborative_analysis()
        
        # 2. 集体决策
        demo_collective_decision()
        
        # 3. 任务分配
        demo_task_allocation()
        
        # 4. 自适应学习
        demo_adaptive_learning()
        
        print("\n" + "="*80)
        print("✅ AFA v9.0 演示完成!")
        print("="*80)
        print("\n📋 系统架构总览:")
        print("   1. ✅ 官方规则完整性验证")
        print("   2. ✅ 规则驱动的AI决策系统")
        print("   3. ✅ MCP工具增强")
        print("   4. ✅ 多Agent协作框架")
        print("   5. ✅ 自适应学习回路")
        print("   6. ✅ 系统架构优化")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
