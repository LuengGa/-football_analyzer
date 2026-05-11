# Agentic Football Analyzer (AFA)

**AI原生足球量化分析数字生命体**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 项目简介

AFA 是一个 AI 原生的足球量化分析数字生命体，通过三层架构实现：

- **意识层** - SOUL + IDENTITY 定义人格和身份
- **工具层** - MCP 服务器提供数学计算引擎
- **生命层** - Memory + Heartbeat 实现持续运行和经验积累

**核心特性**:
- 🧠 **ELO 评分系统** - 球队实力动态评级
- 📊 **Dixon-Coles 模型** - 泊松比分预测
- 🎯 **Kelly 公式** - 最优投注比例计算
- 🔄 **价值投注识别** - 多模型综合分析
- 📝 **持续学习** - 每日复盘和经验积累

---

## 🏗️ 系统架构

### AFA 独立 Agent 系统（当前实现）

```
┌─────────────────────────────────────────────────────────────────┐
│                    AFA 数字生命体                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              AFA Orchestrator (协调器)                   │  │
│  │                   核心大脑                                │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Scout       │  │  Analyst     │  │  (更多...)  │  │
│  │  情报探员   │  │  分析师      │  │             │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Sportsipy 数据源 & 本地缓存                   │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Memory (记忆系统)                           │   │
│  │  每日分析记录 │ Elo历史 │ 投注台账 │ 复盘知识库      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 经典三层架构（原始设计）

```
┌─────────────────────────────────────────────────────────┐
│                    Digital Life                          │
│                    (数字生命体)                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Identity    │  │  Tools       │  │  Life       │  │
│  │  意识层     │  │  工具层      │  │  生命层     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│  ELO/Dixon-Coles/Kelly/Monte Carlo  计算引擎           │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
football_analyzer/
├── 🧠 identity/               # 数字生命体配置
│   ├── SOUL.md               # 人格定义
│   ├── IDENTITY.md           # 身份定义
│   └── HEARTBEAT.md          # 定时任务
├── 🔧 tools/                  # 工具和脚本
│   ├── afa_mcp_server.py     # MCP 工具服务器
│   ├── afa_cli.py            # CLI 工具
│   ├── afa_daily_report.py   # 每日报告生成
│   ├── afa_toolkit.py        # 工具包
│   └── test_afa_tools.py     # 工具测试
├── 📝 memory/                 # 每日记录和记忆
│   └── 2026-05-06.md
├── 💾 data/                   # 数据存储
│   ├── elo_ratings.json      # Elo 评分数据库
│   └── test_dbs/             # 测试数据库
├── 📦 src/                    # 核心代码库
│   ├── calculations/         # 数学计算模块
│   ├── agents/               # Agent 基础
│   └── core/                 # 核心功能
├── 🤖 agents/                 # Agent 配置
├── 📚 docs/                   # 项目文档
│   ├── AFA_ACTIVATION_GUIDE.md
│   └── archive/              # 历史文档
├── ⚙️  configs/               # 配置文件
├── 🔩 scripts/                # 运维脚本
├── 🧪 tests/                  # 测试套件
├── 🎫 tickets/                # 投注记录
├── pyproject.toml            # 项目配置
├── .env.example             # 环境变量示例
└── README.md                 # 本文件
```

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- DeepSeek API密钥 或 OpenAI API密钥（可选）

### 安装步骤

```bash
# 1. 进入项目目录
cd football_analyzer

# 2. 安装依赖
pip install -e .

# 3. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 测试系统（推荐）

```bash
# 运行完整的 AFA Agent 系统测试
python3 tools/test_afa_system.py
```

### 使用 AFA Orchestrator（主要方式）

```python
from src.agents.afa.orchestrator import AFAOrchestrator

# 1. 创建协调器（激活 AFA）
afa = AFAOrchestrator()

# 2. 获取即将进行的比赛
matches = afa.get_upcoming_matches(league="Premier League", days=7)
print(f"找到 {len(matches)} 场比赛")

# 3. 分析一场比赛
report = afa.analyze_match(
    home_team="Arsenal",
    away_team="Chelsea",
    odds_home=1.85,
    odds_draw=3.40,
    odds_away=4.20
)

# 4. 查看分析报告
print(report["summary"])

# 5. 查看更详细的分析
print(f"Elo评分: 阿森纳 {report['analysis']['elo_ratings']['home']}, 切尔西 {report['analysis']['elo_ratings']['away']}")
print(f"胜率预测: 阿森纳胜 {report['analysis']['predictions']['win_prob_home']:.1%}")
print(f"凯利公式: {report['analysis']['kelly']['simplified']}")
```

### 查看分析历史

AFA 会自动保存每一次分析结果到 `memory/` 目录下，作为数字生命体的记忆。

---

## 🛠️ 核心工具

| 工具 | 功能 |
|------|------|
| `elo_calculate` | ELO 评分计算与更新 |
| `dixon_coles_predict` | Dixon-Coles 泊松比分预测 |
| `kelly_analyze` | 凯利公式投注分析 |
| `odds_implied_probabilities` | 赔率隐含概率计算 |
| `comprehensive_match_analysis` | 综合比赛分析报告 |

---

## 📖 更多文档

- **[AFA_ACTIVATION_GUIDE.md](docs/AFA_ACTIVATION_GUIDE.md)** - 数字生命体激活指南
- **[历史文档](docs/archive/)** - 项目历史和架构设计

---

## 🔒 安全注意事项

⚠️ **重要**: 请勿将`.env`文件提交到Git仓库！

1. `.env`文件已在`.gitignore`中排除
2. 如不慎提交，请立即撤销API密钥并重新生成
3. 使用密钥管理服务（如HashiCorp Vault）存储敏感信息

---

## 📄 许可证

本项目采用MIT许可证。

---

**最后更新**: 2026-05-06
**项目状态**: ✅ 已激活并整理 (v1.0.0)
