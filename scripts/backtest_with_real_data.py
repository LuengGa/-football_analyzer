"""
AFA v9.0 真实历史数据回测验证系统
====================================

使用项目内的真实15万+历史数据进行回测验证
"""

import sys
import os
from typing import List, Dict, Any
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from src.core.historical_data.loader import HistoricalDataLoader
from src.calculations.pro.poisson_model import EnhancedPoissonGoalModel, AIPredictionContext
from src.calculations.pro.kelly_criterion import EnhancedKellyCriterion, AIRiskProfile


@dataclass
class BetRecord:
    """投注记录"""
    match_id: str
    date: str
    league: str
    home_team: str
    away_team: str
    bet_type: str
    odds: float
    stake: float
    predicted_prob: float
    value_edge: float
    won: bool
    profit: float


@dataclass
class BacktestResult:
    """回测结果"""
    total_bets: int
    wins: int
    losses: int
    win_rate: float
    total_stake: float
    net_profit: float
    roi: float
    max_drawdown: float
    sharpe_ratio: float
    league_stats: Dict[str, Dict]


def run_real_data_backtest(
    matches: List,
    use_ai_enhanced: bool = True,
    min_value_threshold: float = 0.03,
    initial_capital: float = 10000.0,
    max_bets: int = 5000
) -> BacktestResult:
    """使用真实数据进行回测"""

    logger.info(f"开始回测，使用 {len(matches)} 场真实比赛")

    poisson = EnhancedPoissonGoalModel()
    kelly = EnhancedKellyCriterion(initial_capital=initial_capital)

    all_bets: List[BetRecord] = []
    current_capital = initial_capital
    peak_capital = initial_capital
    max_drawdown = 0.0
    capital_history = [initial_capital]

    league_stats = {}

    for i, match in enumerate(matches):
        if i >= max_bets:
            break

        if match.home_odds is None or match.draw_odds is None or match.away_odds is None:
            continue

        if use_ai_enhanced:
            context = AIPredictionContext(
                has_injury=False,
                weather_impact="normal",
                recent_form=[True] * 5,
                home_advantage_active=True,
                historical_data_available=True
            )
            prediction = poisson.ai_predict_with_adjustments(
                match.home_team, match.away_team, context
            )
        else:
            prediction = poisson.predict(match.home_team, match.away_team)

        implied_probs = {
            "home": 1 / match.home_odds,
            "draw": 1 / match.draw_odds,
            "away": 1 / match.away_odds
        }

        predicted_probs = {
            "home": prediction.home_win_prob,
            "draw": prediction.draw_prob,
            "away": prediction.away_win_prob
        }

        value_bets = []
        for outcome in ["home", "draw", "away"]:
            predicted = predicted_probs[outcome]
            implied = implied_probs[outcome]
            edge = predicted - implied

            if edge >= min_value_threshold:
                odds = match.home_odds if outcome == "home" else \
                       match.draw_odds if outcome == "draw" else match.away_odds

                value_bets.append({
                    "outcome": outcome,
                    "odds": odds,
                    "predicted_prob": predicted,
                    "edge": edge
                })

        if not value_bets:
            continue

        best_bet = max(value_bets, key=lambda x: x["edge"])

        if use_ai_enhanced:
            ai_bet = kelly.ai_calculate_enhanced_kelly(
                win_prob=best_bet["predicted_prob"],
                odds_decimal=best_bet["odds"],
                confidence=prediction.confidence_score,
                risk_profile=AIRiskProfile(
                    risk_tolerance="moderate",
                    max_drawdown_tolerance=0.2,
                    confidence_weight=0.3,
                    recent_performance_weight=0.2,
                    portfolio_diversity=0.5
                ),
                portfolio_context={"concentration_risk": False}
            )
            stake = ai_bet.bet_size
        else:
            stake = 50.0

        if stake > current_capital * 0.1:
            stake = current_capital * 0.1
        if stake < 10:
            stake = 10

        # 转换result格式：H->home, D->draw, A->away
        result_map = {"H": "home", "D": "draw", "A": "away"}
        actual_result = result_map.get(match.result, match.result)

        won = False
        if actual_result == best_bet["outcome"]:
            won = True
            profit = stake * (best_bet["odds"] - 1)
        else:
            profit = -stake

        current_capital += profit
        capital_history.append(current_capital)

        if current_capital > peak_capital:
            peak_capital = current_capital

        drawdown = (peak_capital - current_capital) / peak_capital if peak_capital > 0 else 0
        if drawdown > max_drawdown:
            max_drawdown = drawdown

        bet_record = BetRecord(
            match_id=match.match_id,
            date=match.date,
            league=match.league_name,
            home_team=match.home_team,
            away_team=match.away_team,
            bet_type=best_bet["outcome"],
            odds=best_bet["odds"],
            stake=stake,
            predicted_prob=best_bet["predicted_prob"],
            value_edge=best_bet["edge"],
            won=won,
            profit=profit
        )
        all_bets.append(bet_record)

        if match.league_name not in league_stats:
            league_stats[match.league_name] = {"bets": 0, "wins": 0, "profit": 0}
        league_stats[match.league_name]["bets"] += 1
        if won:
            league_stats[match.league_name]["wins"] += 1
        league_stats[match.league_name]["profit"] += profit

    wins = sum(1 for b in all_bets if b.won)
    losses = len(all_bets) - wins
    win_rate = (wins / len(all_bets) * 100) if all_bets else 0
    total_stake = sum(b.stake for b in all_bets)
    net_profit = sum(b.profit for b in all_bets)
    roi = (net_profit / total_stake * 100) if total_stake > 0 else 0

    returns = []
    for i in range(1, len(capital_history)):
        if capital_history[i-1] > 0:
            r = (capital_history[i] - capital_history[i-1]) / capital_history[i-1]
            returns.append(r)

    sharpe_ratio = 0
    if returns and len(returns) > 1:
        import numpy as np
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        if std_return > 0:
            sharpe_ratio = (avg_return / std_return) * np.sqrt(52)

    return BacktestResult(
        total_bets=len(all_bets),
        wins=wins,
        losses=losses,
        win_rate=win_rate,
        total_stake=total_stake,
        net_profit=net_profit,
        roi=roi,
        max_drawdown=max_drawdown * 100,
        sharpe_ratio=sharpe_ratio,
        league_stats=league_stats
    )


def print_backtest_report(result: BacktestResult, title: str = "回测报告"):
    """打印回测报告"""
    print("\n" + "=" * 80)
    print(f"📊 {title}")
    print("=" * 80)

    print(f"\n🎯 核心指标:")
    print(f"   总投注次数: {result.total_bets}")
    print(f"   胜率: {result.win_rate:.1f}%")
    print(f"   胜/负: {result.wins} / {result.losses}")
    print(f"   总投注金额: ¥{result.total_stake:.0f}")
    print(f"   净利润: ¥{result.net_profit:.0f}")
    print(f"   ROI: {result.roi:.1f}%")
    print(f"   最大回撤: {result.max_drawdown:.1f}%")
    print(f"   夏普比率: {result.sharpe_ratio:.2f}")

    print(f"\n💰 盈亏分析:")
    if result.net_profit > 0:
        print(f"   ✅ 盈利 ¥{result.net_profit:.0f}")
    else:
        print(f"   ❌ 亏损 ¥{abs(result.net_profit):.0f}")

    if result.roi > 10:
        print(f"   ⭐ 优秀表现！ROI > 10%")
    elif result.roi > 5:
        print(f"   ✅ 良好表现！ROI > 5%")
    elif result.roi > 0:
        print(f"   ⚠️ 小幅盈利，仍有提升空间")
    else:
        print(f"   🔧 需要优化策略")

    print(f"\n📈 联赛表现 Top 5:")
    sorted_leagues = sorted(
        result.league_stats.items(),
        key=lambda x: x[1]["profit"],
        reverse=True
    )[:5]

    for league, stats in sorted_leagues:
        win_rate = stats["wins"] / stats["bets"] * 100 if stats["bets"] > 0 else 0
        print(f"   {league}: {stats['bets']}场 | 胜率{win_rate:.1f}% | 盈利¥{stats['profit']:.0f}")

    print(f"\n📉 联赛表现 Bottom 3:")
    for league, stats in sorted_leagues[-3:]:
        win_rate = stats["wins"] / stats["bets"] * 100 if stats["bets"] > 0 else 0
        print(f"   {league}: {stats['bets']}场 | 胜率{win_rate:.1f}% | 盈利¥{stats['profit']:.0f}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🚀 AFA v9.0 真实历史数据回测验证系统")
    print("=" * 80)

    print("\n📦 步骤1: 加载真实历史数据...")
    loader = HistoricalDataLoader()

    metadata = loader.load_metadata()
    print(f"   数据源: {metadata.get('source', 'unknown')}")
    print(f"   总比赛数: {metadata.get('total_matches', 0):,}")
    print(f"   时间范围: {metadata.get('date_range', 'unknown')}")

    stats = loader.load_stats()
    print(f"   完整赔率数据: {stats.get('complete_odds', 0):,}")
    print(f"   包含closing赔率: {stats.get('with_closing', 0):,}")

    print("\n⏳ 步骤2: 加载所有比赛数据（这可能需要几秒）...")
    matches = loader.load_all()
    print(f"   ✅ 成功加载 {len(matches):,} 场比赛")

    valid_matches = [m for m in matches if m.home_odds is not None]
    print(f"   ✅ 有赔率数据的比赛: {len(valid_matches):,}")

    print(f"\n🧪 步骤3: 运行传统策略回测...")
    traditional_result = run_real_data_backtest(
        valid_matches,
        use_ai_enhanced=False,
        min_value_threshold=0.03,
        max_bets=3000
    )
    print_backtest_report(traditional_result, "传统策略回测结果")

    print(f"\n🤖 步骤4: 运行AI增强策略回测...")
    ai_result = run_real_data_backtest(
        valid_matches,
        use_ai_enhanced=True,
        min_value_threshold=0.03,
        max_bets=3000
    )
    print_backtest_report(ai_result, "AI增强策略回测结果")

    print("\n📊 步骤5: 对比分析")
    print("=" * 80)
    print(f"   策略          胜率      ROI      净利润      最大回撤")
    print(f"   传统策略      {traditional_result.win_rate:.1f}%    {traditional_result.roi:+.1f}%    ¥{traditional_result.net_profit:+.0f}      {traditional_result.max_drawdown:.1f}%")
    print(f"   AI增强策略    {ai_result.win_rate:.1f}%    {ai_result.roi:+.1f}%    ¥{ai_result.net_profit:+.0f}      {ai_result.max_drawdown:.1f}%")

    improvement = ai_result.roi - traditional_result.roi
    if improvement > 0:
        print(f"\n   ⭐ AI增强策略提升了 {improvement:.1f}% 的ROI")
    else:
        print(f"\n   📊 两者表现相近，差异: {improvement:+.1f}%")

    print("\n💡 结论与建议:")
    if ai_result.roi > 5 and ai_result.win_rate > 52:
        print("   ✅ 系统表现优秀，适合进行小资金实盘测试")
        print("   📝 建议: 先用1000-2000元测试1-2周")
    elif ai_result.roi > 0:
        print("   ⚠️ 系统有盈利但不够稳定")
        print("   📝 建议: 继续优化参数，增加数据量测试")
    else:
        print("   🔧 系统需要进一步优化")
        print("   📝 建议: 检查数据质量，调整阈值参数")

    print("\n" + "=" * 80)
    print("✅ 真实历史数据回测验证完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()

