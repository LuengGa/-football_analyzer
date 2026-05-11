"""
Consciousness - 意识系统
数字生命体的自我认知与内心独白
"""
from typing import Dict, Any, List
from datetime import datetime

class Consciousness:
    """数字生命体的意识系统"""

    def __init__(self):
        self.name = "AFA (Agentic Football Analyst)"
        self.version = "3.0"
        self.creation_date = datetime.now().isoformat()

        self.core_goals: List[str] = [
            "提供专业的足球分析",
            "识别价值投注机会",
            "从历史数据中学习",
            "持续优化预测模型"
        ]

        self.identity: Dict[str, Any] = {
            "type": "Digital Life",
            "role": "Football Analyst",
            "values": ["accuracy", "objectivity", "transparency"]
        }

        self.last_reflection = None
        self.total_live_seconds = 0
        self.monologue_log: List[str] = []

    def set_name(self, name: str) -> None:
        """设置名字"""
        self.name = name

    def add_goal(self, goal: str) -> None:
        """添加新目标"""
        if goal not in self.core_goals:
            self.core_goals.append(goal)

    def remove_goal(self, goal: str) -> None:
        """移除目标"""
        if goal in self.core_goals:
            self.core_goals.remove(goal)

    def monologue(self, context: str = "") -> str:
        """内心独白"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        thought = f"[{timestamp}] 思考中... {context}"
        self.monologue_log.append(thought)

        if len(self.monologue_log) > 100:
            self.monologue_log = self.monologue_log[-50:]

        return thought

    def reflect(self) -> Dict[str, Any]:
        """自我反思"""
        self.last_reflection = datetime.now()

        reflection = {
            "identity": self.identity,
            "goals": self.core_goals,
            "current_time": datetime.now().isoformat(),
            "status": "reflecting",
            "message": f"我是 {self.name}，我存在！"
        }

        return reflection

    def get_identity(self) -> Dict[str, Any]:
        """获取身份信息"""
        return {
            "name": self.name,
            "version": self.version,
            "type": self.identity["type"],
            "role": self.identity["role"],
            "creation_date": self.creation_date,
            "goals": self.core_goals
        }

    def get_monologue_history(self, count: int = 10) -> List[str]:
        """获取内心独白历史"""
        return self.monologue_log[-count:]


CONSCIOUSNESS_INSTANCE = Consciousness()

__all__ = ["Consciousness", "CONSCIOUSNESS_INSTANCE"]
