#!/usr/bin/env python3
"""
AFA v9.0 MCP工具完整验证脚本

测试所有MCP工具的功能和集成
"""

import asyncio
import json
import sys
from datetime import datetime

sys.path.insert(0, ".")

from src.core.mcp.adapter import MCP_SERVER


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(name, result):
    status = "✅" if result.get("success", True) else "❌"
    print(f"{status} {name}")
    if "data" in result:
        data = result["data"]
        if isinstance(data, dict):
            for key, value in list(data.items())[:3]:
                if key not in ["raw_data", "raw_text", "raw_weather"]:
                    print(f"   - {key}: {value}")
    elif "error" in result:
        print(f"   Error: {result['error'][:50]}...")


async def main():
    print_header("AFA v9.0 MCP工具完整验证")

    stats = MCP_SERVER.get_tool_stats()
    print(f"\n📊 MCP服务器状态:")
    print(f"   - 总工具数: {stats['total_tools']}")
    print(f"   - 总调用次数: {stats['total_usage']}")
    print(f"   - 工具分类: {len(stats['categories'])}")

    print_header("1. 实时赔率工具 (odds)")
    print_result("get_odds", await MCP_SERVER.call_tool("get_odds", {"match_id": "123"}))
    print_result("get_live_odds", await MCP_SERVER.call_tool("get_live_odds", {
        "home_team": "Arsenal",
        "away_team": "Chelsea"
    }))

    print_header("2. 比赛实时数据 (live)")
    print_result("get_live_match_data", await MCP_SERVER.call_tool("get_live_match_data", {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "league": "EPL"
    }))

    print_header("3. 伤病报告 (browser)")
    print_result("get_injury_report", await MCP_SERVER.call_tool("get_injury_report", {
        "team_name": "Arsenal"
    }))

    print_header("4. 天气数据 (weather)")
    print_result("get_weather", await MCP_SERVER.call_tool("get_weather", {
        "venue": "Emirates Stadium"
    }))

    print_header("5. 历史数据查询 (historical)")
    print_result("get_data_overview", await MCP_SERVER.call_tool("get_data_overview", {}))
    print_result("query_league_matches", await MCP_SERVER.call_tool("query_league_matches", {
        "league_code": "E0",
        "year": 2024,
        "limit": 3
    }))

    print_header("6. 资金管理 (bankroll)")
    print_result("calculate_stake", await MCP_SERVER.call_tool("calculate_stake", {
        "odds": 2.5,
        "probability": 0.45,
        "confidence": 0.8
    }))
    print_result("get_bet_status", await MCP_SERVER.call_tool("get_bet_status", {
        "period": "daily"
    }))

    print_header("7. 投注追踪 (tracking)")
    print_result("record_bet", await MCP_SERVER.call_tool("record_bet", {
        "match_id": "test_001",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "selection": "home",
        "odds": 2.1,
        "stake": 50.0,
        "kelly_fraction": 0.1,
        "confidence": 0.8
    }))
    print_result("get_bet_history", await MCP_SERVER.call_tool("get_bet_history", {
        "limit": 5,
        "status": "all"
    }))

    print_header("8. 策略回测 (backtest)")
    print_result("compare_strategies", await MCP_SERVER.call_tool("compare_strategies", {
        "league_code": "E0",
        "year": 2024
    }))

    print_header("9. 搜索工具 (search)")
    print_result("search_web", await MCP_SERVER.call_tool("search_web", {
        "query": "Premier League Arsenal Chelsea match odds",
        "source": "general"
    }))

    print_header("10. 系统工具 (system)")
    print_result("get_cache_status", await MCP_SERVER.call_tool("get_cache_status", {}))
    print_result("search_memory", await MCP_SERVER.call_tool("search_memory", {
        "query": "betting strategy",
        "limit": 3
    }))

    print_header("📋 最终统计")
    final_stats = MCP_SERVER.get_tool_stats()
    print(f"\n   总工具数: {final_stats['total_tools']}")
    print(f"   总调用次数: {final_stats['total_usage']}")

    print("\n✅ MCP工具验证完成!")
    return True


if __name__ == "__main__":
    asyncio.run(main())
