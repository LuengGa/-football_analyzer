#!/usr/bin/env python3
"""AFA CLI — 足球分析命令行入口"""
import sys, json, math, argparse
sys.path.insert(0, '/Volumes/J ZAO 9 SER 1/Python/TRAE-SOLO/football_analyzer')

from src.calculations.elo_rating import ELORatingSystem
from src.calculations.elo_calibrator import ELOCalibrator
from src.calculations.market_probability_engine import MarketProbabilityEngine

def analyze_match(home_team, away_team, home_elo, away_elo,
                  odds_home, odds_draw, odds_away,
                  home_attack=None, home_defense=None,
                  away_attack=None, away_defense=None):
    """单场比赛综合分析"""
    result = {"home": home_team, "away": away_team}
    
    # ELO
    elo = ELORatingSystem()
    exp_home = 1.0 / (1.0 + 10 ** ((away_elo - home_elo) / 400.0))
    result["elo"] = {
        "home_win_prob": round(exp_home, 4),
        "away_win_prob": round(1-exp_home, 4)
    }
    
    # 市场概率
    mpe = MarketProbabilityEngine()
    odds_dict = {"home": odds_home, "draw": odds_draw, "away": odds_away}
    result["market"] = dict((k, round(v,4)) for k,v in mpe.implied_probabilities_from_odds(odds_dict).items())
    
    # ELO 校准
    cal = ELOCalibrator()
    cal_result = cal.predict(home_elo, away_elo)
    result["elo_calibrated"] = {k: round(v,4) for k,v in cal_result.items()}
    
    # Dixon-Coles (纯数学)
    if all(v is not None for v in [home_attack, home_defense, away_attack, away_defense]):
        import math
        lam_h = math.exp(home_attack + away_defense + 0.3)
        lam_a = math.exp(away_attack + home_defense)
        hw = dw = aw = 0.0
        for i in range(9):
            pi = (lam_h**i)*math.exp(-lam_h)/math.factorial(i)
            for j in range(9):
                prob = pi * ((lam_a**j)*math.exp(-lam_a)/math.factorial(j))
                if i > j: hw += prob
                elif i == j: dw += prob
                else: aw += prob
        result["dixon_coles"] = {
            "home_win_prob": round(hw,4), "draw_prob": round(dw,4),
            "away_win_prob": round(aw,4),
            "expected_home_goals": round(lam_h,3), "expected_away_goals": round(lam_a,3)
        }
    
    # 集成
    probs_h = [result["elo"]["home_win_prob"], result["market"]["home"]]
    probs_a = [result["elo"]["away_win_prob"], result["market"]["away"]]
    if "dixon_coles" in result:
        probs_h.append(result["dixon_coles"]["home_win_prob"])
        probs_a.append(result["dixon_coles"]["away_win_prob"])
    result["ensemble"] = {
        "home_win_prob": round(sum(probs_h)/len(probs_h), 4),
        "away_win_prob": round(sum(probs_a)/len(probs_a), 4),
    }
    
    # Kelly (1/4 Kelly)
    implied = 1/odds_home
    edge = result["ensemble"]["home_win_prob"] - implied
    if edge > 0:
        kelly = edge / (odds_home - 1)
        result["kelly"] = {
            "edge": round(edge, 4), "kelly_fraction": round(kelly, 6),
            "quarter_kelly_pct": round(kelly * 25, 2)
        }
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AFA Match Analyzer")
    parser.add_argument("--home", required=True, help="Home team")
    parser.add_argument("--away", required=True, help="Away team")
    parser.add_argument("--elo-home", type=float, default=1500)
    parser.add_argument("--elo-away", type=float, default=1500)
    parser.add_argument("--odds-home", type=float, default=2.0)
    parser.add_argument("--odds-draw", type=float, default=3.2)
    parser.add_argument("--odds-away", type=float, default=3.5)
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    
    result = analyze_match(args.home, args.away, args.elo_home, args.elo_away,
                          args.odds_home, args.odds_draw, args.odds_away)
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else yaml_fmt(result))
