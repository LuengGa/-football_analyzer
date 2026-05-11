"""
历史数据向量化脚本
====================

向量化158,971场比赛数据到向量数据库

运行:
    python scripts/vectorize_historical_data.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.historical_data import (
    HISTORICAL_LOADER,
    HISTORICAL_VECTORIZER,
    HistoricalVectorizer,
)


def main():
    print("\n" + "=" * 60)
    print("📊 历史数据向量化")
    print("=" * 60)

    print("\n📁 加载历史数据...")
    matches = HISTORICAL_LOADER.load_all()
    print(f"   加载完成: {len(matches)} 场比赛")

    print("\n🔢 向量化数据...")
    print("   (这可能需要几分钟...)")

    vectorizer = HistoricalVectorizer()

    stats = vectorizer.vectorize_all(batch_size=1000)

    print(f"\n✅ 向量化完成!")
    print(f"   成功向量化: {stats} 场比赛")

    print("\n📊 最终统计:")
    final_stats = vectorizer.get_vectorization_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 60)
    print("🎉 向量化完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
