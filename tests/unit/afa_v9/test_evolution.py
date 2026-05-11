import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.afa_v9.evolution import (
    EvolutionEngine,
    EVOLUTION_ENGINE,
    EvolutionPhase,
    OutcomeType,
    Experience,
    EvolvedSkill,
    Pattern,
    Hypothesis,
)


def test_evolution_engine_creation():
    engine = EvolutionEngine()
    assert engine is not None
    assert engine.current_phase == EvolutionPhase.OBSERVATION


def test_record_experience():
    engine = EvolutionEngine()
    exp = engine.record_experience(
        context={"league": "Premier League", "odds": 2.0},
        action="bet_home_win",
        outcome=OutcomeType.SUCCESS,
        metrics={"profit": 1.0, "roi": 100.0},
        tags=["premier_league", "home_win"],
    )
    
    assert exp is not None
    assert exp.id.startswith("exp_")
    assert exp.outcome == OutcomeType.SUCCESS


def test_create_skill():
    engine = EvolutionEngine()
    skill = engine.create_skill(
        name="Test Skill",
        description="A test skill",
        tags=["test"],
        source="unit_test",
    )
    
    assert skill is not None
    assert skill.name == "Test Skill"
    assert skill.id in engine.skills


def test_apply_skill():
    engine = EvolutionEngine()
    skill = engine.create_skill(
        name="Apply Test Skill",
        description="Testing skill application",
    )
    
    engine.apply_skill(skill.id, success=True, profit=0.5)
    assert skill.usage_count == 1
    assert skill.success_count == 1


def test_generate_hypothesis():
    engine = EvolutionEngine()
    hyp = engine.generate_hypothesis(
        description="Test hypothesis",
        hypothesis_type="test_type",
        conditions={"league": "Premier League"},
        predicted_effect="Higher win rate",
    )
    
    assert hyp is not None
    assert hyp.status == "pending"


def test_evaluate_performance():
    engine = EvolutionEngine()
    perf = engine.evaluate_performance()
    
    assert "overall_effectiveness" in perf
    assert "total_skills" in perf
    assert isinstance(perf["total_skills"], int)


def test_evolution_singleton():
    assert EVOLUTION_ENGINE is not None
    assert isinstance(EVOLUTION_ENGINE, EvolutionEngine)


def test_evolution_phases():
    engine = EvolutionEngine()
    
    engine.analyze_patterns()
    assert engine.current_phase == EvolutionPhase.ANALYSIS
