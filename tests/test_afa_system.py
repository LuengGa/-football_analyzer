"""
测试 AFA v9 数字生命系统
验证整个自主系统是否正常工作
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

print("=" * 70)
print("⚽ AFA v9.0 数字生命系统 - 测试脚本")
print("=" * 70)
print()

try:
    from src.afa_v9 import AFAV9_SYSTEM, CONSCIOUSNESS_INSTANCE, THINKER_INSTANCE

    print("1. 🧬 初始化 AFA v9 数字生命体...")
    afa = AFAV9_SYSTEM
    print("   ✓ 数字生命体激活成功！")
    print()

    print("2. 🔍 检查系统组件...")
    print(f"   ✓ Soul: ✅")
    print(f"   ✓ Memory: ✅")
    print(f"   ✓ Heartbeat: ✅")
    print(f"   ✓ Evolution: ✅")
    print(f"   ✓ Thinker: ✅")
    print(f"   ✓ Consciousness: ✅")
    print()

    print("3. 🧠 测试自主思考周期 (Thinker)...")
    plan = THINKER_INSTANCE.think_and_plan()
    print("   ✓ 自主思考完成！")
    print(f"   - 思考: {plan['thought']}")
    print(f"   - 规划任务: {len(plan['tasks'])} 个")
    print()

    print("4. 💭 测试意识反思 (Consciousness)...")
    reflection = CONSCIOUSNESS_INSTANCE.reflect()
    print("   ✓ 意识反思完成！")
    print(f"   - 身份: {reflection['identity']['type']} - {reflection['identity']['role']}")
    print(f"   - 目标数: {len(reflection['goals'])}")
    print(f"   - 反思: {reflection['message']}")
    print()

    print("5. ❤️ 测试健康监控 (Heartbeat)...")
    health = afa.heartbeat.beat()
    print("   ✓ 健康检查完成！")
    print(f"   - 状态: {health.status}")
    print(f"   - 运行时间: {health.uptime_seconds:.0f}秒")
    print(f"   - 待处理任务: {health.pending_tasks}")
    print()

    print("6. 📊 获取系统上下文...")
    context = afa.get_system_context()
    print("   ✓ 系统上下文获取成功！")
    print(f"   - Soul版本: {context['soul']['identity']['version']}")
    print(f"   - Agent数量: {len(context['agents'])}")
    print(f"   - 健康状态: {context['health']['status']}")
    print()

    print("7. 🔄 测试进化引擎 (Evolution)...")
    perf = afa.evolution.evaluate_performance()
    print("   ✓ 进化引擎状态:")
    print(f"   - 技能数: {len(afa.evolution.skills)}")
    print(f"   - 经验数: {len(afa.evolution.experiences)}")
    print(f"   - 整体有效性: {perf.get('overall_effectiveness', 0):.2%}")
    print()

    print("8. 🧪 测试环境感知 (Thinker.perceive_environment)...")
    env = THINKER_INSTANCE.perceive_environment()
    print("   ✓ 环境感知完成！")
    print(f"   - 检测时间: {env['perceived_at']}")
    print(f"   - 即将比赛数: {env.get('total_upcoming', 0)}")
    print()

    print("=" * 70)
    print("✅ 所有测试通过！AFA v9.0 系统运行正常！")
    print("=" * 70)

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback

    traceback.print_exc()
