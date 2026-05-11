"""
训练历史数据模型
使用用户提供的20万+场比赛数据训练ELO和xG模型
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.calculations.math.elo_rating import EloRating
from src.calculations.math.dixon_coles_predictor import DixonColesPredictor

print("=" * 70)
print("🏆 历史数据模型训练")
print("=" * 70)

# 加载数据
print("\n📂 加载历史数据...")
with open('data/COMPLETE_FOOTBALL_DATA_FINAL_UPDATED.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

matches = data['matches']
print(f"✅ 成功加载 {len(matches):,} 场比赛")

# 转换为DataFrame
df = pd.DataFrame(matches)
print(f"\n📊 数据统计:")
print(f"   日期范围: {df['date'].min()} 至 {df['date'].max()}")
print(f"   联赛数量: {df['league'].nunique()}")
print(f"   球队数量: {len(set(df['home_team'].unique()) | set(df['away_team'].unique()))}")

# 计算基础统计
total_matches = len(df)
home_wins = (df['result'].str.startswith('3')).sum()
draws = (df['result'] == 'X').sum() if df['result'].dtype == object else (df['home_goals'] == df['away_goals']).sum()
away_wins = (df['result'].str.startswith('0')).sum() if df['result'].dtype == object else (df['home_goals'] < df['away_goals']).sum()

print(f"\n⚽ 比赛结果分布:")
print(f"   主场胜: {home_wins:,} ({home_wins/total_matches*100:.1f}%)")
print(f"   平局: {draws:,} ({draws/total_matches*100:.1f}%)")
print(f"   客场胜: {away_wins:,} ({away_wins/total_matches*100:.1f}%)")

# 训练ELO评分系统
print("\n" + "=" * 70)
print("📈 训练 ELO 评分系统...")
print("=" * 70)

elo = EloRating(initial_rating=1800, k_factor=32)

# 初始化所有球队的ELO
teams = list(set(df['home_team'].unique()) | set(df['away_team'].unique()))
elo_ratings = {team: 1800 for team in teams}

# 按日期排序并更新ELO
df_sorted = df.sort_values('date')
update_count = 0

for _, row in df_sorted.iterrows():
    home_team = row['home_team']
    away_team = row['away_team']
    
    home_elo = elo_ratings[home_team]
    away_elo = elo_ratings[away_team]
    
    # 计算期望胜率
    expected_home = elo.calculate_expectation(home_elo, away_elo)
    
    # 确定实际结果
    home_goals = row['home_goals']
    away_goals = row['away_goals']
    
    if home_goals > away_goals:
        actual_home = 1.0
    elif home_goals == away_goals:
        actual_home = 0.5
    else:
        actual_home = 0.0
    
    # 更新ELO
    elo_ratings[home_team] = elo.calculate_elo_after_match(home_elo, expected_home, actual_home)
    elo_ratings[away_team] = elo.calculate_elo_after_match(away_elo, 1 - expected_home, 1 - actual_home)
    
    update_count += 1

print(f"✅ ELO更新完成: {update_count:,} 场比赛")

# 显示TOP 20强队
print("\n🏆 TOP 20 ELO评分最高的球队:")
top_teams = sorted(elo_ratings.items(), key=lambda x: -x[1])[:20]
for i, (team, rating) in enumerate(top_teams, 1):
    print(f"   {i:2d}. {team:25s} {rating:.0f}")

# 显示最弱球队
print("\n📉 ELO评分最低的5支球队:")
bottom_teams = sorted(elo_ratings.items(), key=lambda x: x[1])[:5]
for i, (team, rating) in enumerate(bottom_teams, 1):
    print(f"   {i}. {team:25s} {rating:.0f}")

# 保存ELO评分
print("\n💾 保存ELO评分...")
with open('data/elo_ratings.json', 'w', encoding='utf-8') as f:
    json.dump(elo_ratings, f, ensure_ascii=False, indent=2)
print(f"✅ ELO评分已保存到 data/elo_ratings.json")

# 训练xG模型
print("\n" + "=" * 70)
print("📊 训练 xG 预测模型...")
print("=" * 70)

# 计算联赛平均进球
avg_goals = df['home_goals'].mean() + df['away_goals'].mean()
print(f"场均进球数: {avg_goals:.2f}")

# 计算球队进攻/防守能力
home_stats = df.groupby('home_team').agg({
    'home_goals': 'mean',
    'away_goals': 'mean'
}).rename(columns={'home_goals': 'home_scored', 'away_goals': 'home_conceded'})

away_stats = df.groupby('away_team').agg({
    'away_goals': 'mean',
    'home_goals': 'mean'
}).rename(columns={'away_goals': 'away_scored', 'home_goals': 'away_conceded'})

team_stats = pd.merge(home_stats, away_stats, left_index=True, right_index=True)
team_stats['avg_attack'] = (team_stats['home_scored'] + team_stats['away_scored']) / 2
team_stats['avg_defense'] = (team_stats['home_conceded'] + team_stats['away_conceded']) / 2

# 标准化
avg_attack = team_stats['avg_attack'].mean()
avg_defense = team_stats['avg_defense'].mean()

team_stats['attack_norm'] = team_stats['avg_attack'] / avg_attack
team_stats['defense_norm'] = avg_defense / team_stats['avg_defense']

# 主场优势
home_advantage = home_wins / total_matches
print(f"主场胜率: {home_advantage*100:.1f}%")

# 保存xG参数
xg_params = {
    'avg_goals': round(avg_goals, 3),
    'avg_attack': round(avg_attack, 3),
    'avg_defense': round(avg_defense, 3),
    'home_advantage': round(home_advantage, 3),
    'teams': {}
}

for team in team_stats.index:
    xg_params['teams'][team] = {
        'attack': round(team_stats.loc[team, 'attack_norm'], 3),
        'defense': round(team_stats.loc[team, 'defense_norm'], 3)
    }

print(f"✅ xG模型训练完成: {len(xg_params['teams'])} 支球队")

# 保存xG参数
with open('data/xg_params.json', 'w', encoding='utf-8') as f:
    json.dump(xg_params, f, ensure_ascii=False, indent=2)
print(f"✅ xG参数已保存到 data/xg_params.json")

# 训练Dixon-Coles模型
print("\n" + "=" * 70)
print("🧮 训练 Dixon-Coles 预测模型...")
print("=" * 70)

dc = DixonColesPredictor()

# 准备训练数据
dc_matches = []
for _, row in df_sorted.iterrows():
    dc_matches.append({
        'home_team': row['home_team'],
        'away_team': row['away_team'],
        'home_goals': int(row['home_goals']),
        'away_goals': int(row['away_goals'])
    })

dc.fit(dc_matches)
print(f"✅ Dixon-Coles模型训练完成")

# 生成联赛统计
print("\n📋 联赛统计:")
for league in df['league'].unique()[:10]:
    league_df = df[df['league'] == league]
    print(f"   {league}: {len(league_df):,} 场比赛")

print("\n" + "=" * 70)
print("✅ 历史数据模型训练完成！")
print("=" * 70)
print(f"""
📊 训练结果摘要:
   • ELO评分: {len(elo_ratings)} 支球队
   • xG模型: {len(xg_params['teams'])} 支球队
   • Dixon-Coles: 已训练
   • 数据覆盖: {df['date'].min()} 至 {df['date'].max()}

🎯 系统现在可以:
   1. 使用训练好的ELO评分预测比赛
   2. 使用xG模型评估球队进攻/防守能力
   3. 使用Dixon-Coles模型预测概率分布
   4. 支持所有29种玩法类型

💡 提示: 历史数据已加载，模型已训练完成！
""")
