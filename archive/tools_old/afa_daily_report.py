#!/usr/bin/env python3
"""AFA 每日分析报告 — 供 cron 调用"""
import sys, json
sys.path.insert(0, '/Volumes/J ZAO 9 SER 1/Python/TRAE-SOLO/football_analyzer')

from afa_cli import analyze_match
from datetime import datetime

# 示例比赛（实际可对接 API 获取实时赛程）
demo_matches = [
    {"home": "Arsenal", "away": "Chelsea", "elo_h": 1650, "elo_a": 1580,
     "odds_h": 2.1, "odds_d": 3.4, "odds_a": 3.6,
     "att_h": 1.2, "def_h": -0.3, "att_a": 0.9, "def_a": -0.1},
    {"home": "Liverpool", "away": "Man City", "elo_h": 1700, "elo_a": 1750,
     "odds_h": 2.8, "odds_d": 3.3, "odds_a": 2.5,
     "att_h": 1.5, "def_h": -0.5, "att_a": 1.8, "def_a": -0.6},
]

report = []
for m in demo_matches:
    result = analyze_match(m["home"], m["away"], m["elo_h"], m["elo_a"],
                          m["odds_h"], m["odds_d"], m["odds_a"],
                          m["att_h"], m["def_h"], m["att_a"], m["def_a"])
    report.append(result)

# 写报告
date = datetime.now().strftime("%Y-%m-%d")
output = {"date": date, "matches": len(report), "report": report}

# 写文件
report_path = f"/Users/jand/Library/Application Support/LobsterAI/openclaw/workspace-afa/memory/{date}.md"
with open(report_path, "w") as f:
    f.write(f"# AFA 每日分析报告 — {date}\n\n")
    for r in report:
        f.write(f"## {r['home']} vs {r['away']}\n\n")
        f.write(f"- **ELO 概率**: 主胜 {r['elo']['home_win_prob']:.1%} | 客胜 {r['elo']['away_win_prob']:.1%}\n")
        f.write(f"- **市场概率**: 主胜 {r['market']['home']:.1%} | 平 {r['market']['draw']:.1%} | 客胜 {r['market']['away']:.1%}\n")
        if "dixon_coles" in r:
            f.write(f"- **泊松期望**: {r['dixon_coles']['expected_home_goals']:.2f} - {r['dixon_coles']['expected_away_goals']:.2f}\n")
        f.write(f"- **集成预测**: 主胜 {r['ensemble']['home_win_prob']:.1%} | 客胜 {r['ensemble']['away_win_prob']:.1%}\n")
        if "kelly" in r:
            f.write(f"- **Kelly 建议**: 边缘 {r['kelly']['edge']:.1%} → 1/4 Kelly {r['kelly']['quarter_kelly_pct']:.1f}%\n")
        f.write("\n---\n\n")

print(f"✅ Daily report written to {report_path}")
print(json.dumps(output, ensure_ascii=False, indent=2))
