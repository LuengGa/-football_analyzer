#!/usr/bin/env python3
"""验证备份文件的内容"""

import zipfile
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent
backup_dir = project_root / "backups"

# 获取最新的备份文件
backup_files = sorted(backup_dir.glob("official_lottery_rules_backup_*.zip"), reverse=True)

if not backup_files:
    print("未找到备份文件！")
    sys.exit(1)

latest_backup = backup_files[0]

print("=" * 80)
print(f"验证备份文件: {latest_backup.name}")
print("=" * 80)

with zipfile.ZipFile(latest_backup, "r") as zipf:
    print(f"\n文件总数: {len(zipf.namelist())}")
    print("\n备份内容:")
    print("-" * 80)
    
    for name in zipf.namelist():
        info = zipf.getinfo(name)
        print(f"✓ {name} ({info.file_size} bytes)")
    
    print("\n" + "=" * 80)
    print("验证README.txt内容:")
    print("-" * 80)
    if "README.txt" in zipf.namelist():
        readme_content = zipf.read("README.txt").decode("utf-8")
        print(readme_content)
    else:
        print("⚠️  README.txt 未找到")

print("=" * 80)
print("✓ 备份文件验证完成！")
print(f"✓ 备份文件位置: {latest_backup}")
print("=" * 80)
