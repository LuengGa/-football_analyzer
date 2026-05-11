"""
Recommendation Schema - 推荐结果 schema
用于表示推荐投注信息
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class RecommendedBet:
    """单个推荐投注"""
    match_id: str
    lottery_type: str
    play_type: str
    market: str
    selection: str
    odds: Optional[float] = None
    probability: Optional[float] = None
    value_score: Optional[float] = None
    confidence: Optional[float] = None
    handicap: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecommendationSchema:
    """推荐结果"""
    timestamp: str
    recommended_bets: List[RecommendedBet] = field(default_factory=list)
    strategy_name: Optional[str] = None
    overall_confidence: Optional[float] = None
    risk_level: Optional[str] = None  # "low" | "medium" | "high"
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecommendationSchemaAdapter:
    """推荐结果适配器"""
    
    @staticmethod
    def to_dict(schema: RecommendationSchema) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": schema.timestamp,
            "recommended_bets": [
                {
                    "match_id": bet.match_id,
                    "lottery_type": bet.lottery_type,
                    "play_type": bet.play_type,
                    "market": bet.market,
                    "selection": bet.selection,
                    "odds": bet.odds,
                    "probability": bet.probability,
                    "value_score": bet.value_score,
                    "confidence": bet.confidence,
                    "handicap": bet.handicap,
                    "metadata": bet.metadata
                } for bet in schema.recommended_bets
            ],
            "strategy_name": schema.strategy_name,
            "overall_confidence": schema.overall_confidence,
            "risk_level": schema.risk_level,
            "metadata": schema.metadata
        }


__all__ = ["RecommendationSchema", "RecommendationSchemaAdapter", "RecommendedBet"]
