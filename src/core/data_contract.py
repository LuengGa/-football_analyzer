
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class NormalizedMatch:
    match_id: str
    league_code: str
    home_team_id: str
    away_team_id: str
    kickoff_time_utc: str
    status: str
    source: str
    confidence: float
    raw_ref: str
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    
    def __post_init__(self):
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class NormalizedOdds:
    match_id: str
    lottery_type: str
    play_type: str
    market: str
    handicap: Optional[float]
    selections: Dict[str, Dict]
    source: str
    confidence: float
    raw_ref: str
    
    def __post_init__(self):
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class NormalizedLiveState:
    match_id: str
    minute: Optional[int] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    is_live: bool = False
    source: Optional[str] = None
    raw_ref: Optional[str] = None


@dataclass
class NormalizedResult:
    match_id: str
    home_score: int
    away_score: int
    status: str = "FINISHED"
    source: Optional[str] = None
    raw_ref: Optional[str] = None


__all__ = ["NormalizedMatch", "NormalizedOdds", "NormalizedLiveState", "NormalizedResult"]
