# AFA v9 项目架构规范

## 📋 目录概述

这个文档定义了项目的架构规范，确保所有代码都能被正确地组织。

---

## 📁 目录结构

```
football_analyzer/
├── src/                          # 源代码目录
│   ├── afa_v9/                   # AFA v9 AI Agent 系统
│   ├── calculations/              # 计算层（纯数学、无状态）
│   ├── config/                    # 配置加载器
│   ├── core/                      # 核心基础设施
│   ├── tools/                     # 工具层（网络抓取、浏览器等）
│   └── cli/                       # 命令行入口
├── scripts/                       # 辅助脚本
├── data/                          # 数据目录
├── docs/                          # 文档
├── tests/                         # 测试
└── archive/                       # 旧版代码存档
```

---

## 🎯 模块放置规范

### ✅ 单一真实来源原则

**所有官方规则和配置必须从统一入口访问，禁止零散定义。**

### 1. **彩票官方规则** (单一真实来源)

**⚠️ 只放这里：** `src/calculations/lottery/`

**禁止：** 任何地方直接复制粘贴官方规则数据。

**怎么访问：**

```python
# 方式1：直接访问官方规则（程序化使用）
from src.calculations.lottery import (
    LOTTERY_KNOWLEDGE,  # 官方规则
    LOTTERY_QUERY,      # 查询接口
)

jingcai = LOTTERY_KNOWLEDGE.get_lottery('JINGCAI')
beidan = LOTTERY_KNOWLEDGE.get_lottery('BEIDAN')

bonus = LOTTERY_QUERY.calculate_bonus('JINGCAI', [1.85, 2.1])

# 方式2：通过语义记忆查询（自然语言接口，给LLM使用）
from src.afa_v9.memory import UnifiedMemory
memory = UnifiedMemory()

# 自然语言查询规则
rules = memory.query_rules("竞彩返奖率是多少？")
rules = memory.query_rules("北单的上下单双玩法是什么？")

# 或者直接使用语义记忆
from src.afa_v9.memory.semantic import get_lottery_semantic_memory
semantic = get_lottery_semantic_memory()
results = semantic.query("胜平负玩法有哪些选项？")
```

### 2. **计算层** (`src/calculations/`)

| 模块 | 说明 | 放哪里 |
|------|------|--------|
| 彩票官方规则 | 竞彩/北单玩法、赔率、返奖率 | `lottery/` |
| 量化计算 | Elo、Bayesian、Kelly 等 | `quant/` |
| 赔率分析 | 赔率转换、定价 | `odds/` |
| 回测引擎 | 策略回测 | `backtesting/` |
| 结算引擎 | 投注结算 | `settlement/` |
| 数学工具 | 通用数学 | `math/` |
| 专业计算 | 复杂分析 | `pro/` |

### 3. **AI Agent 系统** (`src/afa_v9/`)

| 模块 | 说明 | 放哪里 |
|------|------|--------|
| Agents | 各种 AI 角色 | `agents/` |
| 记忆 | 短期/长期记忆系统 | `memory/` |
| 技能 | Agent 可执行的技能 | `skills/` |
| 执行 | 投注执行、风控 | `execution/` |
| 回测 | Agent 回测 | `backtest.py` |

### 4. **工具层** (`src/tools/`)

| 模块 | 说明 |
|------|------|
| 赔率抓取 | 抓取竞彩/北单赔率 | `odds/` |
| 情报抓取 | 足球情报数据 | `intel/` |
| 浏览器工具 | 浏览器自动化 | `browser/` |

---

## 🧠 语义记忆系统

### 1. **官方规则的语义化存储**

官方规则现在以两种方式存储：

| 存储方式 | 位置 | 用途 |
|---------|------|------|
| 结构化数据 | `src/calculations/lottery/` | 程序化使用、计算、验证 |
| 语义化知识 | `src/afa_v9/memory/semantic/` | LLM自然语言查询、问答 |

### 2. **语义记忆架构**

```
src/afa_v9/memory/
├── __init__.py          # 统一记忆系统接口
└── semantic/
    ├── __init__.py      # 语义记忆模块
    └── lottery_knowledge.py  # 彩票规则语义记忆
```

### 3. **知识块结构**

每个规则被转换为 `RuleChunk` 对象，包含：

- **id**: 唯一标识符
- **content**: 自然语言描述的规则内容
- **category**: 分类（jingcai/beidan/general）
- **play_type**: 玩法类型（可选）
- **metadata**: 元数据
- **importance**: 重要性（0-1）

---

## 🚫 禁止行为

1. **❌ 禁止在代码中硬编码官方规则**
2. **❌ 禁止复制粘贴官方规则数据**
3. **❌ 禁止创建新的 Agent 系统或计算引擎**
4. **❌ 禁止在 `src/` 根目录下创建新文件夹**

---

## 🔍 如何检查架构

```bash
# 运行架构检查
python scripts/check_architecture.py
```
