from .analyzer_api import *
from .asian_handicap_analyzer import *
from .bayesian_xg import *
from .dark_intel import *
from .domestic_500_beidan_sp import *
from .domestic_500_fixtures import *
from .domestic_500_jczq_sp import *
from .domestic_500_live_state import *
from .domestic_500_results import *
from .domestic_odds_500 import *
from .domestic_sources import *
from .entity_resolver import *
from .global_odds_fetcher import *
from .historical_db_loader import *
from .market_deep_analyzer import *
from .markowitz_portfolio import *
from .mcp_beidan_scraper import *
try:
    from .mcp_tools import *
except ImportError:
    pass
from .memory_manager import *
from .monte_carlo import *
from .multisource_fetcher import *
from .network_gatekeeper import *
from .parlay_filter_matrix import *
from .paths import *
from .snapshot_store import *
from .smart_money_tracker import *
try:
    from .statsbomb_tracking import *
except ImportError:
    pass
from .vision_odds_reader import *
from .visual_browser import *
from .waterfall_odds_fetcher import *
from .web_intel_extractor import *

# Check which files exist before importing
import os
from pathlib import Path

_odds_dir = Path(__file__).parent

# 增强工具 (可选导入)
_optional_modules = [
    "dixon_coles",
    "st_gnn_simulator",
    "bayesian_updater",
    "monte_carlo_simulator",
    "portfolio_optimizer",
    "market_probability_engine",
    "anomaly_detector",
    "backtest_engine",
    "smart_bet_selector",
    "elo_update_service",
    "player_xg_adjuster",
    "clv_predictor",
    "historical_impact",
]

for _mod in _optional_modules:
    _path = _odds_dir / f"{_mod}.py"
    if _path.exists():
        try:
            exec(f"from .{_mod} import *")
        except ImportError:
            pass
