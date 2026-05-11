import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.afa_v9.agents import (
    ALL_AGENTS,
    AuditorAgent,
    MarketAgent,
    QuantAgent,
    RiskAgent,
    ScoutAgent,
    TraderAgent,
    get_agent_by_name,
)


def test_agent_creation():
    scout = ScoutAgent()
    assert scout.soul.name == "Scout"
    assert scout.soul.role == "情报收集专家"


def test_all_agents_created():
    assert len(ALL_AGENTS) == 6
    agent_names = [a.soul.name for a in ALL_AGENTS]
    assert "Scout" in agent_names
    assert "Quant" in agent_names
    assert "Market" in agent_names
    assert "Risk" in agent_names
    assert "Trader" in agent_names
    assert "Auditor" in agent_names


def test_get_agent_by_name():
    scout = get_agent_by_name("scout")
    assert scout is not None
    assert scout.soul.name == "Scout"


def test_agent_execution():
    scout = ScoutAgent()
    state = {"home_team": "Man City", "away_team": "Arsenal"}
    result = scout.execute(state)

    assert "scout_report" in result
    assert "current_step" in result
    assert result["current_step"] == "scout_done"


def test_agent_status():
    scout = ScoutAgent()
    status = scout.get_status()

    assert status["name"] == "Scout"
    assert "execution_count" in status
    assert status["available"] is True


def test_risk_agent_kelly():
    risk = RiskAgent()
    state = {
        "poisson_probs": {"home_win": 0.6},
        "odds_data": {"home_win": 2.0},
    }
    result = risk.execute(state)

    assert "risk_report" in result
    assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
