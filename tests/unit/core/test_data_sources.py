import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.core.data_sources import (
    CONFIG,
    DataSourceConfig,
    RATE_LIMITER,
    RateLimiter,
    DATA_SOURCE_MANAGER,
    DataSourceManager,
)
from src.core.mcp import MCP_SERVER, MCPServer


def test_config():
    assert CONFIG is not None
    assert "api_football" in CONFIG.BASE_URLS
    assert "football_data" in CONFIG.BASE_URLS


def test_rate_limiter():
    status = RATE_LIMITER.get_status("api_football")
    assert "source" in status
    assert "available" in status


def test_rate_limiter_acquire():
    result = RATE_LIMITER.acquire("the_sports_db", timeout=1.0)
    assert isinstance(result, bool)


def test_mcp_server():
    assert MCP_SERVER is not None
    schemas = MCP_SERVER.get_tool_schemas()
    assert len(schemas) > 0


def test_mcp_tool_get_match_data():
    schemas = MCP_SERVER.get_tool_schemas()
    tool_names = [s["name"] for s in schemas]
    assert "get_match_data" in tool_names
    assert "get_odds" in tool_names
    assert "get_team_stats" in tool_names


def test_mcp_tool_stats():
    stats = MCP_SERVER.get_tool_stats()
    assert "total_tools" in stats
    assert stats["total_tools"] > 0


def test_data_source_manager():
    assert DATA_SOURCE_MANAGER is not None
    assert DATA_SOURCE_MANAGER.cache is not None


def test_data_cache():
    cache = DATA_SOURCE_MANAGER.cache
    cache.set("test_key", {"data": "test"}, ttl=60)
    result = cache.get("test_key", max_age=120)
    assert result is not None
    assert result["data"] == "test"
