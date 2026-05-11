#!/usr/bin/env python3
"""
快速综合测试 - 验证所有关键系统组件
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("AFA v9.0 快速综合测试")
print("=" * 80)

success_count = 0
total_tests = 0

def test_result(test_name, success, details=""):
    global success_count, total_tests
    total_tests += 1
    if success:
        success_count += 1
        print(f"  ✅ {test_name}: 成功")
        if details:
            print(f"     {details}")
    else:
        print(f"  ❌ {test_name}: 失败")
        if details:
            print(f"     {details}")

try:
    print("\n1️⃣  测试官方规则系统...")
    from src.calculations.lottery import LOTTERY_KNOWLEDGE, LOTTERY_QUERY
    jingcai = LOTTERY_KNOWLEDGE.get_lottery("JINGCAI")
    beidan = LOTTERY_KNOWLEDGE.get_lottery("BEIDAN")
    
    # 安全获取名称
    jc_name = "竞彩足球"
    bd_name = "北京单场"
    if hasattr(jingcai, 'get'):
        jc_name = jingcai.get('name', '竞彩足球')
    if hasattr(beidan, 'get'):
        bd_name = beidan.get('name', '北京单场')
    
    test_result("彩票知识库加载", jingcai is not None and beidan is not None,
                f"{jc_name}, {bd_name}")
    
    # 测试奖金计算
    bonus_jc = LOTTERY_QUERY.calculate_bonus("JINGCAI", [1.85, 2.1])
    bonus_bd = LOTTERY_QUERY.calculate_bonus("BEIDAN", [1.85, 2.1])
    test_result("奖金计算", bonus_jc is not None and bonus_bd is not None,
                f"竞彩{bonus_jc:.2f}元, 北单{bonus_bd:.2f}元")
except Exception as e:
    test_result("彩票系统", False, str(e))

try:
    print("\n2️⃣  测试语义记忆系统...")
    from src.afa_v9.memory.semantic import get_lottery_semantic_memory
    semantic = get_lottery_semantic_memory()
    result1 = semantic.query("竞彩返奖率")
    result2 = semantic.query("M串N")
    test_result("语义记忆查询", len(result1) > 0 and len(result2) > 0,
                f"返奖率{len(result1)}条, M串N{len(result2)}条")
except Exception as e:
    test_result("语义记忆系统", False, str(e))

try:
    print("\n3️⃣  测试M串N计算...")
    from src.calculations.lottery.mxn_calculator import MxnCalculator
    calc = MxnCalculator()
    matches = [
        {"id": "1", "odds": {"home": 1.8, "draw": 3.4, "away": 4.2}},
        {"id": "2", "odds": {"home": 2.1, "draw": 3.2, "away": 3.5}},
    ]
    mxn_result = calc.calculate(matches, 2, 3, stake=200)
    test_result("M串N计算器", bool(mxn_result),
                f"总投注{mxn_result.get('stake',0)}元")
except Exception as e:
    test_result("M串N计算", False, str(e))

try:
    print("\n4️⃣  测试玩法文件加载...")
    jc_play_dir = project_root / "data/knowledge/jingcai/play_types"
    bd_play_dir = project_root / "data/knowledge/beidan/play_types"
    jc_plays = list(jc_play_dir.glob("*.json"))
    bd_plays = list(bd_play_dir.glob("*.json"))
    test_result("玩法文件", len(jc_plays) >= 6 and len(bd_plays) >= 6,
                f"竞彩{len(jc_plays)}个, 北单{len(bd_plays)}个")
except Exception as e:
    test_result("玩法文件", False, str(e))

try:
    print("\n5️⃣  测试主规则文件完整性...")
    jc_main = project_root / "data/knowledge/jingcai-rules.json"
    bd_main = project_root / "data/knowledge/beidan-rules.json"
    import json
    with open(jc_main, "r", encoding="utf-8") as f:
        jc_data = json.load(f)
    with open(bd_main, "r", encoding="utf-8") as f:
        bd_data = json.load(f)
    has_pass_types_detail = "pass_types_detail" in jc_data["betting_rules"]
    has_mcn = "M串N" in jc_data["betting_rules"]["pass_types_detail"]
    test_result("主规则文件", has_pass_types_detail and has_mcn,
                "包含M串N详细规则")
except Exception as e:
    test_result("主规则文件", False, str(e))

try:
    print("\n6️⃣  检查备份文件...")
    backup_dir = project_root / "backups"
    if backup_dir.exists():
        backups = list(backup_dir.glob("*.zip"))
        test_result("备份文件", len(backups) >= 1,
                    f"{len(backups)}个备份文件")
    else:
        test_result("备份文件", False, "backups目录不存在")
except Exception as e:
    test_result("备份文件", False, str(e))

print("\n" + "=" * 80)
print(f"测试完成: {success_count}/{total_tests} 成功")
if success_count == total_tests:
    print("🎯 所有测试通过！系统运行正常！")
else:
    print(f"⚠️  {total_tests - success_count}个测试失败")
print("=" * 80)
