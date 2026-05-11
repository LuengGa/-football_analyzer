# AFA v9 模块索引与导航指南

## 📚 目录概览

本文件为 AFA v9 系统的完整模块索引，帮助开发者快速找到所需的功能模块。

---

## 🎯 核心架构原则

### 单一真实来源 (Single Source of Truth)

- **彩票官方规则**：必须从 `src/calculations/lottery/` 获取
- **禁止硬编码**：任何地方都不能直接定义官方规则（返奖率、最大串关等）

### 模块放置规范

所有计算相关的代码必须放入 `src/calculations/` 的对应子目录，**禁止直接放在根目录**。

---

## 📂 calculations/ 模块索引

### 1. lottery/ - 中国体育彩票官方规则（单一真实来源）

| 文件 | 功能描述 | 主要类/函数 |
|------|----------|-------------|
| `lottery_knowledge.py` | 彩票官方规则知识库（返奖率、玩法、联赛等） | `LotteryKnowledge`, `LOTTERY_KNOWLEDGE` |
| `lottery_queries.py` | 彩票规则查询接口 | `LotteryQuery`, `LOTTERY_QUERY` |
| `lottery_router.py` | 彩票类型路由器（物理隔离竞彩/北单/足彩） | `LotteryRouter` |
| `chinese_lottery_official_calc.py` | 官方奖金计算器 | `ChineseLotteryOfficialCalculator` |
| `lottery_math_engine.py` | 全景概率引擎（泊松分布计算所有玩法） | `LotteryMathEngine` |
| `lottery_league_classifier.py` | 联赛资格分类器 | `LotteryLeagueClassifier` |
| `game_type_manager.py` | 玩法管理器 | - |
| `mxn_calculator.py` | M串N 组合计算器 | - |

**使用示例**：
```python
from src.calculations.lottery import (
    LOTTERY_KNOWLEDGE,
    LOTTERY_QUERY,
    LotteryRouter,
    ChineseLotteryOfficialCalculator
)

# 获取竞彩信息
jingcai = LOTTERY_KNOWLEDGE.get_lottery('JINGCAI')

# 计算奖金
bonus = ChineseLotteryOfficialCalculator.calculate_jingcai_bonus([1.85, 2.1])
```

---

### 2. odds/ - 赔率分析模块

| 文件 | 功能描述 | 主要类/函数 |
|------|----------|-------------|
| `odds_analyzer.py` | 赔率分析器 | - |
| `odds_converter.py` | 赔率转换器 | - |
| `omni_market_pricer.py` | 全能市场定价器 | - |
| `market_probability_engine.py` | 市场概率引擎（从赔率反推概率） | `MarketProbabilityEngine` |
| `bookmaker_analyzer.py` | 庄家分析器 | - |
| `betfair_anomaly.py` | 必发异常检测 | - |

---

### 3. quant/ - 量化分析模块

| 文件 | 功能描述 | 主要类/函数 |
|------|----------|-------------|
| `dixon_coles.py` | Dixon-Coles 预测模型 | - |
| `elo_rating.py` | Elo 评分系统 | - |
| `elo_calibrator.py` | Elo 校准器 | - |
| `elo_storage.py` | Elo 数据存储 | - |
| `elo_update_service.py` | Elo 更新服务 | - |
| `bayesian_updater.py` | 贝叶斯更新器 | - |
| `monte_carlo_simulator.py` | 蒙特卡洛模拟器 | - |
| `kelly_variance_analyzer.py` | 凯利方差分析器 | - |
| `portfolio_optimizer.py` | 投资组合优化器 | - |
| `six_layer_analyzer.py` | 六层分析器 | - |
| `enhanced_six_layer.py` | 增强六层分析器 | - |
| `hardcore_quant_math.py` | 硬核量化数学 | - |
| `advanced_lottery_math.py` | 高级彩票数学 | - |
| `smart_bet_selector.py` | 智能选注器 | - |
| `st_gnn_simulator.py` | ST-GNN 生成式世界模型 | - |
| `anomaly_detector.py` | 异常检测器 | - |
| `trap_identifier.py` | 陷阱识别器 | - |
| `clv_predictor.py` | CLV 预测器 | - |
| `match_value_analyzer.py` | 比赛价值分析器 | - |
| `player_xg_adjuster.py` | 球员 xG 调整器 | - |
| `latency_arbitrage.py` | 时差套利检测器 | - |
| `environment_analyzer.py` | 环境分析器 | - |
| `pre_filter.py` | 比赛初筛过滤器 | `MatchPreFilter` |

---

### 4. backtesting/ - 回测引擎模块

| 文件 | 功能描述 | 主要类/函数 |
|------|----------|-------------|
| `backtest_engine.py` | 回测引擎 | - |
| `capability_matrix_smoke.py` | 能力矩阵冒烟测试 | - |

---

### 5. settlement/ - 结算引擎模块

| 文件 | 功能描述 | 主要类/函数 |
|------|----------|-------------|
| `settlement_engine.py` | 结算引擎 | - |
| `simulated_execution_engine.py` | 模拟执行引擎 | `SimulatedExecutionEngine` |

---

### 6. history/ - 历史数据模块

| 文件 | 功能描述 | 主要类/函数 |
|------|----------|-------------|
| `historical_data_loader.py` | 历史数据加载器 | - |
| `historical_data_manager.py` | 历史数据管理器 | - |
| `historical_impact.py` | 历史影响分析 | - |

---

### 7. math/ - 通用数学工具

| 文件 | 功能描述 | 主要类/函数 |
|------|----------|-------------|
| `dixon_coles_predictor.py` | Dixon-Coles 预测器 | - |
| `elo_rating.py` | Elo 评分 | - |
| `odds_probability.py` | 赔率概率计算 | - |

---

### 8. pro/ - 专业高级模块

| 文件 | 功能描述 | 主要类/函数 |
|------|----------|-------------|
| `advanced_backtest.py` | 高级回测 | - |
| `advanced_features.py` | 高级特征工程 | - |
| `advanced_features_v2.py` | 高级特征工程 V2 | - |
| `advanced_markets.py` | 高级市场分析 | - |
| `dixon_coles_model.py` | Dixon-Coles 模型 | - |
| `domain_models.py` | 领域模型 | - |
| `feature_engineering.py` | 特征工程 | - |
| `kelly_criterion.py` | 凯利准则 | - |
| `ml_predictors.py` | 机器学习预测器 | - |
| `phase2_enhancements.py` | 第二阶段增强 | - |
| `phase3_future.py` | 第三阶段未来规划 | - |
| `poisson_model.py` | 泊松模型 | - |
| `strategy_backtest.py` | 策略回测 | - |
| `team_ratings.py` | 球队评分 | - |
| `value_finder.py` | 价值发现器 | - |
| `visualization.py` | 可视化工具 | - |
| `walk_forward.py` | 滚动向前验证 | - |

---

### 9. utils/ - 工具模块

| 文件 | 功能描述 | 主要类/函数 |
|------|----------|-------------|
| `tool_registry_v2.py` | 工具注册表 V3 | `REGISTRY`, `get_openai_tools()`, `get_mcp_tools()` |

---

## 🔗 其他重要模块

### src/afa_v9/ - AI Agent 系统

| 目录 | 功能描述 |
|------|----------|
| `agents/` | 各种 AI 角色（历史分析、思考等） |
| `memory/` | 记忆系统（短期/长期/语义记忆） |
| `skills/` | Agent 可执行技能 |
| `execution/` | 投注执行、风控 |
| `evolution/` | 进化系统 |
| `ai_augmented/` | AI 增强模块 |
| `data_sources/` | 数据源管理 |
| `langgraph_adapter/` | LangGraph 适配器 |
| `plugins/` | 插件系统 |
| `queue/` | 任务队列 |
| `soul/` | AI 灵魂（目标、人格等） |

### src/tools/ - 工具层

| 目录 | 功能描述 |
|------|----------|
| `odds/` | 赔率抓取与分析 |
| `intel/` | 情报收集（伤停、新闻等） |
| `browser/` | 浏览器自动化工具 |

### src/core/ - 核心基础设施

| 目录 | 功能描述 |
|------|----------|
| `agentic_os/` | Agent 操作系统 |
| `data_pipeline/` | 数据管道 |
| `data_sources/` | 数据源管理 |
| `historical_data/` | 历史数据服务 |
| `llm/` | LLM 服务 |
| `mcp/` | MCP 适配器 |
| `vector_store/` | 向量存储 |

---

## 🚨 常见问题与注意事项

### Q: 新的计算模块应该放在哪里？

A: 根据功能分类放入 `src/calculations/` 的对应子目录：
- 彩票相关 → `lottery/`
- 赔率分析 → `odds/`
- 量化计算 → `quant/`
- 回测 → `backtesting/`
- 结算 → `settlement/`
- 历史数据 → `history/`
- 通用工具 → `utils/`

### Q: 如何访问彩票官方规则？

A: **永远不要硬编码**，请统一使用：
```python
from src.calculations.lottery import LOTTERY_KNOWLEDGE, LOTTERY_QUERY
```

### Q: 如何检查架构是否合规？

A: 运行架构检查脚本：
```bash
python scripts/check_architecture.py
```

### Q: 提交代码时会自动检查架构吗？

A: 是的！pre-commit 钩子会在每次提交和推送时自动运行架构检查。

---

## 📋 快速参考卡片

### 导入速查表

```python
# 彩票官方规则（必须使用这个）
from src.calculations.lottery import (
    LotteryKnowledge,
    LOTTERY_KNOWLEDGE,
    LotteryQuery,
    LOTTERY_QUERY,
    LotteryRouter,
    ChineseLotteryOfficialCalculator
)

# 赔率分析
from src.calculations.odds import MarketProbabilityEngine

# 量化分析
from src.calculations.quant import (
    MatchPreFilter,
    SmartBetSelector
)

# 工具注册表
from src.calculations.utils.tool_registry_v2 import (
    REGISTRY,
    get_openai_tools,
    get_mcp_tools
)
```

---

## 🔄 更新日志

- **2026-XX-XX**：完成深度架构整理，所有模块分类清晰
