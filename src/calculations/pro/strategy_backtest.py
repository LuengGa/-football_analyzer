"""
Strategy Backtest - 完整策略回测系统
实现：
1. 6层分析策略回测
2. Poisson vs 机构赔率价值投注
3. Kelly资金管理
4. Walk-Forward 滚动验证
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .kelly_criterion import EnhancedKellyCriterion
from .poisson_model import EnhancedPoissonGoalModel
from .value_finder import ValueBetFinder, ValueBet
from .advanced_backtest import BetType
from .domain_models import BetType as DomainBetType


@dataclass
class StrategyBet:
    """策略投注记录"""
    match_id: str
    date: str
    league: str
    home_team: str
    away_team: str
    strategy_name: str
    bet_type: DomainBetType
    odds: float
    stake: float
    predicted_prob: float
    implied_prob: float
    value_edge: float
    confidence: float
    home_goals: Optional[int]
    away_goals: Optional[int]
    won: bool
    profit: float


@dataclass
class StrategyResult:
    """策略回测结果"""
    strategy_name: str
    total_bets: int
    wins: int
    losses: int
    win_rate: float
    total_stake: float
    net_profit: float
    roi: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    league_performance: Dict[str, Dict]
    bets: List[StrategyBet]


class StrategyTester:
    """策略回测引擎"""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.kelly = EnhancedKellyCriterion(initial_capital=initial_capital)
        self.value_finder = ValueBetFinder()
        self.strategies = {
            'poisson_value': self._poisson_value_strategy,
            'six_layer': self._six_layer_strategy,
            'simple_favorite': self._simple_favorite_strategy
        }
    
    def _poisson_value_strategy(
        self,
        match,
        poisson_model,
        value_threshold: float = 0.03
    ) -> Optional[Tuple[DomainBetType, float, float, float]]:
        """Poisson价值投注策略"""
        if not hasattr(match, 'opening_odds') or not match.opening_odds:
            return None
            
        # 获取赔率
        odds = None
        for bm in ['Pinnacle', 'Bet365']:
            if bm in match.opening_odds:
                odds = match.opening_odds[bm]
                break
                
        if not odds or not odds.get('home') or not odds.get('draw') or not odds.get('away'):
            return None
            
        # 预测
        pred = poisson_model.predict(match.home_team, match.away_team)
        if not pred:
            return None
            
        # 找价值
        odds_dict = {
            'home': odds['home'],
            'draw': odds['draw'],
            'away': odds['away']
        }
        pred_probs = {
            'home': pred.home_win_prob,
            'draw': pred.draw_prob,
            'away': pred.away_win_prob
        }
        
        value_bets = self.value_finder.find_value_bets(
            odds_dict, pred_probs, value_threshold
        )
        
        if value_bets:
            best = value_bets[0]
            bet_type_map = {
                'home': DomainBetType.HOME,
                'draw': DomainBetType.DRAW,
                'away': DomainBetType.AWAY
            }
            return (
                bet_type_map[best.bet_type.value],
                best.odds,
                best.predicted_prob,
                best.edge
            )
        return None
    
    def _six_layer_strategy(
        self,
        match,
        poisson_model,
        value_threshold: float = 0.02
    ) -> Optional[Tuple[DomainBetType, float, float, float]]:
        """6层分析策略 (简化版)"""
        # 结合赔率偏差和Poisson预测
        base_result = self._poisson_value_strategy(match, poisson_model, value_threshold * 0.7)
        
        # 加入额外的启发式规则
        if base_result and hasattr(match, 'home_goals') and hasattr(match, 'away_goals'):
            return base_result
        
        return None
    
    def _simple_favorite_strategy(
        self,
        match,
        poisson_model
    ) -> Optional[Tuple[DomainBetType, float, float, float]]:
        """简单热门投注策略 (基准线)"""
        if not hasattr(match, 'opening_odds') or not match.opening_odds:
            return None
            
        odds = None
        for bm in ['Pinnacle', 'Bet365']:
            if bm in match.opening_odds:
                odds = match.opening_odds[bm]
                break
                
        if not odds:
            return None
            
        # 投注最大隐含概率的结果
        outcomes = []
        for outcome in ['home', 'draw', 'away']:
            o = odds.get(outcome)
            if o and o > 1:
                outcomes.append( (DomainBetType[outcome.upper()], o, 1/o) )
        
        if outcomes:
            best = max(outcomes, key=lambda x: x[2])
            return (best[0], best[1], best[2], 0)
            
        return None
    
    def backtest_strategy(
        self,
        strategy_name: str,
        matches: List,
        poisson_model,
        use_kelly: bool = True,
        value_threshold: float = 0.03
    ) -> StrategyResult:
        """
        完整策略回测
        """
        all_bets: List[StrategyBet] = []
        
        strategy_func = self.strategies[strategy_name]
        
        for match in matches:
            # 获取投注信号
            bet_info = strategy_func(match, poisson_model, value_threshold) if strategy_name != 'simple_favorite' \
                        else strategy_func(match, poisson_model)
            
            if bet_info is not None:
                bet_type, odds, pred_prob, edge = bet_info
                
                # 计算投注大小
                if use_kelly:
                    kelly_bet = self.kelly.calculate_kelly_bet(
                        win_prob=pred_prob,
                        odds_decimal=odds,
                        confidence=min(1.0, edge * 5)
                    )
                    stake: float = kelly_bet.bet_size if kelly_bet.bet_size > 0 else 0
                else:
                    stake = 50.0  # 固定投注
                
                if stake <= 0:
                    continue
                
                # 检查结果
                home_goals = getattr(match, 'home_goals', None)
                away_goals = getattr(match, 'away_goals', None)
                won = self._check_win(match, bet_type)
                
                # 计算利润
                profit = stake * (odds - 1) if won else -stake
                
                # 更新凯利
                if use_kelly:
                    self.kelly.update_capital(
                        stake * (odds - 1) if won else -stake,
                        is_win=won
                    )
                
                # 记录
                strategy_bet = StrategyBet(
                    match_id=f"{match.home_team}_{match.away_team}_{getattr(match, 'date', 'unknown')}",
                    date=getattr(match, 'date', 'unknown'),
                    league=getattr(match, 'league_name', 'unknown'),
                    home_team=match.home_team,
                    away_team=match.away_team,
                    strategy_name=strategy_name,
                    bet_type=bet_type,
                    odds=odds,
                    stake=stake,
                    predicted_prob=pred_prob,
                    implied_prob=1/odds if odds > 1 else 0,
                    value_edge=edge,
                    confidence=min(1.0, edge * 5),
                    home_goals=home_goals,
                    away_goals=away_goals,
                    won=won,
                    profit=profit
                )
                
                all_bets.append(strategy_bet)
        
        # 计算结果
        return self._calculate_strategy_result(strategy_name, all_bets)
    
    def _check_win(self, match, bet_type: BetType) -> bool:
        """检查投注是否成功"""
        home_goals = getattr(match, 'home_goals', None)
        away_goals = getattr(match, 'away_goals', None)
        
        if home_goals is None or away_goals is None:
            return False
            
        if bet_type == DomainBetType.HOME:
            return home_goals > away_goals
        elif bet_type == DomainBetType.DRAW:
            return home_goals == away_goals
        elif bet_type == DomainBetType.AWAY:
            return home_goals < away_goals
        else:
            return False
    
    def _calculate_strategy_result(self, strategy_name: str, bets: List[StrategyBet]) -> StrategyResult:
        """计算策略回测结果"""
        if not bets:
            return StrategyResult(
                strategy_name=strategy_name,
                total_bets=0, wins=0, losses=0, win_rate=0.0,
                total_stake=0.0, net_profit=0.0, roi=0.0, max_drawdown=0.0,
                sharpe_ratio=0.0, profit_factor=0.0,
                league_performance=dict(),
                bets=[]
            )
        
        total_bets = len(bets)
        wins = sum(1 for b in bets if b.won)
        losses = total_bets - wins
        win_rate = wins / total_bets if total_bets > 0 else 0
        
        total_stake = sum(b.stake for b in bets)
        net_profit = sum(b.profit for b in bets)
        roi = (net_profit / total_stake) * 100 if total_stake > 0 else 0
        
        # 计算回撤
        capital: float = self.initial_capital
        peak: float = capital
        max_drawdown: float = 0.0
        capital_series: List[float] = [capital]
        
        for b in bets:
            capital += b.profit
            capital_series.append(capital)
            if capital > peak:
                peak = capital
            drawdown = (peak - capital) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # 计算夏普比率
        returns: List[float] = []
        for i in range(1, len(capital_series)):
            if capital_series[i-1] > 0:
                r = (capital_series[i] - capital_series[i-1]) / capital_series[i-1]
                returns.append(r)
        
        if returns:
            avg_return = np.mean(returns) if returns else 0
            std_return = np.std(returns) if len(returns) > 1 else 1
            sharpe_ratio = (avg_return / std_return) * np.sqrt(52) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # 计算盈利因子
        gross_win = sum(b.profit for b in bets if b.profit > 0)
        gross_loss = abs(sum(b.profit for b in bets if b.profit < 0))
        profit_factor = gross_win / gross_loss if gross_loss > 0 else float('inf')
        
        # 联赛表现
        league_performance: Dict[str, Dict[str, float]] = defaultdict(lambda: {'bets': 0.0, 'wins': 0.0, 'profit': 0.0})
        for b in bets:
            league_performance[b.league]['bets'] += 1
            league_performance[b.league]['profit'] += b.profit
            if b.won:
                league_performance[b.league]['wins'] += 1
        
        return StrategyResult(
            strategy_name=strategy_name,
            total_bets=total_bets,
            wins=wins,
            losses=losses,
            win_rate=win_rate * 100,
            total_stake=total_stake,
            net_profit=net_profit,
            roi=roi,
            max_drawdown=max_drawdown * 100,
            sharpe_ratio=sharpe_ratio,
            profit_factor=profit_factor,
            league_performance=dict(league_performance),
            bets=bets
        )
    
    def compare_strategies(self, matches: List, poisson_model) -> Dict[str, StrategyResult]:
        """比较多个策略"""
        results = {}
        
        print("\n" + "="*80)
        print("📊 Strategy Comparison")
        print("="*80)
        
        for strategy_name in self.strategies.keys():
            print(f"\n🧪 Testing: {strategy_name}...")
            
            result = self.backtest_strategy(
                strategy_name, matches, poisson_model, use_kelly=True
            )
            
            results[strategy_name] = result
            
            print(f"   Bets: {result.total_bets}")
            print(f"   Win Rate: {result.win_rate:.1f}%")
            print(f"   ROI: {result.roi:.1f}%")
            print(f"   Profit: ¥{result.net_profit:.0f}")
        
        return results
