#!/usr/bin/env python3
"""
AFA v9.0 数据获取能力全面测试
=====================================

测试所有数据源和获取方式
"""

import asyncio
import json
import sys
from datetime import datetime

sys.path.insert(0, ".")

from src.core.mcp.adapter import MCP_SERVER


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(title):
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {title}{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")


def print_result(name, success, details=""):
    status = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
    print(f"  {status} {name}")
    if details:
        for line in details.split('\n'):
            if line.strip():
                print(f"      {line}")


async def test_historical_data():
    """测试历史数据获取"""
    print_header("📊 历史数据获取测试")

    tests = []

    # 1. 数据库概览
    print("\n  [1] 数据库概览")
    result = await MCP_SERVER.call_tool("get_data_overview", {})
    success = result.get("success") and "total_matches" in result.get("data", {})
    data = result.get("data", {})
    details = f"比赛总数: {data.get('total_matches', 0):,} | 联赛: {data.get('leagues', 0)}个 | 范围: {data.get('date_range', 'N/A')}"
    print_result("get_data_overview", success, details)
    tests.append(("数据库概览", success))

    # 2. 联赛比赛查询
    print("\n  [2] 联赛比赛查询")
    for league, code in [("英超", "E0"), ("德甲", "D1"), ("西甲", "SP1"), ("意甲", "I1")]:
        result = await MCP_SERVER.call_tool("query_league_matches", {
            "league_code": code,
            "year": 2024,
            "limit": 5
        })
        success = result.get("success") and len(result.get("data", {}).get("matches", [])) > 0
        matches = result.get("data", {}).get("matches", [])
        sample = f"{matches[0]['home_team']} vs {matches[0]['away_team']}" if matches else "无数据"
        print_result(f"{league} (E0/24)", success, f"找到{len(matches)}场 | 示例: {sample}")
        tests.append((f"{league}比赛", success))

    # 3. 球队历史查询
    print("\n  [3] 球队历史查询")
    teams = ["Arsenal", "Bayern Munich", "Real Madrid", "Juventus", "PSG"]
    for team in teams:
        result = await MCP_SERVER.call_tool("query_team_history", {
            "team_name": team,
            "limit": 3
        })
        success = result.get("success")
        matches = result.get("data", {}).get("matches", [])
        details = f"找到{len(matches)}场" if success else "失败"
        print_result(f"{team}", success, details)
        tests.append((f"{team}历史", success))

    # 4. 球队统计
    print("\n  [4] 球队统计")
    for team in ["Arsenal", "Man United", "Liverpool"]:
        result = await MCP_SERVER.call_tool("get_team_statistics", {"team_name": team})
        success = result.get("success")
        stats = result.get("data", {})
        matches = stats.get("total_matches", 0)
        win_rate = stats.get("win_rate", 0)
        details = f"比赛{matches}场 | 胜率{win_rate:.1f}%" if success else "失败"
        print_result(f"{team}", success, details)
        tests.append((f"{team}统计", success))

    # 5. 赔率统计
    print("\n  [5] 赔率统计")
    for league in ["E0", "D1", "SP1"]:
        result = await MCP_SERVER.call_tool("get_odds_statistics", {"league_code": league})
        success = result.get("success")
        print_result(f"{league}赔率", success)
        tests.append((f"{league}赔率统计", success))

    return tests


async def test_live_data():
    """测试实时数据获取"""
    print_header("⚡ 实时数据获取测试")

    tests = []

    # 1. 实时赔率获取
    print("\n  [1] 实时赔率获取")
    match_pairs = [
        ("Arsenal", "Chelsea"),
        ("Man City", "Liverpool"),
        ("Real Madrid", "Barcelona"),
    ]
    for home, away in match_pairs:
        result = await MCP_SERVER.call_tool("get_live_odds", {
            "home_team": home,
            "away_team": away,
            "source": "auto"
        })
        success = result.get("success")
        data = result.get("data", {})
        sources = data.get("source", [])
        h2h = data.get("h2h", {})
        details = f"来源: {sources or ['无']} | H2H: {h2h if h2h else '无数据'}"
        print_result(f"{home} vs {away}", success, details[:80])
        tests.append((f"{home}赔率", success))

    # 2. 比赛实时数据
    print("\n  [2] 比赛实时数据")
    result = await MCP_SERVER.call_tool("get_live_match_data", {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "league": "EPL"
    })
    success = result.get("success")
    data = result.get("data", {})
    raw = data.get("raw_data", "")[:100] if data.get("raw_data") else "无原始数据"
    details = f"数据来源: {data.get('source', [])} | 原始: {raw[:50]}..."
    print_result("Arsenal vs Chelsea", success, details)
    tests.append(("实时比赛数据", success))

    # 3. 伤病报告
    print("\n  [3] 伤病报告")
    for team in ["Arsenal", "Man City", "Chelsea"]:
        result = await MCP_SERVER.call_tool("get_injury_report", {
            "team_name": team,
            "use_browser": True
        })
        success = result.get("success")
        data = result.get("data", {})
        injuries = data.get("injuries", [])
        sources = data.get("source", [])
        details = f"来源: {sources or ['无']} | 伤病: {len(injuries)}人"
        print_result(f"{team}", success, details)
        tests.append((f"{team}伤病", success))

    # 4. 天气数据
    print("\n  [4] 天气数据")
    venues = [
        "Emirates Stadium",
        "Anfield",
        "Old Trafford",
        "Stamford Bridge"
    ]
    for venue in venues:
        result = await MCP_SERVER.call_tool("get_weather", {
            "venue": venue,
            "date": "2026-05-15"
        })
        success = result.get("success")
        data = result.get("data", {})
        temp = data.get("temperature")
        condition = data.get("condition", "未知")
        details = f"温度: {temp}°C | 天气: {condition}" if temp else f"天气: {condition}"
        print_result(venue.split()[0], success, details)
        tests.append((f"{venue}天气", success))

    return tests


async def test_bankroll():
    """测试资金管理"""
    print_header("💰 资金管理测试")

    tests = []

    # 1. Kelly计算
    print("\n  [1] Kelly投注计算")
    test_cases = [
        (2.0, 0.55, "主场热门"),
        (3.5, 0.35, "冷门高赔"),
        (2.5, 0.45, "价值投注"),
        (1.8, 0.60, "低赔稳赢?"),
    ]
    for odds, prob, desc in test_cases:
        result = await MCP_SERVER.call_tool("calculate_stake", {
            "odds": odds,
            "probability": prob,
            "confidence": 0.8
        })
        success = result.get("success")
        data = result.get("data", {})
        edge = data.get("value_edge", 0)
        stake = data.get("recommended_stake", 0)
        rec = data.get("recommendation", "未知")
        details = f"赔率{odds}|概率{prob}|优势{edge:.2f}|投注¥{stake:.0f}|{rec}"
        print_result(desc, success, details)
        tests.append((f"Kelly({odds},{prob})", success))

    # 2. 投注状态
    print("\n  [2] 投注状态查询")
    for period in ["daily", "weekly", "monthly", "overall"]:
        result = await MCP_SERVER.call_tool("get_bet_status", {"period": period})
        success = result.get("success")
        data = result.get("data", {})
        balance = data.get("bankroll", {}).get("balance", 0)
        roi = data.get("bankroll", {}).get("roi", 0)
        details = f"余额: ¥{balance:,.0f} | ROI: {roi*100:.2f}%"
        print_result(f"{period}", success, details)
        tests.append((f"状态({period})", success))

    # 3. 记录投注
    print("\n  [3] 投注记录")
    result = await MCP_SERVER.call_tool("record_bet", {
        "match_id": f"test_{datetime.now().strftime('%H%M%S')}",
        "home_team": "Test Home",
        "away_team": "Test Away",
        "selection": "home",
        "odds": 2.2,
        "stake": 30.0,
        "kelly_fraction": 0.08,
        "confidence": 0.75
    })
    success = result.get("success") and result.get("data", {}).get("success")
    data = result.get("data", {})
    bet_id = data.get("bet_id", "N/A")
    new_balance = data.get("new_balance", 0)
    details = f"ID: {bet_id} | 新余额: ¥{new_balance:,.2f}"
    print_result("新投注记录", success, details)
    tests.append(("投注记录", success))

    # 4. 投注历史
    print("\n  [4] 投注历史")
    result = await MCP_SERVER.call_tool("get_bet_history", {
        "limit": 10,
        "status": "all"
    })
    success = result.get("success")
    data = result.get("data", {})
    bets = data.get("bets", [])
    details = f"共 {len(bets)} 条记录"
    print_result("投注历史", success, details)
    tests.append(("投注历史", success))

    return tests


async def test_search():
    """测试搜索功能"""
    print_header("🔍 搜索功能测试")

    tests = []

    # 1. 网络搜索
    print("\n  [1] 网络搜索")
    queries = [
        ("Premier League odds", "odds"),
        ("Arsenal injury news", "injuries"),
        ("Man City team news", "news"),
    ]
    for query, source in queries:
        result = await MCP_SERVER.call_tool("search_web", {
            "query": query,
            "source": source
        })
        success = result.get("success")
        data = result.get("data", {})
        results = data.get("results", [])
        details = f"来源: {source} | 结果数: {len(results)}"
        print_result(f"搜索: {query[:30]}...", success, details)
        tests.append((f"搜索({source})", success))

    # 2. 记忆搜索
    print("\n  [2] 记忆系统搜索")
    result = await MCP_SERVER.call_tool("search_memory", {
        "query": "betting strategy",
        "limit": 5
    })
    success = result.get("success")
    data = result.get("data", {})
    results = data.get("results", [])
    details = f"找到 {len(results)} 条记忆"
    print_result("记忆搜索", success, details)
    tests.append(("记忆搜索", success))

    return tests


async def test_backtest():
    """测试策略回测"""
    print_header("📈 策略回测测试")

    tests = []

    # 1. 策略比较
    print("\n  [1] 策略比较")
    result = await MCP_SERVER.call_tool("compare_strategies", {
        "league_code": "E0",
        "year": 2024
    })
    success = result.get("success")
    data = result.get("data", {})
    strategies = data.get("strategies", {})
    match_count = data.get("total_matches_tested", 0)

    for name, stats in strategies.items():
        roi = stats.get("roi", "0%")
        wr = stats.get("win_rate", "0%")
        bets = stats.get("total_bets", 0)
        details = f"测试{match_count}场 | 投注{bets}笔 | 胜率{wr} | ROI{roi}"
        print_result(name, success, details)
        tests.append((f"策略({name})", success))

    # 2. 单策略回测
    print("\n  [2] 单策略详细回测")
    for strategy in ["poisson_value", "six_layer", "simple_favorite"]:
        result = await MCP_SERVER.call_tool("backtest_strategy", {
            "strategy_name": strategy,
            "league_code": "E0",
            "year": 2024,
            "use_kelly": True,
            "value_threshold": 0.03
        })
        success = result.get("success")
        data = result.get("data", {})
        roi = data.get("roi", "0%")
        wr = data.get("win_rate", "0%")
        profit = data.get("net_profit", 0)
        details = f"胜率{wr} | ROI{roi} | 盈利¥{profit:.0f}"
        print_result(strategy, success, details)
        tests.append((f"回测({strategy})", success))

    return tests


async def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "AFA v9.0 数据获取能力全面测试" + " " * 16 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Colors.END}")

    # 收集所有测试结果
    all_tests = []

    # 1. 历史数据
    tests = await test_historical_data()
    all_tests.extend(tests)

    # 2. 实时数据
    tests = await test_live_data()
    all_tests.extend(tests)

    # 3. 资金管理
    tests = await test_bankroll()
    all_tests.extend(tests)

    # 4. 搜索功能
    tests = await test_search()
    all_tests.extend(tests)

    # 5. 策略回测
    tests = await test_backtest()
    all_tests.extend(tests)

    # 汇总报告
    print_header("📋 测试结果汇总")

    total = len(all_tests)
    passed = sum(1 for _, s in all_tests if s)
    failed = total - passed

    print(f"\n  总测试数: {total}")
    print(f"  {Colors.GREEN}通过: {passed}{Colors.END}")
    print(f"  {Colors.RED}失败: {failed}{Colors.END}")
    print(f"  通过率: {Colors.BOLD}{(passed/total*100):.1f}%{Colors.END}")

    # 失败列表
    if failed > 0:
        print(f"\n  {Colors.RED}失败项目:{Colors.END}")
        for name, success in all_tests:
            if not success:
                print(f"    - {name}")

    # MCP工具统计
    print_header("🔧 MCP工具统计")
    stats = MCP_SERVER.get_tool_stats()
    print(f"\n  总工具数: {stats['total_tools']}")
    print(f"  总调用次数: {stats['total_usage']}")
    print(f"\n  工具分类:")
    for cat in sorted(set(t.category for t in MCP_SERVER.tools.values())):
        tools = [t.name for t in MCP_SERVER.tools.values() if t.category == cat]
        print(f"    [{cat}]: {len(tools)}个 - {', '.join(tools[:3])}...")

    print("\n" + "="*70)
    print(f"{Colors.GREEN}✅ 测试完成!{Colors.END}")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
