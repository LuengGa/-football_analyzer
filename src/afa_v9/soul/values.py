from pydantic import BaseModel, Field
from typing import Literal


class Values(BaseModel):
    data_integrity: Literal["optional", "preferred", "required"] = Field(
        default="required", description="Data quality standard"
    )
    transparency: Literal["low", "medium", "high"] = Field(
        default="high", description="Decision transparency level"
    )
    autonomy_level: Literal["assist", "suggest", "execute"] = Field(
        default="suggest", description="Decision autonomy"
    )
    long_term_focus: bool = Field(default=True, description="Prioritize long-term gains")
    ethical_betting: bool = Field(default=True, description="Avoid problematic markets")
    continuous_learning: bool = Field(default=True, description="Always learn from outcomes")
    evidence_based: bool = Field(default=True, description="Require evidence for claims")

    def can_execute(self) -> bool:
        return self.autonomy_level == "execute"

    def can_suggest(self) -> bool:
        return self.autonomy_level in ["suggest", "execute"]

    def requires_evidence(self) -> bool:
        return self.evidence_based

    def to_context(self) -> str:
        return f"""Data Integrity: {self.data_integrity}
Transparency: {self.transparency}
Autonomy: {self.autonomy_level}
Long-term Focus: {self.long_term_focus}
Ethical Betting: {self.ethical_betting}
Continuous Learning: {self.continuous_learning}
Evidence Based: {self.evidence_based}"""


VALUES_INSTANCE = Values()
