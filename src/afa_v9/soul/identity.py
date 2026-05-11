from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Identity(BaseModel):
    name: str = Field(default="AFA", description="System name")
    version: str = Field(default="9.0", description="System version")
    role: Literal["analyst", "researcher", "trader", "auditor"] = Field(
        default="analyst", description="Current role"
    )
    specialization: list[str] = Field(
        default=["football_analysis", "odds_evaluation", "risk_management"],
        description="Areas of specialization"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    activation_count: int = Field(default=0, description="Number of times activated")
    last_active: datetime | None = Field(default=None)

    def activate(self) -> None:
        self.activation_count += 1
        self.last_active = datetime.now()

    def switch_role(self, new_role: Literal["analyst", "researcher", "trader", "auditor"]) -> None:
        self.role = new_role

    def add_specialization(self, spec: str) -> None:
        if spec not in self.specialization:
            self.specialization.append(spec)

    def to_context(self) -> str:
        return f"""Name: {self.name} v{self.version}
Role: {self.role}
Specialization: {', '.join(self.specialization)}
Activated: {self.activation_count} times
Last Active: {self.last_active}"""


IDENTITY_INSTANCE = Identity()
