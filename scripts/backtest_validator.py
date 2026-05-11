"""
AFA v9.0 回测验证系统
=====================

目标：验证系统的预测准确率和盈利能力
"""

import sys
import os
import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculations.pro.poisson_model import EnhancedPoissonGoalModel, AIPredictionContext
from calculations.pro.kelly_criterion import EnhancedKellyCriterion, AIRiskProfile
from calculations.six_layer_analyzer import EnhancedSixLayerAnalyzer


@dataclass
class MatchData:
    """比赛数据"""
    match_id: str
    date: str
    league: str
    home_team: str
    away_team: str
    home_odds: float
    draw_odds: float
    away_odds: float
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None
    result: Optional[str] = None


@dataclass
class BetRecord:
    """投注记录"""
    match_id: str
    date: str
    home_team: str
    away_team: str
    bet_type: str
    odds: float
    stake: float
    predicted_prob: float
    actual_prob: float
    won: bool
    profit: float
    reasoning: str


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
    bets: List[BetRecord]


def generate_mock_matches(count: int = 500, leagues: List[str] = None) -> List[MatchData]:
    """生成模拟比赛数据"""
    if leagues is None:
        leagues = ["EPL", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]

    teams = {
        "EPL": ["Man City", "Arsenal", "Liverpool", "Man United", "Chelsea", "Tottenham",
                "Newcastle", "Brighton", "Aston Villa", "West Ham"],
        "La Liga": ["Real Madrid", "Barcelona", "Atletico Madrid", "Real Sociedad",
                   "Villarreal", "Sevilla", "Athletic Bilbao", "Real Betis"],
        "Serie A": ["Inter Milan", "AC Milan", "Juventus", "Napoli", "Roma",
                   "Lazio", "Atalanta", "Fiorentina"],
        "Bundesliga": ["Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Leverkusen",
                      "Union Berlin", "Freiburg", "Wolfsburg", "Eintracht Frankfurt"],
        "Ligue 1": ["PSG", "Marseille", "Monaco", "Lyon", "Lille", "Nice",
                   "Rennes", "Lens"]
    }

    matches = []
    base_date = datetime.now() - timedelta(days=count)

    for i in range(count):
        league = random.choice(leagues)
        league_teams = teams[league]
        home = random.choice(league_teams)
        away = random.choice([t for t in league_teams if t != home])

        base_date_i = base_date + timedelta(days=random.randint(0, count))
        date_str = base_date_i.strftime("%Y-%m-%d")

        odds_range = {
            "home": (1.5, 4.5),
            "draw": (3.0, 4.5),
            "away": (1.8, 6.0)
        }

        home_odds = round(random.uniform(*odds_range["home"]), 2)
        draw_odds = round(random.uniform(*odds_range["draw"]), 2)
        away_odds = round(random.uniform(*odds_range["away"]), 2)

        home_prob = 1 / home_odds + random.uniform(-0.05, 0.05)
        away_prob = 1 / away_odds + random.uniform(-0.05, 0.05)
        draw_prob = 1 - home_prob - away_prob

        if draw_prob < 0.2:
            draw_prob = 0.25
        if home_prob + away_prob + draw_prob > 1:
            total = home_prob + away_prob + draw_prob
            home_prob /= total
            away_prob /= total
            draw_prob /= total

        r = random.random()
        if r < home_prob:
            home_goals = random.randint(1, 4)
            away_goals = random.randint(0, home_goals - 1)
            result = "home"
        elif r < home_prob + away_prob:
            home_goals = random.randint(0, 2)
            away_goals = random.randint(home_goals + 1, 4)
            result = "away"
        else:
            home_goals = random.randint(0, 2)
            away_goals = home_goals
            result = "draw"

        match = MatchData(
            match_id=f"{league}_{home}_{away}_{date_str}",
            date=date_str,
            league=league,
            home_team=home,
            away_team=away,
            home_odds=home_odds,
            draw_odds=draw_odds,
            away_odds=away_odds,
            home_goals=home_goals,
            away_goals=away_goals,
            result=result
        )
        matches.append(match)

    return matches


def run_backtest(
    matches: List[MatchData],
    use_ai_enhanced: bool = True,
    min_value_threshold: float = 0.03,
    initial_capital: float = 10000.0
) -> BacktestResult:
    """运行回测"""

    poisson = EnhancedPoissonGoalModel()
    kelly = EnhancedKellyCriterion(initial_capital=initial_capital)
    six_layer = EnhancedSixLayerAnalyzer()

    all_bets: List[BetRecord] = []
    current_capital = initial_capital
    peak_capital = initial_capital
    max_drawdown = 0.0
    capital_history = []

    for match in matches:
        if use_ai_enhanced:
            context = AIPredictionContext(
                has_injury=random.random() < 0.1,
                weather_impact=random.choice(["normal", "normal", "rain"]),
                recent_form=[random.random() > 0.5 for _ in range(5)],
                home_advantage_active=True,
                historical_data_available=True
            )
            prediction = poisson.ai_predict_with_adjustments(
                match.home_team, match.away_team, context
            )
        else:
            prediction = poisson.predict(match.home_team, match.away_team)

        predicted_probs = {
            "home": prediction.home_win_prob,
            "draw": prediction.draw_prob,
            "away": prediction.away_win_prob
        }

        implied_probs = {
            "home": 1 / match.home_odds,
            "draw": 1 / match.draw_odds,
            "away": 1 / match.away_odds
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

        won = False
        if match.result == best_bet["outcome"]:
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

        reasoning = f"预测主队{ prediction.home_win_prob:.1%} | 庄家{implied_probs['home']:.1%} | 价值:{best_bet['edge']:.1%}"

        bet_record = BetRecord(
            match_id=match.match_id,
            date=match.date,
            home_team=match.home_team,
            away_team=match.away_team,
            bet_type=best_bet["outcome"],
            odds=best_bet["odds"],
            stake=stake,
            predicted_prob=best_bet["predicted_prob"],
            actual_prob=implied_probs[best_bet["outcome"]],
            won=won,
            profit=profit,
            reasoning=reasoning
        )
        all_bets.append(bet_record)

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
        bets=all_bets
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

    print(f"\n📈 最近10笔投注:")
    for bet in result.bets[-10:]:
        status = "✅" if bet.won else "❌"
        print(f"   {status} {bet.home_team} vs {bet.away_team} | "
              f"{bet.bet_type} @ {bet.odds} | "
              f"预测:{bet.predicted_prob:.1%} | "
              f"利润: ¥{bet.profit:.0f}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🚀 AFA v9.0 智能回测验证系统")
    print("=" * 80)

    print("\n📦 步骤1: 生成模拟比赛数据...")
    matches = generate_mock_matches(count=500)
    print(f"   ✅ 生成 {len(matches)} 场比赛")

    leagues = {}
    for m in matches:
        leagues[m.league] = leagues.get(m.league, 0) + 1
    print(f"   ✅ 涵盖 {len(leagues)} 个联赛: {', '.join(leagues.keys())}")

    print("\n🧪 步骤2: 运行传统策略回测...")
    traditional_result = run_backtest(matches, use_ai_enhanced=False)
    print_backtest_report(traditional_result, "传统策略回测结果")

    print("\n🤖 步骤3: 运行AI增强策略回测...")
    ai_result = run_backtest(matches, use_ai_enhanced=True)
    print_backtest_report(ai_result, "AI增强策略回测结果")

    print("\n📊 步骤4: 对比分析")
    print("=" * 80)
    print(f"   策略          胜率      ROI      净利润")
    print(f"   传统策略      {traditional_result.win_rate:.1f}%    {traditional_result.roi:+.1f}%    ¥{traditional_result.net_profit:+.0f}")
    print(f"   AI增强策略    {ai_result.win_rate:.1f}%    {ai_result.roi:+.1f}%    ¥{ai_result.net_profit:+.0f}")

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
    print("✅ 回测验证完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()

