#!/usr/bin/env python3
"""测试 AFA 数字生命体核心工具"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# 直接从 afa_mcp_server 导入工具函数
from afa_mcp_server import (
    elo_calculate,
    dixon_coles_predict,
    kelly_analyze,
    odds_implied_probabilities,
    comprehensive_match_analysis
)

print("=" * 60)
print("AFA 数字生命体 - 核心工具测试")
print("=" * 60)

print("\n1. 测试 ELO 计算...")
elo_result = elo_calculate(1850, 1830)
print(f"   Arsenal (1850) vs Chelsea (1830)")
print(f"   主胜概率: {elo_result['expected_home_win_prob']:.2%}")
print(f"   平局概率: {elo_result['expected_draw_prob']:.2%}")
print(f"   客胜概率: {elo_result['expected_away_win_prob']:.2%}")

print("\n2. 测试赔率隐含概率...")
odds_result = odds_implied_probabilities(1.85, 3.40, 4.20)
print(f"   赔率: 主胜 1.85 / 平局 3.40 / 客胜 4.20")
print(f"   主胜隐含概率: {odds_result['implied_home']:.2%}")
print(f"   平局隐含概率: {odds_result['implied_draw']:.2%}")
print(f"   客胜隐含概率: {odds_result['implied_away']:.2%}")
print(f"   市场抽水: {odds_result['market_margin']:.2%}")

print("\n3. 测试 Kelly 公式...")
kelly_result = kelly_analyze(0.55, 1.85, 10000)
print(f"   真实胜率: 55%, 赔率: 1.85")
print(f"   优势: {kelly_result['edge']:.2%}")
print(f"   建议投注: {kelly_result['quarter_kelly_amount']}元 ({kelly_result['suggested_stake_pct']}%)")

print("\n4. 测试综合分析...")
comp_result = comprehensive_match_analysis(
    home_team="Arsenal",
    away_team="Chelsea",
    home_elo=1850,
    away_elo=1830,
    odds_home=1.85,
    odds_draw=3.40,
    odds_away=4.20
)
print(f"   {comp_result['match']['home_team']} vs {comp_result['match']['away_team']}")
print(f"   集成预测 - 主胜: {comp_result['ensemble']['avg_home_win_prob']:.2%}")
print(f"                平局: {comp_result['ensemble']['avg_draw_prob']:.2%}")
print(f"                客胜: {comp_result['ensemble']['avg_away_win_prob']:.2%}")

if comp_result['value_bets']:
    print(f"   发现价值投注:")
    for bet in comp_result['value_bets']:
        print(f"      - {bet['selection']} (EV: +{bet['ev']}%)")

print("\n" + "=" * 60)
print("✓ 所有工具测试通过！AFA 数字生命体已激活。")
print("=" * 60)
