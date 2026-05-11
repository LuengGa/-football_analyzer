#!/usr/bin/env python3
"""
AFA Plugin & Task Queue CLI

用法:
  python -m src.afa_v9.plugins.cli list          # 列出插件
  python -m src.afa_v9.plugins.cli enable <id>   # 启用插件
  python -m src.afa_v9.plugins.cli disable <id>  # 禁用插件
  python -m src.afa_v9.plugins.cli tasks         # 列出任务
  python -m src.afa_v9.plugins.cli stats         # 显示统计
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.afa_v9.plugins import PLUGIN_REGISTRY, PluginState, PluginType
from src.afa_v9.queue import TASK_QUEUE, TaskStatus


def format_plugin_table(plugins):
    lines = []
    for p in plugins:
        state_icon = {
            PluginState.LOADED: "🔵",
            PluginState.ENABLED: "🟢",
            PluginState.DISABLED: "🔴",
            PluginState.ERROR: "❌",
            PluginState.UNLOADED: "⚪",
        }.get(p.state, "❓")
        lines.append(
            f"  {state_icon} {p.metadata.id:<25} │ {p.metadata.plugin_type.value:<10} │ "
            f"v{p.metadata.version} │ {p.metadata.description[:40]}"
        )
    return "\n".join(lines)


def cmd_list(args):
    if args.type:
        try:
            ptype = PluginType(args.type)
            plugins = PLUGIN_REGISTRY.list_plugins(plugin_type=ptype)
        except ValueError:
            print(f"❌ Unknown type: {args.type}")
            return 1
    else:
        plugins = PLUGIN_REGISTRY.list_plugins()

    if not plugins:
        print("📭 No plugins registered")
        return 0

    print(f"\n{'='*90}")
    print(f"🔌 AFA Plugin Registry — {len(plugins)} plugins")
    print(f"{'='*90}")
    print(format_plugin_table(plugins))
    return 0


def cmd_enable(args):
    if PLUGIN_REGISTRY.enable_plugin(args.plugin_id):
        print(f"✅ Plugin '{args.plugin_id}' enabled")
        return 0
    else:
        print(f"❌ Failed to enable plugin '{args.plugin_id}'")
        return 1


def cmd_disable(args):
    if PLUGIN_REGISTRY.disable_plugin(args.plugin_id):
        print(f"✅ Plugin '{args.plugin_id}' disabled")
        return 0
    else:
        print(f"❌ Failed to disable plugin '{args.plugin_id}'")
        return 1


def cmd_tasks(args):
    tasks = TASK_QUEUE.list_tasks(status=args.status, limit=args.limit)
    if not tasks:
        print("📭 No tasks found")
        return 0

    print(f"\n{'='*90}")
    print(f"📋 AFA Task Queue — {len(tasks)} tasks")
    print(f"{'='*90}")
    for t in tasks:
        status_icon = {
            TaskStatus.PENDING.value: "⏳",
            TaskStatus.RUNNING.value: "🔄",
            TaskStatus.COMPLETED.value: "✅",
            TaskStatus.FAILED.value: "❌",
            TaskStatus.CANCELLED.value: "🚫",
        }.get(t.status, "❓")
        print(f"  {status_icon} {t.id[:8]}... │ {t.name:<30} │ {t.status:<10} │ {t.created_at[:19]}")
    return 0


def cmd_stats(args):
    plugin_stats = PLUGIN_REGISTRY.get_stats()
    task_stats = TASK_QUEUE.get_stats()

    print(f"\n📊 AFA System Statistics")
    print(f"{'='*50}")
    print(f"\n🔌 Plugins:")
    print(f"  Total: {plugin_stats['total']}")
    for state, count in plugin_stats['by_state'].items():
        if count > 0:
            print(f"  {state}: {count}")

    print(f"\n📋 Tasks:")
    print(f"  Total: {task_stats['total']}")
    print(f"  Running: {task_stats['running']}")
    print(f"  Pending: {task_stats['pending']}")
    print(f"  Completed: {task_stats['completed']}")
    print(f"  Failed: {task_stats['failed']}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="AFA Plugin & Task Queue CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    list_p = sub.add_parser("list", help="List plugins")
    list_p.add_argument("--type", help=f"Filter by type: {[t.value for t in PluginType]}")

    enable_p = sub.add_parser("enable", help="Enable plugin")
    enable_p.add_argument("plugin_id", help="Plugin ID")

    disable_p = sub.add_parser("disable", help="Disable plugin")
    disable_p.add_argument("plugin_id", help="Plugin ID")

    tasks_p = sub.add_parser("tasks", help="List tasks")
    tasks_p.add_argument("--status", help=f"Filter by status")
    tasks_p.add_argument("--limit", type=int, default=50)

    sub.add_parser("stats", help="Show statistics")

    args = parser.parse_args()

    if args.cmd == "list":
        return cmd_list(args)
    elif args.cmd == "enable":
        return cmd_enable(args)
    elif args.cmd == "disable":
        return cmd_disable(args)
    elif args.cmd == "tasks":
        return cmd_tasks(args)
    elif args.cmd == "stats":
        return cmd_stats(args)


if __name__ == "__main__":
    sys.exit(main())
