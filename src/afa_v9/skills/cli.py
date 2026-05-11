#!/usr/bin/env python3
"""
AFA Skill Registry CLI — 查看和管理技能注册表

用法:
  python -m src.afa_v9.skills.cli list                    # 列出所有技能
  python -m src.afa_v9.skills.cli list --category data   # 按分类列出
  python -m src.afa_v9.skills.cli search arbitrage       # 搜索技能
  python -m src.afa_v9.skills.cli export --format json    # 导出为JSON
  python -m src.afa_v9.skills.cli export --format yaml    # 导出为YAML
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.afa_v9.skills import SKILL_REGISTRY, SkillCategory


def format_skill_table(skills):
    lines = []
    for s in skills:
        status = "⚠️ DEPRECATED" if s.metadata.deprecated else ""
        approval = "🔒" if s.metadata.requires_approval else ""
        lines.append(
            f"  {s.metadata.name:<35} │ {s.metadata.category.value:<10} │ "
            f"{', '.join(s.metadata.tags[:3]):<30} │ {status} {approval}"
        )
    return "\n".join(lines)


def cmd_list(args):
    if args.category:
        try:
            cat = SkillCategory(args.category)
            skills = SKILL_REGISTRY.list_by_category(cat)
        except ValueError:
            print(f"❌ Unknown category: {args.category}")
            print(f"Available: {[c.value for c in SkillCategory]}")
            return 1
    else:
        skills = SKILL_REGISTRY.get_all()

    if not skills:
        print("📭 No skills found")
        return 0

    print(f"\n{'='*90}")
    print(f"📦 AFA Skill Registry — {len(skills)} skills")
    print(f"{'='*90}")
    print(f"  {'Name':<35} │ {'Category':<10} │ {'Tags':<30} │ Status")
    print(f"  {'-'*35}─┼─{'─'*10}─┼─{'─'*30}─┼──────")

    print(format_skill_table(skills))

    print(f"\n{'='*90}")
    print(f"\n📊 按分类统计:")
    for cat in SkillCategory:
        count = len(SKILL_REGISTRY.list_by_category(cat))
        if count:
            print(f"  {cat.value:<15}: {count}")

    return 0


def cmd_search(args):
    results = SKILL_REGISTRY.search(args.query)
    if not results:
        print(f"🔍 No skills found matching '{args.query}'")
        return 1

    print(f"\n🔍 Search results for '{args.query}': {len(results)} found\n")
    print(format_skill_table(results))
    return 0


def cmd_export(args):
    if args.format == "json":
        data = SKILL_REGISTRY.export_agentskills()
        output = json.dumps(data, indent=2, ensure_ascii=False)
    elif args.format == "markdown":
        output = SKILL_REGISTRY.export_markdown()
    else:
        print(f"❌ Unsupported format: {args.format}")
        return 1

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ Exported to {args.output}")
    else:
        print(output)

    return 0


def main():
    parser = argparse.ArgumentParser(description="AFA Skill Registry CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    list_p = sub.add_parser("list", help="List all skills")
    list_p.add_argument("--category", help=f"Filter by category: {[c.value for c in SkillCategory]}")

    search_p = sub.add_parser("search", help="Search skills")
    search_p.add_argument("query", help="Search query")

    export_p = sub.add_parser("export", help="Export skills")
    export_p.add_argument("--format", choices=["json", "markdown"], default="json")
    export_p.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    if args.cmd == "list":
        return cmd_list(args)
    elif args.cmd == "search":
        return cmd_search(args)
    elif args.cmd == "export":
        return cmd_export(args)


if __name__ == "__main__":
    sys.exit(main())
