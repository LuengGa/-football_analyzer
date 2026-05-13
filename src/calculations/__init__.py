"""
统一后的计算模块入口
=======================================

所有计算模块已分类到子目录:
- lottery/       : 彩票官方规则
- odds/          : 赔率分析
- quant/         : 量化计算
- backtesting/   : 回测引擎
- math/          : 数学计算
- pro/           : 专业计算
- settlement/    : 结算引擎
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .quant.six_layer_analyzer import EnhancedSixLayerAnalyzer as SixLayerAnalyzerV1
    from .quant.enhanced_six_layer import EnhancedSixLayerAnalyzer as SixLayerAnalyzerV2
    from .history.historical_data_manager import HistoricalDataManager as HistDataManager
    from .lottery.game_type_manager import GameTypeManager as GameTypeMgr

# 优先导入彩票官方规则 (单一真实来源)
try:
    from .lottery import (
        LotteryKnowledge,
        LOTTERY_KNOWLEDGE,
        get_lottery_knowledge,
        LotteryQuery,
        LOTTERY_QUERY,
        get_lottery_query,
        LotteryRouter,
        ChineseLotteryOfficialCalculator,
    )
except Exception as e:
    pass

# 向后兼容的导入 (可选，不影响核心功能)
try:
    from .backtesting.backtest_engine import *
    from .settlement.settlement_engine import *
    from .settlement.simulated_execution_engine import *
    from .odds.odds_analyzer import *
    from .odds.odds_converter import *
    from .odds.omni_market_pricer import *
    from .odds.market_probability_engine import *
    from .odds.bookmaker_analyzer import *
    from .odds.betfair_anomaly import *
    from .quant.advanced_lottery_math import *
    from .quant.hardcore_quant_math import *
    from .quant.bayesian_updater import *
    from .quant.dixon_coles import *
    from .quant.elo_calibrator import *
    from .quant.elo_rating import *
    from .quant.elo_storage import *
    from .quant.elo_update_service import *
    from .quant.enhanced_six_layer import *
    from .quant.kelly_variance_analyzer import *
    from .quant.monte_carlo_simulator import *
    from .quant.portfolio_optimizer import *
    from .quant.six_layer_analyzer import *
    from .quant.smart_bet_selector import *
    from .quant.st_gnn_simulator import *
    from .quant.trap_identifier import *
    from .quant.latency_arbitrage import *
    from .quant.clv_predictor import *
    from .quant.match_value_analyzer import *
    from .quant.player_xg_adjuster import *
    from .quant.environment_analyzer import *
    from .quant.pre_filter import *
    from .quant.anomaly_detector import *
    from .lottery.lottery_math_engine import *
    from .lottery.lottery_league_classifier import *
    from .lottery.game_type_manager import *
    from .lottery.mxn_calculator import *
    from .history.historical_data_loader import *
    from .history.historical_data_manager import *
    from .history.historical_impact import *
    from .utils.tool_registry_v2 import *
except ImportError as e:
    pass

__all__ = [
    "LotteryKnowledge",
    "LOTTERY_KNOWLEDGE",
    "get_lottery_knowledge",
    "LotteryQuery",
    "LOTTERY_QUERY",
    "get_lottery_query",
    "LotteryRouter",
    "ChineseLotteryOfficialCalculator",
]
