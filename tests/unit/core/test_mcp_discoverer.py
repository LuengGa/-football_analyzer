import pytest

from src.core.mcp_discoverer import MCPToolDiscoverer

def test_discover_tools():
    discoverer = MCPToolDiscoverer()
    # Mocking discovery
    tools = discoverer.discover_local_tools("tests/mock_mcp_servers")
    
    assert isinstance(tools, list)
    if len(tools) > 0:
        assert "type" in tools[0]
        assert tools[0]["type"] == "function"
