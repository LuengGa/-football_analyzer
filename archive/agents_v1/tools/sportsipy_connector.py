"""
Sportsipy 数据源连接器
为 AFA 数字生命体提供体育数据
"""
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "..", "data")
CACHE_DIR = os.path.join(DATA_DIR, "sportsipy_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

class SportsipyConnector:
    """
    Sportsipy 数据源连接器
    
    支持模式：
    - 模拟模式 (默认) - 使用本地模拟数据，不需要外部依赖
    - 真实模式 - 接入真实的 Sportsipy API
    
    说明：为了避免外部依赖，默认使用模拟模式
    """
    
    def __init__(self, use_cache: bool = True, use_real_api: bool = False):
        self.use_cache = use_cache
        self.use_real_api = use_real_api
        self._init_sample_data()
        
    def _init_sample_data(self):
        """初始化示例数据"""
        self.sample_teams = {
            "Arsenal": {
                "name": "Arsenal",
                "elo": 1850,
                "recent_form": "WWWDW",
                "goals_scored": 45,
                "goals_conceded": 28,
                "league": "Premier League",
                "league_position": 2
            },
            "Chelsea": {
                "name": "Chelsea",
                "elo": 1830,
                "recent_form": "WWLWD",
                "goals_scored": 42,
                "goals_conceded": 30,
                "league": "Premier League",
                "league_position": 4
            },
            "Liverpool": {
                "name": "Liverpool",
                "elo": 1880,
                "recent_form": "WWWWW",
                "goals_scored": 52,
                "goals_conceded": 22,
                "league": "Premier League",
                "league_position": 1
            },
            "Manchester City": {
                "name": "Manchester City",
                "elo": 1920,
                "recent_form": "WWWWD",
                "goals_scored": 58,
                "goals_conceded": 18,
                "league": "Premier League",
                "league_position": 3
            },
            "Tottenham Hotspur": {
                "name": "Tottenham Hotspur",
                "elo": 1800,
                "recent_form": "WLWDW",
                "goals_scored": 38,
                "goals_conceded": 35,
                "league": "Premier League",
                "league_position": 5
            },
            "Manchester United": {
                "name": "Manchester United",
                "elo": 1780,
                "recent_form": "WLDLW",
                "goals_scored": 35,
                "goals_conceded": 38,
                "league": "Premier League",
                "league_position": 6
            }
        }
        
        self.sample_matches = []
        today = datetime.now()
        for i in range(1, 15):
            match_date = today + timedelta(days=i)
            if i == 4:
                self.sample_matches.append({
                    "id": f"{match_date.strftime('%Y-%m-%d')}_Arsenal_Chelsea",
                    "date": match_date.strftime("%Y-%m-%d"),
                    "league": "Premier League",
                    "home_team": "Arsenal",
                    "away_team": "Chelsea",
                    "home_goals": None,
                    "away_goals": None,
                    "odds": {"home": 1.85, "draw": 3.40, "away": 4.20}
                })
            elif i == 5:
                self.sample_matches.append({
                    "id": f"{match_date.strftime('%Y-%m-%d')}_Liverpool_Manchester City",
                    "date": match_date.strftime("%Y-%m-%d"),
                    "league": "Premier League",
                    "home_team": "Liverpool",
                    "away_team": "Manchester City",
                    "home_goals": None,
                    "away_goals": None,
                    "odds": {"home": 2.40, "draw": 3.20, "away": 2.80}
                })
            elif i == 7:
                self.sample_matches.append({
                    "id": f"{match_date.strftime('%Y-%m-%d')}_Tottenham Hotspur_Manchester United",
                    "date": match_date.strftime("%Y-%m-%d"),
                    "league": "Premier League",
                    "home_team": "Tottenham Hotspur",
                    "away_team": "Manchester United",
                    "home_goals": None,
                    "away_goals": None,
                    "odds": {"home": 2.20, "draw": 3.30, "away": 3.10}
                })
        
        self.historical_results = {}
        for i in range(1, 30):
            match_date = today - timedelta(days=i)
            if i == 16:
                self.historical_results[f"{match_date.strftime('%Y-%m-%d')}_Arsenal_Chelsea"] = {
                    "home_goals": 2,
                    "away_goals": 1
                }
            elif i == 47:
                self.historical_results[f"{match_date.strftime('%Y-%m-%d')}_Liverpool_Arsenal"] = {
                    "home_goals": 2,
                    "away_goals": 2
                }
            elif i == 10:
                self.historical_results[f"{match_date.strftime('%Y-%m-%d')}_Tottenham Hotspur_Aston Villa"] = {
                    "home_goals": 3,
                    "away_goals": 1
                }
        
    def get_teams(self, league: str = "Premier League") -> List[Dict]:
        """
        获取联赛球队列表
        
        Args:
            league: 联赛名称
            
        Returns:
            球队列表
        """
        cache_file = os.path.join(CACHE_DIR, f"teams_{league}.json")
        if self.use_cache and os.path.exists(cache_file):
            cache_time = os.path.getmtime(cache_file)
            if time.time() - cache_time < 3600 * 6:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        
        if self.use_real_api:
            try:
                return self._get_real_teams(league)
            except Exception as e:
                print(f"[Sportsipy] 真实 API 失败，使用模拟数据: {e}")
        
        teams = list(self.sample_teams.values())
        
        if self.use_cache:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(teams, f, ensure_ascii=False, indent=2)
        
        return teams
    
    def get_team_info(self, team_name: str) -> Optional[Dict]:
        """
        获取球队信息
        
        Args:
            team_name: 球队名称
            
        Returns:
            球队信息
        """
        if team_name in self.sample_teams:
            return self.sample_teams[team_name]
        return None
    
    def get_upcoming_matches(self, league: str = "Premier League", days: int = 7) -> List[Dict]:
        """
        获取即将进行的比赛
        
        Args:
            league: 联赛名称
            days: 未来天数
            
        Returns:
            比赛列表
        """
        cache_file = os.path.join(CACHE_DIR, f"upcoming_{league}_{days}.json")
        if self.use_cache and os.path.exists(cache_file):
            cache_time = os.path.getmtime(cache_file)
            if time.time() - cache_time < 3600 * 2:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        
        if self.use_real_api:
            try:
                matches = self._get_real_upcoming_matches(league, days)
                if matches:
                    if self.use_cache:
                        with open(cache_file, "w", encoding="utf-8") as f:
                            json.dump(matches, f, ensure_ascii=False, indent=2)
                    return matches
            except Exception as e:
                print(f"[Sportsipy] 真实 API 失败，使用模拟数据: {e}")
        
        today = datetime.now()
        matches = []
        
        for match in self.sample_matches:
            match_date = datetime.strptime(match["date"], "%Y-%m-%d")
            if 0 <= (match_date - today).days <= days:
                matches.append(match)
        
        if self.use_cache:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(matches, f, ensure_ascii=False, indent=2)
        
        return matches
    
    def get_match_result(self, match_id: str) -> Optional[Dict]:
        """
        获取比赛结果
        
        Args:
            match_id: 比赛ID
            
        Returns:
            比赛结果
        """
        if self.use_real_api:
            try:
                result = self._get_real_match_result(match_id)
                if result:
                    return result
            except Exception as e:
                pass
        
        return self.historical_results.get(match_id)
    
    def get_historical_matches(self, team_name: str, limit: int = 10) -> List[Dict]:
        """
        获取球队历史比赛
        
        Args:
            team_name: 球队名称
            limit: 返回数量限制
            
        Returns:
            历史比赛列表
        """
        team = self.get_team_info(team_name)
        if not team:
            return []
        
        historical = []
        today = datetime.now()
        
        if team_name == "Arsenal":
            historical = [
                {"date": (today - timedelta(days=10)).strftime("%Y-%m-%d"), "opponent": "West Ham", "result": "W", "score": "3-1"},
                {"date": (today - timedelta(days=16)).strftime("%Y-%m-%d"), "opponent": "Chelsea", "result": "W", "score": "2-1"},
                {"date": (today - timedelta(days=23)).strftime("%Y-%m-%d"), "opponent": "Brighton", "result": "W", "score": "2-0"},
                {"date": (today - timedelta(days=30)).strftime("%Y-%m-%d"), "opponent": "Aston Villa", "result": "D", "score": "1-1"},
                {"date": (today - timedelta(days=37)).strftime("%Y-%m-%d"), "opponent": "Newcastle", "result": "W", "score": "2-0"}
            ]
        elif team_name == "Chelsea":
            historical = [
                {"date": (today - timedelta(days=10)).strftime("%Y-%m-%d"), "opponent": "Everton", "result": "W", "score": "2-0"},
                {"date": (today - timedelta(days=16)).strftime("%Y-%m-%d"), "opponent": "Arsenal", "result": "L", "score": "1-2"},
                {"date": (today - timedelta(days=23)).strftime("%Y-%m-%d"), "opponent": "Fulham", "result": "L", "score": "1-2"},
                {"date": (today - timedelta(days=30)).strftime("%Y-%m-%d"), "opponent": "Nottingham Forest", "result": "W", "score": "3-0"},
                {"date": (today - timedelta(days=37)).strftime("%Y-%m-%d"), "opponent": "Wolves", "result": "D", "score": "1-1"}
            ]
        elif team_name == "Liverpool":
            historical = [
                {"date": (today - timedelta(days=10)).strftime("%Y-%m-%d"), "opponent": "Crystal Palace", "result": "W", "score": "4-0"},
                {"date": (today - timedelta(days=17)).strftime("%Y-%m-%d"), "opponent": "Man City", "result": "W", "score": "2-1"},
                {"date": (today - timedelta(days=24)).strftime("%Y-%m-%d"), "opponent": "Brentford", "result": "W", "score": "3-0"},
                {"date": (today - timedelta(days=31)).strftime("%Y-%m-%d"), "opponent": "Luton Town", "result": "W", "score": "4-1"},
                {"date": (today - timedelta(days=38)).strftime("%Y-%m-%d"), "opponent": "Arsenal", "result": "D", "score": "2-2"}
            ]
        elif team_name == "Manchester City":
            historical = [
                {"date": (today - timedelta(days=10)).strftime("%Y-%m-%d"), "opponent": "Burnley", "result": "W", "score": "5-0"},
                {"date": (today - timedelta(days=17)).strftime("%Y-%m-%d"), "opponent": "Liverpool", "result": "L", "score": "1-2"},
                {"date": (today - timedelta(days=24)).strftime("%Y-%m-%d"), "opponent": "Southampton", "result": "W", "score": "3-1"},
                {"date": (today - timedelta(days=31)).strftime("%Y-%m-%d"), "opponent": "West Ham", "result": "W", "score": "4-1"},
                {"date": (today - timedelta(days=38)).strftime("%Y-%m-%d"), "opponent": "Chelsea", "result": "D", "score": "1-1"}
            ]
        elif team_name == "Tottenham Hotspur":
            historical = [
                {"date": (today - timedelta(days=10)).strftime("%Y-%m-%d"), "opponent": "Aston Villa", "result": "W", "score": "3-1"},
                {"date": (today - timedelta(days=17)).strftime("%Y-%m-%d"), "opponent": "Everton", "result": "L", "score": "0-2"},
                {"date": (today - timedelta(days=24)).strftime("%Y-%m-%d"), "opponent": "Brentford", "result": "W", "score": "2-1"},
                {"date": (today - timedelta(days=31)).strftime("%Y-%m-%d"), "opponent": "Man United", "result": "D", "score": "2-2"},
                {"date": (today - timedelta(days=38)).strftime("%Y-%m-%d"), "opponent": "Burnley", "result": "W", "score": "1-0"}
            ]
        
        return historical[:limit]
    
    def clear_cache(self):
        """清理缓存"""
        for filename in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    
    def _get_real_teams(self, league: str) -> List[Dict]:
        """获取真实的球队数据（需要安装 Sportsipy）"""
        raise NotImplementedError("需要安装 Sportsipy 库: pip install sportsipy")
    
    def _get_real_upcoming_matches(self, league: str, days: int) -> List[Dict]:
        """获取真实的比赛数据（需要安装 Sportsipy）"""
        raise NotImplementedError("需要安装 Sportsipy 库: pip install sportsipy")
    
    def _get_real_match_result(self, match_id: str) -> Optional[Dict]:
        """获取真实的比赛结果（需要安装 Sportsipy）"""
        raise NotImplementedError("需要安装 Sportsipy 库: pip install sportsipy")
    
    def enable_real_api(self):
        """启用真实 API 模式"""
        self.use_real_api = True
        print("[Sportsipy] 已启用真实 API 模式")
    
    def disable_real_api(self):
        """禁用真实 API 模式"""
        self.use_real_api = False
        print("[Sportsipy] 已启用模拟模式")

# 单例实例
_sportsipy_connector = None

def get_sportsipy_connector() -> SportsipyConnector:
    """获取 Sportsipy 连接器单例"""
    global _sportsipy_connector
    if _sportsipy_connector is None:
        _sportsipy_connector = SportsipyConnector()
    return _sportsipy_connector
