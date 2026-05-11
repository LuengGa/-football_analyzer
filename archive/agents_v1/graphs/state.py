from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator
from enum import Enum


class MatchPhase(Enum):
    PRE_MATCH = "pre_match"
    IN_PLAY = "in_play"
    POST_MATCH = "post_match"


class AgentState(TypedDict):
    """
    AFA Agent System State (LangGraph State)
    
    遵循TradingAgents最佳实践：
    - 包含完整的比赛上下文
    - 包含各Agent的输出结果
    - 包含历史记忆（用于持续进化）
    """
    # 基础比赛信息
    match_id: str
    home_team: str
    away_team: str
    match_date: str
    phase: MatchPhase
    
    # Scout Agent 输出
    scout_report: Optional[Dict[str, Any]] = None
    match_intel: Optional[Dict[str, Any]] = None
    
    # Quant Agent 输出
    quant_report: Optional[Dict[str, Any]] = None
    elo_ratings: Optional[Dict[str, float]] = None
    poisson_probs: Optional[Dict[str, float]] = None
    
    # Market Agent 输出
    market_report: Optional[Dict[str, Any]] = None
    odds_data: Optional[Dict[str, float]] = None
    value_opportunities: Optional[List[Dict]] = None
    
    # Risk Agent 输出
    risk_report: Optional[Dict[str, Any]] = None
    kelly_stake: Optional[float] = None
    risk_level: Optional[str] = None  # "LOW", "MEDIUM", "HIGH"
    
    # Trader Agent 输出
    trader_decision: Optional[Dict[str, Any]] = None
    final_bet: Optional[Dict] = None
    
    # Auditor 输出（复盘用）
    auditor_feedback: Optional[Dict[str, Any]] = None
    
    # 历史记忆（Checkpoint恢复用）
    historical_decisions: Annotated[List[Dict[str, Any]], operator.add] = None
    memory_log: Optional[List[str]] = None
    
    # 系统状态
    current_step: str
    errors: List[str]
    
    # 消息历史（用于LLM对话）
    messages: Annotated[List, operator.add]
