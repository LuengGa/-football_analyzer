#!/usr/bin/env python3
"""
AFA v9 System - 核心模块测试
测试泊松模型、回测引擎、价值发现等功能
"""

import sys
import os
sys.path.insert(0, os.path.abspath('src'))

from src.calculations.pro.poisson_model import PoissonGoalModel
from src.calculations.pro.advanced_backtest import AdvancedBacktestEngine, BetType
from src.calculations.pro.value_finder import ValueBetFinder
from src.calculations.historical_data_loader import HistoricalDataLoader
from src.afa_v9 import AFAV9_SYSTEM

def test_poisson_model(loader):
    """测试泊松模型"""
    print("="*80)
    print("🎯 测试泊松进球模型")
    print("="*80)

    model = PoissonGoalModel()
    model.fit(loader.matches)

    print("\n📊 示例预测:")
    print("  拜仁慕尼黑 vs 多特蒙德 (虚构示例)")

    test_home = "Bayern Munich"
    test_away = "Dortmund"

    prediction = model.predict(test_home, test_away)

    if prediction:
        print(f"\n  预测结果:")
        print(f"  期望进球: 主: {prediction.home_goals_mean:.2f} - {prediction.away_goals_mean:.2f}")
        print(f"  概率:")
        print(f"    主胜: {prediction.home_win_prob:.1%}")
        print(f"    平局: {prediction.draw_prob:.1%}")
        print(f"    客胜: {prediction.away_win_prob:.1%}")
        print(f"  最可能比分: {prediction.most_likely_score}")
        print(f"  大球概率: 大: {prediction.over_2_5_prob:.1%}, 小: {prediction.under_2_5_prob:.1%}")

    return model

def test_backtest(loader, model):
    """测试回测引擎"""
    print("\n" + "="*80)
    print("🧪 测试回测引擎")
    print("="*80)

    engine = AdvancedBacktestEngine(initial_bankroll=10000)

    test_matches = loader.matches[:100]

    for match in test_matches:
        try:
            prediction = model.predict(match['home_team'], match['away_team'])
            if prediction:
                result = {
                    'home_goals': match.get('home_goals', 0),
                    'away_goals': match.get('away_goals', 0)
                }
                engine.process_match_result(prediction, result, match.get('odds', {}))
        except Exception:
            continue

    summary = engine.get_summary()
    print(f"\n📈 回测结果:")
    print(f"  总投注: {summary['total_bets']}")
    print(f"  胜率: {summary['win_rate']:.1%}")
    print(f"  最终余额: ${summary['final_balance']:.2f}")
    print(f"  ROI: {summary['roi']:.1%}")

    return engine

def test_afa_v9_system():
    """测试 AFA v9 核心系统"""
    print("\n" + "="*80)
    print("🚀 测试 AFA v9 核心系统")
    print("="*80)

    print(f"\n✅ 系统状态:")
    print(f"   版本: v9.0")
    print(f"   Soul: {AFAV9_SYSTEM.soul is not None}")
    print(f"   Memory: {AFAV9_SYSTEM.memory is not None}")
    print(f"   Heartbeat: {AFAV9_SYSTEM.heartbeat is not None}")
    print(f"   Evolution: {AFAV9_SYSTEM.evolution is not None}")
    print(f"   Thinker: {AFAV9_SYSTEM.thinker is not None}")

    health = AFAV9_SYSTEM.heartbeat.beat()
    print(f"\n❤️ 健康状态: {health.status}")
    print(f"   运行时间: {health.uptime_seconds:.0f}s")
    print(f"   错误数: {health.error_count}")

    return AFAV9_SYSTEM

def main():
    print("="*80)
    print("  AFA v9.0 核心系统测试")
    print("="*80)

    loader = HistoricalDataLoader()

    try:
        loader.load()
        print(f"\n✅ 历史数据加载成功: {len(loader.matches)} 场比赛")
    except Exception as e:
        print(f"⚠️ 历史数据加载失败: {e}")
        return

    test_afa_v9_system()

    test_poisson_model(loader)

    model = PoissonGoalModel()
    try:
        model.fit(loader.matches)
        test_backtest(loader, model)
    except Exception as e:
        print(f"⚠️ 回测失败: {e}")

    print("\n" + "="*80)
    print("✅ 测试完成!")
    print("="*80)

if __name__ == "__main__":
    main()
