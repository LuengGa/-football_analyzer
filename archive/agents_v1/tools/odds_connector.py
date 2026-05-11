"""
Odds Connector - 赔率数据连接器（增强版）
支持多个赔率数据源的统一接口，包括API-Football和Sportmonks
"""
from typing import Dict, Any, List, Optional
import requests
import time
import json
import os
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

# 加载配置
try:
    from src.config.config_loader import load_env_file
    load_env_file()
except ImportError:
    # 手动加载 .env 文件（项目根目录）
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip("'\"")


class BaseOddsSource(ABC):
    """赔率数据源基类"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.name = "BaseOddsSource"
        self.rate_limit = 10
        self.last_request_time = 0
        self.available = False
        
    def _rate_limit_wait(self):
        """速率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < (60 / self.rate_limit):
            time.sleep((60 / self.rate_limit) - time_since_last)
        self.last_request_time = time.time()
    
    @abstractmethod
    def get_odds(self, league: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """获取赔率数据"""
        pass
    
    @abstractmethod
    def get_match_odds(self, match_id: str) -> Optional[Dict[str, Any]]:
        """获取特定比赛的赔率"""
        pass
    
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        return self.api_key is not None and self.available


class FootballDataConnector(BaseOddsSource):
    """football-data.org 连接器"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.name = "FootballData"
        self.base_url = "https://api.football-data.org/v4"
        self.rate_limit = 10
        if api_key:
            self.available = True
        
    def get_odds(self, league: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """获取赔率数据"""
        if not self.is_available():
            return []
        
        self._rate_limit_wait()
        
        headers = {"X-Auth-Token": self.api_key}
        
        try:
            params = {}
            if league:
                league_map = {
                    "Premier League": "PL",
                    "La Liga": "PD",
                    "Serie A": "SA",
                    "Bundesliga": "BL1",
                    "Ligue 1": "FL1",
                    "Champions League": "CL"
                }
                params["competitions"] = league_map.get(league, "PL")
            
            response = requests.get(
                f"{self.base_url}/matches",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get("matches", [])
                
                odds_list = []
                for match in matches[:20]:
                    odds_data = {
                        "match_id": str(match.get("id", "")),
                        "league": match.get("competition", {}).get("name", ""),
                        "home_team": match.get("homeTeam", {}).get("name", ""),
                        "away_team": match.get("awayTeam", {}).get("name", ""),
                        "date": match.get("utcDate", ""),
                        "status": match.get("status", ""),
                        "source": self.name
                    }
                    odds_list.append(odds_data)
                
                print(f"[FootballData] 获取到 {len(odds_list)} 场比赛")
                return odds_list
            else:
                print(f"[FootballData] 请求失败: {response.status_code}")
                self.available = False
                return []
                
        except Exception as e:
            print(f"[FootballData] 获取赔率失败: {e}")
            self.available = False
            return []
    
    def get_match_odds(self, match_id: str) -> Optional[Dict[str, Any]]:
        """获取特定比赛的赔率"""
        if not self.is_available():
            return None
        
        self._rate_limit_wait()
        
        headers = {"X-Auth-Token": self.api_key}
        
        try:
            response = requests.get(
                f"{self.base_url}/matches/{match_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                match_data = response.json()
                return {
                    "match_id": str(match_data.get("id", "")),
                    "home_team": match_data.get("homeTeam", {}).get("name", ""),
                    "away_team": match_data.get("awayTeam", {}).get("name", ""),
                    "date": match_data.get("utcDate", ""),
                    "status": match_data.get("status", ""),
                    "source": self.name
                }
            else:
                return None
                
        except Exception as e:
            print(f"[FootballData] 获取比赛详情失败: {e}")
            return None


class TheOddsAPIConnector(BaseOddsSource):
    """the-odds-api.com 连接器"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.name = "TheOddsAPI"
        self.base_url = "https://api.the-odds-api.com/v4"
        self.rate_limit = 50
        if api_key:
            self.available = True
        
    def get_odds(self, league: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """获取赔率数据"""
        if not self.is_available():
            return []
        
        self._rate_limit_wait()
        
        sport_map = {
            "Premier League": "soccer_epl",
            "La Liga": "soccer_spain_la_liga",
            "Serie A": "soccer_italy_serie_a",
            "Bundesliga": "soccer_germany_bundesliga",
            "Ligue 1": "soccer_france_ligue_one"
        }
        
        sport_key = sport_map.get(league, "soccer_epl") if league else "soccer_epl"
        
        try:
            params = {
                "apiKey": self.api_key,
                "regions": "uk,eu,us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "decimal"
            }
            
            response = requests.get(
                f"{self.base_url}/sports/{sport_key}/odds",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                odds_data = response.json()
                
                formatted_odds = []
                for bookmaker in odds_data:
                    bookmakers = bookmaker.get("bookmakers", [])
                    if bookmakers:
                        for market in bookmakers[0].get("markets", []):
                            if market.get("key") == "h2h":
                                outcomes = market.get("outcomes", [])
                                odds_entry = {
                                    "match_id": bookmaker.get("id", ""),
                                    "league": sport_key,
                                    "home_team": "",
                                    "away_team": "",
                                    "date": bookmaker.get("commence_time", ""),
                                    "odds_home": 0,
                                    "odds_draw": 0,
                                    "odds_away": 0,
                                    "bookmaker": bookmakers[0].get("title", ""),
                                    "source": self.name
                                }
                                
                                for outcome in outcomes:
                                    name = outcome.get("name", "")
                                    price = outcome.get("price", 0)
                                    if "Draw" in name or "平局" in name:
                                        odds_entry["odds_draw"] = price
                                    elif odds_entry["home_team"] == "":
                                        odds_entry["home_team"] = name
                                        odds_entry["odds_home"] = price
                                    else:
                                        odds_entry["away_team"] = name
                                        odds_entry["odds_away"] = price
                                
                                formatted_odds.append(odds_entry)
                
                print(f"[TheOddsAPI] 获取到 {len(formatted_odds)} 条赔率")
                return formatted_odds
            else:
                print(f"[TheOddsAPI] 请求失败: {response.status_code}")
                self.available = False
                return []
                
        except Exception as e:
            print(f"[TheOddsAPI] 获取赔率失败: {e}")
            self.available = False
            return []
    
    def get_match_odds(self, match_id: str) -> Optional[Dict[str, Any]]:
        """获取特定比赛的赔率"""
        return None


class APIFootballConnector(BaseOddsSource):
    """API-Football (RapidAPI) 连接器"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.name = "APIFootball"
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.rate_limit = 10
        if api_key:
            self.available = True
        
    def get_odds(self, league: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """获取赔率数据"""
        if not self.is_available():
            return []
        
        self._rate_limit_wait()
        
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        
        league_map = {
            "Premier League": 39,
            "La Liga": 140,
            "Serie A": 135,
            "Bundesliga": 78,
            "Ligue 1": 61,
            "Champions League": 2
        }
        
        try:
            league_id = league_map.get(league, 39)
            date_from = datetime.now().strftime("%Y-%m-%d")
            date_to = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            
            params = {
                "league": league_id,
                "season": "2024",
                "from": date_from,
                "to": date_to
            }
            
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                fixtures = data.get("response", [])
                
                odds_list = []
                for fixture in fixtures[:20]:
                    fixture_data = fixture.get("fixture", {})
                    teams = fixture.get("teams", {})
                    odds_data = fixture.get("odds", {})
                    
                    odds_entry = {
                        "match_id": str(fixture_data.get("id", "")),
                        "league": league,
                        "home_team": teams.get("home", {}).get("name", ""),
                        "away_team": teams.get("away", {}).get("name", ""),
                        "date": fixture_data.get("date", ""),
                        "status": fixture_data.get("status", {}).get("short", ""),
                        "source": self.name
                    }
                    
                    if odds_data:
                        for bookmaker in odds_data.get("bookmakers", []):
                            for bet in bookmaker.get("bets", []):
                                if bet.get("name") == "Match Winner":
                                    values = bet.get("values", [])
                                    for v in values:
                                        if v.get("value") == "Home":
                                            odds_entry["odds_home"] = v.get("odd")
                                        elif v.get("value") == "Draw":
                                            odds_entry["odds_draw"] = v.get("odd")
                                        elif v.get("value") == "Away":
                                            odds_entry["odds_away"] = v.get("odd")
                                    break
                            break
                    
                    odds_list.append(odds_entry)
                
                print(f"[APIFootball] 获取到 {len(odds_list)} 场比赛")
                return odds_list
            else:
                print(f"[APIFootball] 请求失败: {response.status_code}")
                self.available = False
                return []
                
        except Exception as e:
            print(f"[APIFootball] 获取赔率失败: {e}")
            self.available = False
            return []
    
    def get_match_odds(self, match_id: str) -> Optional[Dict[str, Any]]:
        """获取特定比赛的赔率"""
        if not self.is_available():
            return None
        
        self._rate_limit_wait()
        
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        
        try:
            params = {"fixture": match_id}
            
            response = requests.get(
                f"{self.base_url}/odds",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                odds_data = data.get("response", [])
                if odds_data:
                    return {
                        "match_id": match_id,
                        "source": self.name,
                        "raw_data": odds_data
                    }
            return None
                
        except Exception as e:
            print(f"[APIFootball] 获取比赛详情失败: {e}")
            return None


class SportmonksConnector(BaseOddsSource):
    """Sportmonks API 连接器"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.name = "Sportmonks"
        self.base_url = "https://api.sportmonks.com/v3/football"
        self.rate_limit = 10
        if api_key:
            self.available = True
        
    def get_odds(self, league: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """获取赔率数据"""
        if not self.is_available():
            return []
        
        self._rate_limit_wait()
        
        try:
            params = {
                "api_token": self.api_key,
                "include": "odds"
            }
            
            response = requests.get(
                f"{self.base_url}/fixtures",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                fixtures = data.get("data", [])
                
                odds_list = []
                for fixture in fixtures[:20]:
                    odds_entry = {
                        "match_id": str(fixture.get("id", "")),
                        "league": fixture.get("league", {}).get("name", ""),
                        "home_team": fixture.get("teams", {}).get("home", {}).get("name", ""),
                        "away_team": fixture.get("teams", {}).get("away", {}).get("name", ""),
                        "date": fixture.get("starting_at", {}).get("date", ""),
                        "status": fixture.get("status", {}).get("short", ""),
                        "source": self.name
                    }
                    
                    odds = fixture.get("odds", {})
                    if odds:
                        for market in odds.get("data", []):
                            if market.get("name") == "Match Winner":
                                for outcome in market.get("outcomes", []):
                                    if outcome.get("label") == "Home":
                                        odds_entry["odds_home"] = outcome.get("odds")
                                    elif outcome.get("label") == "Draw":
                                        odds_entry["odds_draw"] = outcome.get("odds")
                                    elif outcome.get("label") == "Away":
                                        odds_entry["odds_away"] = outcome.get("odds")
                                break
                    
                    odds_list.append(odds_entry)
                
                print(f"[Sportmonks] 获取到 {len(odds_list)} 场比赛")
                return odds_list
            else:
                print(f"[Sportmonks] 请求失败: {response.status_code}")
                self.available = False
                return []
                
        except Exception as e:
            print(f"[Sportmonks] 获取赔率失败: {e}")
            self.available = False
            return []
    
    def get_match_odds(self, match_id: str) -> Optional[Dict[str, Any]]:
        """获取特定比赛的赔率"""
        if not self.is_available():
            return None
        
        self._rate_limit_wait()
        
        try:
            params = {
                "api_token": self.api_key,
                "include": "odds"
            }
            
            response = requests.get(
                f"{self.base_url}/fixtures/{match_id}",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                fixture = data.get("data", {})
                return {
                    "match_id": match_id,
                    "source": self.name,
                    "raw_data": fixture
                }
            return None
                
        except Exception as e:
            print(f"[Sportmonks] 获取比赛详情失败: {e}")
            return None


class LocalOddsCache:
    """本地赔率缓存"""
    
    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            cache_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "data", "odds_cache"
            )
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def save_odds(self, odds_data: List[Dict[str, Any]], source: str):
        """保存赔率到缓存"""
        cache_file = os.path.join(
            self.cache_dir,
            f"odds_{source}_{datetime.now().strftime('%Y%m%d_%H')}.json"
        )
        
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "source": source,
                    "data": odds_data
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
    
    def load_odds(self, source: str, max_age_hours: int = 6) -> Optional[List[Dict[str, Any]]]:
        """加载缓存的赔率"""
        cache_file = os.path.join(
            self.cache_dir,
            f"odds_{source}_{datetime.now().strftime('%Y%m%d_%H')}.json"
        )
        
        if not os.path.exists(cache_file):
            for hour in range(1, max_age_hours + 1):
                check_time = datetime.now() - timedelta(hours=hour)
                check_file = os.path.join(
                    self.cache_dir,
                    f"odds_{source}_{check_time.strftime('%Y%m%d_%H')}.json"
                )
                if os.path.exists(check_file):
                    cache_file = check_file
                    break
            else:
                return None
        
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
                
            cached_time = datetime.fromisoformat(cached["timestamp"])
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                return None
            
            return cached["data"]
            
        except Exception as e:
            return None


class OddsConnector:
    """赔率数据连接器 - 支持多数据源自动切换"""
    
    def __init__(
        self,
        football_data_key: str = None,
        odds_api_key: str = None,
        api_football_key: str = None,
        sportmonks_key: str = None
    ):
        self.sources = []
        
        if football_data_key:
            self.sources.append(FootballDataConnector(football_data_key))
            print(f"✅ 已加载数据源: FootballData")
        
        if odds_api_key:
            self.sources.append(TheOddsAPIConnector(odds_api_key))
            print(f"✅ 已加载数据源: TheOddsAPI")
        
        if api_football_key:
            self.sources.append(APIFootballConnector(api_football_key))
            print(f"✅ 已加载数据源: APIFootball")
        
        if sportmonks_key:
            self.sources.append(SportmonksConnector(sportmonks_key))
            print(f"✅ 已加载数据源: Sportmonks")
        
        self.cache = LocalOddsCache()
        
        if not self.sources:
            print("[OddsConnector] 警告: 未配置任何API Key，将使用模拟数据")
            self.use_mock = True
        else:
            self.use_mock = False
        
        print(f"[OddsConnector] 初始化完成，已加载 {len(self.sources)} 个数据源")
    
    def get_odds(
        self,
        league: str = None,
        days: int = 7,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """获取赔率数据"""
        if self.use_mock:
            return self._get_mock_odds(league)
        
        if use_cache:
            for source in self.sources:
                cached = self.cache.load_odds(source.name)
                if cached:
                    return cached
        
        all_odds = []
        for source in self.sources:
            if source.is_available():
                odds = source.get_odds(league, days)
                if odds:
                    all_odds.extend(odds)
                    self.cache.save_odds(odds, source.name)
                    break
        
        if not all_odds:
            return self._get_mock_odds(league)
        
        return all_odds
    
    def get_match_odds(
        self,
        match_id: str,
        league: str = None
    ) -> Optional[Dict[str, Any]]:
        """获取特定比赛的赔率"""
        if self.use_mock:
            return self._get_mock_match_odds(match_id)
        
        for source in self.sources:
            if source.is_available():
                odds = source.get_match_odds(match_id)
                if odds:
                    return odds
        
        return None
    
    def _get_mock_odds(self, league: str) -> List[Dict[str, Any]]:
        """生成模拟赔率数据"""
        leagues = {
            "Premier League": [("Arsenal", "Chelsea"), ("Liverpool", "Manchester City"), ("Manchester United", "Tottenham"), ("Leicester", "Everton"), ("West Ham", "Aston Villa")],
            "La Liga": [("Real Madrid", "Barcelona"), ("Atletico Madrid", "Sevilla"), ("Valencia", "Betis"), ("Villarreal", "Real Sociedad"), ("Athletic Bilbao", "Osasuna")],
            "Serie A": [("Juventus", "AC Milan"), ("Inter Milan", "Napoli"), ("Roma", "Lazio"), ("Atalanta", "Fiorentina"), ("Sassuolo", "Verona")],
            "Bundesliga": [("Bayern Munich", "Borussia Dortmund"), ("RB Leipzig", "Bayer Leverkusen"), ("Wolfsburg", "Freiburg"), ("Eintracht Frankfurt", "Bremen"), ("Cologne", "Hoffenheim")],
            "Ligue 1": [("Paris SG", "Marseille"), ("Lyon", "Monaco"), ("Lille", "Nice"), ("Rennes", "Reims"), ("Brest", "Toulouse")]
        }
        
        if league:
            matchups = leagues.get(league, leagues["Premier League"])
        else:
            matchups = [(t1, t2) for teams in leagues.values() for t1, t2 in teams]
        
        mock_odds = []
        for i, (home, away) in enumerate(matchups):
            mock_odds.append({
                "match_id": f"mock_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "league": league or "Premier League",
                "home_team": home,
                "away_team": away,
                "date": (datetime.now() + timedelta(days=i+1)).isoformat(),
                "odds_home": round(1.6 + (i * 0.1), 2),
                "odds_draw": round(3.2 + (i * 0.05), 2),
                "odds_away": round(3.8 + (i * 0.15), 2),
                "bookmaker": "Mock Bookmaker",
                "source": "Mock"
            })
        
        return mock_odds
    
    def _get_mock_match_odds(self, match_id: str) -> Dict[str, Any]:
        """生成模拟比赛赔率"""
        return {
            "match_id": match_id,
            "league": "Premier League",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "date": datetime.now().isoformat(),
            "odds_home": 1.85,
            "odds_draw": 3.40,
            "odds_away": 4.20,
            "bookmaker": "Mock Bookmaker",
            "source": "Mock"
        }
    
    def update_orchestrator(self, orchestrator):
        """更新 Orchestrator 的赔率数据"""
        print("[OddsConnector] 更新 Orchestrator 赔率数据...")
        
        odds_data = self.get_odds()
        
        if odds_data:
            if hasattr(orchestrator, 'agents') and 'scout' in orchestrator.agents:
                orchestrator.agents['scout'].update_odds_data(odds_data)
            
            print(f"[OddsConnector] 已更新 {len(odds_data)} 条赔率数据")
            return True
        else:
            print("[OddsConnector] 更新失败")
            return False
    
    def get_available_leagues(self) -> List[str]:
        """获取支持的联赛列表"""
        return [
            "Premier League",
            "La Liga",
            "Serie A",
            "Bundesliga",
            "Ligue 1",
            "Champions League"
        ]
    
    def get_active_sources(self) -> List[str]:
        """获取当前活跃的数据源"""
        return [source.name for source in self.sources if source.is_available()]


_odds_connector_instance = None

def get_odds_connector(
    football_data_key: str = None,
    odds_api_key: str = None,
    api_football_key: str = None,
    sportmonks_key: str = None
) -> OddsConnector:
    """获取或创建全局赔率连接器实例"""
    global _odds_connector_instance
    
    if _odds_connector_instance is None:
        if football_data_key is None:
            football_data_key = os.getenv("FOOTBALL_DATA_API_KEY")
        if odds_api_key is None:
            odds_api_key = os.getenv("ODDS_API_KEY")
        if api_football_key is None:
            api_football_key = os.getenv("API_FOOTBALL_KEY")
        if sportmonks_key is None:
            sportmonks_key = os.getenv("SPORTMONKS_API_KEY")
        
        _odds_connector_instance = OddsConnector(
            football_data_key=football_data_key,
            odds_api_key=odds_api_key,
            api_football_key=api_football_key,
            sportmonks_key=sportmonks_key
        )
    
    return _odds_connector_instance


if __name__ == "__main__":
    print("测试增强版赔率连接器...")
    
    connector = get_odds_connector()
    
    print("\n支持的联赛:")
    for league in connector.get_available_leagues():
        print(f"  - {league}")
    
    print(f"\n活跃数据源: {connector.get_active_sources()}")
    
    print("\n获取赔率数据:")
    odds = connector.get_odds(league="Premier League")
    
    for o in odds[:3]:
        print(f"  {o['home_team']} vs {o['away_team']}")
        if 'odds_home' in o:
            print(f"    赔率: {o['odds_home']} - {o.get('odds_draw', '-')} - {o['odds_away']}")
