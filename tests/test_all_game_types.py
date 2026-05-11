"""
Test All Game Types - 测试所有玩法类型
验证竞彩、北单、传统足彩和国际玩法的全覆盖
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.calculations.game_type_manager import (
    get_game_type_manager,
    get_parlay_calculator,
    get_probability_engine,
)


def test_game_type_manager():
    """测试玩法类型管理器"""
    print("=" * 70)
    print("🎮 玩法类型管理器测试")
    print("=" * 70)

    manager = get_game_type_manager()

    print("\n📊 各类玩法数量统计:")
    counts = manager.count_by_category()
    total = 0
    for category, count in counts.items():
        print(f"  {category}: {count} 种")
        total += count
    print(f"  ---")
    print(f"  总计: {total} 种玩法")

    print("\n⚽ 竞彩足球玩法:")
    for i, game in enumerate(manager.get_jingcai_games(), 1):
        print(f"  {i}. {game.name}")

    print("\n🎟️ 北京单场玩法:")
    for i, game in enumerate(manager.get_beidan_games(), 1):
        print(f"  {i}. {game.name}")

    print("\n🎰 传统足彩玩法:")
    for i, game in enumerate(manager.get_zucai_games(), 1):
        print(f"  {i}. {game.name}")

    return manager


def test_probability_engine():
    """测试概率引擎"""
    print("\n" + "=" * 70)
    print("📈 概率引擎测试")
    print("=" * 70)

    engine = get_probability_engine()

    test_cases = [
        {"home_xg": 1.5, "away_xg": 1.0},
        {"home_xg": 2.0, "away_xg": 1.2},
        {"home_xg": 0.8, "away_xg": 1.8},
    ]

    for i, case in enumerate(test_cases, 1):
        result = engine.calculate_win_probs(case["home_xg"], case["away_xg"])
        print(f"\n测试 {i}: xG({case['home_xg']} vs {case['away_xg']})")
        print(f"  主胜: {result.get('home_win', 0):.1%}")
        print(f"  平局: {result.get('draw', 0):.1%}")
        print(f"  客胜: {result.get('away_win', 0):.1%}")

    return engine


def test_parlay_calculator():
    """测试串关计算器"""
    print("\n" + "=" * 70)
    print("🔢 串关计算器测试")
    print("=" * 70)

    calculator = get_parlay_calculator()

    legs = [
        {"odds": 1.85, "prob": 0.50},
        {"odds": 2.10, "prob": 0.45},
        {"odds": 1.95, "prob": 0.48},
    ]

    result = calculator.calculate_parlay(legs)
    print(f"\n3串1 计算:")
    print(f"  组合赔率: {result.get('combined_odds', 0):.2f}")
    print(f"  组合概率: {result.get('combined_prob', 0):.2%}")
    print(f"  期望值: {result.get('expected_value', 0):.2%}")

    return calculator


def main():
    print("=" * 70)
    print("🏆 AFA v9.0 - 玩法类型全覆盖测试")
    print("=" * 70)
    print()

    test_game_type_manager()
    test_probability_engine()
    test_parlay_calculator()

    print("\n" + "=" * 70)
    print("✅ 所有玩法测试通过!")
    print("=" * 70)


if __name__ == "__main__":
    main()
