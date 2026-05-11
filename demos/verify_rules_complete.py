#!/usr/bin/env python3
"""验证更新后的彩票规则完整性"""

import sys
from pathlib import Path
import json

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))


def verify_rules():
    """验证规则完整性"""
    print("=" * 60)
    print("彩票规则完整性验证")
    print("=" * 60)
    
    try:
        # 读取竞彩规则
        jingcai_file = project_root / "data" / "knowledge" / "jingcai-rules.json"
        with open(jingcai_file, "r", encoding="utf-8") as f:
            jingcai_data = json.load(f)
        
        print("\n1. 竞彩 M串N 组合检查:")
        print("-" * 40)
        mcn_rules_jc = jingcai_data["betting_rules"]["pass_types_detail"]["M串N"]["tolerance_rules"]
        print(f"  竞彩 M串N 组合总数: {len(mcn_rules_jc)}")
        expected_jingcai_mcn = [
            "2×3", "3×4", "3×7", "4×5", "4×11", "4×15",
            "5×6", "5×16", "5×26", "5×31",
            "6×7", "6×22", "6×42", "6×57", "6×63",
            "7×8", "7×29", "7×64", "7×99", "7×120", "7×127",
            "8×9", "8×37", "8×93", "8×163", "8×219", "8×247", "8×255"
        ]
        missing_mcn_jc = [x for x in expected_jingcai_mcn if x not in mcn_rules_jc]
        extra_mcn_jc = [x for x in mcn_rules_jc if x not in expected_jingcai_mcn]
        
        if missing_mcn_jc:
            print(f"  ❌ 缺失的 M串N 组合: {missing_mcn_jc}")
        else:
            print(f"  ✓ 所有预期的 M串N 组合都已包含")
        
        if extra_mcn_jc:
            print(f"  ⚠️ 额外的 M串N 组合: {extra_mcn_jc}")
        
        # 读取北单规则
        beidan_file = project_root / "data" / "knowledge" / "beidan-rules.json"
        with open(beidan_file, "r", encoding="utf-8") as f:
            beidan_data = json.load(f)
        
        print("\n2. 北单过关方式检查:")
        print("-" * 40)
        pass_types = beidan_data["betting_rules"]["pass_types"]
        print(f"  北单支持的过关方式: {pass_types}")
        
        if "pass_types_detail" in beidan_data["betting_rules"]:
            m1_detail = beidan_data["betting_rules"]["pass_types_detail"]["M串1"]
            print(f"  北单 M串1 组合数: {len(m1_detail['combinations'])}")
            print(f"  北单 M串1 组合: {m1_detail['combinations']}")
            
            if "M串N" in beidan_data["betting_rules"]["pass_types_detail"]:
                mcn_rules_bd = beidan_data["betting_rules"]["pass_types_detail"]["M串N"]["tolerance_rules"]
                print(f"  北单 M串N 组合总数: {len(mcn_rules_bd)}")
                print(f"\n  北单 M串N 组合概览（前28个与竞彩相同，之后是9-15场）:")
                for i, combo in enumerate(sorted(mcn_rules_bd.keys())[:40]):
                    print(f"    {i+1:2d}. {combo}")
                if len(mcn_rules_bd) > 40:
                    print(f"    ... 还有 {len(mcn_rules_bd) - 40} 个组合")
        
        print("\n" + "=" * 60)
        print("✅ 规则完整性验证完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = verify_rules()
    sys.exit(0 if success else 1)
