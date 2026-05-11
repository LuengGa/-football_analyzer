"""
HistoricalDataManager - 历史数据管理器
负责加载、处理和分析历史比赛数据
支持多种数据格式和20万+场历史数据
"""
from typing import Dict, Any, List, Optional
import os
import json
import csv
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path


class DataLoader:
    """数据加载器基类"""
    
    def __init__(self):
        pass
    
    def load(self, file_path: str) -> pd.DataFrame:
        """加载数据"""
        raise NotImplementedError


class CSVLoader(DataLoader):
    """CSV文件加载器"""
    
    def load(self, file_path: str) -> pd.DataFrame:
        """加载CSV文件"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            print(f"[CSVLoader] 成功加载 {len(df)} 条记录")
            return df
        except Exception as e:
            print(f"[CSVLoader] 加载失败: {e}")
            return pd.DataFrame()


class JSONLoader(DataLoader):
    """JSON文件加载器"""
    
    def load(self, file_path: str) -> pd.DataFrame:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
            else:
                df = pd.DataFrame([data])
            
            print(f"[JSONLoader] 成功加载 {len(df)} 条记录")
            return df
        except Exception as e:
            print(f"[JSONLoader] 加载失败: {e}")
            return pd.DataFrame()


class ParquetLoader(DataLoader):
    """Parquet文件加载器"""
    
    def load(self, file_path: str) -> pd.DataFrame:
        """加载Parquet文件"""
        try:
            df = pd.read_parquet(file_path)
            print(f"[ParquetLoader] 成功加载 {len(df)} 条记录")
            return df
        except Exception as e:
            print(f"[ParquetLoader] 加载失败: {e}")
            return pd.DataFrame()


class HistoricalDataManager:
    """历史数据管理器"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "historical"
            )
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 注册加载器
        self.loaders = {
            '.csv': CSVLoader(),
            '.json': JSONLoader(),
            '.parquet': ParquetLoader(),
            '.pq': ParquetLoader()
        }
        
        # 已加载的数据
        self.matches_data = None
        self.teams_data = None
        self.odds_data = None
        
        # 统计信息
        self.stats = {}
    
    def load_data(self, file_path: str) -> bool:
        """加载数据文件"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in self.loaders:
            print(f"[HistoricalDataManager] 不支持的文件格式: {file_ext}")
            return False
        
        loader = self.loaders[file_ext]
        df = loader.load(file_path)
        
        if df.empty:
            return False
        
        # 根据文件名推断数据类型
        file_name = Path(file_path).name.lower()
        
        if 'match' in file_name or 'fixture' in file_name:
            self.matches_data = df
            self._process_matches_data()
        elif 'team' in file_name:
            self.teams_data = df
        elif 'odd' in file_name:
            self.odds_data = df
        
        return True
    
    def load_directory(self, dir_path: str = None) -> int:
        """加载目录中的所有数据文件"""
        if dir_path is None:
            dir_path = self.data_dir
        
        loaded_count = 0
        for file_path in Path(dir_path).glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.loaders:
                if self.load_data(str(file_path)):
                    loaded_count += 1
        
        print(f"[HistoricalDataManager] 共加载 {loaded_count} 个文件")
        return loaded_count
    
    def _process_matches_data(self):
        """处理比赛数据"""
        if self.matches_data is None:
            return
        
        df = self.matches_data.copy()
        
        # 确保必要的列存在
        required_columns = ['home_team', 'away_team', 'home_goals', 'away_goals', 'date']
        for col in required_columns:
            if col not in df.columns:
                print(f"[HistoricalDataManager] 警告: 缺少列 {col}")
        
        # 转换日期格式
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # 计算比赛结果
        if 'home_goals' in df.columns and 'away_goals' in df.columns:
            df['result'] = np.where(df['home_goals'] > df['away_goals'], 'H',
                                   np.where(df['home_goals'] < df['away_goals'], 'A', 'D'))
        
        self.matches_data = df
        self._calculate_stats()
    
    def _calculate_stats(self):
        """计算统计信息"""
        if self.matches_data is None:
            return
        
        df = self.matches_data
        
        self.stats = {
            'total_matches': len(df),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d') if not df['date'].isna().all() else None,
                'end': df['date'].max().strftime('%Y-%m-%d') if not df['date'].isna().all() else None
            },
            'leagues': df['league'].nunique() if 'league' in df.columns else 0,
            'teams': len(set(df['home_team'].unique()) | set(df['away_team'].unique())) if 'home_team' in df.columns else 0,
            'result_distribution': {
                'home_win': (df['result'] == 'H').sum(),
                'draw': (df['result'] == 'D').sum(),
                'away_win': (df['result'] == 'A').sum()
            } if 'result' in df.columns else {}
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats
    
    def get_matches_by_league(self, league: str) -> pd.DataFrame:
        """按联赛获取比赛"""
        if self.matches_data is None:
            return pd.DataFrame()
        
        return self.matches_data[self.matches_data['league'] == league]
    
    def get_matches_by_team(self, team: str) -> pd.DataFrame:
        """按球队获取比赛"""
        if self.matches_data is None:
            return pd.DataFrame()
        
        return self.matches_data[
            (self.matches_data['home_team'] == team) | (self.matches_data['away_team'] == team)
        ]
    
    def get_recent_matches(self, days: int = 30) -> pd.DataFrame:
        """获取近期比赛"""
        if self.matches_data is None:
            return pd.DataFrame()
        
        if 'date' not in self.matches_data.columns:
            return pd.DataFrame()
        
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        return self.matches_data[self.matches_data['date'] >= cutoff_date]
    
    def prepare_for_backtesting(self) -> pd.DataFrame:
        """准备回测数据"""
        if self.matches_data is None:
            return pd.DataFrame()
        
        df = self.matches_data.copy()
        
        # 确保数据完整
        required_cols = ['home_team', 'away_team', 'home_goals', 'away_goals']
        df = df.dropna(subset=required_cols)
        
        # 添加计算字段
        df['total_goals'] = df['home_goals'] + df['away_goals']
        df['goal_diff'] = df['home_goals'] - df['away_goals']
        
        return df
    
    def train_elo(self, initial_rating: int = 1800, k_factor: int = 32) -> Dict[str, int]:
        """训练ELO评分"""
        if self.matches_data is None:
            return {}
        
        df = self.prepare_for_backtesting()
        if df.empty:
            return {}
        
        # 按日期排序
        df = df.sort_values('date')
        
        # 初始化ELO评分
        teams = set(df['home_team'].unique()) | set(df['away_team'].unique())
        elo_ratings = {team: initial_rating for team in teams}
        
        # 计算比赛
        for _, row in df.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']
            home_goals = row['home_goals']
            away_goals = row['away_goals']
            
            home_elo = elo_ratings[home_team]
            away_elo = elo_ratings[away_team]
            
            # 计算期望胜率
            expected_home = 1 / (1 + 10 ** ((away_elo - home_elo) / 400))
            
            # 确定实际结果
            if home_goals > away_goals:
                actual_home = 1.0
            elif home_goals == away_goals:
                actual_home = 0.5
            else:
                actual_home = 0.0
            
            # 更新ELO
            elo_ratings[home_team] += k_factor * (actual_home - expected_home)
            elo_ratings[away_team] += k_factor * ((1 - actual_home) - (1 - expected_home))
        
        # 四舍五入
        elo_ratings = {team: round(rating) for team, rating in elo_ratings.items()}
        
        print(f"[HistoricalDataManager] ELO训练完成，覆盖 {len(elo_ratings)} 支球队")
        return elo_ratings
    
    def train_xg_model(self) -> Dict[str, Any]:
        """训练xG模型"""
        if self.matches_data is None:
            return {}
        
        df = self.prepare_for_backtesting()
        if df.empty:
            return {}
        
        # 计算球队进攻/防守能力
        home_stats = df.groupby('home_team').agg({
            'home_goals': 'mean',
            'away_goals': 'mean'
        }).rename(columns={'home_goals': 'home_scored', 'away_goals': 'home_conceded'})
        
        away_stats = df.groupby('away_team').agg({
            'away_goals': 'mean',
            'home_goals': 'mean'
        }).rename(columns={'away_goals': 'away_scored', 'home_goals': 'away_conceded'})
        
        # 合并统计
        team_stats = pd.merge(home_stats, away_stats, left_index=True, right_index=True)
        team_stats['attack'] = (team_stats['home_scored'] + team_stats['away_scored']) / 2
        team_stats['defense'] = (team_stats['home_conceded'] + team_stats['away_conceded']) / 2
        
        # 标准化
        avg_attack = team_stats['attack'].mean()
        avg_defense = team_stats['defense'].mean()
        
        team_stats['attack_norm'] = team_stats['attack'] / avg_attack
        team_stats['defense_norm'] = avg_defense / team_stats['defense']
        
        # 计算主场优势
        home_win_rate = (df['result'] == 'H').mean()
        away_win_rate = (df['result'] == 'A').mean()
        home_advantage = home_win_rate / (home_win_rate + away_win_rate)
        
        return {
            'team_stats': team_stats[['attack_norm', 'defense_norm']].to_dict('index'),
            'home_advantage': round(home_advantage - 0.5, 3),
            'avg_goals': round(avg_attack, 2),
            'teams_count': len(team_stats)
        }
    
    def export_elo_ratings(self, file_path: str):
        """导出ELO评分"""
        elo_ratings = self.train_elo()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(elo_ratings, f, ensure_ascii=False, indent=2)
        
        print(f"[HistoricalDataManager] ELO评分已导出到 {file_path}")
    
    def export_xg_params(self, file_path: str):
        """导出xG参数"""
        xg_params = self.train_xg_model()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(xg_params, f, ensure_ascii=False, indent=2)
        
        print(f"[HistoricalDataManager] xG参数已导出到 {file_path}")
    
    def get_team_history(self, team: str, recent_n: int = 10) -> List[Dict[str, Any]]:
        """获取球队近期战绩"""
        matches = self.get_matches_by_team(team)
        if matches.empty:
            return []
        
        matches = matches.sort_values('date', ascending=False).head(recent_n)
        
        history = []
        for _, row in matches.iterrows():
            is_home = row['home_team'] == team
            opponent = row['away_team'] if is_home else row['home_team']
            goals_for = row['home_goals'] if is_home else row['away_goals']
            goals_against = row['away_goals'] if is_home else row['home_goals']
            
            history.append({
                'date': row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else None,
                'is_home': is_home,
                'opponent': opponent,
                'goals_for': int(goals_for),
                'goals_against': int(goals_against),
                'result': 'W' if goals_for > goals_against else 'D' if goals_for == goals_against else 'L'
            })
        
        return history
    
    def get_league_table(self, league: str = None) -> pd.DataFrame:
        """获取积分榜"""
        if self.matches_data is None:
            return pd.DataFrame()
        
        df = self.matches_data.copy()
        if league:
            df = df[df['league'] == league]
        
        # 计算积分
        points = []
        for _, row in df.iterrows():
            if row['result'] == 'H':
                points.append({'team': row['home_team'], 'points': 3, 'gd': row['home_goals'] - row['away_goals'], 'gf': row['home_goals'], 'ga': row['away_goals']})
                points.append({'team': row['away_team'], 'points': 0, 'gd': row['away_goals'] - row['home_goals'], 'gf': row['away_goals'], 'ga': row['home_goals']})
            elif row['result'] == 'A':
                points.append({'team': row['home_team'], 'points': 0, 'gd': row['home_goals'] - row['away_goals'], 'gf': row['home_goals'], 'ga': row['away_goals']})
                points.append({'team': row['away_team'], 'points': 3, 'gd': row['away_goals'] - row['home_goals'], 'gf': row['away_goals'], 'ga': row['home_goals']})
            else:
                points.append({'team': row['home_team'], 'points': 1, 'gd': 0, 'gf': row['home_goals'], 'ga': row['away_goals']})
                points.append({'team': row['away_team'], 'points': 1, 'gd': 0, 'gf': row['away_goals'], 'ga': row['home_goals']})
        
        if not points:
            return pd.DataFrame()
        
        points_df = pd.DataFrame(points)
        table = points_df.groupby('team').agg({
            'points': 'sum',
            'gd': 'sum',
            'gf': 'sum',
            'ga': 'sum'
        }).reset_index()
        
        table['matches'] = df.groupby('home_team').size() + df.groupby('away_team').size()
        table = table.sort_values(['points', 'gd', 'gf'], ascending=False).reset_index(drop=True)
        table['rank'] = table.index + 1
        
        return table[['rank', 'team', 'matches', 'gf', 'ga', 'gd', 'points']]


# 全局实例
_historical_data_manager = None

def get_historical_data_manager(data_dir: str = None) -> HistoricalDataManager:
    """获取历史数据管理器实例"""
    global _historical_data_manager
    
    if _historical_data_manager is None:
        _historical_data_manager = HistoricalDataManager(data_dir)
    
    return _historical_data_manager


if __name__ == "__main__":
    print("=" * 60)
    print("📊 历史数据管理器测试")
    print("=" * 60)
    
    manager = get_historical_data_manager()
    
    print("\n测试数据加载功能:")
    print("  • 支持格式: CSV, JSON, Parquet")
    print("  • 数据目录: ", manager.data_dir)
    
    # 创建示例数据进行测试
    sample_data = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'league': 'Premier League',
        'home_team': ['Arsenal', 'Liverpool', 'Man United', 'Chelsea', 'Tottenham'] * 20,
        'away_team': ['Chelsea', 'Arsenal', 'Liverpool', 'Tottenham', 'Man United'] * 20,
        'home_goals': np.random.randint(0, 5, 100),
        'away_goals': np.random.randint(0, 5, 100)
    })
    
    # 保存示例数据
    sample_file = manager.data_dir / 'sample_matches.csv'
    sample_data.to_csv(sample_file, index=False)
    
    # 加载数据
    manager.load_data(str(sample_file))
    
    print("\n📈 数据统计:")
    stats = manager.get_stats()
    print(f"  比赛总数: {stats['total_matches']}")
    print(f"  日期范围: {stats['date_range']['start']} - {stats['date_range']['end']}")
    print(f"  球队数量: {stats['teams']}")
    
    print("\n🏆 积分榜:")
    table = manager.get_league_table('Premier League')
    print(table[['rank', 'team', 'points', 'gd']].to_string(index=False))
    
    print("\n⚽ ELO训练:")
    elo = manager.train_elo()
    top_teams = sorted(elo.items(), key=lambda x: -x[1])[:5]
    for team, rating in top_teams:
        print(f"  {team}: {rating}")
    
    print("\n✅ 历史数据管理器测试完成！")
