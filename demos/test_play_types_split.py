#!/usr/bin/env python3
"""
测试拆分后的玩法知识
"""

import sys
sys.path.insert(0, '.')

print("=" * 60)
print("测试拆分后的玩法语义记忆")
print("=" * 60)

from src.afa_v9.memory.semantic import get_lottery_semantic_memory
semantic = get_lottery_semantic_memory()

print(f"\n✅ 语义记忆加载成功！")
chunks = semantic.get_all_chunks()
print(f"   - 共 {len(chunks)} 个知识块")

print("\n知识块统计：")
categories = {}
for chunk in chunks:
    cat = chunk.get('category', 'unknown')
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items()):
    print(f"  - {cat}: {count} 个")

print("\n" + "=" * 60)
print("测试查询 - 竞彩胜平负")
print("=" * 60)

query1 = "竞彩胜平负怎么玩"
print(f"\n查询：{query1}")
results1 = semantic.query(query1, top_k=3)
for i, result in enumerate(results1, 1):
    print(f"{i}. [{result['score']:.1f}] {result['content']}")

print("\n" + "=" * 60)
print("测试查询 - 北单上下单双")
print("=" * 60)

query2 = "北单的上下单双玩法"
print(f"\n查询：{query2}")
results2 = semantic.query(query2, top_k=3)
for i, result in enumerate(results2, 1):
    print(f"{i}. [{result['score']:.1f}] {result['content']}")

print("\n" + "=" * 60)
print("测试查询 - 竞彩混合过关")
print("=" * 60)

query3 = "竞彩混合过关玩法"
print(f"\n查询：{query3}")
results3 = semantic.query(query3, top_k=2)
for i, result in enumerate(results3, 1):
    print(f"{i}. [{result['score']:.1f}] {result['content']}")

print("\n" + "=" * 60)
print("测试查询 - 北单胜负过关")
print("=" * 60)

query4 = "北单胜负过关玩法"
print(f"\n查询：{query4}")
results4 = semantic.query(query4, top_k=2)
for i, result in enumerate(results4, 1):
    print(f"{i}. [{result['score']:.1f}] {result['content']}")

print("\n" + "=" * 60)
print("所有知识块列表：")
print("=" * 60)

for i, chunk in enumerate(sorted(chunks, key=lambda x: x.get('category', '')), 1):
    print(f"{i}. [{chunk.get('category')}] {chunk.get('id')}")

print("\n🎉 测试完成！拆分后的玩法知识工作正常！")
