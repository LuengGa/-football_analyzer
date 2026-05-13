"""
Advanced Backtest Engine - 专业级回测引擎
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any, Union
from dataclasses import dataclass
from collections import defaultdict
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .domain_models import BetType

@dataclass
class AdvancedBet:
    """高级投注记录"""
    match_id: str
    date: str
    league: str
    home_team: str
    away_team: str
    bet_type: BetType
    odds: float
    stake: float
    result: Optional[str]
    home_goals: Optional[int]
    away_goals: Optional[int]
    won: bool = False
    profit: float = 0.0
    confidence: float = 0.0

@dataclass
class AdvancedBacktestResult:
    """高级回测结果"""
    total_bets: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    total_staked: float = 0.0
    total_return: float = 0.0
    net_profit: float = 0.0
    roi: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    profit_factor: float = 0.0
    cagr: float = 0.0
    bets_by_league: Optional[Dict[str, Dict[Any, Any]]] = None
    monthly_returns: Optional[Dict[str, float]] = None
    bets: Optional[List[AdvancedBet]] = None

class AdvancedBacktestEngine:
    """专业级回测引擎"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.peak_capital = initial_capital
        self.bets: List[AdvancedBet] = []
        self.capital_history: List[float] = [initial_capital]
    
    def reset(self):
        """重置回测引擎"""
        self.capital = self.initial_capital
        self.peak_capital = self.initial_capital
        self.bets = []
        self.capital_history = [self.initial_capital]
    
    def place_bet(
        self,
        match,
        bet_type: BetType,
        odds: float,
        stake: float,
        confidence: float = 0.5
    ) -> Optional[AdvancedBet]:
        """
        下投注单
        
        Args:
            match: 比赛对象
            bet_type: 投注类型
            odds: 赔率
            stake: 投注金额
            confidence: 信心度
        """
        # 确定是否中奖
        won = self._check_win(match, bet_type)
        profit = stake * (odds - 1) if won else -stake
        
        # 更新资金
        self.capital += profit
        self.capital_history.append(self.capital)
        
        # 更新峰值
        if self.capital > self.peak_capital:
            self.peak_capital = self.capital
        
        # 创建投注记录
        bet = AdvancedBet(
            match_id=match.match_id if hasattr(match, 'match_id') else f"{match.home_team}_{match.away_team}",
            date=match.date if hasattr(match, 'date') else "unknown",
            league=match.league_name if hasattr(match, 'league_name') else "unknown",
            home_team=match.home_team,
            away_team=match.away_team,
            bet_type=bet_type,
            odds=odds,
            stake=stake,
            result=match.result if hasattr(match, 'result') else None,
            home_goals=match.home_goals if hasattr(match, 'home_goals') else None,
            away_goals=match.away_goals if hasattr(match, 'away_goals') else None,
            won=won,
            profit=profit,
            confidence=confidence
        )
        
        self.bets.append(bet)
        return bet
    
    def _check_win(self, match: Any, bet_type: BetType) -> bool:
        """检查是否中奖"""
        if not hasattr(match, 'home_goals') or match.home_goals is None:
            return False  # type: ignore[return-value]
        if not hasattr(match, 'away_goals') or match.away_goals is None:
            return False  # type: ignore[return-value]
        
        home_goals = match.home_goals  # type: ignore[union-attr]
        away_goals = match.away_goals  # type: ignore[union-attr]
        total_goals = home_goals + away_goals
        
        if bet_type == BetType.HOME:
            return home_goals > away_goals  # type: ignore[no-any-return]
        elif bet_type == BetType.DRAW:
            return home_goals == away_goals  # type: ignore[no-any-return]
        elif bet_type == BetType.AWAY:
            return home_goals < away_goals  # type: ignore[no-any-return]
        elif bet_type == BetType.OVER_2_5:
            return total_goals > 2.5  # type: ignore[no-any-return]
        elif bet_type == BetType.UNDER_2_5:
            return total_goals < 2.5  # type: ignore[no-any-return]
        else:
            return False
    
    def calculate_metrics(self) -> AdvancedBacktestResult:
        """计算回测指标"""
        if not self.bets:
            return AdvancedBacktestResult()
        
        total_bets = len(self.bets)
        wins = sum(1 for b in self.bets if b.won)
        losses = total_bets - wins
        win_rate = wins / total_bets if total_bets > 0 else 0
        total_staked = sum(b.stake for b in self.bets)
        total_return = sum(max(0, b.profit + b.stake) for b in self.bets)
        net_profit = self.capital - self.initial_capital
        roi = (net_profit / total_staked) * 100 if total_staked > 0 else 0
        
        # 最大回撤
        max_drawdown = self._calculate_max_drawdown()
        
        # 夏普比率
        sharpe_ratio = self._calculate_sharpe_ratio()
        
        # 盈利因子
        gross_win = sum(b.profit for b in self.bets if b.profit > 0)
        gross_loss = abs(sum(b.profit for b in self.bets if b.profit < 0))
        profit_factor = gross_win / gross_loss if gross_loss > 0 else float('inf')
        
        # CAGR (假设是3年数据)
        cagr = self._calculate_cagr()
        
        # 联赛表现
        bets_by_league: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'bets': 0, 'wins': 0, 'profit': 0.0})
        for bet in self.bets:
            bets_by_league[bet.league]['bets'] += 1
            bets_by_league[bet.league]['profit'] += bet.profit
            if bet.won:
                bets_by_league[bet.league]['wins'] += 1
        
        # 月度收益
        monthly_returns = self._calculate_monthly_returns()
        
        return AdvancedBacktestResult(
            total_bets=total_bets,
            wins=wins,
            losses=losses,
            win_rate=win_rate * 100,
            total_staked=total_staked,
            total_return=total_return,
            net_profit=net_profit,
            roi=roi,
            max_drawdown=max_drawdown * 100,
            sharpe_ratio=sharpe_ratio,
            profit_factor=profit_factor,
            cagr=cagr * 100,
            bets_by_league=dict(bets_by_league),
            monthly_returns=monthly_returns,
            bets=self.bets
        )
    
    def _calculate_max_drawdown(self) -> float:
        """计算最大回撤"""
        max_dd = 0.0
        peak = self.capital_history[0]
        
        for value in self.capital_history:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """计算夏普比率 (简化版)"""
        if len(self.capital_history) < 2:
            return 0.0
        
        # 计算日收益率
        returns = []
        for i in range(1, len(self.capital_history)):
            if self.capital_history[i-1] <= 0:
                ret: float = 0
            else:
                ret = (self.capital_history[i] - self.capital_history[i-1]) / self.capital_history[i-1]
            returns.append(ret)
        
        if not returns:
            return 0.0
        
        avg_return = sum(returns) / len(returns)
        std_return = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / len(returns)) if len(returns) > 1 else 0
        
        if std_return == 0:
            return 0.0
        
        # 年化（假设 365 天，但实际比赛更少，用简化）
        annual_factor = math.sqrt(52)  # 假设每周
        return ((avg_return * 52) - risk_free_rate) / (std_return * annual_factor) if std_return != 0 else 0
    
    def _calculate_cagr(self, years: float = 3.0) -> float:
        """计算 CAGR"""
        if self.initial_capital <= 0:
            return 0.0
        return (self.capital / self.initial_capital) ** (1 / years) - 1  # type: ignore[no-any-return]
    
    def _calculate_monthly_returns(self) -> Dict[str, float]:
        """计算月度收益"""
        return {}  # type: ignore[return-value]
    
    def print_summary(self, result: AdvancedBacktestResult):
        """打印回测摘要"""
        print("\n" + "="*80)
        print("📊 专业级回测结果摘要")
        print("="*80)
        
        print(f"\n🎯 投注统计:")
        print(f"  总投注: {result.total_bets:,} 场")
        print(f"  命中: {result.wins:,} 场 ({result.win_rate:.1f}%)")
        print(f"  未中: {result.losses:,} 场 ({100-result.win_rate:.1f}%)")
        
        print(f"\n💰 资金统计:")
        print(f"  初始资金: ¥{self.initial_capital:,.2f}")
        print(f"  最终资金: ¥{self.capital:,.2f}")
        print(f"  总投入: ¥{result.total_staked:,.2f}")
        print(f"  净利润: ¥{result.net_profit:,.2f}")
        print(f"  ROI: {result.roi:.2f}%")
        
        print(f"\n📈 风险指标:")
        print(f"  最大回撤: {result.max_drawdown:.2f}%")
        print(f"  夏普比率: {result.sharpe_ratio:.3f}")
        print(f"  盈利因子: {result.profit_factor:.2f}")
        print(f"  CAGR: {result.cagr:.2f}%")
        
        if result.bets_by_league:
            print(f"\n🏆 最佳联赛 (Top 5):")
            sorted_leagues = sorted(
                result.bets_by_league.items(),
                key=lambda x: x[1]['profit'],
                reverse=True
            )[:5]
            for league, stats in sorted_leagues:
                win_rate_l = (stats['wins'] / stats['bets']) * 100 if stats['bets'] > 0 else 0
                print(f"  {league}: {stats['bets']}场, ¥{stats['profit']:,.0f}, {win_rate_l:.1f}%")
        
        print("\n" + "="*80)
