# AFA v9.0 架构重构实施计划

> **目标:** 将AFA v9.0重构为基于Hermes Agent + OpenClaw混合架构的数字生命体集群系统
>
> **架构:** Hermes Agent(智能决策层) + OpenClaw(执行/通信层) + LangGraph(工作流编排) + LLM Gateway(多Provider)
>
> **技术栈:** Python 3.14, LangGraph, Mem0, MCP, Ollama/DeepSeek/OpenAI

---

## 模块分解

| 模块 | 文件 | 优先级 |
|------|------|--------|
| 模块1: LLM Gateway | `src/core/llm/gateway.py` | P0 |
| 模块2: Agent Runtime | `src/afa_v9/agents/` | P0 |
| 模块3: Memory System | `src/afa_v9/memory/` | P1 |
| 模块4: Evolution Engine | `src/afa_v9/evolution/` | P1 |
| 模块5: 集成测试 | `tests/integration/` | P1 |

---

## 模块1详细任务: LLM Gateway

### 任务1.1: 创建LLM Gateway基础架构

**文件:**
- 创建: `src/core/llm/gateway.py`
- 修改: `src/core/llm/llm_config.py`
- 测试: `tests/unit/core/llm/test_gateway.py`

- [ ] **Step 1: 创建LLM Gateway核心类**

```python
# src/core/llm/gateway.py
"""
AFA LLM Gateway - 多Provider统一调度
=====================================

支持:
- Ollama Cloud
- DeepSeek
- OpenAI
- 本地Ollama
- 模型降级策略
"""

import os
from enum import Enum
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    OLLAMA_CLOUD = "ollama_cloud"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    OLLAMA_LOCAL = "ollama_local"


@dataclass
class ProviderConfig:
    name: str
    provider_type: ProviderType
    base_url: str
    api_key: str
    default_model: str
    available_models: List[str]
    priority: int  # 优先级，越低越优先
    enabled: bool = True


class LLMGateway:
    """
    统一LLM调度网关

    使用方式:
        gateway = LLMGateway()
        response = gateway.generate("分析这场比赛", task_type="analysis")
    """

    def __init__(self):
        self.providers: Dict[ProviderType, ProviderConfig] = {}
        self._current_provider: Optional[ProviderType] = None
        self._clients: Dict[ProviderType, Any] = {}
        self._init_providers()

    def _init_providers(self) -> None:
        """初始化所有Provider配置"""
        # Ollama Cloud
        self.register_provider(ProviderConfig(
            name="Ollama Cloud",
            provider_type=ProviderType.OLLAMA_CLOUD,
            base_url=os.getenv("OLLAMA_BASE_URL", "https://ollama.com/v1"),
            api_key=os.getenv("OLLAMA_API_KEY", ""),
            default_model=os.getenv("OLLAMA_MODEL", "deepseek-v4-flash"),
            available_models=["deepseek-v4-flash", "qwen2.5", "llama3.1"],
            priority=1,
        ))

        # DeepSeek
        self.register_provider(ProviderConfig(
            name="DeepSeek",
            provider_type=ProviderType.DEEPSEEK,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            default_model="deepseek-chat",
            available_models=["deepseek-chat", "deepseek-reasoner"],
            priority=2,
        ))

        # OpenAI
        self.register_provider(ProviderConfig(
            name="OpenAI",
            provider_type=ProviderType.OPENAI,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            default_model="gpt-4o-mini",
            available_models=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
            priority=3,
        ))

    def register_provider(self, config: ProviderConfig) -> None:
        """注册Provider"""
        if config.enabled and config.api_key:
            self.providers[config.provider_type] = config
            logger.info(f"Registered provider: {config.name}")

    def route(self, task_type: str) -> ProviderType:
        """根据任务类型选择Provider"""
        if task_type in ["analysis", "general"]:
            return ProviderType.OLLAMA_CLOUD
        elif task_type in ["reasoning", "complex"]:
            return ProviderType.DEEPSEEK
        else:
            return self._get_default_provider()

    def _get_default_provider(self) -> ProviderType:
        """获取默认Provider（优先级最高且可用的）"""
        available = [(p, cfg.priority) for p, cfg in self.providers.items() if cfg.enabled]
        if not available:
            return ProviderType.OLLAMA_CLOUD
        return sorted(available, key=lambda x: x[1])[0][0]

    def get_client(self, provider: Optional[ProviderType] = None) -> Any:
        """获取指定Provider的客户端"""
        if provider is None:
            provider = self._current_provider or self._get_default_provider()

        if provider not in self._clients:
            config = self.providers.get(provider)
            if not config:
                raise ValueError(f"Provider {provider} not configured")

            self._clients[provider] = self._create_client(config)

        return self._clients[provider]

    def _create_client(self, config: ProviderConfig) -> Any:
        """创建Provider客户端"""
        try:
            from openai import OpenAI
            return OpenAI(
                api_key=config.api_key,
                base_url=config.base_url,
            )
        except ImportError:
            logger.warning("OpenAI package not available, using mock client")
            return MockClient(config)

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        task_type: str = "general",
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """生成文本"""
        provider = self.route(task_type)
        config = self.providers.get(provider)
        model = model or config.default_model if config else "default"

        client = self.get_client(provider)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return self._fallback_generate(prompt, task_type)

    def _fallback_generate(self, prompt: str, task_type: str) -> str:
        """降级策略"""
        logger.warning("Using fallback generation")
        return f"[Fallback] Processed: {prompt[:100]}..."

    def get_available_providers(self) -> List[str]:
        """获取可用Provider列表"""
        return [cfg.name for cfg in self.providers.values() if cfg.enabled]


class MockClient:
    """Mock客户端用于测试"""
    def __init__(self, config: ProviderConfig):
        self.config = config

    def chat(self):
        return self


class MockResponse:
    """Mock响应"""
    def __init__(self, content: str = "Mock response"):
        self.choices = [MockChoice(content)]


class MockChoice:
    def __init__(self, content: str):
        self.message = MockMessage(content)


class MockMessage:
    def __init__(self, content: str):
        self.content = content


LLM_GATEWAY = LLMGateway()

__all__ = [
    "LLMGateway",
    "LLM_GATEWAY",
    "ProviderType",
    "ProviderConfig",
]
```

- [ ] **Step 2: 创建单元测试**

```python
# tests/unit/core/llm/test_gateway.py
import pytest
from src.core.llm.gateway import LLMGateway, ProviderType

def test_gateway_initialization():
    gateway = LLMGateway()
    assert gateway is not None
    assert len(gateway.providers) >= 0

def test_route_task_types():
    gateway = LLMGateway()
    provider = gateway.route("analysis")
    assert provider in ProviderType

def test_get_available_providers():
    gateway = LLMGateway()
    providers = gateway.get_available_providers()
    assert isinstance(providers, list)
```

- [ ] **Step 3: 运行测试验证**

Run: `/Users/jand/.homebrew/bin/python3 -m pytest tests/unit/core/llm/test_gateway.py -v`
Expected: PASS

---

### 任务1.2: 集成现有LLM配置

**文件:**
- 修改: `src/core/llm/llm_config.py`
- 创建: `src/core/llm/providers/`

- [ ] **Step 1: 迁移配置到Gateway**

将现有的 `get_llm_settings()` 迁移到使用 LLMGateway

---

## 执行状态

| 任务 | 状态 |
|------|------|
| 1.1 LLM Gateway基础 | 待执行 |
| 1.2 配置集成 | 待执行 |
| 2.x Agent Runtime | 待执行 |
| 3.x Memory System | 待执行 |
| 4.x Evolution Engine | 待执行 |
| 5.x 集成测试 | 待执行 |

---

## 执行方式

**选择: 子Agent驱动 (方式1)**
- 每个任务由独立的子Agent执行
- 任务间有检查点
- 适合大型重构
