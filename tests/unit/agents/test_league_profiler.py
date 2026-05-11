import json

import pytest

from src.agents.league_profiler_v2 import get_league_persona


@pytest.mark.skip(reason="get_league_persona profile format changed, needs update")
def test_league_profiler_returns_persona():
    result_str = get_league_persona("Premier League")
    result = json.loads(result_str)
    assert "profile" in result
    assert "persona" in result["profile"]
    assert "variance" in result["profile"]
    assert "tactical_style" in result["profile"]
