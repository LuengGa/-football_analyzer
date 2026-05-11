#!/usr/bin/env python3
"""
深度分析数据集
"""
import json
import sys
from pathlib import Path
from collections import Counter

def deep_analyze(file_path):
    """深度分析数据"""
    
    print("="*80)
    print("🔎 深度数据分析")
    print("="*80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matches = data['matches']
    
    print(f"\n📊 总比赛数: {len(matches):,}")
    
    # 分析赔率数据
    print("\n" + "="*80)
    print("💰 赔率数据分析")
    print("="*80)
    
    opening_bookmakers = set()
    closing_bookmakers = set()
    matches_with_closing = 0
    matches_with_opening_and_closing = 0
    
    asian_opening = 0
    asian_closing = 0
    
    for match in matches:
        three_way = match.get('three_way_odds', {})
        
        if 'opening' in three_way and three_way['opening']:
            opening_bookmakers.update(three_way['opening'].keys())
        
        if 'closing' in three_way and three_way['closing']:
            closing_bookmakers.update(three_way['closing'].keys())
            matches_with_closing += 1
            
            if 'opening' in three_way and three_way['opening']:
                matches_with_opening_and_closing += 1
        
        # 亚盘
        asian = match.get('asian_handicap', {})
        if 'opening' in asian and asian['opening']:
            asian_opening += 1
        if 'closing' in asian and asian['closing']:
            asian_closing += 1
    
    print(f"\n🏛️  博彩公司:")
    print(f"  • 初盘机构数: {len(opening_bookmakers)}")
    print(f"  • 终盘机构数: {len(closing_bookmakers)}")
    print(f"  • 机构列表 (初盘): {sorted(list(opening_bookmakers))[:10]}")
    
    print(f"\n📈 数据覆盖:")
    print(f"  • 有终盘: {matches_with_closing:,} ({matches_with_closing/len(matches)*100:.1f}%)")
    print(f"  • 初盘+终盘: {matches_with_opening_and_closing:,} ({matches_with_opening_and_closing/len(matches)*100:.1f}%)")
    print(f"  • 亚盘初盘: {asian_opening:,} ({asian_opening/len(matches)*100:.1f}%)")
    print(f"  • 亚盘终盘: {asian_closing:,} ({asian_closing/len(matches)*100:.1f}%)")
    
    # 找几个有初盘和终盘的完整例子
    print("\n" + "="*80)
    print("📄 完整比赛示例 (含初盘和终盘)")
    print("="*80)
    
    complete_matches = []
    for match in matches:
        three_way = match.get('three_way_odds', {})
        if ('opening' in three_way and three_way['opening'] and 
            'closing' in three_way and three_way['closing']):
            complete_matches.append(match)
            if len(complete_matches) >= 3:
                break
    
    for i, match in enumerate(complete_matches, 1):
        print(f"\n{'='*80}")
        print(f"🎯 完整比赛 {i}: {match['home_team']} vs {match['away_team']} ({match['date']})")
        print(f"{'='*80}")
        print(f"比分: {match['home_goals']}-{match['away_goals']} ({match['result']})")
        
        three_way = match['three_way_odds']
        print(f"\n📊 初盘:")
        for bm, odds in three_way['opening'].items():
            print(f"  {bm}: H={odds['home']}, D={odds['draw']}, A={odds['away']}")
        
        print(f"\n📊 终盘:")
        for bm, odds in three_way['closing'].items():
            print(f"  {bm}: H={odds['home']}, D={odds['draw']}, A={odds['away']}")
    
    # 分析比赛统计数据完整性
    print("\n" + "="*80)
    print("📈 比赛统计数据完整性")
    print("="*80)
    
    stats_fields = {
        'shots.home': 0,
        'shots.home_on_target': 0, 
        'shots.away': 0,
        'shots.away_on_target': 0,
        'corners.home': 0,
        'corners.away': 0,
        'fouls.home': 0,
        'fouls.away': 0,
        'cards.home_yellow': 0,
        'cards.away_yellow': 0,
    }
    
    for match in matches:
        ms = match.get('match_stats', {})
        for field in stats_fields.keys():
            parts = field.split('.')
            if len(parts) == 2:
                cat, sub = parts
                if cat in ms and isinstance(ms[cat], dict) and sub in ms[cat] and ms[cat][sub] is not None:
                    stats_fields[field] += 1
    
    print(f"\n📊 统计数据完整度:")
    for field, count in stats_fields.items():
        print(f"  {field}: {count:,} ({count/len(matches)*100:.1f}%)")
    
    # 分析赛季和联赛分布
    print("\n" + "="*80)
    print("🏆 联赛和赛季分布")
    print("="*80)
    
    league_counts = Counter()
    season_counts = Counter()
    
    for match in matches:
        league_counts[match['league_name']] += 1
        season_counts[match['season']] += 1
    
    print(f"\n📊 联赛分布 (Top 10):")
    for league, cnt in league_counts.most_common(10):
        print(f"  {league}: {cnt:,} 场")
    
    print(f"\n📊 赛季分布 (最新):")
    for season in sorted(season_counts.keys(), reverse=True)[:10]:
        print(f"  {season}: {season_counts[season]:,} 场")
    
    # 保存数据结构说明
    print("\n" + "="*80)
    print("📋 数据结构文档")
    print("="*80)
    
    doc = {
        'total_matches': len(matches),
        'data_coverage': {
            'matches_with_opening': sum(1 for m in matches if m['three_way_odds'].get('opening')),
            'matches_with_closing': matches_with_closing,
            'matches_with_both': matches_with_opening_and_closing,
        },
        'bookmakers': {
            'opening': list(opening_bookmakers),
            'closing': list(closing_bookmakers),
        },
        'leagues': list(league_counts.keys()),
        'seasons': list(season_counts.keys()),
        'match_fields': list(matches[0].keys()) if matches else [],
    }
    
    with open('/Volumes/J ZAO 9 SER 1/Python/TRAE-SOLO/football_analyzer/data/data_documentation.json', 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据文档已保存到: data/data_documentation.json")


if __name__ == '__main__':
    data_file = '/Volumes/J ZAO 9 SER 1/Python/TRAE-SOLO/football_analyzer/INTEGRATED_COMPLETE_DATA.json'
    
    if not Path(data_file).exists():
        print(f"❌ 文件不存在: {data_file}")
        sys.exit(1)
    
    deep_analyze(data_file)
