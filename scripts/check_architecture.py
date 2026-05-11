#!/usr/bin/env python3
"""
AFA v9 架构检查脚本
检查项目是否符合架构规范，防止重复定义和代码散落。
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict


def check_official_rules_duplicates():
    """检查是否有重复的官方规则定义"""
    print("=" * 70)
    print("🧐 检查官方规则单一性")
    print("=" * 70)
    print()

    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"

    # 更精确的检测：寻找字典或常量定义的模式
    suspicious_patterns = [
        # 返奖率硬编码
        r'return_rate\s*[:=]\s*0\.6[59]',
        r'JINGCAI.*69',
        r'BEIDAN.*65',
        # 最大串关硬编码（排除合理的内部业务配置）
        r'play_types\s*[:=]\s*\[',
        # 官方规则注释或说明，但实际已在 lottery_knowledge.py 中
        r'玩法.*胜平负.*让球.*比分.*混合.*过关',
    ]

    # 官方规则唯一真实来源：src/calculations/lottery/
    allowed_source = src_dir / "calculations" / "lottery"

    issues = []

    # 检查所有 Python 文件
    for root, _, files in os.walk(src_dir):
        for file in files:
            if not file.endswith(".py"):
                continue
            file_path = Path(root) / file

            # 跳过官方规则源文件
            if str(allowed_source) in str(file_path):
                continue
            # 跳过测试文件
            if "test" in file_path.parts:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                    for i, line in enumerate(lines, 1):
                        # 检查是否有硬编码的官方规则模式
                        for pattern in suspicious_patterns:
                            if re.search(pattern, line):
                                # 排除注释、导入语句
                                stripped = line.strip()
                                if not stripped.startswith('#') and \
                                   not stripped.startswith('from') and \
                                   not stripped.startswith('import') and \
                                   not 'confidence' in stripped.lower() and \
                                   not 'threshold' in stripped.lower():
                                    issues.append({
                                        "file": str(file_path.relative_to(project_root)),
                                        "line": i,
                                        "text": stripped,
                                    })
                                    break
            except Exception:
                pass

    if issues:
        print("⚠️  发现潜在的官方规则硬编码（共 {} 处）：\n".format(len(issues)))
        for issue in issues[:20]:  # 只显示前20个
            print(f"  📄 {issue['file']}:{issue['line']}")
            print(f"     {issue['text']}")
        if len(issues) > 20:
            print(f"\n    ... (还有 {len(issues)-20} 处未显示)")
        print("\n💡 提示：官方规则应从 src.calculations.lottery 统一获取，避免重复定义")
    else:
        print("✅ 官方规则单一性检查通过！\n")

    return len(issues) == 0


def check_modules_placing():
    """检查模块是否正确放置"""
    print("=" * 70)
    print("📁 检查模块放置规范")
    print("=" * 70)
    print()

    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    calculations_dir = src_dir / "calculations"

    issues = []

    # 1. 检查 src/ 根目录下是否有新的文件夹（禁止）
    skip_dirs = [
        '__pycache__', '.git', '.pytest_cache', 'archive',
        'data', 'docs', 'scripts', 'tests', 'archive'
    ]
    allowed_src_dirs = ['afa_v9', 'calculations', 'config', 'core', 'tools', 'cli']

    for item in src_dir.iterdir():
        if item.is_dir() and \
           item.name not in allowed_src_dirs and \
           item.name not in skip_dirs and \
           not item.name.startswith('.') and \
           not item.name.endswith('.egg-info'):
            issues.append({
                "type": "forbidden_dir",
                "path": str(item.relative_to(project_root)),
            })

    # 2. 检查 calculations/ 根目录下是否有直接的 .py 文件（除了 __init__.py）
    if calculations_dir.exists():
        for item in calculations_dir.iterdir():
            if item.is_file() and item.name.endswith('.py') and item.name != '__init__.py':
                issues.append({
                    "type": "loose_file",
                    "path": str(item.relative_to(project_root)),
                })

    # 3. 检查 calculations/ 的子目录是否符合规范
    allowed_calculations_subdirs = [
        'lottery', 'odds', 'quant', 'backtesting', 
        'math', 'pro', 'settlement', 'history', 'utils'
    ]
    
    if calculations_dir.exists():
        for item in calculations_dir.iterdir():
            if item.is_dir() and item.name not in allowed_calculations_subdirs and \
               not item.name.startswith('.') and not item.name == '__pycache__':
                issues.append({
                    "type": "unknown_subdir",
                    "path": str(item.relative_to(project_root)),
                })

    if issues:
        print("❌ 发现违规的目录结构：\n")
        for issue in issues:
            if issue["type"] == "forbidden_dir":
                print(f"  🚫 禁止创建目录：{issue['path']}")
            elif issue["type"] == "loose_file":
                print(f"  📄 文件应放入子目录：{issue['path']}")
            elif issue["type"] == "unknown_subdir":
                print(f"  📂 未知子目录：{issue['path']}")
        print()
    else:
        print("✅ 模块放置检查通过！\n")

    return len(issues) == 0


def check_duplicate_files():
    """检查是否有重复的文件名"""
    print("=" * 70)
    print("🔍 检查重复文件名")
    print("=" * 70)
    print()

    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"

    # 这些文件名重复是合理的，不需要报告
    reasonable_duplicates = [
        '__init__.py',  # 正常的包初始化文件
        'base.py',      # 基类文件在不同模块中正常
        'config.py',    # 配置文件在不同模块中正常
        'cli.py',       # CLI文件在不同模块中正常
        'registry.py',  # 注册表文件在不同模块中正常
        'loader.py',    # 加载器文件在不同模块中正常
        'pipeline.py',  # 管道文件在不同模块中正常
        # 以下是经过评估，功能不同的同名文件
        'tool_registry_v2.py',
        'pre_filter.py',
        'mcp_tools.py',
        'domain_kernel.py',
        'match_identity.py',
        'recommendation_schema.py',
        'data_contract.py',
        'ticket_schema.py',
        'lottery_knowledge.py',
        'elo_rating.py',
    ]

    file_names = defaultdict(list)
    issues = []

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py') and 'test' not in Path(root).parts:
                file_names[file].append(str(Path(root) / file))

    for name, paths in file_names.items():
        if len(paths) > 1 and name not in reasonable_duplicates:
            issues.append({
                "name": name,
                "paths": [str(Path(p).relative_to(project_root)) for p in paths]
            })

    if issues:
        print("⚠️  发现重复文件名（可能是重复代码）：\n")
        for issue in issues:
            print(f"  📄 {issue['name']}:")
            for path in issue['paths']:
                print(f"     - {path}")
        print()
        print(f"💡 提示：{len(issues)}个潜在重复文件（已排除{len(reasonable_duplicates)}种合理重复）")
    else:
        print("✅ 无重复文件名检查通过！\n")

    return len(issues) == 0


def check_archive_clean():
    """检查 archive 是否有旧代码残留（可选）"""
    print("=" * 70)
    print("📦 检查旧代码存档")
    print("=" * 70)
    print()
    project_root = Path(__file__).parent.parent
    archive_dir = project_root / "archive"

    if archive_dir.exists():
        print(f"✅ 旧代码已正确存档在 archive/ 下\n")
        print("存档内容：")
        for item in sorted(archive_dir.iterdir()):
            print(f"  - {item.name}")
        print()
    else:
        print("⚠️  未找到 archive 目录\n")

    return True


def main():
    """主检查函数"""
    print("\n" + "=" * 70)
    print("🏗️   AFA v9 架构检查")
    print("=" * 70)
    print()

    all_ok = True

    if not check_official_rules_duplicates():
        all_ok = False

    if not check_modules_placing():
        all_ok = False

    if not check_duplicate_files():
        all_ok = False

    check_archive_clean()

    print("=" * 70)
    if all_ok:
        print("✅ 所有架构检查通过！")
    else:
        print("❌ 发现架构问题，请修复！")
    print("=" * 70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
