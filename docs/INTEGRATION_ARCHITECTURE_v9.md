# AFA v9.0 - 融合架构设计文档

> **更新时间**: 2026-05-09
> **架构版本**: v9.0-final
> **参考框架**: Hermes Agent + OpenClaw + LangGraph

## 一、融合理念

### Hermes Agent 核心优势
- 自我进化机制（核心亮点）
- 技能自动生成与优化
- 跨会话学习能力
- 多LLM灵活切换

### OpenClaw 核心优势
- 数字生命架构（SOUL/IDENTITY/MEMORY）
- 本地化记忆系统
- Agent通信协议(ACP)
- 丰富的平台集成

### 整合目标
```
┌─────────────────────────────────────────────────────────────┐
│              AFA v9.0 - 足球领域数字生命Agent               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Hermes Agent              +           OpenClaw            │
│   ├─ 自我进化                               ├─ SOUL/IDENTITY │
│   ├─ 技能系统              ────────→        ├─ 记忆架构     │
│   └─ 经验学习                               └─ ACP协议      │
│                                                             │
│                        ↓                                    │
│              ┌───────────────────────┐                      │
│              │   足球领域专业化Agent   │                      │
│              │  ├─ 赛前分析Agent      │                      │
│              │  ├─ 滚球分析Agent      │                      │
│              │  ├─ 风控Agent         │                      │
│              │  └─ 复盘Agent(进化)   │                      │
│              └───────────────────────┘                      │
│                                                             │
│   底层框架：LangGraph + Ollama Cloud                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、架构设计

### 2.1 核心组件

```
src/
├── core/
│   └── llm/
│       └── gateway.py              # LLM Gateway (多Provider)
│
├── afa_v9/
│   ├── soul/                      # Soul模块（数字生命身份）
│   │   └── __init__.py            # SOUL_INSTANCE
│   │
│   ├── memory/                    # Memory模块（多层记忆）
│   │   ├── __init__.py            # MEMORY_INSTANCE
│   │   ├── WorkingMemory          # 短期记忆
│   │   ├── EpisodicMemory         # 情景记忆
│   │   ├── SemanticMemory         # 语义记忆
│   │   └── BM25Search             # BM25全文搜索
│   │
│   ├── evolution/                  # Evolution模块（7阶段自进化）
│   │   ├── __init__.py            # EVOLUTION_ENGINE
│   │   ├── Experience             # 经验条目
│   │   ├── EvolvedSkill           # 进化技能
│   │   ├── Pattern                # 发现模式
│   │   ├── Hypothesis             # 假说
│   │   └── data_accumulator.py    # 数据积累器
│   │
│   ├── agents/                    # Agent集群（数字生命体）
│   │   ├── base.py               # Agent基类 (Soul + Brain + LLM)
│   │   ├── __init__.py           # 6个Agent实例
│   │   ├── ScoutAgent            # 情报收集
│   │   ├── QuantAgent            # 量化分析
│   │   ├── MarketAgent           # 市场分析
│   │   ├── RiskAgent            # 风险控制
│   │   ├── TraderAgent          # 交易决策
│   │   └── AuditorAgent         # 审计监督
│   │
│   └── langgraph_adapter/         # LangGraph编排
│       └── __init__.py           # LANGGRAPH_ADAPTER
│
└── tests/
    ├── unit/
    │   ├── core/llm/
    │   │   └── test_gateway.py
    │   └── afa_v9/
    │       ├── test_agents.py
    │       ├── test_memory.py
    │       └── test_evolution.py
    └── integration/
        └── test_afa_v9_complete.py
```

### 2.2 Agent结构

每个Agent = Soul + Brain + LLM

```
┌────────────────────────────────────────┐
│                 SOUL                    │
│  ├── name: Agent名称                   │
│  ├── role: Agent角色                   │
│  ├── description: Agent描述            │
│  ├── personality: 性格特征            │
│  ├── goals: Agent目标                 │
│  └── values: 价值观                   │
├────────────────────────────────────────┤
│                 BRAIN                   │
│  ├── skills: 技能列表                 │
│  ├── rules: 决策规则                  │
│  └── patterns: 经验模式               │
├────────────────────────────────────────┤
│                 LLM                     │
│  └── Gateway (多Provider)              │
└────────────────────────────────────────┘
```

### 2.3 7阶段进化流程

```
OBSERVATION ──→ ANALYSIS ──→ HYPOTHESIS ──→ EXPERIMENT
     │              │             │              │
     │              │             │              ▼
     │              │             │         VALIDATION
     │              │             │              │
     │              │             │              ▼
     │              │             │        INTEGRATION
     │              │             │              │
     │              │             │              ▼
     └──────────────┴─────────────┴─────→ CONSOLIDATION
```

---

## 三、LLM Gateway

### 3.1 支持的Provider

| Provider | 用途 | 优先级 |
|----------|------|--------|
| Ollama Cloud | 分析/通用 | 1 |
| DeepSeek | 推理/复杂 | 2 |
| OpenAI | 备用 | 3 |

### 3.2 路由策略

```python
gateway = LLMGateway()
gateway.route("analysis")    # → Ollama Cloud
gateway.route("reasoning")   # → DeepSeek
gateway.route("general")     # → 默认Provider
```

---

## 四、使用示例

### 4.1 LLM Gateway

```python
from src.core.llm.gateway import LLM_GATEWAY

# 生成文本
response = LLM_GATEWAY.generate(
    prompt="分析这场比赛",
    task_type="analysis"
)

# 异步生成
response = await LLM_GATEWAY.generate_async(
    prompt="分析这场比赛",
    task_type="reasoning"
)
```

### 4.2 Agent集群

```python
from src.afa_v9.agents import get_agent_by_name

# 获取Agent
scout = get_agent_by_name("scout")

# 执行任务
result = scout.execute({
    "home_team": "Manchester City",
    "away_team": "Arsenal"
})

# Agent思考（调用LLM）
thought = scout.think("分析主队近期状态")
```

### 4.3 记忆系统

```python
from src.afa_v9.memory import MEMORY_INSTANCE

# 存储记忆
MEMORY_INSTANCE.store_interaction(
    "match_analysis",
    {"result": "win", "confidence": 0.85},
    importance=0.9
)

# 搜索记忆
results = MEMORY_INSTANCE.search_memory("Manchester City")

# 获取LLM上下文
context = MEMORY_INSTANCE.get_full_context()
```

### 4.4 进化引擎

```python
from src.afa_v9.evolution import EVOLUTION_ENGINE, OutcomeType

# 记录经验
EVOLUTION_ENGINE.record_experience(
    context={"league": "Premier League", "odds": 2.0},
    action="bet_home_win",
    outcome=OutcomeType.SUCCESS,
    metrics={"profit": 1.0, "roi": 100.0}
)

# 执行进化
result = EVOLUTION_ENGINE.evolve()

# 获取进化报告
report = EVOLUTION_ENGINE.get_evolution_report()
```

---

## 五、测试

### 5.1 运行测试

```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 完整测试
pytest tests/ -v
```

### 5.2 测试覆盖

| 模块 | 测试数 | 状态 |
|------|--------|------|
| LLM Gateway | 5 | ✅ PASS |
| Agent Runtime | 6 | ✅ PASS |
| Memory System | 7 | ✅ PASS |
| Evolution Engine | 8 | ✅ PASS |
| 集成测试 | 7 | ✅ PASS |
| **总计** | **33** | **✅ 100%** |
│   ├── pre_match_flow.py     # 赛前分析流程
│   ├── in_play_flow.py       # 滚球分析流程
│   └── post_match_flow.py     # 赛后复盘流程
│
├── llm/                      # LLM集成
│   ├── client.py              # Ollama Cloud客户端
│   ├── prompts/               # Agent提示词库
│   └── providers/             # 多Provider支持
│
└── skills/                   # 足球领域技能库
    ├── football_analysis.py   # 足球分析技能
    ├── odds_calculation.py    # 赔率计算技能
    ├── risk_management.py     # 风险管理技能
    └── strategy_patterns.py   # 策略模式库
```

### 2.2 记忆系统设计

```
记忆层级（融合两者）：

┌─────────────────────────────────────────────┐
│           长期记忆（Long-term）              │
│  ┌───────────────────────────────────────┐ │
│  │ 技能库 (Skills) - Hermes风格           │ │
│  │ - 自动生成                             │ │
│  │ - 使用中优化                           │ │
│  │ - 可被发现和复用                       │ │
│  └───────────────────────────────────────┘ │
│  ┌───────────────────────────────────────┐ │
│  │ 知识库 (Knowledge) - 足球领域专精     │ │
│  │ - 球队信息                             │ │
│  │ - 历史战绩                             │ │
│  │ - 赔率规律                             │ │
│  └───────────────────────────────────────┘ │
│  ┌───────────────────────────────────────┐ │
│  │ 事件记忆 (Episodes) - OpenClaw风格    │ │
│  │ - 本地文件存储                          │ │
│  │ - JSON格式                             │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
                      ↑
                      ↓
┌─────────────────────────────────────────────┐
│           短期记忆（Short-term）             │
│  - 当前会话状态                              │
│  - 实时分析数据                              │
│  - 决策过程记录                              │
└─────────────────────────────────────────────┘
```

### 2.3 进化系统设计

```
自我进化闭环（Hermes核心）：

    ┌──────────────┐
    │   复盘分析    │
    │  (Auditor)   │
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │  经验挖掘    │ ← 从复盘中提取模式
    │(Experience) │
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │  技能生成    │ ← 生成可复用技能
    │(Skill Gen)  │
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │  技能库更新  │ ← 持久化到记忆
    │(Skill Store)│
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │  下次分析    │ ← 使用已有技能
    │   应用技能   │
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │  技能优化    │ ← 使用中持续改进
    │(Optimization)│
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │  效果评估    │ ← 评估技能表现
    │  (评估)      │
    └──────┬───────┘
           ↓
           └────────→ 回到"复盘分析"
```

---

## 三、核心模块详解

### 3.1 灵魂模块（SOUL）

```python
# soul/identity.py
class AFAAgentIdentity:
    """AFA Agent身份定义"""
    
    NAME = "AFA Football Analyst"
    ROLE = "Professional Football Betting Analyst"
    SPECIALIZATION = "Football match analysis and betting strategy"
    
    PERSONALITY = {
        "risk_tolerance": "conservative",  # 风险承受度
        "decision_style": "data_driven",    # 决策风格
        "learning_approach": "continuous"  # 持续学习
    }
    
    GOALS = [
        "Maximize expected value",
        "Minimize risk exposure",
        "Continuous self-improvement"
    ]
```

### 3.2 技能生成器（Hermes风格）

```python
# evolution/skill_generator.py
class SkillGenerator:
    """
    从经验中自动生成可复用技能
    Hermes Agent的核心机制
    """
    
    def generate_skill(self, experience: Dict) -> Skill:
        """从复盘经验生成新技能"""
        
        prompt = f"""
        从以下足球分析经验中提取可复用的技能规则：
        
        经验：{experience}
        
        要求：
        1. 提取具体的分析模式
        2. 提炼决策规则
        3. 识别关键触发条件
        4. 给出适用场景
        """
        
        skill = self.llm.generate(prompt)
        return self.parse_and_validate(skill)
    
    def optimize_skill(self, skill: Skill, results: List[Result]) -> Skill:
        """使用结果优化现有技能"""
        
        prompt = f"""
        基于使用结果优化技能：
        
        技能：{skill}
        使用结果：{results}
        
        分析：
        1. 哪些规则有效？
        2. 哪些规则需要调整？
        3. 如何提高准确性？
        """
        
        return self.llm.generate(prompt)
```

### 3.3 记忆存储（OpenClaw风格）

```python
# memory/episodic_store.py
class EpisodicMemoryStore:
    """
    本地文件存储的记忆系统
    OpenClaw风格的隐私优先设计
    """
    
    MEMORY_DIR = ".afa/memory/"
    
    def __init__(self):
        self.base_dir = Path(self.MEMORY_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 目录结构
        self.episodes_dir = self.base_dir / "episodes"
        self.skills_dir = self.base_dir / "skills"
        self.knowledge_dir = self.base_dir / "knowledge"
        
        for d in [self.episodes_dir, self.skills_dir, self.knowledge_dir]:
            d.mkdir(exist_ok=True)
    
    def save_episode(self, episode: Dict):
        """保存事件记忆"""
        timestamp = datetime.now().isoformat()
        filename = f"{timestamp.replace(':', '-')}.json"
        filepath = self.episodes_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(episode, f, ensure_ascii=False, indent=2)
    
    def search_episodes(self, query: str) -> List[Dict]:
        """搜索历史事件"""
        # 实现FTS5全文搜索
        pass
```

---

## 四、实现优先级

### Phase 1: 基础架构（1周）
- [ ] 目录结构搭建
- [ ] 灵魂模块（SOUL）
- [ ] 基础记忆系统
- [ ] LangGraph流程编排

### Phase 2: 核心功能（2周）
- [ ] 6个专业Agent实现
- [ ] Ollama Cloud集成
- [ ] 赛前分析流程
- [ ] 基础复盘功能

### Phase 3: 进化系统（2周）
- [ ] 技能自动生成器
- [ ] 技能优化器
- [ ] 学习闭环
- [ ] 经验知识库

### Phase 4: 高级功能（1周）
- [ ] 滚球实时分析
- [ ] 多流程编排
- [ ] ACP协议集成
- [ ] 技能库UI

---

## 五、技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| **LLM引擎** | Ollama Cloud | 本项目已配置 |
| **编排框架** | LangGraph | 状态机编排 |
| **记忆存储** | 本地文件 | JSON格式，隐私优先 |
| **搜索** | SQLite FTS5 | 全文搜索 |
| **Agent** | 自主开发 | 足球领域专业化 |
| **进化** | Hermes启发 | 自动技能生成 |

---

## 六、与现有系统的关系

### 继承关系
```
AFA v8.6 (当前)          →         AFA v9.0 (目标)
│                                         │
├── agents/graphs/           →           ├── soul/
├── agents/llm/               →           ├── llm/
├── agents/evolution/         →           ├── evolution/
└── calculations/pro/        →           ├── skills/

新增：
├── memory/                               (全新)
└── graph/                                (升级)
```

---

## 七、预期收益

| 维度 | 当前(v8.6) | 目标(v9.0) |
|------|-----------|------------|
| **自我进化** | 基础复盘 | 自动技能生成 |
| **记忆能力** | 有限 | 跨会话持续学习 |
| **专业化** | 一般 | 足球领域顶尖 |
| **可扩展性** | 中等 | 高度模块化 |
| **维护性** | 中等 | 清晰的架构 |

---

## 八、风险与挑战

| 风险 | 应对措施 |
|------|---------|
| 开发周期长 | 分阶段交付，每阶段可独立运行 |
| 技能质量 | 人工审核 + 效果评估双保险 |
| 记忆膨胀 | 定期清理 + 压缩机制 |
| LLM依赖 | 支持多Provider切换 |

---

## 九、下一步行动

1. **确认架构设计**
2. **Phase 1实施**
3. **持续迭代优化**

---

*文档版本：v1.0*
*创建时间：2026-05-07*
*目标版本：AFA v9.0*
