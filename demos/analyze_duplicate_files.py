#!/usr/bin/env python3
"""
分析重复文件，判断是否真正需要清理
"""

import sys
import hashlib
from pathlib import Path


def file_hash(file_path):
    """计算文件内容的hash"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def analyze_duplicates():
    project_root = Path(__file__).parent
    
    # 从架构检查中发现的重复文件
    duplicate_files = [
        ("tool_registry_v2.py", 
         ["src/tools/tool_registry_v2.py", "src/calculations/utils/tool_registry_v2.py"]),
        ("market_probability_engine.py", 
         ["src/tools/odds/market_probability_engine.py", "src/calculations/odds/market_probability_engine.py"]),
        ("pre_filter.py", 
         ["src/tools/odds/pre_filter.py", "src/calculations/quant/pre_filter.py"]),
        ("mcp_tools.py", 
         ["src/tools/odds/mcp_tools.py", "src/afa_v9/ai_augmented/mcp_tools.py"]),
        ("domain_kernel.py", 
         ["src/core/domain_kernel.py", "src/core/models/domain_kernel.py"]),
        ("match_identity.py", 
         ["src/core/match_identity.py", "src/core/models/match_identity.py"]),
        ("recommendation_schema.py", 
         ["src/core/recommendation_schema.py", "src/core/models/recommendation_schema.py"]),
        ("data_contract.py", 
         ["src/core/data_contract.py", "src/core/data/data_contract.py"]),
        ("ticket_schema.py", 
         ["src/core/ticket_schema.py", "src/core/models/ticket_schema.py"]),
        ("elo_rating.py", 
         ["src/calculations/quant/elo_rating.py", "src/calculations/math/elo_rating.py"]),
    ]
    
    print("=" * 90)
    print("🔍 重复文件分析报告")
    print("=" * 90)
    print()
    
    needs_cleanup = []
    different_functions = []
    
    for name, paths in duplicate_files:
        full_paths = [project_root / p for p in paths]
        
        print(f"📄 {name}:")
        
        # 检查文件是否都存在
        existing = [p for p in full_paths if p.exists()]
        if len(existing) < 2:
            print(f"   ⚠️  部分文件不存在")
            print()
            continue
        
        # 计算hash
        hashes = []
        for p in existing:
            h = file_hash(p)
            hashes.append(h)
            print(f"   - {p.relative_to(project_root)}: {h[:8]}...")
        
        if len(set(hashes)) == 1:
            print(f"   ✅ 内容完全相同！建议清理")
            needs_cleanup.append((name, paths))
        else:
            print(f"   ⚠️  内容不同，可能是不同功能")
            different_functions.append((name, paths))
        
        print()
    
    print("=" * 90)
    print("📊 分析结果")
    print("=" * 90)
    print()
    print(f"需要清理的重复文件（内容相同）: {len(needs_cleanup)}")
    print(f"功能不同的同名文件: {len(different_functions)}")
    print()
    
    if needs_cleanup:
        print("建议清理的文件：")
        for name, paths in needs_cleanup:
            print(f"  - {name}: {paths}")
    
    if different_functions:
        print()
        print("可能不需要清理的文件（功能不同）：")
        for name, paths in different_functions:
            print(f"  - {name}: {paths}")
    
    print()
    
    return needs_cleanup, different_functions


if __name__ == "__main__":
    analyze_duplicates()
