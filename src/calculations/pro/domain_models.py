"""
Domain Models - 统一数据契约与API
v7.0 系统核心数据模型，定义所有模块共享的数据结构
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Union
from enum import Enum
from datetime import datetime


class BetType(Enum):
    """投注类型枚举 - 扩展版"""
    HOME = "home"
    DRAW = "draw"
    AWAY = "away"
    
    # 大小球 (多种球门线)
    OVER_0_5 = "over_0_5"
    UNDER_0_5 = "under_0_5"
    OVER_1_5 = "over_1_5"
    UNDER_1_5 = "under_1_5"
    OVER_2_5 = "over_2_5"
    UNDER_2_5 = "under_2_5"
    OVER_3_5 = "over_3_5"
    UNDER_3_5 = "under_3_5"
    OVER_4_5 = "over_4_5"
    UNDER_4_5 = "under_4_5"
    
    # 双方进球
    BOTH_TEAMS_TO_SCORE = "btts"
    BOTH_TEAMS_TO_SCORE_YES = "btts_yes"
    BOTH_TEAMS_TO_SCORE_NO = "btts_no"
    
    # 双胜
    DOUBLE_CHANCE_HOME_DRAW = "dc_hd"
    DOUBLE_CHANCE_HOME_AWAY = "dc_ha"
    DOUBLE_CHANCE_DRAW_AWAY = "dc_da"
    
    # 比分预测
    CORRECT_SCORE_0_0 = "cs_0_0"
    CORRECT_SCORE_1_0 = "cs_1_0"
    CORRECT_SCORE_0_1 = "cs_0_1"
    CORRECT_SCORE_1_1 = "cs_1_1"
    CORRECT_SCORE_2_0 = "cs_2_0"
    CORRECT_SCORE_0_2 = "cs_0_2"
    CORRECT_SCORE_2_1 = "cs_2_1"
    CORRECT_SCORE_1_2 = "cs_1_2"
    CORRECT_SCORE_2_2 = "cs_2_2"
    CORRECT_SCORE_OTHER = "cs_other"
    
    # 半场玩法
    HALF_TIME_HOME = "ht_home"
    HALF_TIME_DRAW = "ht_draw"
    HALF_TIME_AWAY = "ht_away"
    
    # 半全场 (9种组合)
    HTFT_HH = "htft_hh"
    HTFT_HD = "htft_hd"
    HTFT_HA = "htft_ha"
    HTFT_DH = "htft_dh"
    HTFT_DD = "htft_dd"
    HTFT_DA = "htft_da"
    HTFT_AH = "htft_ah"
    HTFT_AD = "htft_ad"
    HTFT_AA = "htft_aa"
    
    # 角球玩法
    CORNERS_OVER = "corners_over"
    CORNERS_UNDER = "corners_under"
    CORNERS_HOME_OVER = "corners_home_over"
    CORNERS_AWAY_OVER = "corners_away_over"
    
    # 总进球数 (精确)
    TOTAL_GOALS_0 = "tg_0"
    TOTAL_GOALS_1 = "tg_1"
    TOTAL_GOALS_2 = "tg_2"
    TOTAL_GOALS_3 = "tg_3"
    TOTAL_GOALS_4 = "tg_4"
    TOTAL_GOALS_5_PLUS = "tg_5_plus"
    
    # 进球单双
    GOALS_ODD = "goals_odd"
    GOALS_EVEN = "goals_even"


@dataclass
class MatchOdds:
    """比赛赔率数据"""
    bookmaker: str
    home: Optional[float] = None
    draw: Optional[float] = None
    away: Optional[float] = None
    over_2_5: Optional[float] = None
    under_2_5: Optional[float] = None
    asian_handicap: Optional[Dict[str, Any]] = None


@dataclass
class MatchStats:
    """比赛统计数据"""
    shots: Optional[Dict[str, int]] = None
    shots_on_target: Optional[Dict[str, int]] = None
    corners: Optional[Dict[str, int]] = None
    fouls: Optional[Dict[str, int]] = None
    yellow_cards: Optional[Dict[str, int]] = None
    red_cards: Optional[Dict[str, int]] = None


@dataclass
class HalfTimeScore:
    """半场比分"""
    home: Optional[int] = None
    away: Optional[int] = None


@dataclass
class HistoricalMatch:
    """历史比赛核心数据契约"""
    match_id: str
    date: str
    league: str
    league_name: str
    season: str
    season_year: int
    home_team: str
    away_team: str
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None
    result: Optional[str] = None
    half_time: Optional[HalfTimeScore] = None
    match_stats: Optional[MatchStats] = None
    opening_odds: Dict[str, MatchOdds] = field(default_factory=dict)
    closing_odds: Dict[str, MatchOdds] = field(default_factory=dict)
    bookmakers_count: int = 0

    @property
    def has_full_odds(self) -> bool:
        return len(self.opening_odds) > 0 and len(self.closing_odds) > 0

    @property
    def has_home_odds(self) -> bool:
        return any(odds.home is not None for odds in self.opening_odds.values())


@dataclass
class PredictionResult:
    """预测结果通用结构"""
    model_name: str
    home_win_prob: float = 0.0
    draw_prob: float = 0.0
    away_win_prob: float = 0.0
    expected_home_goals: float = 0.0
    expected_away_goals: float = 0.0
    predicted_score: str = ""
    confidence: float = 0.0


@dataclass
class ValueBetOpportunity:
    """价值投注机会"""
    match_id: str
    home_team: str
    away_team: str
    bet_type: BetType
    odds: float
    implied_prob: float
    predicted_prob: float
    edge: float
    expected_value: float
    confidence: float
    kelly_fraction: Optional[float] = None


@dataclass
class BacktestResult:
    """回测结果"""
    strategy_name: str
    total_bets: int
    wins: int
    losses: int
    win_rate: float
    total_staked: float
    net_profit: float
    roi: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    start_capital: float
    end_capital: float
    bets: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TeamRating:
    """球队评级"""
    team_name: str
    rating: float
    rating_deviation: float = 350
    volatility: float = 0.06
    games_played: int = 0
    last_update: str = ""


@dataclass
class LeagueInfo:
    """联赛信息"""
    league_id: str
    league_name: str
    country: str
    tier: int
    avg_goals_per_match: float
    avg_home_goals: float
    avg_away_goals: float
    avg_total_goals: float
    home_win_rate: float
    draw_rate: float
    away_win_rate: float


# ==== API Interfaces ====

class ModelTrainer:
    """模型训练器接口"""

    def fit(self, matches: List[HistoricalMatch]) -> None:
        raise NotImplementedError

    def predict(self, home_team: str, away_team: str, league: Optional[str] = None) -> Optional[PredictionResult]:
        raise NotImplementedError


class Strategy:
    """策略接口"""

    def generate_bets(self, matches: List[HistoricalMatch], predictor) -> List[ValueBetOpportunity]:
        raise NotImplementedError


class Backtester:
    """回测引擎接口"""

    def run_backtest(self, matches: List[HistoricalMatch], strategy, start_capital: float = 10000) -> BacktestResult:
        raise NotImplementedError
