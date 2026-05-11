#!/usr/bin/env python3
"""
AFA v9.0 - MCP 工具完整演示

演示如何使用 AI 增强的 MCP 工具，特别是规则驱动的决策功能。
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("=" * 100)
print("🎯 AFA v9.0 - MCP 工具完整演示")
print("=" * 100)
print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ============================================================================
# 演示 1: 规则查询
# ============================================================================
print("\n" + "=" * 100)
print("1️⃣  演示 1: 查询官方投注规则")
print("=" * 100)
print()

try:
    from src.afa_v9.ai_augmented import AI_AUGMENTED_MCP
    
    print("✅ MCP 工具导入成功")
    print()
    
    # 查询竞彩规则
    queries = [
        "竞彩奖金怎么计算？",
        "M串N容错是什么意思？",
        "北单单关赔率怎么算？",
    ]
    
    for query in queries:
        print(f"\n🔍 查询: '{query}'")
        result = AI_AUGMENTED_MCP.query_lottery_rules(query, limit=3)
        
        if result.get("success"):
            print(f"✅ 找到 {result.get('total_found', 0)} 条结果")
            for i, rule in enumerate(result.get("results", [])[:2], 1):
                content = rule.get("content", "")[:120]
                print(f"  {i}. {content}...")
        else:
            print(f"⚠️ 查询失败: {result.get('error')}")
            
except Exception as e:
    print(f"⚠️ 演示 1 执行提示: {e}")
    print("此功能需要语义记忆模块已正确配置。")

# ============================================================================
# 演示 2: 列出所有可用工具
# ============================================================================
print("\n" + "=" * 100)
print("2️⃣  演示 2: 列出所有可用 MCP 工具")
print("=" * 100)
print()

try:
    from src.afa_v9.ai_augmented import AI_AUGMENTED_MCP
    
    tools_result = AI_AUGMENTED_MCP.list_available_tools()
    
    if tools_result.get("success"):
        print("✅ 可用工具:")
        print()
        
        tools_dict = tools_result.get("tools", {})
        for category, tools in tools_dict.items():
            print(f"📦 分类: {category}")
            for tool in tools:
                print(f"  • {tool.get('name')}: {tool.get('description')}")
            print()
    else:
        print(f"⚠️ 获取工具列表失败: {tools_result.get('error')}")
        
except Exception as e:
    print(f"⚠️ 演示 2 执行提示: {e}")

# ============================================================================
# 演示 3: 规则驱动决策（结构测试）
# ============================================================================
print("\n" + "=" * 100)
print("3️⃣  演示 3: 规则驱动决策功能结构")
print("=" * 100)
print()

try:
    from src.afa_v9.ai_augmented import AI_AUGMENTED_MCP
    from src.afa_v9.ai_augmented.rules_driven_decision import (
        RulesDrivenDecider,
        RuleContext,
    )
    
    print("✅ 规则驱动决策模块导入成功")
    print()
    
    # 测试决策上下文创建
    print("📋 规则决策上下文示例:")
    test_context = RuleContext(
        lottery_type="JINGCAI",
        play_type="胜平负",
        match_info={
            "home_team": "曼联",
            "away_team": "利物浦",
            "league": "英超",
        },
        odds_data={
            "胜": 2.10,
            "平": 3.40,
            "负": 3.25,
        },
        bet_type="single",
    )
    
    print(f"  • 彩种: {test_context.lottery_type}")
    print(f"  • 玩法: {test_context.play_type}")
    print(f"  • 比赛: {test_context.match_info.get('home_team')} vs {test_context.match_info.get('away_team')}")
    print(f"  • 赔率: {test_context.odds_data}")
    
    print()
    print("📋 规则驱动决策功能已就绪")
    print("完整的规则驱动 AI 决策包括:")
    print("  1. 自动规则检索 (基于语义记忆)")
    print("  2. 规则注入 LLM 提示词")
    print("  3. LLM 基于规则的决策")
    print("  4. 决策合规性检查")
    print()
    print("⚠️ 注意: 完整的 LLM 调用需要配置 LLM 服务")
    
except Exception as e:
    print(f"⚠️ 演示 3 执行提示: {e}")

# ============================================================================
# 演示 4: 整合演示结构
# ============================================================================
print("\n" + "=" * 100)
print("4️⃣  演示 4: 完整分析流程结构")
print("=" * 100)
print()

print("📊 完整分析流程:")
print()
print("步骤 1: 查询相关规则")
print("  → 调用: query_lottery_rules('英超 投注规则 奖金计算')")
print()
print("步骤 2: 执行规则驱动决策")
print("  → 调用: rules_driven_decide(...)")
print()
print("步骤 3: 执行标准分析")
print("  → 调用: full_analysis(...)")
print()
print("步骤 4: 整合结果")
print("  → 返回完整分析报告")
print()

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 100)
print("🎯 MCP 工具使用说明")
print("=" * 100)
print()

print("📦 主要工具分类:")
print("  1️⃣  规则驱动")
print("     • rules_driven_decide - 官方规则驱动的 AI 决策")
print("     • query_lottery_rules - 查询官方投注规则")
print("     • rules_based_full_analysis - 基于官方规则的完整分析")
print()
print("  2️⃣  LLM 决策")
print("     • llm_decide - LLM 投注决策")
print("     • llm_calculate_kelly - LLM 动态 Kelly 计算")
print("     • llm_six_layer_analyze - LLM 动态六层分析")
print()
print("  3️⃣  预测分析")
print("     • llm_predict_goals - LLM 增强进球预测")
print("     • llm_generate_strategy - LLM 自动生成投注策略")
print("     • full_analysis - 完整 AI 分析")
print()
print("  4️⃣  记忆搜索")
print("     • llm_semantic_search - LLM 语义搜索")
print("     • llm_recommend_memories - LLM 记忆推荐")
print()
print("  5️⃣  执行管理")
print("     • llm_intelligent_execution - LLM 智能投注执行")
print("     • llm_dynamic_bankroll - LLM 动态资金管理")
print()

print("💡 使用示例:")
print()
print("  # 基础导入")
print("  from src.afa_v9.ai_augmented import AI_AUGMENTED_MCP")
print()
print("  # 查询规则")
print("  rules = AI_AUGMENTED_MCP.query_lottery_rules('竞彩奖金计算')")
print()
print("  # 规则驱动决策")
print("  decision = AI_AUGMENTED_MCP.rules_driven_decide(")
print("      home_team='曼联',")
print("      away_team='利物浦',")
print("      home_odds=2.10,")
print("      draw_odds=3.40,")
print("      away_odds=3.25,")
print("      league='英超',")
print("      lottery_type='JINGCAI'")
print("  )")
print()
print("  # 完整分析")
print("  analysis = AI_AUGMENTED_MCP.rules_based_full_analysis(...)")
print()

print("=" * 100)
print("🎊 MCP 工具演示完成！")
print("=" * 100)
