"""
AFA v9.0 工作流执行测试
======================

测试LangGraph完整链路：
1. Scout → 情报收集
2. Quant → 量化分析
3. Market → 市场分析
4. Risk → 风险评估
5. Trader → 交易决策
6. Auditor → 审计确认

使用方法:
    python scripts/test_workflow_execution.py
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.afa_v9 import AFAV9_SYSTEM, OutcomeType


MOCK_MATCH_DATA = {
    "match_id": "test_20260509_001",
    "home_team": "Manchester City",
    "away_team": "Arsenal",
    "league": "Premier League",
    "venue_city": "Manchester",
    "match_time": "2026-05-10 20:00 UTC",
    "odds": {
        "home_win": 1.85,
        "draw": 3.60,
        "away_win": 4.20,
        "over_2_5": 1.95,
        "under_2_5": 1.90,
    },
    "home_stats": {
        "position": 1,
        "form": "WWWDW",
        "home_record": "12W-2D-1L",
        "goals_scored": 45,
        "goals_conceded": 15,
    },
    "away_stats": {
        "position": 2,
        "form": "WWWWL",
        "away_record": "10W-3D-2L",
        "goals_scored": 38,
        "goals_conceded": 18,
    },
    "head_to_head": {
        "total_matches": 10,
        "home_wins": 6,
        "draws": 2,
        "away_wins": 2,
    },
}


MOCK_TASKS = [
    {
        "type": "pre_match_analysis",
        "match_id": "test_20260509_001",
        "home_team": "Manchester City",
        "away_team": "Arsenal",
        "venue_city": "Manchester",
    },
    {
        "type": "value_finding",
        "league": "Premier League",
        "min_odds": 2.0,
        "max_odds": 5.0,
    },
    {
        "type": "portfolio_review",
        "current_exposure": 0.15,
        "target_exposure": 0.10,
    },
]


def test_workflow_with_match(afa: AFAV9, match_data: Dict[str, Any]) -> Dict[str, Any]:
    """测试单场比赛工作流"""
    print("\n" + "=" * 60)
    print(f"🧪 工作流测试: {match_data['home_team']} vs {match_data['away_team']}")
    print("=" * 60)

    try:
        result = afa.process_match(
            match_id=match_data["match_id"],
            home_team=match_data["home_team"],
            away_team=match_data["away_team"],
            venue_city=match_data.get("venue_city"),
            thread_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        )

        print("\n📋 工作流执行结果:")
        print(f"  - 状态: {'✅ 成功' if result else '❌ 失败'}")
        print(f"  - 决策: {result.get('trader_decision', {}).get('approved', 'N/A')}")
        print(f"  - 推荐: {result.get('trader_decision', {}).get('recommendation', 'N/A')}")

        return {"status": "success", "result": result}

    except Exception as e:
        print(f"\n❌ 工作流执行失败: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def test_workflow_with_tasks(afa: AFAV9, tasks: list) -> Dict[str, Any]:
    """测试任务工作流"""
    print("\n" + "=" * 60)
    print("🧪 多任务工作流测试")
    print("=" * 60)

    results = []
    for i, task in enumerate(tasks, 1):
        print(f"\n📌 任务 {i}/{len(tasks)}: {task['type']}")

        try:
            result = afa.process(
                task=task,
                thread_id=f"test_task_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )
            print(f"  ✅ 完成")
            results.append({"task": task["type"], "status": "success", "result": result})
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            results.append({"task": task["type"], "status": "error", "error": str(e)})

    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n📊 任务统计: {success_count}/{len(tasks)} 成功")

    return {"status": "completed", "results": results}


def test_evolution_integration(afa: AFAV9) -> Dict[str, Any]:
    """测试Evolution集成"""
    print("\n" + "=" * 60)
    print("🧪 Evolution系统集成测试")
    print("=" * 60)

    evo = afa.evolution

    test_experiences = [
        {
            "context": {"league": "Premier League", "odds": 1.9, "home_team": "Man City"},
            "action": "bet_home_win",
            "outcome": OutcomeType.SUCCESS,
            "metrics": {"profit": 0.9, "roi": 90.0},
            "tags": ["premier_league", "favorite"],
        },
        {
            "context": {"league": "Premier League", "odds": 3.5, "away_team": "Arsenal"},
            "action": "bet_away_win",
            "outcome": OutcomeType.SUCCESS,
            "metrics": {"profit": 2.5, "roi": 250.0},
            "tags": ["premier_league", "underdog"],
        },
        {
            "context": {"league": "La Liga", "odds": 2.2, "home_team": "Real Madrid"},
            "action": "bet_home_win",
            "outcome": OutcomeType.PARTIAL,
            "metrics": {"profit": 0.2, "roi": 20.0},
            "tags": ["la_liga", "favorite"],
        },
        {
            "context": {"league": "Serie A", "odds": 4.5, "home_team": "Inter"},
            "action": "bet_home_win",
            "outcome": OutcomeType.FAILURE,
            "metrics": {"profit": -1.0, "roi": -100.0},
            "tags": ["serie_a", "underdog"],
        },
        {
            "context": {"league": "Bundesliga", "odds": 1.6, "home_team": "Bayern"},
            "action": "bet_home_win",
            "outcome": OutcomeType.SUCCESS,
            "metrics": {"profit": 0.6, "roi": 60.0},
            "tags": ["bundesliga", "strong_favorite"],
        },
    ]

    print(f"\n📝 注入 {len(test_experiences)} 条测试经验...")
    for exp in test_experiences:
        evo.record_experience(
            context=exp["context"],
            action=exp["action"],
            outcome=exp["outcome"],
            metrics=exp.get("metrics"),
            tags=exp.get("tags"),
        )

    print("\n🔄 执行模式分析...")
    pattern_result = evo.analyze_patterns()
    print(f"  - 发现模式: {pattern_result.get('patterns_found', 0)}")
    print(f"  - 总体成功率: {pattern_result.get('overall_success_rate', 0):.1%}")
    print(f"  - 联赛表现: {pattern_result.get('league_rates', {})}")

    print("\n🧬 执行进化...")
    evolution_result = evo.evolve()
    print(f"  - 新假说: {evolution_result.get('new_hypotheses', 0)}")
    print(f"  - 实验结果: {len(evolution_result.get('experiment_results', []))}")

    print("\n📈 性能评估...")
    performance = evo.evaluate_performance()
    print(f"  - 总体效能: {performance['overall_effectiveness']:.1%}")
    print(f"  - 平均成功率: {performance['avg_success_rate']:.1%}")
    print(f"  - 技能总数: {performance['total_skills']}")
    print(f"  - 活跃技能: {performance['active_skills']}")

    print("\n🏆 Top 5 技能:")
    top_skills = evo.get_best_skills(5)
    for i, skill in enumerate(top_skills, 1):
        print(f"  {i}. {skill.name}: 效能 {skill.effectiveness:.1%} | 使用 {skill.usage_count}次")

    print("\n📋 Evolution报告:")
    report = evo.get_evolution_report()
    print(report)

    return {"pattern_analysis": pattern_result, "evolution": evolution_result, "performance": performance}


def test_system_health(afa: AFAV9) -> Dict[str, Any]:
    """测试系统健康状态"""
    print("\n" + "=" * 60)
    print("🏥 系统健康检查")
    print("=" * 60)

    health = afa.heartbeat.health_status
    print(f"\n  心跳状态: {health.status}")
    print(f"  运行时间: {health.uptime_seconds:.0f}秒")
    print(f"  总任务数: {health.total_tasks}")
    print(f"  完成任务: {health.completed_tasks}")
    print(f"  失败任务: {health.failed_tasks}")
    print(f"  队列长度: {health.queue_length}")

    agents = afa.get_agent_status()
    print(f"\n  智能体状态:")
    for name, status in agents.items():
        print(f"    - {name}: 执行 {status['execution_count']}次")

    return {"health": health.model_dump(), "agents": agents}


def run_full_test_suite():
    """运行完整测试套件"""
    print("\n" + "🎯" * 30)
    print("AFA v9.0 完整工作流测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯" * 30)

    afa = AFAV9_SYSTEM

    print("\n🔧 系统初始化...")
    afa.activate()
    afa.initialize_workflow("pre_match")
    print("✅ 系统就绪")

    results = {
        "health_check": test_system_health(afa),
        "match_workflow": test_workflow_with_match(afa, MOCK_MATCH_DATA),
        "task_workflow": test_workflow_with_tasks(afa, MOCK_TASKS),
        "evolution_integration": test_evolution_integration(afa),
    }

    print("\n" + "=" * 60)
    print("📊 测试汇总")
    print("=" * 60)

    all_success = True
    for test_name, result in results.items():
        status = "✅" if result.get("status") != "error" else "❌"
        print(f"  {status} {test_name}: {result.get('status', 'N/A')}")
        if result.get("status") == "error":
            all_success = False

    print("\n" + "=" * 60)
    if all_success:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查日志")
    print("=" * 60)

    return results


if __name__ == "__main__":
    run_full_test_suite()
