#!/usr/bin/env python3
"""
AFA Evolution - 进化与自我优化测试
测试进化引擎和自我优化功能
"""

import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from src.afa_v9 import AFAV9_SYSTEM, EVOLUTION_ENGINE
from src.calculations.historical_data_loader import HistoricalDataLoader
from src.calculations.pro.poisson_model import PoissonGoalModel


def main():
    print("=" * 80)
    print("🏆 AFA v9.0 - 进化与自我优化测试")
    print("=" * 80)

    print("\n[1] 进化引擎状态")
    perf = EVOLUTION_ENGINE.evaluate_performance()
    print(f"   技能数量: {len(EVOLUTION_ENGINE.skills)}")
    print(f"   经验数量: {len(EVOLUTION_ENGINE.experiences)}")
    print(f"   整体有效性: {perf.get('overall_effectiveness', 0):.2%}")

    print("\n[2] 添加测试经验")
    EVOLUTION_ENGINE.add_experience(
        {
            "task_type": "match_analysis",
            "outcome": "success",
            "roi": 0.15,
            "match": "Bayern Munich vs Dortmund",
        }
    )
    EVOLUTION_ENGINE.add_experience(
        {
            "task_type": "match_analysis",
            "outcome": "failure",
            "roi": -0.05,
            "match": "Arsenal vs Chelsea",
        }
    )
    print("   ✅ 添加了2条测试经验")

    print("\n[3] 分析经验模式")
    analysis = EVOLUTION_ENGINE.analyze_experiences()
    print(f"   总经验数: {analysis.get('total_experiences', 0)}")
    print(f"   成功率: {analysis.get('success_rate', 0):.1%}")
    print(f"   模式: {analysis.get('patterns', [])}")
    print(f"   洞察: {analysis.get('insights', [])}")

    print("\n[4] 生成新技能")
    skill = EVOLUTION_ENGINE.generate_skill(name="test_skill", description="测试生成的技能")
    print(f"   ✅ 生成技能: {skill.name} (ID: {skill.id})")

    print("\n[5] 触发自我评估")
    evaluation = EVOLUTION_ENGINE.evaluate_self()
    print(f"   状态: {evaluation.get('status')}")
    print(f"   进化次数: {evaluation.get('evolution_count')}")
    print(f"   建议数量: {len(evaluation.get('suggestions', []))}")

    print("\n" + "=" * 80)
    print("✅ 进化测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
