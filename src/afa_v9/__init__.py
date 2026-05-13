from typing import Any

from .soul import Soul, SOUL_INSTANCE
from .memory import Memory, MEMORY_INSTANCE
from .heartbeat import HeartbeatMonitor, HEARTBEAT_MONITOR, HealthStatus
from .evolution import (
    EvolutionEngine,
    EVOLUTION_ENGINE,
    EvolvedSkill,
    Experience,
    Pattern,
    Hypothesis,
    OutcomeType,
    EvolutionPhase,
)
from .langgraph_adapter import LangGraphAdapter, LANGGRAPH_ADAPTER
from .thinker import Thinker, THINKER_INSTANCE
from .consciousness import Consciousness, CONSCIOUSNESS_INSTANCE
from .agents import (
    SCOUT_NODE,
    QUANT_NODE,
    MARKET_NODE,
    RISK_NODE,
    TRADER_NODE,
    AUDITOR_NODE,
    ALL_AGENTS,
    get_agent_by_name,
)
from .execution import (
    BANKROLL_MANAGER,
    BET_RECORDER,
    EXECUTION_ENGINE,
    RESULT_TRACKER,
)


class AFAV9:
    def __init__(self):
        self.soul = SOUL_INSTANCE
        self.memory = MEMORY_INSTANCE
        self.heartbeat = HEARTBEAT_MONITOR
        self.evolution = EVOLUTION_ENGINE
        self.langgraph = LANGGRAPH_ADAPTER
        self.thinker = THINKER_INSTANCE
        self.consciousness = CONSCIOUSNESS_INSTANCE
        self._initialized = True
        self._workflow_compiled = False

    def initialize_workflow(self, workflow_type: str = "pre_match") -> None:
        """初始化工作流"""
        self.langgraph.create_graph(workflow_type)
        self.langgraph.compile()
        self._workflow_compiled = True
        print(f"✅ 工作流 '{workflow_type}' 初始化完成")

    def get_system_context(self) -> dict:
        return {
            "soul": self.soul.to_dict(),
            "memory": self.memory.get_full_context(),
            "evolution": self.evolution.evaluate_performance(),
            "health": {
                "status": self.heartbeat.health_status.status,
                "uptime": self.heartbeat.health_status.uptime_seconds,
            },
            "agents": self.get_agent_status(),
        }

    def process_match(
        self,
        match_id: str,
        home_team: str,
        away_team: str,
        venue_city: str | None = None,
        thread_id: str = "default",
    ) -> dict:
        """处理一场比赛分析"""
        self.heartbeat.beat()
        self.heartbeat.record_task()

        if not self._workflow_compiled:
            self.initialize_workflow()

        initial_state = {
            "match_id": match_id,
            "home_team": home_team,
            "away_team": away_team,
            "venue_city": venue_city,
            "soul_context": self.soul.get_full_context(),
            "memory_context": self.memory.get_full_context(),
        }

        print(f"\n🚀 开始分析比赛: {home_team} vs {away_team}")
        result = self.langgraph.run(initial_state, thread_id)  # type: ignore[no-any-return]

        self.heartbeat.record_task(pending=False)

        outcome = OutcomeType.SUCCESS if result.get("trader_decision", {}).get("approved", False) else OutcomeType.FAILURE
        self.evolution.record_experience(
            context={
                "match_id": match_id,
                "home_team": home_team,
                "away_team": away_team,
            },
            action="match_analysis",
            outcome=outcome,
            metrics={"approved": result.get("trader_decision", {}).get("approved", False)},
            tags=["match_analysis"],
        )

        print(f"\n📊 分析完成!")
        return result  # type: ignore[no-any-return]

    def process(self, task: dict, thread_id: str = "default") -> dict:
        """通用任务处理"""
        self.heartbeat.beat()
        self.heartbeat.record_task()

        if not self._workflow_compiled:
            self.initialize_workflow()

        initial_state = {
            "task": task,
            "soul_context": self.soul.get_full_context(),
            "memory_context": self.memory.get_full_context(),
        }

        result = self.langgraph.run(initial_state, thread_id)

        self.heartbeat.record_task(pending=False)

        self.evolution.record_experience(
            context={
                "task_type": task.get("type", "unknown"),
            },
            action="task_processing",
            outcome=OutcomeType.SUCCESS,
            metrics={"result_keys": list(result.keys()) if result else []},
            tags=[task.get("type", "unknown")],
        )

        return result  # type: ignore[no-any-return]

    def evolve(self) -> dict:
        """触发自我进化"""
        return self.evolution.evolve()  # type: ignore[no-any-return]

    def get_agent_status(self) -> dict:
        """获取所有智能体状态"""
        result: dict[str, Any] = {}
        for agent in ALL_AGENTS:
            agent_name = getattr(agent, "name", str(agent))  # type: ignore[attr-defined]
            result[agent_name] = {
                "role": getattr(agent, "role", str(agent)),
                "description": getattr(agent, "description", ""),
                "execution_count": getattr(agent, "execution_count", 0),
                "last_executed": getattr(agent, "last_executed", None),
            }
        return result

    def activate(self) -> None:
        """激活系统"""
        self.soul.identity.activate()
        print(f"🎉 {self.soul.identity.name} v{self.soul.identity.version} 已激活")


AFAV9_SYSTEM = AFAV9()

__all__ = [
    "Soul",
    "SOUL_INSTANCE",
    "Memory",
    "MEMORY_INSTANCE",
    "HeartbeatMonitor",
    "HEARTBEAT_MONITOR",
    "HealthStatus",
    "EvolutionEngine",
    "EVOLUTION_ENGINE",
    "EvolvedSkill",
    "Experience",
    "Pattern",
    "Hypothesis",
    "OutcomeType",
    "EvolutionPhase",
    "LangGraphAdapter",
    "LANGGRAPH_ADAPTER",
    "Thinker",
    "THINKER_INSTANCE",
    "Consciousness",
    "CONSCIOUSNESS_INSTANCE",
    "SCOUT_NODE",
    "QUANT_NODE",
    "MARKET_NODE",
    "RISK_NODE",
    "TRADER_NODE",
    "AUDITOR_NODE",
    "ALL_AGENTS",
    "get_agent_by_name",
    "AFAV9",
    "AFAV9_SYSTEM",
]
