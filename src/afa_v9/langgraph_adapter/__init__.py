from typing import Any, Callable, Dict, Optional, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from ..soul import SOUL_INSTANCE
from ..memory import MEMORY_INSTANCE
from ..agents import (
    SCOUT_AGENT,
    QUANT_AGENT,
    MARKET_AGENT,
    RISK_AGENT,
    TRADER_AGENT,
    AUDITOR_AGENT,
    Agent,
)


class LangGraphAdapter:
    def __init__(self):
        self.soul = SOUL_INSTANCE
        self.memory = MEMORY_INSTANCE
        self.graph: StateGraph | None = None
        self.compiled_graph: Any = None
        self.checkpointer = MemorySaver()
        self._agents = {
            "scout": SCOUT_AGENT,
            "quant": QUANT_AGENT,
            "market": MARKET_AGENT,
            "risk": RISK_AGENT,
            "trader": TRADER_AGENT,
            "auditor": AUDITOR_AGENT,
        }

    def create_graph(self, workflow_type: str = "pre_match") -> StateGraph:
        """创建工作流图"""
        self.graph = StateGraph(dict)
        
        if workflow_type == "pre_match":
            self._build_pre_match_workflow()
        elif workflow_type == "in_play":
            self._build_in_play_workflow()
        else:
            self._build_default_workflow()
        
        return self.graph

    def _build_pre_match_workflow(self) -> None:
        """构建赛前分析工作流 - 使用数字生命体Agent"""
        if not self.graph:
            return

        def scout_wrapper(state: Dict) -> Dict:
            state = self.inject_soul_context(state)
            state = self.inject_memory_context(state)
            return self._agents["scout"].execute(state)  # type: ignore[return-value]

        def quant_wrapper(state: Dict) -> Dict:
            return self._agents["quant"].execute(state)  # type: ignore[return-value]

        def market_wrapper(state: Dict) -> Dict:
            return self._agents["market"].execute(state)  # type: ignore[return-value]

        def risk_wrapper(state: Dict) -> Dict:
            return self._agents["risk"].execute(state)  # type: ignore[return-value]

        def trader_wrapper(state: Dict) -> Dict:
            return self._agents["trader"].execute(state)  # type: ignore[return-value]

        def auditor_wrapper(state: Dict) -> Dict:
            return self._agents["auditor"].execute(state)  # type: ignore[return-value]
        
        self.graph.add_node("scout", scout_wrapper)
        self.graph.add_node("quant", quant_wrapper)
        self.graph.add_node("market", market_wrapper)
        self.graph.add_node("risk", risk_wrapper)
        self.graph.add_node("trader", trader_wrapper)
        self.graph.add_node("auditor", auditor_wrapper)
        
        self.graph.set_entry_point("scout")
        self.graph.add_edge("scout", "quant")
        self.graph.add_edge("quant", "market")
        self.graph.add_edge("market", "risk")
        self.graph.add_edge("risk", "trader")
        self.graph.add_edge("trader", "auditor")
        self.graph.add_edge("auditor", END)

    def _build_in_play_workflow(self) -> None:
        """构建实时比赛工作流"""
        if not self.graph:
            return
        
        def market_update(state: Dict) -> Dict:
            print("   -> 📡 实时市场更新")
            return {"in_play_update": {"timestamp": 1234567890}}
        
        def risk_reassess(state: Dict) -> Dict:
            print("   -> 🔄 风险重新评估")
            return {"risk_reassessed": True}
        
        def quick_decision(state: Dict) -> Dict:
            print("   -> ⚡ 快速决策")
            return {"quick_decision": "hold"}
        
        self.graph.add_node("market_update", market_update)
        self.graph.add_node("risk_reassess", risk_reassess)
        self.graph.add_node("quick_decision", quick_decision)
        
        self.graph.set_entry_point("market_update")
        self.graph.add_edge("market_update", "risk_reassess")
        self.graph.add_edge("risk_reassess", "quick_decision")
        self.graph.add_edge("quick_decision", END)

    def _build_default_workflow(self) -> None:
        """构建默认工作流"""
        if not self.graph:
            return
        
        def start_node(state: Dict) -> Dict:
            return {"started": True}
        
        def end_node(state: Dict) -> Dict:
            return {"completed": True}
        
        self.graph.add_node("start", start_node)
        self.graph.add_node("end", end_node)
        
        self.graph.set_entry_point("start")
        self.graph.add_edge("start", "end")
        self.graph.add_edge("end", END)

    def inject_soul_context(self, state: dict) -> dict:
        """注入SOUL上下文"""
        soul_context = self.soul.get_full_context()
        state["soul_context"] = soul_context
        return state

    def inject_memory_context(self, state: dict) -> dict:
        """注入记忆上下文"""
        memory_context = self.memory.get_full_context()
        state["memory_context"] = memory_context
        return state

    def add_node(self, name: str, func: Callable) -> None:
        """添加自定义节点"""
        if self.graph:
            self.graph.add_node(name, func)

    def add_edge(self, from_node: str, to_node: str) -> None:
        """添加边"""
        if self.graph:
            self.graph.add_edge(from_node, to_node)

    def add_conditional_edge(self, from_node: str, condition: Callable, mapping: dict) -> None:
        """添加条件边"""
        if self.graph:
            self.graph.add_conditional_edge(from_node, condition, mapping)

    def compile(self) -> Any:
        """编译图"""
        if self.graph:
            self.compiled_graph = self.graph.compile(checkpointer=self.checkpointer)
        return self.compiled_graph

    def run(self, initial_state: dict, thread_id: str = "default") -> dict:
        """运行工作流"""
        if self.compiled_graph:
            config = {"configurable": {"thread_id": thread_id}}
            try:
                result = self.compiled_graph.invoke(initial_state, config)
                return result  # type: ignore[no-any-return]
            except Exception as e:
                print(f"⚠️ 工作流执行失败: {e}")
                return initial_state  # type: ignore[no-any-return]
        return initial_state  # type: ignore[no-any-return]

    def get_state(self, thread_id: str = "default") -> dict | None:
        """获取当前状态"""
        if self.compiled_graph:
            config = {"configurable": {"thread_id": thread_id}}
            try:
                return self.compiled_graph.get_state(config)  # type: ignore[no-any-return]
            except Exception:
                return None
        return None

    def get_agent_status(self) -> Dict[str, Any]:
        """获取所有Agent状态"""
        return {
            name: agent.get_status()
            for name, agent in self._agents.items()
        }


LANGGRAPH_ADAPTER = LangGraphAdapter()


__all__ = [
    "LangGraphAdapter",
    "LANGGRAPH_ADAPTER",
]
