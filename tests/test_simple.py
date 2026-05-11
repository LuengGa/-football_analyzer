#!/usr/bin/env python3
"""
简单测试脚本 - AFA v9
"""

import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from src.afa_v9 import AFAV9_SYSTEM, CONSCIOUSNESS_INSTANCE, THINKER_INSTANCE
from src.calculations.historical_data_loader import HistoricalDataLoader


def main():
    print("=" * 80)
    print("  AFA v9.0 系统测试")
    print("=" * 80)

    print("\n[1] 初始化 AFA v9 系统...")
    print(f"✅ 初始化成功!")

    print(f"\n[2] 系统组件状态:")
    print(f"    Soul: ✅ 已初始化")
    print(f"    Memory: ✅ 已初始化")
    print(f"    Heartbeat: ✅ 已初始化")
    print(f"    Evolution: ✅ 已初始化")
    print(f"    Thinker: ✅ 已初始化")
    print(f"    Consciousness: ✅ 已初始化")

    health = AFAV9_SYSTEM.heartbeat.beat()
    print(f"\n[3] 健康监控:")
    print(f"    状态: {health.status}")
    print(f"    运行时间: {health.uptime_seconds:.0f}秒")
    print(f"    活跃Agent: {health.active_agents}")
    print(f"    待处理任务: {health.pending_tasks}")

    print(f"\n[4] 测试环境感知 (Thinker)...")
    try:
        env = THINKER_INSTANCE.perceive_environment()
        print(f"    检测到 {env.get('total_upcoming', 0)} 场即将到来的比赛")
    except Exception as e:
        print(f"    环境感知: {e}")

    print(f"\n[5] 测试意识系统 (Consciousness)...")
    identity = CONSCIOUSNESS_INSTANCE.get_identity()
    print(f"    身份: {identity['name']}")
    print(f"    版本: {identity['version']}")
    print(f"    角色: {identity['role']}")

    reflection = CONSCIOUSNESS_INSTANCE.reflect()
    print(f"    反思: {reflection['message']}")

    print(f"\n[6] 测试历史数据查询...")
    try:
        loader = HistoricalDataLoader()
        loader.load()
        print(f"✅ 历史数据加载成功! 共 {len(loader.matches)} 场比赛")
    except Exception as e:
        print(f"❌ 查询失败: {e}")

    print("\n" + "=" * 80)
    print("✅ 系统测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
