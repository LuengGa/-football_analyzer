"""
回测和验证系统 - 基于历史数据验证策略有效性
============================================

功能:
- 使用历史数据回测投注策略
- 评估策略的ROI、胜率、最大回撤
- 验证Kelly准则的有效性
- 生成回测报告
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

from ..core.historical_data.loader import HistoricalDataLoader, MatchRecord
from ..core.historical_data.query_service import HistoricalQueryService

logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    """回测结果"""
    total_bets: int
    wins: int
    losses: int
    pushes: int
    win_rate: float
    total_staked: float
    total_return: float
    roi: float
    max_drawdown: float
    avg_odds: float
    profit_factor: float
    detailed_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BacktestConfig:
    """回测配置"""
    min_odds: float = 1.5
    max_odds: float = 10.0
    min_kelly: float = 0.05
    max_kelly: float = 0.25
    min_confidence: str = "MEDIUM"
    leagues: List[str] = field(default_factory=list)
    start_year: int = 2015
    end_year: int = 2024


class BacktestEngine:
    """回测引擎"""

    def __init__(self):
        self.loader = HistoricalDataLoader()
        self.query_service = HistoricalQueryService()

    def run_backtest(
        self,
        config: BacktestConfig,
        simulate_kelly: bool = True
    ) -> BacktestResult:
        """运行回测"""
        logger.info(f"开始回测: {config.start_year}-{config.end_year}")

        matches = self.loader.load_all()
        valid_matches = [
            m for m in matches
            if config.start_year <= m.year <= config.end_year
            and m.home_odds is not None
            and config.min_odds <= m.home_odds <= config.max_odds
            and (not config.leagues or m.league in config.leagues)
        ]

        logger.info(f"符合条件的比赛: {len(valid_matches)}")

        total_staked = 0.0
        total_return = 0.0
        wins = 0
        losses = 0
        pushes = 0
        detailed: list[dict[str, Any]] = []
        peak = 0.0
        max_dd = 0.0
        cumulative = 0.0

        for match in valid_matches:
            poisson = self._estimate_poisson(match)
            if not poisson:
                continue

            kelly = self._calculate_kelly(poisson, match.home_odds)
            if kelly < config.min_kelly or kelly > config.max_kelly:
                continue

            stake = 100.0 * kelly if simulate_kelly else 100.0
            total_staked += stake

            implied_prob = 1 / match.home_odds
            if poisson["home_win"] > implied_prob + 0.05:
                if match.result == "H":
                    profit = stake * (match.home_odds - 1)
                    wins += 1
                    outcome = "WIN"
                elif match.result == "D":
                    pushes += 1
                    profit = 0
                    outcome = "PUSH"
                else:
                    losses += 1
                    profit = -stake
                    outcome = "LOSS"
            else:
                losses += 1
                profit = -stake
                outcome = "SKIP" if match.result != "H" else "LOSS"

            cumulative += profit
            peak = max(peak, cumulative)
            drawdown = peak - cumulative
            max_dd = max(max_dd, drawdown)

            total_return += profit

            if len(detailed) < 1000:
                detailed.append({
                    "match": f"{match.home_team} vs {match.away_team}",
                    "date": match.date,
                    "result": match.result,
                    "odds": match.home_odds,
                    "prob": poisson["home_win"],
                    "kelly": kelly,
                    "stake": stake,
                    "profit": profit,
                    "cumulative": cumulative,
                    "outcome": outcome,
                })

        total_bets = wins + losses + pushes
        win_rate = wins / total_bets if total_bets > 0 else 0
        roi = (total_return / total_staked * 100) if total_staked > 0 else 0
        profit_factor = abs(total_return / (total_staked - total_return)) if total_staked > total_return else 0
        avg_odds = sum(m.home_odds for m in valid_matches[:total_bets]) / total_bets if total_bets > 0 else 0

        return BacktestResult(
            total_bets=total_bets,
            wins=wins,
            losses=losses,
            pushes=pushes,
            win_rate=win_rate,
            total_staked=total_staked,
            total_return=total_return,
            roi=roi,
            max_drawdown=max_dd,
            avg_odds=avg_odds,
            profit_factor=profit_factor,
            detailed_results=detailed,
        )

    def _estimate_poisson(self, match: MatchRecord) -> Optional[Dict[str, float]]:
        """估算泊松概率"""
        home_stats = self.query_service.get_team_statistics(match.home_team)
        away_stats = self.query_service.get_team_statistics(match.away_team)

        if not home_stats or home_stats.get("total_matches", 0) < 5:
            home_wr = 0.45
        else:
            home_wr = home_stats.get("win_rate", 0.45)

        if not away_stats or away_stats.get("total_matches", 0) < 5:
            away_wr = 0.35
        else:
            away_wr = away_stats.get("win_rate", 0.35)

        draw_rate = 1 - home_wr - away_wr
        draw_rate = max(0.2, min(0.35, draw_rate))

        avg_home = (home_wr + (1 - away_wr)) / 2
        avg_away = (away_wr + (1 - home_wr)) / 2
        avg_draw = draw_rate

        total = avg_home + avg_away + avg_draw
        if total > 0:
            return {
                "home_win": avg_home / total,
                "draw": avg_draw / total,
                "away_win": avg_away / total,
            }
        return None

    def _calculate_kelly(self, poisson: Dict[str, float], odds: float) -> float:
        """计算Kelly指数"""
        p = poisson["home_win"]
        b = odds - 1
        if b <= 0 or p <= 0:
            return 0
        kelly = (p * (b + 1) - 1) / b
        return max(0, min(0.25, kelly))

    def generate_report(self, result: BacktestResult) -> str:
        """生成回测报告"""
        report = []
        report.append("=" * 60)
        report.append("📊 回测报告")
        report.append("=" * 60)
        report.append(f"总投注数: {result.total_bets}")
        report.append(f"胜: {result.wins} | 负: {result.losses} | 走: {result.pushes}")
        report.append(f"胜率: {result.win_rate:.2%}")
        report.append(f"总投入: {result.total_staked:.2f}")
        report.append(f"总收益: {result.total_return:.2f}")
        report.append(f"ROI: {result.roi:+.2f}%")
        report.append(f"最大回撤: {result.max_drawdown:.2f}")
        report.append(f"平均赔率: {result.avg_odds:.2f}")
        report.append(f"盈利因子: {result.profit_factor:.2f}")
        report.append("=" * 60)

        if result.roi > 0:
            report.append("✅ 策略表现良好，正收益")
        else:
            report.append("⚠️ 策略需要优化，当前为负收益")

        return "\n".join(report)


def run_strategy_backtest(
    leagues: List[str] = None,
    years: Tuple[int, int] = (2015, 2024),
    min_kelly: float = 0.05
) -> BacktestResult:
    """运行策略回测的便捷函数"""
    config = BacktestConfig(
        leagues=leagues or ["E0", "D1", "SP1", "I1", "F1"],
        start_year=years[0],
        end_year=years[1],
        min_kelly=min_kelly,
    )

    engine = BacktestEngine()
    result = engine.run_backtest(config)

    print(engine.generate_report(result))

    return result


BACKTEST_ENGINE = BacktestEngine()


if __name__ == "__main__":
    print("=" * 60)
    print("🎯 策略回测系统测试")
    print("=" * 60)

    result = run_strategy_backtest(
        leagues=["E0"],
        years=(2020, 2024),
        min_kelly=0.05,
    )

    if result.detailed_results:
        print("\n最近10场比赛详情:")
        for bet in result.detailed_results[-10:]:
            print(f"  {bet['date']}: {bet['match']} | {bet['outcome']} | 盈亏: {bet['profit']:+.2f}")
