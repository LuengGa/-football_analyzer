#!/usr/bin/env python3
"""
AFA 足球分析运行器 — 每日比赛预测 & 分析
Usage:
  python3 scripts/run_afa_analysis.py                    # 运行演示比赛分析
  python3 scripts/run_afa_analysis.py --save             # 运行并保存结果
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.calculations.elo_rating import ELORatingSystem
from src.calculations.odds_analyzer import OddsAnalyzer

# 演示比赛数据
MATCHES = [
    {"home": "Liverpool",    "away": "Man City",    "home_odds": 2.10, "draw_odds": 3.40, "away_odds": 3.80},
    {"home": "Arsenal",      "away": "Chelsea",     "home_odds": 1.80, "draw_odds": 3.60, "away_odds": 4.50},
    {"home": "Man Utd",      "away": "Tottenham",   "home_odds": 2.00, "draw_odds": 3.50, "away_odds": 3.90},
    {"home": "Newcastle",    "away": "Aston Villa", "home_odds": 2.30, "draw_odds": 3.30, "away_odds": 3.40},
    {"home": "Brighton",     "away": "West Ham",    "home_odds": 1.95, "draw_odds": 3.55, "away_odds": 4.10},
]

def analyze_all(matches, save=False):
    elo = ELORatingSystem()
    oa = OddsAnalyzer()
    
    # Init ELO ratings
    initial_elos = {
        "Liverpool": 1680, "Man City": 1720, "Arsenal": 1640, "Chelsea": 1580,
        "Man Utd": 1550, "Tottenham": 1500, "Newcastle": 1480, "Aston Villa": 1460,
        "Brighton": 1440, "West Ham": 1420,
    }
    for team, rating in initial_elos.items():
        elo.ratings[team] = rating
    
    results = []
    for m in matches:
        home = m["home"]; away = m["away"]
        h_elo = elo.ratings.get(home, 1500)
        a_elo = elo.ratings.get(away, 1500)
        expected_home = 1.0 / (1.0 + 10 ** ((a_elo - h_elo) / 400.0))
        
        odds = {"home": m["home_odds"], "draw": m["draw_odds"], "away": m["away_odds"]}
        implied_home = 1.0 / m["home_odds"]
        implied_draw = 1.0 / m["draw_odds"]
        implied_away = 1.0 / m["away_odds"]
        margin = implied_home + implied_draw + implied_away - 1.0
        
        kelly_home = (expected_home * m["home_odds"] - 1) / (m["home_odds"] - 1) if m["home_odds"] > 1 else 0
        kelly_away = ((1 - expected_home) * m["away_odds"] - 1) / (m["away_odds"] - 1) if m["away_odds"] > 1 else 0
        edge = expected_home - implied_home
        
        if edge > 0.03: rec = "🏠 HOME BET"
        elif -edge > 0.03: rec = "✈️ AWAY BET"
        else: rec = "⏳ NO BET"
        
        results.append({
            "match": f"{home} vs {away}",
            "elo": f"{home}({h_elo:.0f}) vs {away}({a_elo:.0f})",
            "odds": f"{m['home_odds']:.2f} / {m['draw_odds']:.2f} / {m['away_odds']:.2f}",
            "model_prob_home": f"{expected_home:.1%}",
            "implied_home": f"{implied_home:.1%}",
            "edge": f"{edge:+.1%}",
            "kelly_home": f"{max(0,kelly_home):.1%}",
            "recommendation": rec,
        })
    
    # Print pretty report
    print("=" * 90)
    print("     🏆 AFA 足球分析师 — 今日比赛预测报告")
    print("=" * 90)
    print(f"{'比赛':<30} {'赔率(H/D/A)':<22} {'模型概率':<10} {'隐含概率':<10} {'优势':<8} {'Kelly':<8} {'建议':<15}")
    print("-" * 90)
    for r in results:
        print(f"{r['match']:<30} {r['odds']:<22} {r['model_prob_home']:<10} {r['implied_home']:<10} {r['edge']:<8} {r['kelly_home']:<8} {r['recommendation']:<15}")
    print("-" * 90)
    
    bets = [r for r in results if "BET" in r["recommendation"]]
    print(f"\n📊 共 {len(results)} 场比赛，{len(bets)} 个投注建议")
    
    if save:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "analysis_results.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump({"timestamp": __import__("datetime").datetime.now().isoformat(), "results": results}, f, indent=2, ensure_ascii=False)
        print(f"💾 结果已保存至 {path}")
    
    return results

if __name__ == "__main__":
    save = "--save" in sys.argv
    analyze_all(MATCHES, save=save)
