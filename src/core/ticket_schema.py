"""
Ticket Schema - 投注票 schema
用于表示彩票投注票
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class TicketLeg:
    """单注腿"""
    match_id: str
    play_type: str
    selection: str
    odds: Optional[float] = None
    handicap: Optional[float] = None
    confidence: Optional[float] = None


@dataclass
class LotteryTicket:
    """彩票投注票"""
    ticket_id: str
    lottery_type: str  # "JINGCAI" | "BEIDAN" | "ZUCAI"
    play_type: str
    legs: List[TicketLeg] = field(default_factory=list)
    stake: Optional[float] = None
    total_odds: Optional[float] = None
    expected_return: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


__all__ = ["LotteryTicket", "TicketLeg"]
