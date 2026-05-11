#!/usr/bin/env python3
"""详细验证竞彩 M 串 N 组合的完整性"""

import json
from pathlib import Path

project_root = Path(__file__).resolve().parent

# 读取竞彩规则
jingcai_file = project_root / "data" / "knowledge" / "jingcai-rules.json"
with open(jingcai_file, "r", encoding="utf-8") as f:
    jingcai_data = json.load(f)

mcn_rules = jingcai_data["betting_rules"]["pass_types_detail"]["M串N"]["tolerance_rules"]

print("=" * 70)
print("竞彩 M 串 N 组合完整性详细检查")
print("=" * 70)

# 按场次分组
combinations_by_legs = {}
for combo in mcn_rules.keys():
    legs = int(combo.split("×")[0])
    if legs not in combinations_by_legs:
        combinations_by_legs[legs] = []
    combinations_by_legs[legs].append(combo)

# 按场次排序并显示
total_expected = 0
total_actual = 0

for legs in sorted(combinations_by_legs.keys()):
    combos = sorted(combinations_by_legs[legs])
    num_combos = len(combos)
    expected = legs - 1  # 对于 M 场，理论上有 M-1 个容错组合（从容错1场到完全容错）
    
    print(f"\n{legs} 场比赛:")
    print(f"  理论组合数: {expected} 个")
    print(f"  实际组合数: {num_combos} 个")
    print(f"  组合列表: {combos}")
    
    total_expected += expected
    total_actual += num_combos
    
    if num_combos == expected:
        print(f"  ✓ 完整")
    else:
        print(f"  ❌ 不完整")

print("\n" + "=" * 70)
print(f"总计:")
print(f"  理论组合数: {total_expected} 个")
print(f"  实际组合数: {total_actual} 个")

if total_actual == total_expected:
    print("  ✓ 所有 M 串 N 组合完整！")
else:
    print("  ❌ M 串 N 组合不完整！")
print("=" * 70)

# 显示所有组合的详情
print("\n所有组合详情:")
print("-" * 70)
for combo in sorted(mcn_rules.keys()):
    print(f"{combo}: {mcn_rules[combo]}")
