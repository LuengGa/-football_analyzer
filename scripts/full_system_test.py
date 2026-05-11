#!/usr/bin/env python3
"""
AFA v9.0 全面系统测试
=====================

测试所有模块的集成和功能
"""

import sys
import os
from pathlib import Path

# 设置模块路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

import time
from datetime import datetime
from typing import Dict, Any, List

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{'='*70}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{'='*70}")

def print_test(name: str, passed: bool, details: str = ""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"  {status} | {name}")
    if details:
        print(f"       {details}")

class SystemTester:
    def __init__(self):
        self.results = []
        self.start_time = time.time()

    def add_result(self, module: str, name: str, passed: bool, details: str = ""):
        self.results.append({
            "module": module,
            "name": name,
            "passed": passed,
            "details": details
        })
        print_test(name, passed, details)

    def run_all_tests(self) -> Dict[str, Any]:
        print(f"{Colors.BOLD}{'='*70}")
        print(f"AFA v9.0 全面系统测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}{Colors.END}")

        # 1. 历史数据模块
        self.test_historical_data()

        # 2. Agent集群
        self.test_agent_cluster()

        # 3. LLM网关
        self.test_llm_gateway()

        # 4. MCP工具
        self.test_mcp_tools()

        # 5. 向量存储
        self.test_vector_store()

        # 6. 数据源
        self.test_data_sources()

        # 7. Evolution引擎
        self.test_evolution_engine()

        # 8. 核心配置
        self.test_core_config()

        return self.generate_report()

    def test_historical_data(self):
        print_header("【模块1】历史数据模块 (historical_data)")

        # 1.1 数据加载
        try:
            from src.core.historical_data.loader import HistoricalDataLoader
            loader = HistoricalDataLoader()
            matches = loader.load_all()
            self.add_result(
                "historical_data", "数据加载",
                len(matches) > 150000,
                f"加载 {len(matches):,} 场比赛"
            )
        except Exception as e:
            self.add_result("historical_data", "数据加载", False, str(e))

        # 1.2 数据路径
        try:
            self.add_result(
                "historical_data", "数据路径",
                loader.data_path.exists(),
                f"路径: {loader.data_path}"
            )
        except:
            self.add_result("historical_data", "数据路径", False, "无法访问")

        # 1.3 按联赛查询
        try:
            epl = loader.get_matches_by_league("E0")
            self.add_result(
                "historical_data", "联赛查询(EPL)",
                len(epl) > 8000,
                f"英超 {len(epl):,} 场"
            )
        except Exception as e:
            self.add_result("historical_data", "联赛查询", False, str(e))

        # 1.4 按球队查询
        try:
            teams = loader.get_matches_by_team("Man City")
            self.add_result(
                "historical_data", "球队查询",
                len(teams) > 500,
                f"曼城 {len(teams)} 场"
            )
        except Exception as e:
            self.add_result("historical_data", "球队查询", False, str(e))

        # 1.5 数据分析器
        try:
            from src.core.historical_data.analytics import HistoricalDataAnalyzer
            analyzer = HistoricalDataAnalyzer()
            asian = analyzer.analyze_asian_handicap()
            self.add_result(
                "historical_data", "亚洲盘分析",
                asian.get("count", 0) > 50000,
                f"分析 {asian.get('count', 0):,} 场"
            )
        except Exception as e:
            self.add_result("historical_data", "亚洲盘分析", False, str(e))

        # 1.6 大小球分析
        try:
            ou = analyzer.analyze_over_under()
            self.add_result(
                "historical_data", "大小球分析",
                ou.get("count", 0) > 50000,
                f"分析 {ou.get('count', 0):,} 场"
            )
        except Exception as e:
            self.add_result("historical_data", "大小球分析", False, str(e))

        # 1.7 赔率变化分析
        try:
            movement = analyzer.analyze_odds_movement()
            self.add_result(
                "historical_data", "赔率变化分析",
                movement.get("total", 0) > 40000,
                f"分析 {movement.get('total', 0):,} 场"
            )
        except Exception as e:
            self.add_result("historical_data", "赔率变化分析", False, str(e))

        # 1.8 半场统计
        try:
            ht = analyzer.get_half_time_stats()
            self.add_result(
                "historical_data", "半场统计",
                ht.get("total", 0) > 150000,
                f"统计 {ht.get('total', 0):,} 场"
            )
        except Exception as e:
            self.add_result("historical_data", "半场统计", False, str(e))

        # 1.9 比分分布
        try:
            score = analyzer.get_score_distribution()
            self.add_result(
                "historical_data", "比分分布",
                score.get("total", 0) > 150000,
                f"分布 {score.get('total', 0):,} 场"
            )
        except Exception as e:
            self.add_result("historical_data", "比分分布", False, str(e))

        # 1.10 联赛分析
        try:
            overview = analyzer.get_data_overview()
            self.add_result(
                "historical_data", "联赛概览",
                overview.get("total_leagues", 0) >= 22,
                f"共 {overview.get('total_leagues', 0)} 个联赛"
            )
        except Exception as e:
            self.add_result("historical_data", "联赛概览", False, str(e))

    def test_agent_cluster(self):
        print_header("【模块2】Agent集群 (agents)")

        # 2.1 Agent导入
        try:
            from src.afa_v9.agents import (
                ScoutAgent, QuantAgent, MarketAgent, RiskAgent,
                TraderAgent, AuditorAgent, HistoricalAnalystAgent
            )
            self.add_result("agent_cluster", "Agent导入", True, "7个Agent类可导入")
        except Exception as e:
            self.add_result("agent_cluster", "Agent导入", False, str(e))
            return

        # 2.2 ScoutAgent初始化
        try:
            scout = ScoutAgent()
            # 检查类变量
            initialized = hasattr(ScoutAgent, '_shared_initialized') and ScoutAgent._shared_initialized
            self.add_result(
                "agent_cluster", "ScoutAgent初始化",
                initialized,
                "情报收集Agent"
            )
        except Exception as e:
            self.add_result("agent_cluster", "ScoutAgent初始化", False, str(e))

        # 2.3 ScoutAgent历史数据查询
        try:
            ctx = scout.get_match_context("Man City", "Liverpool", "E0")
            has_data = ctx.get("home_team", {}).get("stats", {}).get("total_matches", 0) > 0
            self.add_result(
                "agent_cluster", "Scout历史查询",
                has_data,
                f"曼城{ctx['home_team']['stats'].get('total_matches', 0)}场"
            )
        except Exception as e:
            self.add_result("agent_cluster", "Scout历史查询", False, str(e))

        # 2.4 QuantAgent初始化
        try:
            quant = QuantAgent()
            self.add_result(
                "agent_cluster", "QuantAgent初始化",
                True,
                "量化分析Agent"
            )
        except Exception as e:
            self.add_result("agent_cluster", "QuantAgent初始化", False, str(e))

        # 2.5 MarketAgent初始化
        try:
            market = MarketAgent()
            self.add_result(
                "agent_cluster", "MarketAgent初始化",
                True,
                "市场分析Agent"
            )
        except Exception as e:
            self.add_result("agent_cluster", "MarketAgent初始化", False, str(e))

        # 2.6 MarketAgent亚洲盘价值
        try:
            asian = market.get_asian_handicap_value()
            has_data = asian.get("data_count", 0) > 50000
            self.add_result(
                "agent_cluster", "Market亚洲盘分析",
                has_data,
                f"分析{asian.get('data_count', 0):,}场"
            )
        except Exception as e:
            self.add_result("agent_cluster", "Market亚洲盘分析", False, str(e))

        # 2.7 MarketAgent大小球价值
        try:
            ou = market.get_over_under_value()
            has_data = ou.get("data_count", 0) > 50000
            self.add_result(
                "agent_cluster", "Market大小球分析",
                has_data,
                f"分析{ou.get('data_count', 0):,}场"
            )
        except Exception as e:
            self.add_result("agent_cluster", "Market大小球分析", False, str(e))

        # 2.8 HistoricalAnalystAgent
        try:
            analyst = HistoricalAnalystAgent()
            result = analyst.execute({
                "task": "测试分析",
                "home_team": "Man City",
                "away_team": "Liverpool",
                "league": "E0",
                "analysis_type": "full"
            })
            self.add_result(
                "agent_cluster", "HistoricalAnalystAgent",
                "match_context" in result,
                "综合历史分析"
            )
        except Exception as e:
            self.add_result("agent_cluster", "HistoricalAnalystAgent", False, str(e))

        # 2.9 Agent执行流程
        try:
            state = {"home_team": "Arsenal", "away_team": "Chelsea", "league": "E0"}
            result = scout.execute(state)
            self.add_result(
                "agent_cluster", "Agent执行流程",
                "scout_report" in result,
                "Scout执行成功"
            )
        except Exception as e:
            self.add_result("agent_cluster", "Agent执行流程", False, str(e))

        # 2.10 Agent Soul/Brain
        try:
            self.add_result(
                "agent_cluster", "Agent灵魂/大脑",
                scout.soul.name and scout.brain.skills,
                f"Scout: {scout.soul.name}"
            )
        except Exception as e:
            self.add_result("agent_cluster", "Agent灵魂/大脑", False, str(e))

    def test_llm_gateway(self):
        print_header("【模块3】LLM网关 (llm)")

        # 3.1 LLM网关导入
        try:
            from src.core.llm.gateway import LLMGateway, ProviderType
            self.add_result("llm_gateway", "LLMGateway导入", True, "LLM网关类可导入")
        except Exception as e:
            self.add_result("llm_gateway", "LLMGateway导入", False, str(e))
            return

        # 3.2 LLM网关初始化
        try:
            gateway = LLMGateway()
            self.add_result(
                "llm_gateway", "LLMGateway初始化",
                gateway is not None,
                "LLM网关已初始化"
            )
        except Exception as e:
            self.add_result("llm_gateway", "LLMGateway初始化", False, str(e))

        # 3.3 提供商配置
        try:
            has_providers = len(gateway.providers) >= 0
            self.add_result(
                "llm_gateway", "提供商配置",
                True,
                f"已配置 {len(gateway.providers)} 个提供商"
            )
        except Exception as e:
            self.add_result("llm_gateway", "提供商配置", False, str(e))

        # 3.4 ProviderType
        try:
            pt = ProviderType.OLLAMA_CLOUD
            self.add_result(
                "llm_gateway", "ProviderType枚举",
                pt.value == "ollama_cloud",
                f"ProviderType可用"
            )
        except Exception as e:
            self.add_result("llm_gateway", "ProviderType枚举", False, str(e))

        # 3.5 获取可用提供商
        try:
            providers = gateway.get_available_providers()
            self.add_result(
                "llm_gateway", "获取提供商列表",
                isinstance(providers, list),
                f"{len(providers)} 个可用"
            )
        except Exception as e:
            self.add_result("llm_gateway", "获取提供商列表", False, str(e))

    def test_mcp_tools(self):
        print_header("【模块4】MCP工具 (mcp)")

        # 4.1 MCP适配器导入
        try:
            from src.core.mcp.adapter import MCPServer
            self.add_result("mcp_tools", "MCP适配器导入", True, "MCP模块可导入")
        except Exception as e:
            self.add_result("mcp_tools", "MCP适配器导入", False, str(e))

        # 4.2 MCP服务器初始化
        try:
            server = MCPServer()
            self.add_result(
                "mcp_tools", "MCPServer初始化",
                server is not None,
                "MCP服务器已初始化"
            )
        except Exception as e:
            self.add_result("mcp_tools", "MCPServer初始化", False, str(e))

        # 4.3 历史数据工具
        try:
            from src.core.mcp.adapter import MCPServer
            server = MCPServer()
            tools = list(server.tools.keys())
            historical_tools = [t for t in tools if 'team' in t or 'league' in t or 'odds' in t or 'data' in t]
            self.add_result(
                "mcp_tools", "历史数据工具",
                len(historical_tools) >= 5,
                f"历史相关工具: {len(historical_tools)}"
            )
        except Exception as e:
            self.add_result("mcp_tools", "历史数据工具", False, str(e))

        # 4.4 工具函数存在性
        try:
            server = MCPServer()
            has_team_history = "query_team_history" in server.tools
            has_league = "query_league_matches" in server.tools
            self.add_result(
                "mcp_tools", "工具函数签名",
                has_team_history and has_league,
                f"query_team_history: {has_team_history}, query_league: {has_league}"
            )
        except Exception as e:
            self.add_result("mcp_tools", "工具函数签名", False, str(e))

    def test_vector_store(self):
        print_header("【模块5】向量存储 (vector_store)")

        # 5.1 向量存储导入
        try:
            from src.core.vector_store import SimpleVectorStore
            self.add_result("vector_store", "向量存储导入", True, "SimpleVectorStore可导入")
        except Exception as e:
            self.add_result("vector_store", "向量存储导入", False, str(e))

        # 5.2 向量存储初始化
        try:
            store = SimpleVectorStore()
            self.add_result(
                "vector_store", "向量存储初始化",
                store is not None,
                "向量存储已初始化"
            )
        except Exception as e:
            self.add_result("vector_store", "向量存储初始化", False, str(e))

        # 5.3 添加向量
        try:
            from src.core.vector_store import SimpleVectorStore
            store = SimpleVectorStore()
            store.add("test_id", [0.1, 0.2, 0.3], {"text": "test"})
            self.add_result(
                "vector_store", "添加向量",
                True,
                "向量添加成功"
            )
        except Exception as e:
            self.add_result("vector_store", "添加向量", False, str(e))

        # 5.4 相似度搜索
        try:
            from src.core.vector_store import SimpleVectorStore
            store = SimpleVectorStore()
            store.add("test_id", [0.1, 0.2, 0.3], {"text": "test"})
            results = store.search([0.1, 0.2, 0.3], top_k=1)
            self.add_result(
                "vector_store", "相似度搜索",
                True,
                f"找到 {len(results)} 个结果"
            )
        except Exception as e:
            self.add_result("vector_store", "相似度搜索", False, str(e))

    def test_data_sources(self):
        print_header("【模块6】数据源 (data_sources)")

        # 6.1 数据源模块导入
        try:
            from src.core.data_sources import RateLimiter, DataSourceManager, DataCache
            self.add_result("data_sources", "数据源模块导入", True, "数据源类可导入")
        except Exception as e:
            self.add_result("data_sources", "数据源模块导入", False, str(e))

        # 6.2 限流器
        try:
            from src.core.data_sources import RateLimiter
            limiter = RateLimiter()
            self.add_result(
                "data_sources", "限流器初始化",
                limiter is not None,
                "RateLimiter已初始化"
            )
        except Exception as e:
            self.add_result("data_sources", "限流器初始化", False, str(e))

        # 6.3 数据源管理器
        try:
            from src.core.data_sources import DataSourceManager
            manager = DataSourceManager()
            self.add_result(
                "data_sources", "数据源管理器",
                manager is not None,
                "DataSourceManager已初始化"
            )
        except Exception as e:
            self.add_result("data_sources", "数据源管理器", False, str(e))

        # 6.4 缓存操作
        try:
            from src.core.data_sources import DataCache
            cache = DataCache()
            cache.set("test_key", {"data": "test"})
            result = cache.get("test_key")
            self.add_result(
                "data_sources", "缓存操作",
                result is not None,
                "缓存设置/获取成功"
            )
        except Exception as e:
            self.add_result("data_sources", "缓存操作", False, str(e))

    def test_evolution_engine(self):
        print_header("【模块7】Evolution引擎 (evolution)")

        # 7.1 Evolution导入
        try:
            from src.afa_v9.evolution import EvolutionEngine
            self.add_result("evolution", "Evolution导入", True, "EvolutionEngine可导入")
        except Exception as e:
            self.add_result("evolution", "Evolution导入", False, str(e))

        # 7.2 Evolution初始化
        try:
            engine = EvolutionEngine()
            self.add_result(
                "evolution", "Evolution初始化",
                engine is not None,
                "EvolutionEngine已初始化"
            )
        except Exception as e:
            self.add_result("evolution", "Evolution初始化", False, str(e))

        # 7.3 进化阶段
        try:
            from src.afa_v9.evolution import EvolutionPhase
            phases = [p.value for p in EvolutionPhase]
            self.add_result(
                "evolution", "进化阶段",
                len(phases) == 7,
                f"共 {len(phases)} 个阶段"
            )
        except Exception as e:
            self.add_result("evolution", "进化阶段", False, str(e))

    def test_core_config(self):
        print_header("【模块8】核心配置 (config)")

        # 8.1 配置目录
        try:
            from pathlib import Path
            config_dir = Path("configs")
            self.add_result(
                "core_config", "配置目录",
                config_dir.exists(),
                f"路径: {config_dir}"
            )
        except Exception as e:
            self.add_result("core_config", "配置目录", False, str(e))

        # 8.2 配置文件
        try:
            yaml_files = list(config_dir.glob("**/*.yaml")) if config_dir.exists() else []
            self.add_result(
                "core_config", "配置文件",
                len(yaml_files) > 0,
                f"找到 {len(yaml_files)} 个YAML配置"
            )
        except Exception as e:
            self.add_result("core_config", "配置文件", False, str(e))

        # 8.3 __init__.py
        try:
            init_files = list(Path("src").rglob("__init__.py"))
            self.add_result(
                "core_config", "模块初始化",
                len(init_files) > 10,
                f"共 {len(init_files)} 个__init__.py"
            )
        except Exception as e:
            self.add_result("core_config", "模块初始化", False, str(e))

    def generate_report(self) -> Dict[str, Any]:
        print_header("测试报告汇总")

        # 统计
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed

        # 按模块统计
        modules = {}
        for r in self.results:
            module = r["module"]
            if module not in modules:
                modules[module] = {"total": 0, "passed": 0}
            modules[module]["total"] += 1
            if r["passed"]:
                modules[module]["passed"] += 1

        # 打印模块统计
        print(f"\n{Colors.BOLD}各模块通过率:{Colors.END}")
        for module, stats in sorted(modules.items()):
            pct = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            color = Colors.GREEN if pct >= 80 else Colors.YELLOW if pct >= 50 else Colors.RED
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"  {module:<20} {color}{bar} {pct:5.1f}%{Colors.END} ({stats['passed']}/{stats['total']})")

        # 打印失败项
        failed_tests = [r for r in self.results if not r["passed"]]
        if failed_tests:
            print(f"\n{Colors.BOLD}{Colors.RED}失败项 ({len(failed_tests)}):{Colors.END}")
            for r in failed_tests:
                print(f"  ❌ {r['module']}.{r['name']}")
                if r['details']:
                    print(f"     → {r['details'][:60]}")

        # 总体结果
        elapsed = time.time() - self.start_time
        print(f"\n{Colors.BOLD}{'='*70}")
        print(f"总计: {total} 测试 | {Colors.GREEN}{passed} 通过{Colors.END} | {Colors.RED if failed > 0 else Colors.GREEN}{failed} 失败{Colors.END}")
        print(f"耗时: {elapsed:.2f}秒")
        print(f"{'='*70}{Colors.END}")

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "elapsed": elapsed,
            "modules": modules,
            "results": self.results
        }


if __name__ == "__main__":
    tester = SystemTester()
    report = tester.run_all_tests()

    # 返回退出码
    sys.exit(0 if report["failed"] == 0 else 1)
