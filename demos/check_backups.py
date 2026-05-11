#!/usr/bin/env python3
"""检查两个备份文件的区别"""

import zipfile
from pathlib import Path

project_root = Path(__file__).resolve().parent
backup_dir = project_root / "backups"

# 获取所有备份文件
backup_files = sorted(backup_dir.glob("official_lottery_rules_backup_*.zip"))

print("=" * 90)
print("检查现有备份文件")
print("=" * 90)

for backup_file in backup_files:
    print(f"\n文件: {backup_file.name}")
    print(f"大小: {backup_file.stat().st_size / 1024:.2f} KB")
    print(f"时间: {backup_file.stat().st_mtime}")
    
    with zipfile.ZipFile(backup_file, "r") as zipf:
        print(f"文件数: {len(zipf.namelist())}")
        print("内容:")
        for name in zipf.namelist():
            info = zipf.getinfo(name)
            print(f"  ✓ {name} ({info.file_size} bytes)")

print("\n" + "=" * 90)
print("分析:")
print("=" * 90)
print("\n第一个备份文件（20260512_024213）: 第一次运行时出错（README.txt添加失败），但仍创建了文件")
print("第二个备份文件（20260512_024244）: 修复后完整的备份文件")
print("\n建议:")
print("- 保留第二个文件（较新且完整）")
print("- 可以删除第一个文件（不完整的失败版本）")
print("=" * 90)
