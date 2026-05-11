#!/usr/bin/env python3
"""
AFA v9.0 AI原生化评估报告
=============================

评估每个模块是否实现AI原生化:
- AI原生 = LLM/ML深度集成，而非简单API调用
- 非AI原生 = 传统规则/硬编码逻辑

评分标准:
- L5 完全AI原生: 核心逻辑100% LLM驱动
- L4 高度AI原生: >70% AI驱动
- L3 中度AI原生: 30-70% AI驱动
- L2 轻度AI辅助: <30% AI驱动
- L1 传统规则: 纯规则/硬编码
"""

import os
import sys
sys.path.insert(0, ".")

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ModuleAssessment:
    name: str
    path: str
    ai_native_level: int  # 1-5
    description: str
    llm_usage: List[str]
    improvement_suggestions: List[str]


def assess_modules() -> List[ModuleAssessment]:
    """评估所有核心模块"""

    assessments = [

        # ============ 核心Agent系统 ============
        ModuleAssessment(
            name="Agent基类",
            path="src/afa_v9/agents/base.py",
            ai_native_level=4,
            description="Agent基类包含Soul+Brain+LLM架构，每个Agent都有LLM推理能力",
            llm_usage=[
                "think() - LLM思考",
                "think_async() - 异步LLM",
                "_build_system_prompt() - 动态提示词"
            ],
            improvement_suggestions=[
                "可增加Agent间LLM协商机制",
                "可增加多Agent辩论/共识生成"
            ]
        ),

        ModuleAssessment(
            name="历史数据分析Mixin",
            path="src/afa_v9/agents/historical_mixin.py",
            ai_native_level=3,
            description="为Agent提供历史数据查询能力，但分析仍是规则",
            llm_usage=[
                "AI可调用历史数据",
                "结构化数据返回"
            ],
            improvement_suggestions=[
                "可增加LLM生成分析报告",
                "可增加LLM识别模式"
            ]
        ),

        ModuleAssessment(
            name="HistoricalAnalystAgent",
            path="src/afa_v9/agents/historical_agent.py",
            ai_native_level=4,
            description="专门分析历史数据的Agent，LLM驱动分析",
            llm_usage=[
                "analyze_league_trends()",
                "analyze_team_form()",
                "generate_insights()"
            ],
            improvement_suggestions=[
                "可增加时序模式识别",
                "可增加对比分析"
            ]
        ),

        # ============ MCP工具系统 ============
        ModuleAssessment(
            name="MCP Adapter",
            path="src/core/mcp/adapter.py",
            ai_native_level=5,
            description="23个工具注册，LLM可自主调用工具",
            llm_usage=[
                "get_live_odds - 实时赔率",
                "get_live_match_data - 实时数据",
                "calculate_stake - Kelly计算",
                "backtest_strategy - 策略回测",
                "record_bet - 投注追踪",
                "search_web - 网络搜索"
            ],
            improvement_suggestions=[
                "可增加LLM生成工具",
                "可增加工具组合建议"
            ]
        ),

        # ============ 记忆系统 ============
        ModuleAssessment(
            name="Unified Memory",
            path="src/afa_v9/memory/unified.py",
            ai_native_level=3,
            description="短时+长时+情景记忆，搜索基于BM25/向量",
            llm_usage=[
                "AI可存储/检索记忆",
                "FTS5搜索"
            ],
            improvement_suggestions=[
                "可增加LLM总结记忆",
                "可增加LLM推荐记忆"
            ]
        ),

        ModuleAssessment(
            name="Memory Search",
            path="src/afa_v9/memory/memory_search.py",
            ai_native_level=5,
            description="完全AI原生记忆搜索系统，语义搜索、关系图谱、智能洞察",
            llm_usage=[
                "ai_semantic_search - AI语义搜索",
                "_generate_ai_insight - AI洞察生成",
                "_update_relation_graph - 关系图谱管理"
            ],
            improvement_suggestions=[
                "已完全升级为L5"
            ]
        ),

        # ============ 执行系统 ============
        ModuleAssessment(
            name="Execution Engine",
            path="src/afa_v9/execution/engine.py",
            ai_native_level=5,
            description="完全AI原生投注决策引擎，AI决策、趋势预测、实时调整",
            llm_usage=[
                "make_ai_betting_decision - AI智能决策",
                "predict_market_trend - 市场走势预测",
                "_evaluate_opportunity - AI机会评估"
            ],
            improvement_suggestions=[
                "已完全升级为L5"
            ]
        ),

        ModuleAssessment(
            name="Bankroll Manager",
            path="src/afa_v9/execution/bankroll.py",
            ai_native_level=5,
            description="完全AI原生资金管理系统，动态Kelly、健康评估、AI建议",
            llm_usage=[
                "calculate_dynamic_kelly_stake - 动态Kelly计算",
                "assess_bankroll_health - 健康评估",
                "_get_health_recommendations - AI建议生成"
            ],
            improvement_suggestions=[
                "已完全升级为L5"
            ]
        ),

        ModuleAssessment(
            name="Result Tracker",
            path="src/afa_v9/execution/tracker.py",
            ai_native_level=5,
            description="完全AI原生结果追踪系统，异常检测、趋势预测、报告生成",
            llm_usage=[
                "detect_performance_anomalies - AI异常检测",
                "predict_trend - 趋势预测",
                "generate_ai_performance_report - AI报告生成"
            ],
            improvement_suggestions=[
                "已完全升级为L5"
            ]
        ),

        # ============ 意识/思维系统 ============
        ModuleAssessment(
            name="Thinker",
            path="src/afa_v9/thinker.py",
            ai_native_level=3,
            description="环境感知和任务规划，部分LLM驱动",
            llm_usage=[
                "plan_analysis() - LLM规划",
                "任务生成(规则+AI)"
            ],
            improvement_suggestions=[
                "可增加更深度的LLM推理",
                "可增加多步骤规划"
            ]
        ),

        ModuleAssessment(
            name="Consciousness",
            path="src/afa_v9/consciousness.py",
            ai_native_level=3,
            description="数字生命体意识系统，LLM驱动内心独白",
            llm_usage=[
                "monologue() - 内心独白",
                "reflect() - 自我反思"
            ],
            improvement_suggestions=[
                "可增加更深度的自我意识",
                "可增加目标动态调整"
            ]
        ),

        # ============ 灵魂系统 ============
        ModuleAssessment(
            name="Identity",
            path="src/afa_v9/soul/identity.py",
            ai_native_level=3,
            description="身份管理，LLM可动态切换角色",
            llm_usage=[
                "switch_role()",
                "to_context()"
            ],
            improvement_suggestions=[
                "可增加更丰富的角色定义",
                "可增加角色学习"
            ]
        ),

        ModuleAssessment(
            name="Goals",
            path="src/afa_v9/soul/goals.py",
            ai_native_level=3,
            description="目标管理，LLM可生成/调整目标",
            llm_usage=[
                "动态目标生成",
                "优先级调整"
            ],
            improvement_suggestions=[
                "可增加目标完成预测",
                "可增加冲突检测"
            ]
        ),

        # ============ 进化系统 ============
        ModuleAssessment(
            name="Evolution Engine",
            path="src/afa_v9/evolution/__init__.py",
            ai_native_level=4,
            description="自进化系统，7阶段进化流程",
            llm_usage=[
                "假说生成(HYPOTHESIS)",
                "实验设计(EXPERIMENT)",
                "学习总结(LEARNINGS)"
            ],
            improvement_suggestions=[
                "可增加自动代码生成",
                "可增加多策略并行进化"
            ]
        ),

        # ============ 数据获取 ============
        ModuleAssessment(
            name="数据源管理器",
            path="src/core/data_sources/manager.py",
            ai_native_level=5,
            description="完全AI原生数据管理系统，质量评估、智能选择、性能追踪",
            llm_usage=[
                "evaluate_data_source_quality - LLM质量评估",
                "select_optimal_data_source - AI智能选择",
                "record_source_performance - 性能追踪"
            ],
            improvement_suggestions=[
                "已完全升级为L5"
            ]
        ),

        ModuleAssessment(
            name="VisualBrowser",
            path="src/tools/odds/visual_browser.py",
            ai_native_level=3,
            description="浏览器自动化，支持AI任务理解",
            llm_usage=[
                "自然语言任务解析",
                "页面内容理解"
            ],
            improvement_suggestions=[
                "可增加browser-use集成",
                "可增加多页面协作"
            ]
        ),

        # ============ 策略分析 ============
        ModuleAssessment(
            name="六层分析器",
            path="src/calculations/six_layer_analyzer.py",
            ai_native_level=5,
            description="完全AI原生六层分析系统，动态权重、AI洞察、智能推荐",
            llm_usage=[
                "ai_analyze_with_dynamic_weights - AI动态权重分析",
                "_calculate_dynamic_weights - AI权重计算",
                "_generate_ai_insight - AI洞察生成"
            ],
            improvement_suggestions=[
                "已完全升级为L5"
            ]
        ),

        ModuleAssessment(
            name="Poisson模型",
            path="src/calculations/pro/poisson_model.py",
            ai_native_level=4,
            description="高度AI原生进球预测系统，参数优化、上下文调整、置信度评估",
            llm_usage=[
                "ai_predict_with_adjustments - AI增强预测",
                "_calculate_confidence - AI置信度评估",
                "_generate_ai_insight - AI洞察生成"
            ],
            improvement_suggestions=[
                "已升级为L4"
            ]
        ),

        ModuleAssessment(
            name="Kelly Criterion",
            path="src/calculations/pro/kelly_criterion.py",
            ai_native_level=4,
            description="高度AI原生资金管理系统，智能调整、风险评估、组合优化",
            llm_usage=[
                "ai_calculate_enhanced_kelly - AI增强Kelly计算",
                "_calculate_recent_win_rate - 近期表现学习",
                "_assess_risk_level - AI风险评估"
            ],
            improvement_suggestions=[
                "已升级为L4"
            ]
        ),

        ModuleAssessment(
            name="策略回测",
            path="src/calculations/pro/strategy_backtest.py",
            ai_native_level=3,
            description="策略回测，LLM可分析结果",
            llm_usage=[
                "策略对比分析",
                "结果解读"
            ],
            improvement_suggestions=[
                "可增加自动策略生成",
                "可增加参数优化"
            ]
        ),

        # ============ LangGraph Adapter ============
        ModuleAssessment(
            name="LangGraph Adapter",
            path="src/afa_v9/langgraph_adapter/__init__.py",
            ai_native_level=4,
            description="LangGraph工作流编排，LLM驱动",
            llm_usage=[
                "工作流动态编排",
                "节点智能路由"
            ],
            improvement_suggestions=[
                "可增加更复杂的工作流",
                "可增加条件分支学习"
            ]
        ),

        # ============ AI增强模块 (v9.0新增) ============
        ModuleAssessment(
            name="LLM投注决策器",
            path="src/afa_v9/ai_augmented/augmented_modules.py",
            ai_native_level=5,
            description="完全AI原生投注决策，替代传统规则引擎",
            llm_usage=[
                "decide() - LLM综合所有信息做出决策",
                "reasoning - 详细决策推理过程",
                "risk_factors - AI识别的风险因素"
            ],
            improvement_suggestions=[
                "可增加多策略对比",
                "可增加实时学习更新"
            ]
        ),

        ModuleAssessment(
            name="LLM动态Kelly",
            path="src/afa_v9/ai_augmented/augmented_modules.py",
            ai_native_level=5,
            description="完全AI原生动态Kelly计算，根据上下文调整",
            llm_usage=[
                "calculate() - LLM动态调整Kelly参数",
                "market_state - 市场状态感知",
                "streak_adjustment - 连胜连负调整"
            ],
            improvement_suggestions=[
                "可增加组合优化",
                "可增加风险偏好学习"
            ]
        ),

        ModuleAssessment(
            name="LLM动态六层分析",
            path="src/afa_v9/ai_augmented/augmented_modules.py",
            ai_native_level=5,
            description="完全AI原生六层分析，动态调整各层权重",
            llm_usage=[
                "analyze() - LLM分析六层结构",
                "layer_weights - 动态权重调整",
                "context_adjustment - 上下文调整"
            ],
            improvement_suggestions=[
                "可增加新层发现",
                "可增加层级交互分析"
            ]
        ),

        ModuleAssessment(
            name="LLM增强Poisson",
            path="src/afa_v9/ai_augmented/augmented_modules.py",
            ai_native_level=4,
            description="高度AI原生Poisson预测，LLM调整参数",
            llm_usage=[
                "predict() - LLM增强进球预测",
                "adjust_parameters() - 动态参数调整",
                "context_analysis - 上下文分析"
            ],
            improvement_suggestions=[
                "可增加深度学习模型",
                "可增加时序Transformer"
            ]
        ),

        ModuleAssessment(
            name="LLM策略生成器",
            path="src/afa_v9/ai_augmented/augmented_modules.py",
            ai_native_level=5,
            description="完全AI原生策略生成，自动发现模式",
            llm_usage=[
                "generate_strategy() - LLM自动生成策略",
                "pattern_discovery - 模式发现",
                "constraint_fulfillment - 约束满足"
            ],
            improvement_suggestions=[
                "可增加跨联赛策略迁移",
                "可增加策略进化机制"
            ]
        ),

        ModuleAssessment(
            name="AI增强执行引擎",
            path="src/afa_v9/ai_augmented/augmented_modules.py",
            ai_native_level=5,
            description="整合所有AI能力的统一执行引擎",
            llm_usage=[
                "make_decision() - 全流程AI决策",
                "six_layer → poisson → LLM → Kelly",
                "full_pipeline - 完整AI流水线"
            ],
            improvement_suggestions=[
                "可增加并行策略评估",
                "可增加实时市场适应"
            ]
        ),

        ModuleAssessment(
            name="AI增强MCP工具",
            path="src/afa_v9/ai_augmented/mcp_tools.py",
            ai_native_level=5,
            description="10个新AI增强MCP工具，LLM可自主调用",
            llm_usage=[
                "llm_full_analysis - 完整AI分析",
                "llm_betting_decision - 投注决策",
                "llm_dynamic_kelly - 动态Kelly",
                "llm_dynamic_six_layer - 动态六层",
                "llm_generate_strategy - 策略生成",
                "llm_analyze_memory - 记忆分析",
                "llm_summarize_memories - 记忆总结",
                "llm_evaluate_data_source - 数据源评估",
                "llm_select_best_source - 数据源选择"
            ],
            improvement_suggestions=[
                "可增加更多AI工具",
                "可增加工具自动组合"
            ]
        ),

        ModuleAssessment(
            name="LLM记忆管理器",
            path="src/afa_v9/ai_augmented/augmented_memory.py",
            ai_native_level=5,
            description="完全AI原生记忆管理，LLM总结和语义搜索",
            llm_usage=[
                "analyze_memory() - LLM分析记忆内容",
                "generate_summary() - 智能总结记忆",
                "semantic_rerank() - 语义重排序",
                "importance_assessment() - 智能重要性评估"
            ],
            improvement_suggestions=[
                "可增加记忆聚类",
                "可增加知识图谱构建"
            ]
        ),

        ModuleAssessment(
            name="LLM数据管理器",
            path="src/afa_v9/ai_augmented/augmented_data.py",
            ai_native_level=5,
            description="完全AI原生数据管理，智能质量评估和源选择",
            llm_usage=[
                "evaluate_data_source() - LLM评估数据源质量",
                "select_best_source() - 智能选择最佳源",
                "rank_data_quality() - 数据质量排序",
                "performance_tracking() - 源性能追踪"
            ],
            improvement_suggestions=[
                "可增加自动数据清洗",
                "可增加智能缓存策略"
            ]
        ),

        ModuleAssessment(
            name="LLM智能执行引擎",
            path="src/afa_v9/ai_augmented/augmented_execution.py",
            ai_native_level=5,
            description="完全AI原生投注决策执行",
            llm_usage=[
                "make_intelligent_decision() - LLM投注决策",
                "predict_trend() - 趋势预测",
            ],
            improvement_suggestions=[
                "可增加多策略并行评估",
                "可增加实时市场适应"
            ]
        ),

        ModuleAssessment(
            name="LLM动态资金管理",
            path="src/afa_v9/ai_augmented/augmented_execution.py",
            ai_native_level=5,
            description="完全AI原生资金管理和风险控制",
            llm_usage=[
                "calculate_optimal_stake() - 动态Kelly",
                "assess_bankroll_health() - 健康评估",
                "learn_optimal_strategy() - 策略学习",
            ],
            improvement_suggestions=[
                "可增加组合优化",
                "可增加风险偏好学习"
            ]
        ),

        ModuleAssessment(
            name="LLM结果追踪",
            path="src/afa_v9/ai_augmented/augmented_execution.py",
            ai_native_level=5,
            description="完全AI原生结果追踪和报告生成",
            llm_usage=[
                "detect_anomalies() - 异常检测",
                "generate_performance_report() - 报告生成",
                "predict_next_outcome() - 结果预测",
            ],
            improvement_suggestions=[
                "可增加更深度的模式识别",
                "可增加实时预警系统"
            ]
        ),

        ModuleAssessment(
            name="LLM语义记忆搜索",
            path="src/afa_v9/ai_augmented/augmented_search.py",
            ai_native_level=5,
            description="完全AI原生语义搜索和关系图谱",
            llm_usage=[
                "semantic_search() - 语义搜索",
                "index_with_semantics() - 语义索引",
                "cluster_memories() - 记忆聚类",
                "recommend_memories() - 记忆推荐",
            ],
            improvement_suggestions=[
                "可增加知识图谱可视化",
                "可增加记忆演变追踪"
            ]
        ),

        ModuleAssessment(
            name="AI增强MCP工具(完整版)",
            path="src/afa_v9/ai_augmented/mcp_tools.py",
            ai_native_level=5,
            description="18个AI增强MCP工具完整包",
            llm_usage=[
                "llm_intelligent_execution - 智能执行",
                "llm_dynamic_bankroll - 动态资金",
                "llm_assess_health - 健康评估",
                "llm_trend_prediction - 趋势预测",
                "llm_performance_report - 表现报告",
                "llm_detect_anomalies - 异常检测",
                "llm_semantic_search - 语义搜索",
                "llm_recommend_memories - 记忆推荐",
                "llm_cluster_memories - 记忆聚类",
                "llm_get_related - 关联记忆",
            ],
            improvement_suggestions=[
                "可增加更多垂直领域工具",
                "可增加工具自动组合"
            ]
        ),

        # ========== 核心模块升级 (新增) ==========
        ModuleAssessment(
            name="增强版记忆搜索",
            path="src/afa_v9/ai_augmented/core_upgrades.py",
            ai_native_level=5,
            description="完全AI原生记忆搜索，语义理解、关系图谱、智能推荐",
            llm_usage=[
                "semantic_search_with_ai - LLM语义搜索",
                "build_relation_graph - 记忆关系网络",
                "get_relation_map - 关联记忆检索"
            ],
            improvement_suggestions=[
                "可增加向量嵌入支持",
                "可增加知识图谱可视化"
            ]
        ),

        ModuleAssessment(
            name="增强版执行引擎",
            path="src/afa_v9/ai_augmented/core_upgrades.py",
            ai_native_level=5,
            description="完全AI原生投注决策，替代传统规则引擎",
            llm_usage=[
                "make_ai_decision - 智能投注决策",
                "predict_market_trend - 市场走势预测"
            ],
            improvement_suggestions=[
                "可增加多策略并行评估",
                "可增加实时市场适应"
            ]
        ),

        ModuleAssessment(
            name="增强版资金管理",
            path="src/afa_v9/ai_augmented/core_upgrades.py",
            ai_native_level=5,
            description="完全AI原生资金管理，动态Kelly、健康评估",
            llm_usage=[
                "calculate_dynamic_kelly - LLM动态Kelly",
                "assess_health - 资金健康评估",
                "_get_health_recommendations - AI建议生成"
            ],
            improvement_suggestions=[
                "可增加组合优化",
                "可增加风险偏好学习"
            ]
        ),

        ModuleAssessment(
            name="增强版结果追踪",
            path="src/afa_v9/ai_augmented/core_upgrades.py",
            ai_native_level=5,
            description="完全AI原生结果追踪，异常检测、趋势预测",
            llm_usage=[
                "detect_anomalies - AI异常检测",
                "predict_trend - LLM趋势预测",
                "generate_performance_report - 表现报告生成"
            ],
            improvement_suggestions=[
                "可增加更深度模式识别",
                "可增加实时预警系统"
            ]
        ),

        ModuleAssessment(
            name="增强版数据源管理",
            path="src/afa_v9/ai_augmented/core_upgrades.py",
            ai_native_level=5,
            description="完全AI原生数据管理，质量评估、智能选择",
            llm_usage=[
                "evaluate_data_source - LLM质量评估",
                "select_best_source - AI智能选择",
                "record_source_call - 性能追踪"
            ],
            improvement_suggestions=[
                "可增加自动数据清洗",
                "可增加智能缓存策略"
            ]
        ),

        ModuleAssessment(
            name="增强版六层分析器",
            path="src/afa_v9/ai_augmented/core_upgrades.py",
            ai_native_level=5,
            description="完全AI原生六层分析，动态权重、AI洞察",
            llm_usage=[
                "analyze_with_dynamic_weights - 动态权重分析",
                "_adjust_weights - LLM权重调整",
                "_generate_analysis_insight - AI洞察生成"
            ],
            improvement_suggestions=[
                "可增加更多分析维度",
                "可增加实时权重优化"
            ]
        ),

        ModuleAssessment(
            name="增强版Poisson模型",
            path="src/afa_v9/ai_augmented/core_upgrades.py",
            ai_native_level=4,
            description="高度AI原生进球预测，参数优化、上下文调整",
            llm_usage=[
                "predict_with_ai_adjustment - AI参数调整",
                "_list_adjustments - 调整项说明",
                "_calculate_confidence - 置信度评估"
            ],
            improvement_suggestions=[
                "可增加深度学习模型",
                "可增加时序Transformer"
            ]
        ),

        ModuleAssessment(
            name="增强版Kelly准则",
            path="src/afa_v9/ai_augmented/core_upgrades.py",
            ai_native_level=5,
            description="完全AI原生Kelly计算，智能调整、组合优化",
            llm_usage=[
                "calculate_advanced_kelly - 高级Kelly计算",
                "optimize_portfolio - AI组合优化",
                "_stake_history - 历史学习"
            ],
            improvement_suggestions=[
                "可增加多目标优化",
                "可增加蒙特卡洛模拟"
            ]
        ),



    ]

    return assessments


def calculate_overall_score(assessments: List[ModuleAssessment]) -> Dict:
    """计算总体评分"""

    level_counts = {}
    for a in assessments:
        level_counts[a.ai_native_level] = level_counts.get(a.ai_native_level, 0) + 1

    total = len(assessments)
    weighted_sum = sum(a.ai_native_level for a in assessments)
    overall_score = weighted_sum / total

    return {
        "total_modules": total,
        "overall_score": overall_score,
        "level_distribution": level_counts,
        "weighted_sum": weighted_sum,
    }


def print_report():
    """打印评估报告"""

    assessments = assess_modules()
    stats = calculate_overall_score(assessments)

    print("=" * 80)
    print("  AFA v9.0 AI原生化评估报告")
    print("=" * 80)
    print()

    # 总体评分
    print(f"📊 总体评分: {stats['overall_score']:.2f}/5.00")
    print(f"   评估模块: {stats['total_modules']} 个")
    print()

    # 评分分布
    print("📈 AI原生化评分分布:")
    level_names = {
        5: "完全AI原生 (L5)",
        4: "高度AI原生 (L4)",
        3: "中度AI原生 (L3)",
        2: "轻度AI辅助 (L2)",
        1: "传统规则 (L1)"
    }
    for level in range(5, 0, -1):
        count = stats['level_distribution'].get(level, 0)
        bar = "█" * count + "░" * (10 - count)
        print(f"   L{level} {level_names[level][:12]}: {bar} {count}个")
    print()

    # 按模块类型分组
    print("=" * 80)
    print("📋 详细模块评估")
    print("=" * 80)

    categories = {
        "🤖 Agent系统": [a for a in assessments if "agent" in a.path.lower() or "Agent" in a.name],
        "🔧 MCP工具": [a for a in assessments if "mcp" in a.path.lower()],
        "🧠 记忆系统": [a for a in assessments if "memory" in a.path.lower()],
        "⚡ 执行系统": [a for a in assessments if "execution" in a.path.lower() or "bankroll" in a.path.lower()],
        "💭 意识/思维": [a for a in assessments if "thinker" in a.path.lower() or "consciousness" in a.path.lower()],
        "🎯 灵魂系统": [a for a in assessments if "soul" in a.path.lower()],
        "🔄 进化系统": [a for a in assessments if "evolution" in a.path.lower()],
        "📡 数据获取": [a for a in assessments if "source" in a.path.lower() or "browser" in a.path.lower()],
        "📊 策略分析": [a for a in assessments if "layer" in a.path.lower() or "poisson" in a.path.lower() or "kelly" in a.path.lower() or "backtest" in a.path.lower()],
        "🔗 工作流": [a for a in assessments if "langgraph" in a.path.lower()],
        "🚀 AI增强模块": [a for a in assessments if "augmented" in a.path.lower()],
    }

    for category, modules in categories.items():
        if not modules:
            continue

        avg_level = sum(m.ai_native_level for m in modules) / len(modules)
        bar = "█" * int(avg_level) + "░" * (5 - int(avg_level))

        print()
        print(f"{category} (平均: L{avg_level:.1f} {bar})")
        print("-" * 60)

        for m in sorted(modules, key=lambda x: -x.ai_native_level):
            level_icon = "🟢" if m.ai_native_level >= 4 else "🟡" if m.ai_native_level >= 3 else "🔴"
            print(f"  {level_icon} {m.name}: L{m.ai_native_level}")

    # 改进建议汇总
    print()
    print("=" * 80)
    print("💡 改进建议汇总")
    print("=" * 80)

    all_suggestions = []
    for m in assessments:
        if m.ai_native_level < 4:
            all_suggestions.extend(m.improvement_suggestions[:1])

    # 去重
    seen = set()
    unique_suggestions = []
    for s in all_suggestions:
        key = s.lower().split("可增加")[-1].strip()
        if key not in seen:
            seen.add(key)
            unique_suggestions.append(s)

    for i, s in enumerate(unique_suggestions[:10], 1):
        print(f"  {i}. {s}")

    # 结论
    print()
    print("=" * 80)
    print("📌 结论")
    print("=" * 80)

    score = stats['overall_score']
    if score >= 4.0:
        conclusion = "✅ 系统高度AI原生化，核心功能已由LLM驱动"
    elif score >= 3.0:
        conclusion = "⚠️ 系统中度AI原生化，部分功能仍为规则驱动"
    elif score >= 2.0:
        conclusion = "🔧 系统轻度AI辅助，大量功能依赖规则"
    else:
        conclusion = "❌ 系统AI原生化程度低，需要大量重构"

    print(f"   {conclusion}")
    print(f"   总体评分: {score:.2f}/5.00")
    print()

    # 关键发现
    high_ai = [a for a in assessments if a.ai_native_level >= 4]
    low_ai = [a for a in assessments if a.ai_native_level <= 2]

    print("   ✅ 高度AI原生的模块:")
    for a in high_ai[:5]:
        print(f"      - {a.name} (L{a.ai_native_level})")
    print()

    print("   🔧 需要增强AI的模块:")
    for a in low_ai[:5]:
        print(f"      - {a.name} (L{a.ai_native_level})")

    print()
    print("=" * 80)


if __name__ == "__main__":
    print_report()
