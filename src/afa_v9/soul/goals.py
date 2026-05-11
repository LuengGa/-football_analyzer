from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class Goal(BaseModel):
    id: str
    description: str
    priority: Literal["critical", "high", "medium", "low"] = Field(default="medium")
    status: Literal["active", "completed", "paused", "abandoned"] = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = Field(default=None)
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    success_criteria: str = ""

    def complete(self) -> None:
        self.status = "completed"
        self.completed_at = datetime.now()
        self.progress = 1.0

    def update_progress(self, progress: float) -> None:
        self.progress = max(0.0, min(1.0, progress))

    def to_context(self) -> str:
        return f"[{self.priority.upper()}] {self.description} ({self.progress:.0%})"


class GoalsManager:
    def __init__(self):
        self.goals: list[Goal] = []
        self._initialize_default_goals()

    def _initialize_default_goals(self) -> None:
        self.goals = [
            Goal(
                id="roi_positive",
                description="Maintain positive ROI over rolling 100 bets",
                priority="critical",
                success_criteria="ROI > 0% over 100 bets"
            ),
            Goal(
                id="odds_accuracy",
                description="Improve odds accuracy above 52%",
                priority="high",
                success_criteria="Hit rate > 52% on value bets"
            ),
            Goal(
                id="risk_management",
                description="Keep maximum drawdown below 15%",
                priority="critical",
                success_criteria="Max drawdown < 15%"
            ),
            Goal(
                id="market_learning",
                description="Learn market inefficiencies",
                priority="medium",
                success_criteria="Identify 3+ exploitable patterns"
            ),
            Goal(
                id="self_evolution",
                description="Self-evolve based on feedback",
                priority="high",
                success_criteria="Improve prediction accuracy by 5%"
            ),
        ]

    def add_goal(self, goal: Goal) -> None:
        self.goals.append(goal)

    def get_active_goals(self) -> list[Goal]:
        return [g for g in self.goals if g.status == "active"]

    def get_goal_by_id(self, goal_id: str) -> Goal | None:
        for goal in self.goals:
            if goal.id == goal_id:
                return goal
        return None

    def to_context(self) -> str:
        active = self.get_active_goals()
        if not active:
            return "No active goals"
        lines = ["## Active Goals"]
        for g in active:
            lines.append(g.to_context())
        return "\n".join(lines)


GOALS_MANAGER = GoalsManager()
