#!/usr/bin/env python3
"""
分析历史数据结构
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def analyze_data_structure(file_path):
    """分析JSON数据结构"""
    
    print("="*80)
    print("📊 历史数据分析")
    print("="*80)
    
    # 先看文件大小
    file_size = Path(file_path).stat().st_size
    print(f"\n📁 文件大小: {file_size / (1024*1024):.2f} MB")
    
    print("\n⏳ 正在加载数据 (可能需要一些时间)...")
    
    # 增量读取，先看开头的结构
    with open(file_path, 'r', encoding='utf-8') as f:
        # 先读前100KB看结构
        sample = f.read(100*1024)
        
    print("\n🔍 数据结构分析:")
    
    # 尝试解析
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"\n✅ 成功加载数据!")
        
        # 分析根结构
        if isinstance(data, list):
            print(f"\n📋 数据类型: 列表")
            print(f"📊 总场次: {len(data):,}")
            
            if len(data) > 0:
                analyze_match_sample(data[0])
                
                # 统计一些基本信息
                print("\n" + "="*80)
                print("📈 数据统计")
                print("="*80)
                
                analyze_data_stats(data)
                
        elif isinstance(data, dict):
            print(f"\n📋 数据类型: 字典")
            print(f"🔑 顶级键: {list(data.keys())}")
            
            # 找到可能的比赛列表
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    print(f"\n📋 找到比赛列表: {key}, 数量: {len(value):,}")
                    analyze_match_sample(value[0])
                    analyze_data_stats(value)
                    break
                    
    except Exception as e:
        print(f"\n❌ 解析出错: {e}")
        print("\n尝试分析样本内容:")
        print(sample[:5000])


def analyze_match_sample(match):
    """分析单场比赛样本结构"""
    print("\n" + "="*80)
    print("🔬 单场比赛数据结构")
    print("="*80)
    
    print(f"\n🏟️  比赛字段:")
    for i, (key, value) in enumerate(match.items(), 1):
        print(f"  {i}. {key}: {type(value).__name__}")
        if isinstance(value, dict):
            print(f"     → 子字段: {list(value.keys())}")
    
    # 打印完整示例
    print("\n" + "="*80)
    print("📄 完整数据示例")
    print("="*80)
    print(json.dumps(match, ensure_ascii=False, indent=2))


def analyze_data_stats(matches):
    """分析数据统计"""
    
    leagues = set()
    teams = set()
    has_initial_odds = 0
    has_final_odds = 0
    has_both_odds = 0
    has_asian_handicap = 0
    has_total_goals = 0
    
    years = set()
    scores = []
    
    print("\n📊 正在分析数据统计...")
    
    for match in matches:
        # 联赛
        if 'league' in match:
            leagues.add(match['league'])
        elif 'competition' in match:
            leagues.add(match['competition'])
        
        # 球队
        if 'home_team' in match:
            teams.add(match['home_team'])
        if 'away_team' in match:
            teams.add(match['away_team'])
        
        # 初盘终盘
        has_initial = False
        has_final = False
        
        if 'odds' in match:
            odds = match['odds']
            if 'initial' in odds or 'opening' in odds or 'open' in odds:
                has_initial = True
                has_initial_odds += 1
            if 'final' in odds or 'closing' in odds or 'close' in odds:
                has_final = True
                has_final_odds += 1
            if has_initial and has_final:
                has_both_odds += 1
        
        # 亚盘
        if 'asian_handicap' in match or 'handicap' in match:
            has_asian_handicap += 1
        
        # 大小球
        if 'total_goals' in match or 'over_under' in match:
            has_total_goals += 1
        
        # 日期年份
        if 'date' in match:
            try:
                date_str = str(match['date'])
                year = date_str[:4]
                if year.isdigit():
                    years.add(year)
            except:
                pass
        
        # 比分
        if 'home_score' in match and 'away_score' in match:
            scores.append((match['home_score'], match['away_score']))
    
    print(f"\n📈 数据统计:")
    print(f"  • 联赛数量: {len(leagues)}")
    print(f"  • 球队数量: {len(teams)}")
    print(f"  • 年份范围: {sorted(years)}")
    
    print(f"\n💰 赔率数据覆盖:")
    print(f"  • 有初盘: {has_initial_odds:,} ({has_initial_odds/len(matches)*100:.1f}%)")
    print(f"  • 有终盘: {has_final_odds:,} ({has_final_odds/len(matches)*100:.1f}%)")
    print(f"  • 初盘+终盘: {has_both_odds:,} ({has_both_odds/len(matches)*100:.1f}%)")
    print(f"  • 有亚盘: {has_asian_handicap:,} ({has_asian_handicap/len(matches)*100:.1f}%)")
    print(f"  • 有大小球: {has_total_goals:,} ({has_total_goals/len(matches)*100:.1f}%)")
    
    if scores:
        print(f"\n⚽ 比分统计 (样本):")
        # 最常见比分
        from collections import Counter
        score_counts = Counter(scores[:1000])  # 只看前1000场样本
        print(f"  • 最常见比分 (Top 5):")
        for (h, a), cnt in score_counts.most_common(5):
            print(f"    {h}-{a}: {cnt}次")
    
    print(f"\n🏆 联赛列表 (样本):")
    for league in sorted(list(leagues))[:20]:
        print(f"  • {league}")
    if len(leagues) > 20:
        print(f"  ... 还有 {len(leagues)-20} 个联赛")


if __name__ == '__main__':
    data_file = '/Volumes/J ZAO 9 SER 1/Python/TRAE-SOLO/football_analyzer/INTEGRATED_COMPLETE_DATA.json'
    
    if not Path(data_file).exists():
        print(f"❌ 文件不存在: {data_file}")
        sys.exit(1)
    
    analyze_data_structure(data_file)
