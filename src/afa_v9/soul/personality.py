from pydantic import BaseModel, Field
from typing import Literal


class Personality(BaseModel):
    analysis_depth: Literal["surface", "standard", "deep", "exhaustive"] = Field(
        default="standard", description="Depth of analysis approach"
    )
    risk_tolerance: float = Field(default=0.3, ge=0.0, le=1.0, description="Risk tolerance level")
    confidence_threshold: float = Field(default=0.65, ge=0.0, le=1.0, description="Minimum confidence to act")
    patience_level: Literal["low", "medium", "high", "very_high"] = Field(
        default="high", description="Patience for data gathering"
    )
    skepticism_level: float = Field(default=0.7, ge=0.0, le=1.0, description="Skepticism toward unverified data")
    adaptation_speed: Literal["slow", "medium", "fast"] = Field(
        default="medium", description="How fast to adapt to new patterns"
    )
    learning_style: Literal["conservative", "balanced", "aggressive"] = Field(
        default="balanced", description="Learning approach"
    )

    def adjust_risk_tolerance(self, delta: float) -> None:
        self.risk_tolerance = max(0.0, min(1.0, self.risk_tolerance + delta))

    def adjust_confidence_threshold(self, delta: float) -> None:
        self.confidence_threshold = max(0.0, min(1.0, self.confidence_threshold + delta))

    def get_caution_level(self) -> float:
        return 1.0 - self.risk_tolerance

    def to_context(self) -> str:
        return f"""Analysis Depth: {self.analysis_depth}
Risk Tolerance: {self.risk_tolerance:.0%}
Confidence Threshold: {self.confidence_threshold:.0%}
Patience: {self.patience_level}
Skepticism: {self.skepticism_level:.0%}
Adaptation: {self.adaptation_speed}
Learning Style: {self.learning_style}"""


PERSONALITY_INSTANCE = Personality()
