#!/usr/bin/env python3
"""
AFA Evolution CLI — 自进化系统管理工具

用法:
  python -m src.afa_v9.evolution.cli record <action> <outcome>   # 记录经验
  python -m src.afa_v9.evolution.cli evolve                     # 运行进化
  python -m src.afa_v9.evolution.cli report                     # 生成报告
  python -m src.afa_v9.evolution.cli skills                     # 查看技能
  python -m src.afa_v9.evolution.cli patterns                   # 查看模式
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.afa_v9.evolution import (
    EVOLUTION_ENGINE,
    EvolutionEngine,
    OutcomeType,
    EvolutionPhase,
)


def cmd_record(args):
    try:
        outcome = OutcomeType(args.outcome)
    except ValueError:
        print(f"❌ Invalid outcome: {args.outcome}")
        print(f"Valid options: {[o.value for o in OutcomeType]}")
        return 1

    context = {"league": args.league, "odds": float(args.odds), "market": args.market}
    if args.tags:
        tags = args.tags.split(",")
    else:
        tags = []

    exp = EVOLUTION_ENGINE.record_experience(
        context=context,
        action=args.action,
        outcome=outcome,
        metrics={"profit": float(args.profit)} if args.profit else {},
        tags=tags,
    )
    print(f"✅ Experience recorded: {exp.id}")
    return 0


def cmd_evolve(args):
    print("🚀 Starting evolution cycle...\n")
    result = EVOLUTION_ENGINE.evolve()

    print(f"Phase: {result['phase']}")
    print(f"Patterns analyzed: {result['pattern_analysis']['patterns_found']}")
    print(f"New hypotheses: {result['new_hypotheses']}")
    print(f"Performance: {result['performance']}")
    return 0


def cmd_report(args):
    report = EVOLUTION_ENGINE.get_evolution_report()
    print(report)
    return 0


def cmd_skills(args):
    skills = EVOLUTION_ENGINE.get_best_skills(args.count)

    if not skills:
        print("📭 No skills found")
        return 0

    print(f"\n{'='*80}")
    print(f"🏆 Top {len(skills)} Skills (by effectiveness)")
    print(f"{'='*80}")

    for i, skill in enumerate(skills, 1):
        status = "🟢" if skill.effectiveness > 0.6 else "🟡" if skill.effectiveness > 0.4 else "🔴"
        print(f"\n{i}. {status} {skill.name}")
        print(f"   Effectiveness: {skill.effectiveness:.1%}")
        print(f"   Success Rate: {skill.success_rate:.1%} ({skill.success_count}/{skill.usage_count})")
        print(f"   ROI: {skill.roi:.2f}%")
        print(f"   Source: {skill.source}")
        if skill.tags:
            print(f"   Tags: {', '.join(skill.tags)}")

    return 0


def cmd_patterns(args):
    patterns = EVOLUTION_ENGINE.get_active_patterns()

    if not patterns:
        print("📭 No validated patterns found")
        return 0

    print(f"\n{'='*80}")
    print(f"🔍 Validated Patterns ({len(patterns)})")
    print(f"{'='*80}")

    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. {pattern.name}")
        print(f"   Confidence: {pattern.confidence:.0%}")
        print(f"   Success Rate: {pattern.success_rate:.1%}")
        print(f"   Samples: {pattern.support_count}")
        print(f"   Description: {pattern.description}")

    return 0


def cmd_hypotheses(args):
    hyps = EVOLUTION_ENGINE.hypotheses

    if not hyps:
        print("📭 No hypotheses")
        return 0

    print(f"\n{'='*80}")
    print(f"💡 Hypotheses ({len(hyps)})")
    print(f"{'='*80}")

    for hyp in list(hyps.values())[:10]:
        status_icon = {"pending": "⏳", "testing": "🔬", "validated": "✅"}.get(hyp.status, "❓")
        print(f"\n{status_icon} {hyp.description[:60]}")
        print(f"   Type: {hyp.hypothesis_type}")
        print(f"   Confidence: {hyp.confidence:.0%}")
        print(f"   Status: {hyp.status}")

    return 0


def cmd_stats(args):
    perf = EVOLUTION_ENGINE.evaluate_performance()

    print(f"\n📊 Evolution Statistics")
    print(f"{'='*50}")
    print(f"Total Experiences: {len(EVOLUTION_ENGINE.experiences)}")
    print(f"Total Skills: {perf['total_skills']}")
    print(f"Active Skills: {perf['active_skills']}")
    print(f"Patterns: {len(EVOLUTION_ENGINE.patterns)}")
    print(f"Hypotheses: {len(EVOLUTION_ENGINE.hypotheses)}")
    print(f"\n📈 Performance:")
    print(f"  Overall Effectiveness: {perf['overall_effectiveness']:.1%}")
    print(f"  Avg Success Rate: {perf['avg_success_rate']:.1%}")
    print(f"  Avg ROI: {perf['avg_roi']:.2f}%")
    return 0


def main():
    parser = argparse.ArgumentParser(description="AFA Evolution CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    record_p = sub.add_parser("record", help="Record an experience")
    record_p.add_argument("action", help="Action taken")
    record_p.add_argument("outcome", help="Outcome: success/failure/neutral/partial")
    record_p.add_argument("--league", default="unknown", help="League name")
    record_p.add_argument("--odds", type=float, default=0, help="Odds value")
    record_p.add_argument("--market", default="WDL", help="Market type")
    record_p.add_argument("--profit", type=float, default=0, help="Profit/Loss")
    record_p.add_argument("--tags", help="Comma-separated tags")

    sub.add_parser("evolve", help="Run evolution cycle")
    sub.add_parser("report", help="Generate evolution report")
    sub.add_parser("patterns", help="Show validated patterns")
    sub.add_parser("hypotheses", help="Show hypotheses")
    sub.add_parser("stats", help="Show statistics")

    skills_p = sub.add_parser("skills", help="Show top skills")
    skills_p.add_argument("--count", type=int, default=10, help="Number of skills to show")

    args = parser.parse_args()

    if args.cmd == "record":
        return cmd_record(args)
    elif args.cmd == "evolve":
        return cmd_evolve(args)
    elif args.cmd == "report":
        return cmd_report(args)
    elif args.cmd == "skills":
        return cmd_skills(args)
    elif args.cmd == "patterns":
        return cmd_patterns(args)
    elif args.cmd == "hypotheses":
        return cmd_hypotheses(args)
    elif args.cmd == "stats":
        return cmd_stats(args)


if __name__ == "__main__":
    sys.exit(main())
