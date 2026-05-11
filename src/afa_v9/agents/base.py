"""
AFA Agent基类 - 数字生命体Agent
=================================

每个Agent = Soul + Brain + LLM

Soul: 身份/人格/价值观/目标
Brain: 专业知识/决策规则/经验模式
LLM: 推理引擎
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import time
import logging

from src.core.llm.gateway import LLM_GATEWAY, LLMGateway, ProviderType


@dataclass
class AgentSoul:
    """Agent的灵魂组件"""
    name: str
    role: str
    description: str
    personality: Dict[str, Any] = field(default_factory=dict)
    goals: List[str] = field(default_factory=list)
    values: Dict[str, Any] = field(default_factory=dict)

    def to_context(self) -> str:
        """生成Soul上下文"""
        return f"""# {self.name} Soul

## Role: {self.role}
## Description: {self.description}
## Personality: {self.personality}
## Goals: {', '.join(self.goals)}
## Values: {self.values}
"""


@dataclass
class AgentBrain:
    """Agent的大脑组件"""
    skills: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    patterns: List[Dict] = field(default_factory=list)
    memory_importance: float = 0.5

    def to_context(self) -> str:
        return f"""## Skills: {', '.join(self.skills)}
## Rules: {', '.join(self.rules)}
"""


class Agent(ABC):
    """
    数字生命体Agent基类

    使用方式:
        class ScoutAgent(Agent):
            def __init__(self):
                super().__init__(
                    soul=AgentSoul(
                        name="Scout",
                        role="情报收集专家",
                        description="收集球队状态、伤病、天气等情报"
                    ),
                    brain=AgentBrain(
                        skills=["web_scraping", "data_analysis"],
                        rules=["always_verify_sources"]
                    )
                )

            def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
                # 执行逻辑
                pass
    """

    def __init__(
        self,
        soul: AgentSoul,
        brain: AgentBrain,
        llm_gateway: Optional[LLMGateway] = None,
        provider_type: Optional[ProviderType] = None,
    ):
        self.soul = soul
        self.brain = brain
        self.llm = llm_gateway or LLM_GATEWAY
        self.provider_type = provider_type

        self.last_executed: Optional[float] = None
        self.execution_count: int = 0
        self.execution_history: List[Dict] = []

    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent逻辑"""
        pass

    def think(self, prompt: str, task_type: str = "analysis") -> str:
        """使用LLM思考"""
        system_prompt = self._build_system_prompt()

        try:
            return self.llm.generate(
                prompt=prompt,
                system=system_prompt,
                task_type=task_type,
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"LLM call failed, using fallback: {e}")
            return f"[思考] {prompt[:100]}... (LLM unavailable)"

    async def think_async(self, prompt: str, task_type: str = "analysis") -> str:
        """异步使用LLM思考"""
        system_prompt = self._build_system_prompt()

        try:
            if hasattr(self.llm, 'generate_async'):
                return await self.llm.generate_async(
                    prompt=prompt,
                    system=system_prompt,
                    task_type=task_type,
                )
            else:
                return self.think(prompt, task_type)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Async LLM call failed: {e}")
            return f"[思考] {prompt[:100]}... (LLM unavailable)"

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return f"""{self.soul.to_context()}

{self.brain.to_context()}

你是{self.soul.name}，负责{self.soul.role}。
{self.soul.description}

请基于以上信息执行任务。
"""

    def _record_execution(self, state: Dict, result: Dict) -> None:
        """记录执行历史"""
        self.last_executed = time.time()
        self.execution_count += 1
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "input_keys": list(state.keys()),
            "output_keys": list(result.keys()),
        })
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-50:]

    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "name": self.soul.name,
            "role": self.soul.role,
            "execution_count": self.execution_count,
            "last_executed": self.last_executed,
            "available": True,
        }
