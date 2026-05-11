
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ResolutionMethod(str, Enum):
    """Methods for resolving match identity conflicts."""
    EXACT_MATCH = "exact_match"
    LEAGUE_TIME = "league_time"
    TEAM_NAMES = "team_names"
    MANUAL = "manual"


@dataclass
class IdentityElement:
    """A single element of match identity."""
    key: str
    value: str
    source: str
    confidence: float = 1.0


@dataclass
class MatchIdentity:
    """Unique identity for a match across multiple sources."""
    match_id: str
    elements: List[IdentityElement] = field(default_factory=list)
    resolved: bool = False
    resolution_method: Optional[ResolutionMethod] = None
    
    def get_primary_value(self, key: str) -> Optional[str]:
        """Get the highest confidence value for a key."""
        matching = [e for e in self.elements if e.key == key]
        if not matching:
            return None
        matching.sort(key=lambda e: e.confidence, reverse=True)
        return matching[0].value
    
    def get_all_values(self, key: str) -> List[str]:
        """Get all values for a key."""
        return [e.value for e in self.elements if e.key == key]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "match_id": self.match_id,
            "elements": [
                {"key": e.key, "value": e.value, "source": e.source, "confidence": e.confidence}
                for e in self.elements
            ],
            "resolved": self.resolved,
            "resolution_method": self.resolution_method.value if self.resolution_method else None
        }


class MatchIdentityBuilder:
    """Builder for creating match identities from multiple sources."""
    
    def __init__(self):
        self.elements: List[IdentityElement] = []
    
    def add_element(self, key: str, value: str, source: str, confidence: float = 1.0) -> "MatchIdentityBuilder":
        """Add an identity element."""
        self.elements.append(IdentityElement(key=key, value=value, source=source, confidence=confidence))
        return self
    
    def build(self, match_id: str) -> MatchIdentity:
        """Build the match identity."""
        return MatchIdentity(match_id=match_id, elements=self.elements)


__all__ = ["MatchIdentity", "MatchIdentityBuilder", "ResolutionMethod", "IdentityElement"]
