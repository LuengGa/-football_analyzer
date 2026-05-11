"""
Thinker - 环境感知与任务规划
负责自主思考、分析环境、规划任务
"""
from typing import Dict, Any, List
from datetime import datetime

class Thinker:
    """环境感知与任务规划系统"""

    def __init__(self):
        self.last_action_time = None

    def perceive_environment(self) -> Dict[str, Any]:
        """感知环境"""
        current_time = datetime.now()

        environment = {
            "perceived_at": current_time.isoformat(),
            "upcoming_matches": [],
            "total_upcoming": 0,
            "system_status": "active"
        }

        try:
            from src.agents.tools.sportsipy_connector import get_sportsipy_connector
            connector = get_sportsipy_connector()
            upcoming_matches = connector.get_upcoming_matches(days=7)
            environment["upcoming_matches"] = upcoming_matches
            environment["total_upcoming"] = len(upcoming_matches)
        except Exception:
            pass

        return environment

    def generate_tasks(self, environment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成任务列表"""
        tasks = []
        matches = environment.get("upcoming_matches", [])

        for match in matches[:3]:
            tasks.append({
                "type": "analyze_match",
                "priority": "high",
                "match": match
            })

        tasks.append({
            "type": "audit_recent",
            "priority": "medium"
        })

        tasks.append({
            "type": "learn_and_optimize",
            "priority": "medium"
        })

        return tasks

    def choose_action(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """选择行动"""
        if not tasks:
            return {"action": "idle", "reason": "无待执行任务"}

        high_priority = [t for t in tasks if t.get("priority") == "high"]

        if high_priority:
            return high_priority[0]

        return tasks[0]

    def think_and_plan(self) -> Dict[str, Any]:
        """思考和规划"""
        environment = self.perceive_environment()
        tasks = self.generate_tasks(environment)
        chosen_action = self.choose_action(tasks)

        plan = {
            "thought": "已感知环境，正在规划...",
            "environment": environment,
            "tasks": tasks,
            "chosen_action": chosen_action,
            "next_steps": [
                "执行选定的分析任务",
                "复盘历史比赛",
                "优化模型"
            ]
        }

        self.last_action_time = datetime.now()

        return plan

    def plan_analysis(self, home_team: str, away_team: str) -> Dict[str, Any]:
        """为特定比赛规划分析"""
        plan = {
            "summary": f"分析 {home_team} vs {away_team}",
            "home_team": home_team,
            "away_team": away_team,
            "steps": [
                "收集两队情报",
                "获取四市场赔率数据",
                "运行六层赔率分析",
                "执行量化分析",
                "综合决策",
                "风控评估",
                "生成报告"
            ],
            "estimated_confidence": 0.75,
            "timestamp": datetime.now().isoformat()
        }

        return plan


THINKER_INSTANCE = Thinker()

__all__ = ["Thinker", "THINKER_INSTANCE"]
