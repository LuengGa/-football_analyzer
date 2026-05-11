#!/usr/bin/env python3
"""将所有官方规则文件打包成压缩文件进行备份"""

import zipfile
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent

# 备份文件名称
backup_dir = project_root / "backups"
backup_dir.mkdir(exist_ok=True)

# 生成备份文件名（带日期时间
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backup_dir / f"official_lottery_rules_backup_{timestamp}.zip"

# 需要备份的文件
files_to_backup = [
    # 主规则文件
    project_root / "data/knowledge/jingcai-rules.json",
    project_root / "data/knowledge/beidan-rules.json",
    project_root / "data/knowledge/lottery-rules.json",
    # 竞彩玩法文件
    project_root / "data/knowledge/jingcai/play_types/01_win_draw_loss.json",
    project_root / "data/knowledge/jingcai/play_types/02_handicap_win_draw_loss.json",
    project_root / "data/knowledge/jingcai/play_types/03_score.json",
    project_root / "data/knowledge/jingcai/play_types/04_total_goals.json",
    project_root / "data/knowledge/jingcai/play_types/05_half_full.json",
    project_root / "data/knowledge/jingcai/play_types/06_mixed_parlay.json",
    # 北单玩法文件
    project_root / "data/knowledge/beidan/play_types/01_win_draw_loss.json",
    project_root / "data/knowledge/beidan/play_types/02_over_under_odd_even.json",
    project_root / "data/knowledge/beidan/play_types/03_score.json",
    project_root / "data/knowledge/beidan/play_types/04_half_full.json",
    project_root / "data/knowledge/beidan/play_types/05_total_goals.json",
    project_root / "data/knowledge/beidan/play_types/06_win_loss.json",
]

# 创建压缩文件
print("=" * 80)
print("开始备份官方规则文件...")
print("=" * 80)

with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zipf:
    for file_path in files_to_backup:
        if file_path.exists():
            # 在zip中保持目录结构
            arcname = file_path.relative_to(project_root)
            zipf.write(file_path, arcname)
            print(f"✓ 已添加: {arcname}")
        else:
            print(f"⚠️  跳过(不存在: {file_path}")

    # 添加一个说明文件
    readme_content = f"""官方彩票规则备份
====================
备份时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
备份说明: 此文件包含竞彩和北京单场的完整官方规则

文件清单:
- jingcai-rules.json: 竞彩完整规则
- beidan-rules.json: 北京单场完整规则
- lottery-rules.json: 旧索引文件（向后兼容）
- jingcai/play_types/: 竞彩6个玩法文件
- beidan/play_types/: 北京单场6个玩法文件
"""
    zipf.writestr("README.txt", readme_content)

print("=" * 80)
print(f"✓ 备份完成！")
print(f"✓ 备份文件: {backup_file}")
print(f"✓ 文件大小: {backup_file.stat().st_size / 1024:.2f} KB")
print("=" * 80)
