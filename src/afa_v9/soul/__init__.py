from .identity import Identity, IDENTITY_INSTANCE
from .personality import Personality, PERSONALITY_INSTANCE
from .goals import Goal, GoalsManager, GOALS_MANAGER
from .values import Values, VALUES_INSTANCE


class Soul:
    def __init__(self):
        self.identity = IDENTITY_INSTANCE
        self.personality = PERSONALITY_INSTANCE
        self.goals = GOALS_MANAGER
        self.values = VALUES_INSTANCE

    def get_full_context(self) -> str:
        return f"""# SOUL CONTEXT

## Identity
{self.identity.to_context()}

## Personality
{self.personality.to_context()}

## Values
{self.values.to_context()}

## Goals
{self.goals.to_context()}
"""

    def to_dict(self) -> dict:
        return {
            "identity": {
                "name": self.identity.name,
                "version": self.identity.version,
                "role": self.identity.role,
                "specialization": self.identity.specialization,
            },
            "personality": {
                "analysis_depth": self.personality.analysis_depth,
                "risk_tolerance": self.personality.risk_tolerance,
                "confidence_threshold": self.personality.confidence_threshold,
            },
            "values": {
                "autonomy_level": self.values.autonomy_level,
                "long_term_focus": self.values.long_term_focus,
                "evidence_based": self.values.evidence_based,
            },
        }


SOUL_INSTANCE = Soul()

__all__ = [
    "Identity",
    "IDENTITY_INSTANCE",
    "Personality",
    "PERSONALITY_INSTANCE",
    "Goal",
    "GoalsManager",
    "GOALS_MANAGER",
    "Values",
    "VALUES_INSTANCE",
    "Soul",
    "SOUL_INSTANCE",
]
