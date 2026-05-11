#!/usr/bin/env python3
"""
AFA 工具集 — 统一的 CLI 接口，供 agent 调用。

用法: python3 afa_toolkit.py <tool_name> [--param value ...]

示例:
  python3 afa_toolkit.py elo_calculate --home-elo 1650 --away-elo 1580
  python3 afa_toolkit.py dixon_coles --home-attack 1.2 --home-defense -0.3 --away-attack 0.9 --away-defense -0.1
  python3 afa_toolkit.py kelly --probability 0.65 --odds 1.8 --bankroll 10000
  python3 afa_toolkit.py market_probability --odds-home 2.1 --odds-draw 3.4 --odds-away 3.6
  python3 afa_toolkit.py monte_carlo --home-attack 1.2 --away-defense -0.3 --away-attack 0.9 --home-defense -0.1
  python3 afa_toolkit.py trap_detection --odds 1.8 --true-probability 0.55
  python3 afa_toolkit.py bayesian --prior-alpha 10 --prior-beta 10 --observed-wins 8 --observed-losses 2
  python3 afa_toolkit.py comprehensive --home-elo 1650 --away-elo 1580 --odds-home 2.1 --odds-draw 3.4 --odds-away 3.6
  python3 afa_toolkit.py mxn --lottery jingcai --selections '[[2.1,3.4,3.6],[1.8,3.5,4.0]]' --pass-mode 2x1
  python3 afa_toolkit.py clv --odds 3.0 --true-prob 0.35
  python3 afa_toolkit.py portfolio --returns '[0.05, 0.03]' --cov-matrix '[[0.1,0.02],[0.02,0.08]]'
  python3 afa_toolkit.py lottery_return --odds-list '[2.1, 3.4, 3.6]' --lottery-type jingcai
"""

import sys, json, math, argparse

def _import(src_path: str, name: str):
    """Import 'name' from 'src_path' module."""
    import importlib
    mod = importlib.import_module(src_path)
    return getattr(mod, name)

def cmd_elo(args):
    elo = _import("src.calculations.elo_rating", "ELORatingSystem")()
    exp_home = 1.0 / (1.0 + 10 ** ((args.away_elo - args.home_elo) / 400.0))
    result = {
        "expected_home_win_prob": round(exp_home, 4),
        "expected_away_win_prob": round(1 - exp_home, 4),
        "home_elo": args.home_elo,
        "away_elo": args.away_elo,
    }
    if args.home_goals is not None and args.away_goals is not None:
        actual_home = 1.0 if args.home_goals > args.away_goals else (0.5 if args.home_goals == args.away_goals else 0.0)
        new_home = args.home_elo + args.k_factor * (actual_home - exp_home)
        new_away = args.away_elo + args.k_factor * ((1 - actual_home) - (1 - exp_home))
        result.update(new_home_elo=round(new_home, 1), new_away_elo=round(new_away, 1))
    return result

def cmd_dixon_coles(args):
    lam_h = math.exp(args.home_attack + args.away_defense + args.home_advantage)
    lam_a = math.exp(args.away_attack + args.home_defense)
    MAX = 8
    hw = dw = aw = 0.0
    for i in range(MAX + 1):
        pi = (lam_h ** i) * math.exp(-lam_h) / math.factorial(i)
        for j in range(MAX + 1):
            prob = pi * ((lam_a ** j) * math.exp(-lam_a) / math.factorial(j))
            if i > j: hw += prob
            elif i == j: dw += prob
            else: aw += prob
    return {
        "expected_home_goals": round(lam_h, 3),
        "expected_away_goals": round(lam_a, 3),
        "home_win_prob": round(hw, 4),
        "draw_prob": round(dw, 4),
        "away_win_prob": round(aw, 4),
    }

def cmd_kelly(args):
    implied = 1.0 / args.odds
    edge = args.probability - implied
    kelly = edge / (args.odds - 1) if edge > 0 and args.odds > 1 else 0
    quarter = kelly * 0.25
    return {
        "implied_probability": round(implied, 4),
        "user_probability": round(args.probability, 4),
        "edge": round(edge, 4),
        "has_edge": edge > 0,
        "kelly_fraction": round(kelly, 6),
        "kelly_bet_amount": round(kelly * args.bankroll, 2),
        "quarter_kelly_pct": round(quarter * 100, 2),
    }

def cmd_market_prob(args):
    mpe = _import("src.calculations.market_probability_engine", "MarketProbabilityEngine")()
    return mpe.implied_probabilities_from_odds({"home": args.odds_home, "draw": args.odds_draw, "away": args.odds_away})

def cmd_monte_carlo(args):
    lam_h = max(0.01, math.exp(args.home_attack + args.away_defense))
    lam_a = max(0.01, math.exp(args.away_attack + args.home_defense))
    sim = _import("src.calculations.monte_carlo_simulator", "TimeSliceMonteCarlo")(time_slices=90)
    return sim.simulate_match(lam_h, lam_a, simulations=args.n)

def cmd_trap(args):
    fn = _import("src.calculations.trap_identifier", "identify_low_odds_trap")
    return fn(args.odds, args.true_probability, args.vig)

def cmd_bayesian(args):
    pa = args.prior_alpha + args.observed_wins
    pb = args.prior_beta + args.observed_losses
    posterior = pa / (pa + pb) if (pa + pb) > 0 else 0.5
    prior = args.prior_alpha / (args.prior_alpha + args.prior_beta) if (args.prior_alpha + args.prior_beta) > 0 else 0.5
    return {
        "prior_mean": round(prior, 4),
        "posterior_mean": round(posterior, 4),
        "shift": round(posterior - prior, 4),
        "total_observations": args.observed_wins + args.observed_losses,
    }

def cmd_comprehensive(args):
    result = {"home": args.home, "away": args.away}
    # Elo
    exp_h = 1.0 / (1.0 + 10 ** ((args.away_elo - args.home_elo) / 400.0))
    result["elo"] = {"home_win_prob": round(exp_h, 4), "away_win_prob": round(1 - exp_h, 4)}
    # Market
    mpe = _import("src.calculations.market_probability_engine", "MarketProbabilityEngine")()
    result["market"] = mpe.implied_probabilities_from_odds({"home": args.odds_home, "draw": args.odds_draw, "away": args.odds_away})
    # Integrated
    avg_h = (exp_h + result["market"]["home"]) / 2
    avg_a = (1 - exp_h + result["market"]["away"]) / 2
    result["ensemble"] = {"home_win_prob": round(avg_h, 4), "away_win_prob": round(avg_a, 4)}
    # Edge
    implied_h = 1.0 / args.odds_home
    edge = avg_h - implied_h
    if edge > 0:
        kelly = edge / (args.odds_home - 1) if args.odds_home > 1 else 0
        result["kelly"] = {"edge": round(edge, 4), "quarter_kelly_pct": round(kelly * 25, 2)}
    else:
        result["kelly"] = {"edge": round(edge, 4), "quarter_kelly_pct": 0}
    return result

def cmd_mxn(args):
    mxn = _import("src.calculations.mxn_calculator", "MxnCalculator")()
    selections = json.loads(args.selections)
    return mxn.calculate(args.lottery, selections, args.pass_mode)

def cmd_clv(args):
    predictor = _import("src.calculations.clv_predictor", "CLVPredictor")()
    return predictor.predict(args.odds, args.true_prob)

def cmd_portfolio(args):
    opt = _import("src.calculations.portfolio_optimizer", "PortfolioOptimizer")()
    returns = json.loads(args.returns)
    cov = json.loads(args.cov_matrix)
    return opt.max_sharpe(returns, cov, args.risk_free)

def cmd_anomaly(args):
    detector = _import("src.calculations.anomaly_detector", "AnomalyDetector")()
    return detector.detect(json.loads(args.odds_history))

def cmd_lottery_return(args):
    calc = _import("src.calculations.chinese_lottery_official_calc", "ChineseLotteryOfficialCalculator")()
    return calc.calculate(json.loads(args.odds_list), args.lottery_type)


def main():
    parser = argparse.ArgumentParser(description="AFA 工具集")
    sub = parser.add_subparsers(dest="tool", required=True)

    # elo
    p = sub.add_parser("elo")
    p.add_argument("--home-elo", type=float, required=True)
    p.add_argument("--away-elo", type=float, required=True)
    p.add_argument("--home-goals", type=int, default=None)
    p.add_argument("--away-goals", type=int, default=None)
    p.add_argument("--k-factor", type=int, default=32)

    # dixon_coles
    p = sub.add_parser("dixon_coles")
    p.add_argument("--home-attack", type=float, required=True)
    p.add_argument("--home-defense", type=float, required=True)
    p.add_argument("--away-attack", type=float, required=True)
    p.add_argument("--away-defense", type=float, required=True)
    p.add_argument("--home-advantage", type=float, default=0.3)

    # kelly
    p = sub.add_parser("kelly")
    p.add_argument("--probability", type=float, required=True)
    p.add_argument("--odds", type=float, required=True)
    p.add_argument("--bankroll", type=float, default=10000)

    # market_probability
    p = sub.add_parser("market_probability")
    p.add_argument("--odds-home", type=float, required=True)
    p.add_argument("--odds-draw", type=float, required=True)
    p.add_argument("--odds-away", type=float, required=True)

    # monte_carlo
    p = sub.add_parser("monte_carlo")
    p.add_argument("--home-attack", type=float, required=True)
    p.add_argument("--home-defense", type=float, required=True)
    p.add_argument("--away-attack", type=float, required=True)
    p.add_argument("--away-defense", type=float, required=True)
    p.add_argument("-n", type=int, default=10000)

    # trap
    p = sub.add_parser("trap_detection")
    p.add_argument("--odds", type=float, required=True)
    p.add_argument("--true-probability", type=float, required=True)
    p.add_argument("--vig", type=float, default=0.89)

    # bayesian
    p = sub.add_parser("bayesian")
    p.add_argument("--prior-alpha", type=float, required=True)
    p.add_argument("--prior-beta", type=float, required=True)
    p.add_argument("--observed-wins", type=int, required=True)
    p.add_argument("--observed-losses", type=int, required=True)

    # comprehensive
    p = sub.add_parser("comprehensive")
    p.add_argument("--home", default="Home")
    p.add_argument("--away", default="Away")
    p.add_argument("--home-elo", type=float, required=True)
    p.add_argument("--away-elo", type=float, required=True)
    p.add_argument("--odds-home", type=float, required=True)
    p.add_argument("--odds-draw", type=float, required=True)
    p.add_argument("--odds-away", type=float, required=True)

    # mxn
    p = sub.add_parser("mxn")
    p.add_argument("--lottery", default="jingcai")
    p.add_argument("--selections", required=True)
    p.add_argument("--pass-mode", default="2x1")

    # clv
    p = sub.add_parser("clv")
    p.add_argument("--odds", type=float, required=True)
    p.add_argument("--true-prob", type=float, required=True)

    # portfolio
    p = sub.add_parser("portfolio")
    p.add_argument("--returns", required=True)
    p.add_argument("--cov-matrix", required=True)
    p.add_argument("--risk-free", type=float, default=0.02)

    # anomaly
    p = sub.add_parser("anomaly")
    p.add_argument("--odds-history", required=True)

    # lottery return
    p = sub.add_parser("lottery_return")
    p.add_argument("--odds-list", required=True)
    p.add_argument("--lottery-type", default="jingcai")

    args = parser.parse_args()

    dispatch = {
        "elo": cmd_elo,
        "dixon_coles": cmd_dixon_coles,
        "kelly": cmd_kelly,
        "market_probability": cmd_market_prob,
        "monte_carlo": cmd_monte_carlo,
        "trap_detection": cmd_trap,
        "bayesian": cmd_bayesian,
        "comprehensive": cmd_comprehensive,
        "mxn": cmd_mxn,
        "clv": cmd_clv,
        "portfolio": cmd_portfolio,
        "anomaly": cmd_anomaly,
        "lottery_return": cmd_lottery_return,
    }

    result = dispatch[args.tool](args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
