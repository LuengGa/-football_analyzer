r"""
AFA v9.0 完整集成测试
========================

测试所有模块协同工作：
1. LLM Gateway - 多Provider路由
2. Agent Runtime - 6个数字生命体Agent
3. Memory System - 多层记忆
4. Evolution Engine - 自进化

运行:
    cd /Volumes/J ZAO 9 SER 1/Python/TRAE-SOLO/football_analyzer
    /Users/jand/.homebrew/bin/python3 -m pytest tests/integration/test_afa_v9_complete.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.llm.gateway import LLMGateway, LLM_GATEWAY, ProviderType
from src.afa_v9.agents import (
    ScoutAgent, QuantAgent, MarketAgent, RiskAgent, TraderAgent, AuditorAgent,
    ALL_AGENTS, get_agent_by_name,
)
from src.afa_v9.memory import (
    Memory, MEMORY_INSTANCE, UnifiedMemory,
    WorkingMemory, EpisodicMemory, SemanticMemory, BM25Search,
)
from src.afa_v9.evolution import (
    EvolutionEngine, EVOLUTION_ENGINE,
    EvolutionPhase, OutcomeType,
)


def test_llm_gateway_integration():
    """测试LLM Gateway"""
    gateway = LLMGateway()

    assert gateway is not None
    assert isinstance(gateway.providers, dict)

    providers = gateway.get_available_providers()
    assert isinstance(providers, list)

    provider = gateway.route("analysis")
    assert provider in ProviderType

    print("✅ LLM Gateway 集成测试通过")


def test_agent_runtime_integration():
    """测试Agent Runtime"""
    agents = ALL_AGENTS
    assert len(agents) == 6

    for agent in agents:
        status = agent.get_status()
        assert "name" in status
        assert "execution_count" in status

    scout = get_agent_by_name("scout")
    assert scout is not None

    print("✅ Agent Runtime 集成测试通过")


def test_agent_workflow():
    """测试Agent工作流"""
    state = {
        "home_team": "Manchester City",
        "away_team": "Arsenal",
        "match_id": "test_001",
    }

    scout = get_agent_by_name("scout")
    result = scout.execute(state)
    assert "scout_report" in result
    assert "current_step" in result

    state.update(result)

    quant = get_agent_by_name("quant")
    result = quant.execute(state)
    assert "quant_report" in result

    state.update(result)

    market = get_agent_by_name("market")
    result = market.execute(state)
    assert "market_report" in result

    state.update(result)

    risk = get_agent_by_name("risk")
    result = risk.execute(state)
    assert "risk_report" in result

    state.update(result)

    trader = get_agent_by_name("trader")
    result = trader.execute(state)
    assert "trader_decision" in result

    state.update(result)

    auditor = get_agent_by_name("auditor")
    result = auditor.execute(state)
    assert "audit_report" in result

    print("✅ Agent工作流测试通过")


def test_memory_system_integration():
    """测试Memory System"""
    memory = MEMORY_INSTANCE

    memory.store_interaction("test_match", {"result": "win"}, importance=0.8)

    results = memory.search_memory("test")
    assert isinstance(results, list)

    context = memory.get_full_context()
    assert isinstance(context, str)

    print("✅ Memory System 集成测试通过")


def test_evolution_engine_integration():
    """测试Evolution Engine"""
    engine = EvolutionEngine()

    exp = engine.record_experience(
        context={"league": "Premier League", "odds": 2.0},
        action="bet_home_win",
        outcome=OutcomeType.SUCCESS,
        metrics={"profit": 1.0},
        tags=["premier_league"],
    )
    assert exp is not None

    skill = engine.create_skill(
        name="Test Skill",
        description="Integration test skill",
        source="test",
    )
    assert skill is not None

    engine.apply_skill(skill.id, success=True, profit=0.5)

    perf = engine.evaluate_performance()
    assert "total_skills" in perf

    print("✅ Evolution Engine 集成测试通过")


def test_full_analysis_pipeline():
    """测试完整分析流程"""
    engine = EvolutionEngine()
    engine.reset()

    test_experiences = [
        {
            "context": {"league": "Premier League", "odds": 1.9, "home_team": "Man City"},
            "action": "bet_home_win",
            "outcome": OutcomeType.SUCCESS,
            "metrics": {"profit": 0.9},
            "tags": ["premier_league", "favorite"],
        },
        {
            "context": {"league": "La Liga", "odds": 3.5, "home_team": "Real Madrid"},
            "action": "bet_home_win",
            "outcome": OutcomeType.SUCCESS,
            "metrics": {"profit": 2.5},
            "tags": ["la_liga", "underdog"],
        },
        {
            "context": {"league": "Serie A", "odds": 2.2, "home_team": "Inter"},
            "action": "bet_home_win",
            "outcome": OutcomeType.PARTIAL,
            "metrics": {"profit": 0.2},
            "tags": ["serie_a"],
        },
    ]

    for exp_data in test_experiences:
        engine.record_experience(**exp_data)

    pattern_result = engine.analyze_patterns()
    assert "patterns_found" in pattern_result

    evolution_result = engine.evolve()
    assert "performance" in evolution_result

    report = engine.get_evolution_report()
    assert isinstance(report, str)
    assert "Self-Evolution Report" in report

    print("✅ 完整分析流程测试通过")


def test_cross_module_integration():
    """测试跨模块集成"""
    memory = MEMORY_INSTANCE
    engine = EvolutionEngine()

    memory.store_interaction(
        "premier_league_analysis",
        {"home_team": "Man City", "result": "win"},
        importance=0.9,
    )

    engine.record_experience(
        context={"league": "Premier League", "analysis": "win"},
        action="analyze_match",
        outcome=OutcomeType.SUCCESS,
        metrics={"confidence": 0.85},
        tags=["premier_league"],
    )

    perf = engine.evaluate_performance()
    assert perf["total_skills"] >= 0

    print("✅ 跨模块集成测试通过")


def run_all_tests():
    """运行所有集成测试"""
    print("\n" + "=" * 60)
    print("AFA v9.0 完整集成测试")
    print("=" * 60 + "\n")

    tests = [
        ("LLM Gateway", test_llm_gateway_integration),
        ("Agent Runtime", test_agent_runtime_integration),
        ("Agent Workflow", test_agent_workflow),
        ("Memory System", test_memory_system_integration),
        ("Evolution Engine", test_evolution_engine_integration),
        ("Full Pipeline", test_full_analysis_pipeline),
        ("Cross-Module", test_cross_module_integration),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, "PASS"))
        except Exception as e:
            results.append((name, f"FAIL: {e}"))

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = 0
    for name, result in results:
        icon = "✅" if result == "PASS" else "❌"
        print(f"{icon} {name}: {result}")
        if result == "PASS":
            passed += 1

    print(f"\n总计: {passed}/{len(results)} 通过")
    print("=" * 60)

    return passed == len(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
