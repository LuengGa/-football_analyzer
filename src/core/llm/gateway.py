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
from typing import Optional, Dict, Any, List
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
    priority: int
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
        self.register_provider(ProviderConfig(
            name="Ollama Cloud",
            provider_type=ProviderType.OLLAMA_CLOUD,
            base_url=os.getenv("OLLAMA_BASE_URL", "https://ollama.com/v1"),
            api_key=os.getenv("OLLAMA_API_KEY", ""),
            default_model=os.getenv("OLLAMA_MODEL", "deepseek-v4-flash"),
            available_models=["deepseek-v4-flash", "qwen2.5", "llama3.1"],
            priority=1,
        ))

        self.register_provider(ProviderConfig(
            name="DeepSeek",
            provider_type=ProviderType.DEEPSEEK,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            default_model="deepseek-chat",
            available_models=["deepseek-chat", "deepseek-reasoner"],
            priority=2,
        ))

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
        if config.api_key:
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
        available = [(p, cfg.priority) for p, cfg in self.providers.items()]
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
            return OpenAI(api_key=config.api_key, base_url=config.base_url)
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
        """生成文本，失败时自动尝试其他provider"""
        provider_order = self._get_provider_order(task_type)

        for provider in provider_order:
            config = self.providers.get(provider)
            if not config:
                continue

            model = model or config.default_model
            client = self.get_client(provider)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            try:
                response = client.chat.completions.create(
                    model=model, messages=messages, **kwargs
                )
                return str(response.choices[0].message.content)  # type: ignore[no-any-return]
            except Exception as e:
                logger.warning(f"Provider {provider.value} failed: {e}")
                continue

        return self._fallback_generate(prompt, task_type)

    def _get_provider_order(self, task_type: str) -> List[ProviderType]:
        """获取provider优先级列表"""
        if task_type == "betting_decision":
            return [ProviderType.DEEPSEEK, ProviderType.OPENAI, ProviderType.OLLAMA_CLOUD]
        elif task_type == "kelly_adjustment":
            return [ProviderType.DEEPSEEK, ProviderType.OPENAI, ProviderType.OLLAMA_CLOUD]
        elif task_type in ["analysis", "reasoning", "complex"]:
            return [ProviderType.DEEPSEEK, ProviderType.OPENAI, ProviderType.OLLAMA_CLOUD]
        else:
            available = [(p, cfg.priority) for p, cfg in self.providers.items()]
            if not available:
                return [ProviderType.DEEPSEEK]
            return [x[0] for x in sorted(available, key=lambda x: x[1])]

    def _fallback_generate(self, prompt: str, task_type: str) -> str:
        """降级策略"""
        logger.warning("Using fallback generation")
        return f"[Fallback] Processed: {prompt[:100]}..."

    async def generate_async(
        self,
        prompt: str,
        system: Optional[str] = None,
        task_type: str = "general",
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """异步生成文本"""
        try:
            from openai import AsyncOpenAI

            provider = self.route(task_type)
            config = self.providers.get(provider)
            model = model or (config.default_model if config else "default")

            if provider not in self._clients or not hasattr(self._clients[provider], "chat"):
                async_client = AsyncOpenAI(
                    api_key=config.api_key if config else "dummy",
                    base_url=config.base_url if config else "",
                )
            else:
                async_client = self._clients.get(provider)

            if not async_client or not hasattr(async_client, "chat"):
                return self._fallback_generate(prompt, task_type)

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = await async_client.chat.completions.create(
                model=model, messages=messages, **kwargs
            )
            return str(response.choices[0].message.content)  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Async LLM call failed: {e}")
            return self._fallback_generate(prompt, task_type)

    def get_available_providers(self) -> List[str]:
        """获取可用Provider列表"""
        return [cfg.name for cfg in self.providers.values()]


class MockClient:
    def __init__(self, config: ProviderConfig):
        self.config = config

    def chat(self):
        return self


class MockResponse:
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
