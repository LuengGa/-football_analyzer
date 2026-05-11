"""
历史数据加载器 - A任务: 数据对接和历史数据库建设
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import pickle
from collections import defaultdict

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class HistoricalMatch:
    """历史比赛数据结构"""
    match_id: str
    league: str
    league_name: str
    season: str
    season_year: int
    date: str
    year: int
    month: int
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    result: str
    
    # 赔率数据
    opening_odds: Optional[Dict[str, Dict[str, float]]] = None  # {bookmaker: {home, draw, away}}
    closing_odds: Optional[Dict[str, Dict[str, float]]] = None
    
    # 亚盘
    asian_handicap_opening: Optional[Dict[str, Dict[str, float]]] = None
    asian_handicap_closing: Optional[Dict[str, Dict[str, float]]] = None
    
    # 半场数据
    half_time_home_goals: Optional[int] = None
    half_time_away_goals: Optional[int] = None
    half_time_result: Optional[str] = None
    
    # 比赛统计
    shots_home: Optional[int] = None
    shots_away: Optional[int] = None
    shots_home_on_target: Optional[int] = None
    shots_away_on_target: Optional[int] = None
    corners_home: Optional[int] = None
    corners_away: Optional[int] = None
    fouls_home: Optional[int] = None
    fouls_away: Optional[int] = None
    cards_home_yellow: Optional[int] = None
    cards_away_yellow: Optional[int] = None
    
    bookmakers_count_opening: Optional[int] = None
    bookmakers_count_closing: Optional[int] = None


class HistoricalDataLoader:
    """历史数据加载器"""
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or '/Volumes/J ZAO 9 SER 1/Python/TRAE-SOLO/football_analyzer/INTEGRATED_COMPLETE_DATA.json'
        self.matches: List[HistoricalMatch] = []
        self.matches_by_league: Dict[str, List[HistoricalMatch]] = defaultdict(list)
        self.matches_by_season: Dict[str, List[HistoricalMatch]] = defaultdict(list)
        self.teams: set = set()
        self.leagues: set = set()
        self.loaded = False
    
    def load(self, limit: Optional[int] = None):
        """加载数据"""
        print("📂 正在加载历史数据...")
        
        if not Path(self.data_path).exists():
            raise FileNotFoundError(f"数据文件不存在: {self.data_path}")
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        matches_data = raw_data.get('matches', [])
        
        if limit:
            matches_data = matches_data[:limit]
        
        print(f"📊 解析 {len(matches_data):,} 场比赛...")
        
        for match_data in matches_data:
            match = self._parse_match(match_data)
            self.matches.append(match)
            
            self.matches_by_league[match.league_name].append(match)
            self.matches_by_season[match.season].append(match)
            
            self.teams.add(match.home_team)
            self.teams.add(match.away_team)
            self.leagues.add(match.league_name)
        
        self.loaded = True
        
        print(f"✅ 数据加载完成!")
        print(f"  • 总场次: {len(self.matches):,}")
        print(f"  • 联赛数: {len(self.leagues)}")
        print(f"  • 球队数: {len(self.teams)}")
        
        return self
    
    def _parse_match(self, match_data: Dict) -> HistoricalMatch:
        """解析单场比赛数据"""
        
        # 生成唯一ID
        match_id = f"{match_data['league']}_{match_data['date']}_{match_data['home_team']}_{match_data['away_team']}"
        
        # 赔率数据
        three_way = match_data.get('three_way_odds', {})
        
        opening_odds = three_way.get('opening', {}) if three_way else None
        closing_odds = three_way.get('closing', {}) if three_way else None
        
        # 亚盘
        asian = match_data.get('asian_handicap', {})
        asian_opening = asian.get('opening', {}) if asian else None
        asian_closing = asian.get('closing', {}) if asian else None
        
        # 半场数据
        ht = match_data.get('half_time', {})
        
        # 比赛统计
        ms = match_data.get('match_stats', {})
        shots = ms.get('shots', {}) if ms else {}
        corners = ms.get('corners', {}) if ms else {}
        fouls = ms.get('fouls', {}) if ms else {}
        cards = ms.get('cards', {}) if ms else {}
        
        # 机构数
        bm_count = match_data.get('bookmakers_count', {})
        
        # 转换结果格式: H/D/A -> home/draw/away
        raw_result = match_data['result']
        if raw_result == 'H':
            standard_result = 'home'
        elif raw_result == 'D':
            standard_result = 'draw'
        elif raw_result == 'A':
            standard_result = 'away'
        else:
            standard_result = raw_result
        
        return HistoricalMatch(
            match_id=match_id,
            league=match_data['league'],
            league_name=match_data['league_name'],
            season=match_data['season'],
            season_year=match_data['season_year'],
            date=match_data['date'],
            year=match_data['year'],
            month=match_data['month'],
            home_team=match_data['home_team'],
            away_team=match_data['away_team'],
            home_goals=match_data['home_goals'],
            away_goals=match_data['away_goals'],
            result=standard_result,
            
            opening_odds=opening_odds,
            closing_odds=closing_odds,
            asian_handicap_opening=asian_opening,
            asian_handicap_closing=asian_closing,
            
            half_time_home_goals=ht.get('home_goals'),
            half_time_away_goals=ht.get('away_goals'),
            half_time_result=ht.get('result'),
            
            shots_home=shots.get('home'),
            shots_away=shots.get('away'),
            shots_home_on_target=shots.get('home_on_target'),
            shots_away_on_target=shots.get('away_on_target'),
            corners_home=corners.get('home'),
            corners_away=corners.get('away'),
            fouls_home=fouls.get('home'),
            fouls_away=fouls.get('away'),
            cards_home_yellow=cards.get('home_yellow'),
            cards_away_yellow=cards.get('away_yellow'),
            
            bookmakers_count_opening=bm_count.get('opening'),
            bookmakers_count_closing=bm_count.get('closing'),
        )
    
    def get_matches_by_league(self, league_name: str) -> List[HistoricalMatch]:
        """获取特定联赛的比赛"""
        return self.matches_by_league.get(league_name, [])
    
    def get_matches_by_season(self, season: str) -> List[HistoricalMatch]:
        """获取特定赛季的比赛"""
        return self.matches_by_season.get(season, [])
    
    def get_team_matches(self, team_name: str) -> List[HistoricalMatch]:
        """获取特定球队的所有比赛"""
        team_matches = []
        for match in self.matches:
            if team_name in (match.home_team, match.away_team):
                team_matches.append(match)
        return team_matches
    
    def get_matches_with_full_odds(self) -> List[HistoricalMatch]:
        """获取有初盘和终盘数据的比赛"""
        return [
            m for m in self.matches 
            if m.opening_odds and m.closing_odds
        ]
    
    def get_statistics(self) -> Dict:
        """获取数据统计"""
        full_odds = self.get_matches_with_full_odds()
        
        return {
            'total_matches': len(self.matches),
            'full_odds_matches': len(full_odds),
            'full_odds_percent': len(full_odds)/len(self.matches)*100 if self.matches else 0,
            'leagues': sorted(list(self.leagues)),
            'teams_count': len(self.teams),
            'seasons': sorted(list(self.matches_by_season.keys())),
        }
    
    def save_cache(self, cache_path: str = '/Volumes/J ZAO 9 SER 1/Python/TRAE-SOLO/football_analyzer/data/historical_data.pkl'):
        """保存缓存"""
        print(f"💾 保存缓存到: {cache_path}")
        cache_dir = Path(cache_path).parent
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'wb') as f:
            pickle.dump({
                'matches': self.matches,
                'matches_by_league': dict(self.matches_by_league),
                'matches_by_season': dict(self.matches_by_season),
                'teams': self.teams,
                'leagues': self.leagues,
            }, f)
        
        print("✅ 缓存保存完成!")
    
    def load_cache(self, cache_path: str = '/Volumes/J ZAO 9 SER 1/Python/TRAE-SOLO/football_analyzer/data/historical_data.pkl') -> bool:
        """从缓存加载"""
        if not Path(cache_path).exists():
            return False
        
        print(f"📦 从缓存加载: {cache_path}")
        
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            self.matches = data['matches']
            self.matches_by_league = defaultdict(list, data['matches_by_league'])
            self.matches_by_season = defaultdict(list, data['matches_by_season'])
            self.teams = data['teams']
            self.leagues = data['leagues']
            self.loaded = True
            
            print(f"✅ 缓存加载成功!")
            print(f"  • 总场次: {len(self.matches):,}")
            
            return True
        except Exception as e:
            print(f"⚠️  缓存加载失败: {e}")
            return False


# 全局实例
_data_loader: Optional[HistoricalDataLoader] = None


def get_historical_data_loader() -> HistoricalDataLoader:
    """获取历史数据加载器单例"""
    global _data_loader
    if _data_loader is None:
        _data_loader = HistoricalDataLoader()
    return _data_loader


def initialize_data(force_reload: bool = False):
    """初始化数据 - 尝试缓存，不行就加载原文件"""
    loader = get_historical_data_loader()
    
    if not force_reload:
        if loader.load_cache():
            return loader
    
    loader.load()
    loader.save_cache()
    
    return loader


if __name__ == '__main__':
    print("="*80)
    print("📊 历史数据加载器测试")
    print("="*80)
    
    # 先尝试缓存
    loader = initialize_data()
    
    # 打印统计
    stats = loader.get_statistics()
    print(f"\n📈 数据统计:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 看看一场完整的比赛
    full_odds = loader.get_matches_with_full_odds()
    if full_odds:
        print(f"\n🎯 完整赔率比赛示例:")
        print(json.dumps(asdict(full_odds[0]), indent=2, ensure_ascii=False)[:2000])
