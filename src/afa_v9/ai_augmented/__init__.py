"""
AFA v9.x AI增强模块
=====================

AI原生化升级模块，让传统规则驱动的模块具备LLM能力:

1. LLMBettingDecider - LLM投注决策
2. LLMDynamicKelly - 动态Kelly
3. LLMDynamicSixLayer - 动态六层分析
4. LLMEnhancedPoisson - 增强Poisson预测
5. LLMStrategyGenerator - 自动策略生成
6. AIAugmentedExecutionEngine - 统一执行引擎

真实历史数据驱动的AI原生模块 (新增):
7. CompleteAINativeSystem - 完全AI原生系统
8. AIHistoricalDatabase - AI原生历史数据库
9. AIPatternDiscoverer - AI模式发现引擎
10. AINativePoissonModel - AI原生Poisson预测

规则驱动AI决策系统 (深度优化):
11. RulesDrivenDecider - 官方规则驱动的AI决策
12. RuleContext - 规则决策上下文

MCP工具 (新增):
13. AI_AUGMENTED_MCP - AI增强MCP工具集
14. llm_full_analysis - 便捷的完整AI分析
15. rules_driven_full_analysis - 基于官方规则的完整分析
"""

from .augmented_modules import (
    LLMBettingDecider,
    LLMDynamicKelly,
    LLMDynamicSixLayer,
    LLMEnhancedPoisson,
    LLMStrategyGenerator,
    AIAugmentedExecutionEngine,
    LLM_DECIDER,
    LLM_DYNAMIC_KELLY,
    LLM_SIX_LAYER,
    LLM_POISSON,
    LLM_STRATEGY_GEN,
    AUGMENTED_ENGINE,
)

from .ai_native_historical import (
    CompleteAINativeSystem,
    AIHistoricalDatabase,
    AIPatternDiscoverer,
    AIPredictorEnhancer,
    AI_NATIVE_SYSTEM,
)

from .ai_native_poisson import (
    AINativePoissonModel,
    AIPredictionContext,
    AIPredictionResult,
    AI_NATIVE_POISSON_MODEL,
)

from .rules_driven_decision import (
    RulesDrivenDecider,
    RuleContext,
    RULES_DECIDER,
    get_rules_driven_decider,
)

from .mcp_tools import (
    AI_AUGMENTED_MCP,
    llm_full_analysis,
    rules_driven_full_analysis,
)

__all__ = [
    "LLMBettingDecider",
    "LLMDynamicKelly",
    "LLMDynamicSixLayer",
    "LLMEnhancedPoisson",
    "LLMStrategyGenerator",
    "AIAugmentedExecutionEngine",
    "LLM_DECIDER",
    "LLM_DYNAMIC_KELLY",
    "LLM_SIX_LAYER",
    "LLM_POISSON",
    "LLM_STRATEGY_GEN",
    "AUGMENTED_ENGINE",
    "CompleteAINativeSystem",
    "AIHistoricalDatabase",
    "AIPatternDiscoverer",
    "AIPredictorEnhancer",
    "AI_NATIVE_SYSTEM",
    "AINativePoissonModel",
    "AIPredictionContext",
    "AIPredictionResult",
    "AI_NATIVE_POISSON_MODEL",
    # 新增规则驱动AI决策
    "RulesDrivenDecider",
    "RuleContext",
    "RULES_DECIDER",
    "get_rules_driven_decider",
    # 新增 MCP 工具
    "AI_AUGMENTED_MCP",
    "llm_full_analysis",
    "rules_driven_full_analysis",
]
