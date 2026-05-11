"""
Domain Kernel - 领域核心模型
核心业务模型
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class PlayType(str, Enum):
    """玩法类型"""
    JINGCAI_WDL = "JINGCAI_WDL"
    JINGCAI_HANDICAP = "JINGCAI_HANDICAP"
    JINGCAI_GOALS = "JINGCAI_GOALS"
    JINGCAI_CS = "JINGCAI_CS"
    JINGCAI_HTFT = "JINGCAI_HTFT"
    BEIDAN_WDL = "BEIDAN_WDL"
    BEIDAN_HANDICAP = "BEIDAN_HANDICAP"
    BEIDAN_GOALS = "BEIDAN_GOALS"
    BEIDAN_CS = "BEIDAN_CS"
    BEIDAN_HTFT = "BEIDAN_HTFT"
    BEIDAN_SXDS = "BEIDAN_SXDS"
    BEIDAN_SFGG = "BEIDAN_SFGG"


@dataclass
class Play:
    """玩法"""
    type: PlayType
    selection: str
    odds: Optional[float] = None
    handicap: Optional[float] = None


@dataclass
class OddsModel:
    """赔率模型"""
    name: str
    version: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BacktestResult:
    """回测结果"""
    strategy_name: str
    start_date: str
    end_date: str
    total_bets: int
    winning_bets: int
    total_stake: float
    total_return: float
    roi: float
    win_rate: float
    profit_factor: Optional[float] = None
    max_drawdown: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DomainKernel:
    """领域核心服务"""
    
    @staticmethod
    def calculate_expected_value(probability: float, odds: float) -> float:
        """计算期望价值"""
        return probability * odds - 1.0
    
    @staticmethod
    def calculate_kelly_criterion(probability: float, odds: float, fraction: float = 1.0) -> float:
        """计算凯利公式投注比例"""
        if odds <= 1.0:
            return 0.0
        kelly = (probability * (odds) - 1) / (odds - 1)
        return max(0.0, min(kelly * fraction, 1.0))


__all__ = ["DomainKernel", "Play", "OddsModel", "BacktestResult", "PlayType"]
