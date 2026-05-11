"""
AFA Skill Loader — 从 tool_registry_v2 迁移并注册所有技能
"""

from src.afa_v9.skills.registry import (
    SkillRegistry,
    SkillCategory,
    create_skill_from_tool_registry,
    SkillDefinition,
)
from src.calculations.tool_registry_v2 import REGISTRY as TOOL_REGISTRY


def load_all_skills() -> SkillRegistry:
    registry = SkillRegistry()

    # 数据获取类技能
    _register_data_skills(registry)

    # 分析计算类技能
    _register_analysis_skills(registry)

    # 风控识别类技能
    _register_risk_skills(registry)

    # 投注执行类技能
    _register_execution_skills(registry)

    # 情报收集类技能
    _register_intel_skills(registry)

    return registry


def _register_data_skills(registry: SkillRegistry) -> None:
    data_skills = [
        ("fetch_match_data", "获取指定日期的赛程（通过统一数据网关，聚合多源）", ["fixture", "schedule", "j JingCAI", "BEIDAN"]),
        ("fetch_odds", "获取指定比赛的赔率（多源聚合，含百家赔率）", ["odds", "bookmaker", "line"]),
        ("fetch_standings", "获取联赛积分榜/排名", ["standings", "league_table", "ranking"]),
        ("get_today_fixtures", "获取今日在售赛事池（多源聚合）", ["fixtures", "today", "matches"]),
        ("get_live_odds", "获取实时赔率/盘口（多源聚合）", ["live", "inplay", "realtime"]),
    ]

    for name, desc, tags in data_skills:
        if name in TOOL_REGISTRY:
            tool = TOOL_REGISTRY[name]
            skill = create_skill_from_tool_registry(
                name=name,
                description=desc,
                category=SkillCategory.DATA,
                tags=tags,
                schema=tool.model.model_json_schema(),
                executor=tool.func,
            )
            registry.register(skill)


def _register_analysis_skills(registry: SkillRegistry) -> None:
    analysis_skills = [
        ("run_st_gnn_simulator", "在走地(In-Play)或赛前，运行ST-GNN生成式世界模型", ["stgnn", "tactics", "xg", "simulation"]),
        ("calculate_all_markets", "计算所有衍生玩法的理论概率", ["probability", "markets", "calculation"]),
        ("calculate_poisson_probabilities", "泊松分布计算胜平负真实概率", ["poisson", "probability", "xg"]),
        ("deep_evaluate_all_markets", "22万场历史回测引擎，计算所有玩法的打出概率和EV", ["backtest", "ev", "evaluation"]),
        ("run_monte_carlo_simulation", "10万次蒙特卡洛模拟", ["montecarlo", "simulation", "distribution"]),
        ("detect_smart_money", "对比初盘和即时盘，检测聪明资金砸盘方向", ["smart_money", "line_movement", "sharp"]),
        ("analyze_asian_handicap_divergence", "欧亚转换偏差分析，识别诱盘", ["asian", "handicap", "divergence"]),
    ]

    for name, desc, tags in analysis_skills:
        if name in TOOL_REGISTRY:
            tool = TOOL_REGISTRY[name]
            skill = create_skill_from_tool_registry(
                name=name,
                description=desc,
                category=SkillCategory.ANALYSIS,
                tags=tags,
                schema=tool.model.model_json_schema(),
                executor=tool.func,
            )
            registry.register(skill)


def _register_risk_skills(registry: SkillRegistry) -> None:
    risk_skills = [
        ("identify_low_odds_trap", "低赔诱盘识别", ["trap", "low_odds", "chicken"]),
        ("detect_latency_arbitrage", "时差套利扫描", ["arbitrage", "latency", "pinning"]),
        ("detect_betfair_anomaly", "必发资金异常检测", ["betfair", "anomaly", "smart_money"]),
        ("analyze_kelly_variance", "百家赔率离散度分析", ["kelly", "variance", "bookmaker"]),
        ("get_global_arbitrage_data", "外围高阶数据聚合", ["global", "arbitrage", "pinnacle"]),
    ]

    for name, desc, tags in risk_skills:
        if name in TOOL_REGISTRY:
            tool = TOOL_REGISTRY[name]
            skill = create_skill_from_tool_registry(
                name=name,
                description=desc,
                category=SkillCategory.RISK,
                tags=tags,
                schema=tool.model.model_json_schema(),
                executor=tool.func,
            )
            registry.register(skill)


def _register_execution_skills(registry: SkillRegistry) -> None:
    exec_skills = [
        ("calculate_complex_parlay", "M串N复式投注组合计算", ["parlay", "combo", "multi"]),
        ("calculate_chuantong_combinations", "传统足彩复式注数计算", ["chuantong", "traditional", "combination"]),
        ("generate_simulated_ticket", "生成模拟选号单", ["ticket", "simulated", "slip"]),
        ("retrieve_team_memory", "检索球队的长期记忆和核心领悟", ["memory", "history", "team"]),
    ]

    for name, desc, tags in exec_skills:
        if name in TOOL_REGISTRY:
            tool = TOOL_REGISTRY[name]
            skill = create_skill_from_tool_registry(
                name=name,
                description=desc,
                category=SkillCategory.EXECUTION,
                tags=tags,
                schema=tool.model.model_json_schema(),
                executor=tool.func,
            )
            registry.register(skill)


def _register_intel_skills(registry: SkillRegistry) -> None:
    intel_skills = [
        ("fetch_arbitrage_news", "获取毫秒级最新突发新闻", ["news", "arbitrage", "realtime"]),
        ("execute_quant_script", "在隔离环境执行Python量化代码", ["code", "quant", "sandbox"]),
        ("get_league_persona", "获取联赛的战术画像", ["league", "persona", "profile"]),
        ("gather_match_intelligence", "全网动态感知：伤停、天气、突发新闻", ["intelligence", "injury", "weather"]),
        ("get_live_injuries", "获取实时伤停/停赛信息", ["injury", "suspension"]),
        ("search_news", "搜索新闻（多源）", ["news", "search"]),
        ("get_match_result", "查询历史比赛结果", ["result", "history"]),
    ]

    for name, desc, tags in intel_skills:
        if name in TOOL_REGISTRY:
            tool = TOOL_REGISTRY[name]
            skill = create_skill_from_tool_registry(
                name=name,
                description=desc,
                category=SkillCategory.INTEL,
                tags=tags,
                schema=tool.model.model_json_schema(),
                executor=tool.func,
            )
            registry.register(skill)


SKILL_REGISTRY = load_all_skills()

__all__ = [
    "SkillRegistry",
    "SkillCategory",
    "SkillDefinition",
    "SKILL_REGISTRY",
    "load_all_skills",
]
