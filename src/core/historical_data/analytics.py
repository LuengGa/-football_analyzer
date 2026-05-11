"""
历史数据彻底利用框架
=====================

目标：
1. 提取可计算特征（赔率、统计）
2. 发现历史模式
3. 支持价值发现
4. 驱动Evolution进化

数据结构：
- 158,971场比赛
- 23个联赛
- 670+球队
- 2003-2026年
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class MatchFeatures:
    """比赛特征 - 用于计算和向量化"""
    match_id: str
    league: str
    season: str
    date: str

    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    result: str

    home_odds: float
    draw_odds: float
    away_odds: float

    implied_home_prob: float
    implied_draw_prob: float
    implied_away_prob: float

    bookmaker_margin: float

    home_shots: int
    away_shots: int
    home_corners: int
    away_corners: int

    odds_change_home: float = 0.0
    odds_change_away: float = 0.0

    def to_vector(self) -> List[float]:
        """转换为特征向量"""
        return [
            self.implied_home_prob,
            self.implied_draw_prob,
            self.implied_away_prob,
            self.bookmaker_margin,
            self.home_shots / 20.0,
            self.away_shots / 20.0,
            self.home_corners / 15.0,
            self.away_corners / 15.0,
            self.odds_change_home,
            self.odds_change_away,
        ]


class HistoricalDataAnalyzer:
    """
    历史数据分析器

    功能：
    1. 赔率模式识别
    2. 价值发现（opening vs closing）
    3. 联赛特征提取
    4. 球队画像
    5. 特征向量化
    6. 亚洲盘/大小球分析
    7. 赔率变化分析
    """

    def __init__(self, loader=None):
        self.loader = loader
        self._cache: Dict[str, Any] = {}
        self._data_path = self._find_data_path()

    def _find_data_path(self) -> str:
        """查找数据文件路径"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent.parent
        possible_paths = [
            project_root / "INTEGRATED_COMPLETE_DATA.json",
            project_root / "data" / "archive" / "INTEGRATED_COMPLETE_DATA.json",
            project_root / "data" / "INTEGRATED_COMPLETE_DATA.json",
        ]
        for path in possible_paths:
            if path.exists():
                return str(path)
        return str(possible_paths[0])

    def load_raw_matches(self) -> List[Any]:
        """直接从JSON加载原始数据"""
        if self._cache.get('raw_matches'):
            return self._cache['raw_matches']

        import json
        try:
            with open(self._data_path, 'r') as f:
                data = json.load(f)
            matches = data.get('matches', [])
            self._cache['raw_matches'] = matches
            return matches
        except Exception:
            return []

    def get_data_overview(self) -> Dict[str, Any]:
        """获取数据概览"""
        matches = self.load_raw_matches()
        
        leagues = {}
        for m in matches:
            league = self._get_league(m)
            if league not in leagues:
                leagues[league] = {'count': 0, 'home_wins': 0, 'draws': 0, 'away_wins': 0, 'goals': 0}
            leagues[league]['count'] += 1
            leagues[league]['goals'] += (m.get('home_goals') or 0) + (m.get('away_goals') or 0)
            r = m.get('result', 'D')
            if r == 'H': leagues[league]['home_wins'] += 1
            elif r == 'D': leagues[league]['draws'] += 1
            else: leagues[league]['away_wins'] += 1
        
        field_stats = {}
        for field in ['three_way_odds', 'asian_handicap', 'over_under', 'odds_movement', 'match_stats']:
            count = sum(1 for m in matches if field in m and m[field])
            field_stats[field] = {'count': count, 'pct': count / len(matches) * 100}
        
        return {
            'total_matches': len(matches),
            'total_leagues': len(leagues),
            'field_stats': field_stats,
            'leagues': leagues,
        }

    def analyze_asian_handicap(self, matches: Optional[List[Any]] = None) -> Dict[str, Any]:
        """分析亚洲盘价值"""
        if matches is None:
            matches = self.load_raw_matches()
        
        asian_matches = []
        for m in matches:
            ah = m.get('asian_handicap', {})
            if ah and ah.get('opening'):
                opening = ah.get('opening', {})
                for bm, odds in opening.items():
                    if isinstance(odds, dict) and odds.get('home') and odds.get('away'):
                        h_odds = odds['home']
                        a_odds = odds['away']
                        if h_odds > 0 and a_odds > 0:
                            prob_h = 1 / h_odds
                            prob_a = 1 / a_odds
                            margin = prob_h + prob_a - 1
                            asian_matches.append({
                                'implied_home_prob': prob_h,
                                'actual_home_win': 1 if m.get('result') == 'H' else 0,
                                'margin': margin,
                                'home_favored': h_odds < a_odds,
                            })
                            break
        
        if not asian_matches:
            return {'count': 0}
        
        implied = sum(m['implied_home_prob'] for m in asian_matches) / len(asian_matches)
        actual = sum(m['actual_home_win'] for m in asian_matches) / len(asian_matches)
        
        return {
            'count': len(asian_matches),
            'avg_margin': sum(m['margin'] for m in asian_matches) / len(asian_matches),
            'implied_home_prob': implied,
            'actual_home_win_rate': actual,
            'value': actual - implied,
            'home_favored_pct': sum(1 for m in asian_matches if m['home_favored']) / len(asian_matches),
        }

    def analyze_over_under(self, matches: Optional[List[Any]] = None, line: float = 2.5) -> Dict[str, Any]:
        """分析大小球价值"""
        if matches is None:
            matches = self.load_raw_matches()
        
        ou_matches = []
        for m in matches:
            ou = m.get('over_under', {})
            if ou and ou.get('opening'):
                opening = ou.get('opening', {})
                for bm, odds in opening.items():
                    if isinstance(odds, dict) and odds.get('over') and odds.get('under'):
                        over_odds = odds['over']
                        under_odds = odds['under']
                        if over_odds > 0 and under_odds > 0:
                            prob_over = 1 / over_odds
                            total_goals = (m.get('home_goals') or 0) + (m.get('away_goals') or 0)
                            ou_matches.append({
                                'implied_over_prob': prob_over,
                                'actual_over': 1 if total_goals >= line else 0,
                                'total_goals': total_goals,
                                'over_odds': over_odds,
                                'under_odds': under_odds,
                            })
                            break
        
        if not ou_matches:
            return {'count': 0}
        
        implied = sum(m['implied_over_prob'] for m in ou_matches) / len(ou_matches)
        actual = sum(m['actual_over'] for m in ou_matches) / len(ou_matches)
        
        return {
            'count': len(ou_matches),
            'line': line,
            'implied_over_prob': implied,
            'actual_over_rate': actual,
            'value': actual - implied,
            'avg_over_odds': sum(m['over_odds'] for m in ou_matches) / len(ou_matches),
        }

    def analyze_odds_movement(self, matches: Optional[List[Any]] = None) -> Dict[str, Any]:
        """分析赔率变化价值"""
        if matches is None:
            matches = self.load_raw_matches()
        
        home_favored = []
        away_favored = []
        
        for m in matches:
            om = m.get('odds_movement', {})
            if om and om.get('home'):
                home_data = om.get('home', {})
                if home_data:
                    change = home_data.get('change', 0) or 0
                    actual = 1 if m.get('result') == 'H' else 0
                    closing_prob = home_data.get('close_prob', 0.5) or 0.5
                    
                    if change < 0:
                        home_favored.append({'actual': actual, 'prob': closing_prob})
                    elif change > 0:
                        away_favored.append({'actual': actual, 'prob': closing_prob})
        
        result = {'total': len(home_favored) + len(away_favored)}
        
        if home_favored:
            actual = sum(m['actual'] for m in home_favored) / len(home_favored)
            implied = sum(m['prob'] for m in home_favored) / len(home_favored)
            result['home_favored'] = {
                'count': len(home_favored),
                'actual_win_rate': actual,
                'implied_prob': implied,
                'value': actual - implied,
            }
        
        if away_favored:
            actual = sum(m['actual'] for m in away_favored) / len(away_favored)
            implied = sum(m['prob'] for m in away_favored) / len(away_favored)
            result['away_favored'] = {
                'count': len(away_favored),
                'actual_win_rate': actual,
                'implied_prob': implied,
                'value': actual - implied,
            }
        
        return result

    def get_half_time_stats(self, matches: Optional[List[Any]] = None) -> Dict[str, Any]:
        """获取半场统计"""
        if matches is None:
            matches = self.load_raw_matches()
        
        ht_results: Dict[str, int] = {'H': 0, 'D': 0, 'A': 0}
        ht_ft: Dict[str, int] = {}
        total = 0
        
        for m in matches:
            ht = m.get('half_time', {})
            if ht:
                total += 1
                hg = ht.get('home_goals', 0) or 0
                ag = ht.get('away_goals', 0) or 0
                if hg > ag: ht_res = 'H'
                elif hg == ag: ht_res = 'D'
                else: ht_res = 'A'
                
                ht_results[ht_res] += 1
                ft = m.get('result', 'D')
                key = f"{ht_res}/{ft}"
                ht_ft[key] = ht_ft.get(key, 0) + 1
        
        result = {
            'total': total,
            'ht_results': {k: {'count': v, 'pct': v/total} for k, v in ht_results.items()},
            'ht_ft_combinations': {k: {'count': v, 'pct': v/total} for k, v in ht_ft.items()},
        }
        
        return result

    def get_score_distribution(self, matches: Optional[List[Any]] = None) -> Dict[str, Any]:
        """获取比分分布"""
        if matches is None:
            matches = self.load_raw_matches()
        
        score_dist: Dict[str, int] = defaultdict(int)
        goal_dist: Dict[int, int] = defaultdict(int)
        
        for m in matches:
            hg = m.get('home_goals', 0) or 0
            ag = m.get('away_goals', 0) or 0
            score_dist[f"{hg}-{ag}"] += 1
            goal_dist[hg + ag] += 1
        
        return {
            'total': len(matches),
            'score_distribution': dict(sorted(score_dist.items(), key=lambda x: -x[1])[:20]),
            'goal_distribution': {k: {'count': v, 'pct': v/len(matches)} for k, v in sorted(goal_dist.items())},
        }

    def extract_features(self, match) -> Optional[MatchFeatures]:
        """从原始数据提取特征"""
        try:
            odds = match.get("three_way_odds", {}) if hasattr(match, 'get') else getattr(match, 'three_way_odds', {})
            opening = odds.get("opening", {}) if odds else {}
            closing = odds.get("closing", {}) if odds else {}

            bet365_odds = opening.get("Bet365", {})
            if not bet365_odds:
                bet365_odds = opening.get("Average", {})

            if not bet365_odds:
                return None

            h = bet365_odds.get("home", 2.0)
            d = bet365_odds.get("draw", 3.0)
            a = bet365_odds.get("away", 3.0)

            implied_probs = self._odds_to_prob(h, d, a)

            closing_bet365 = closing.get("Bet365", {})
            odds_change_h = 0.0
            odds_change_a = 0.0
            if closing_bet365:
                odds_change_h = h - closing_bet365.get("home", h)
                odds_change_a = a - closing_bet365.get("away", a)

            stats = match.get("match_stats", {}) if hasattr(match, 'get') else getattr(match, 'match_stats', {})
            shots = stats.get("shots", {}) if stats else {}
            corners = stats.get("corners", {}) if stats else {}

            return MatchFeatures(
                match_id=getattr(match, 'match_id', str(match)) if hasattr(match, 'match_id') else f"{match.get('league', '')}_{match.get('date', '')}",
                league=getattr(match, 'league', match.get('league', '')),
                season=getattr(match, 'season', match.get('season', '')),
                date=getattr(match, 'date', match.get('date', '')),
                home_team=getattr(match, 'home_team', match.get('home_team', '')),
                away_team=getattr(match, 'away_team', match.get('away_team', '')),
                home_goals=getattr(match, 'home_goals', match.get('home_goals', 0)),
                away_goals=getattr(match, 'away_goals', match.get('away_goals', 0)),
                result=getattr(match, 'result', match.get('result', 'D')),
                home_odds=h,
                draw_odds=d,
                away_odds=a,
                implied_home_prob=implied_probs["home"],
                implied_draw_prob=implied_probs["draw"],
                implied_away_prob=implied_probs["away"],
                bookmaker_margin=implied_probs["margin"],
                home_shots=shots.get("home", 0) or 0 if shots else 0,
                away_shots=shots.get("away", 0) or 0 if shots else 0,
                home_corners=corners.get("home", 0) or 0 if corners else 0,
                away_corners=corners.get("away", 0) or 0 if corners else 0,
                odds_change_home=odds_change_h,
                odds_change_away=odds_change_a,
            )
        except Exception as e:
            return None

    def _odds_to_prob(self, h: float, d: float, a: float) -> Dict[str, float]:
        """赔率转概率"""
        if h <= 0 or d <= 0 or a <= 0:
            return {"home": 0.33, "draw": 0.33, "away": 0.33, "margin": 0.1}

        prob_h = 1 / h
        prob_d = 1 / d
        prob_a = 1 / a
        total = prob_h + prob_d + prob_a
        margin = total - 1.0

        return {
            "home": prob_h / total if total > 0 else 0.33,
            "draw": prob_d / total if total > 0 else 0.33,
            "away": prob_a / total if total > 0 else 0.33,
            "margin": margin,
        }

    def _gen_id(self, match: Dict) -> str:
        league = match.get("league", "")
        date = match.get("date", "")
        home = match.get("home_team", "")
        away = match.get("away_team", "")
        return f"{league}_{date}_{home}_{away}"[:50]

    def _get_league(self, match) -> str:
        if hasattr(match, 'league'):
            return match.league
        elif hasattr(match, 'get'):
            return match.get('league', '')
        else:
            return ''

    def _get_home_team(self, match) -> str:
        if hasattr(match, 'home_team'):
            return match.home_team
        elif hasattr(match, 'get'):
            return match.get('home_team', '')
        else:
            return ''

    def _get_away_team(self, match) -> str:
        if hasattr(match, 'away_team'):
            return match.away_team
        elif hasattr(match, 'get'):
            return match.get('away_team', '')
        else:
            return ''

    def analyze_league(self, league_code: str, matches: List) -> Dict[str, Any]:
        """分析联赛特征"""
        league_matches = [m for m in matches if self._get_league(m) == league_code]

        if not league_matches:
            return {"count": 0}

        features = [self.extract_features(m) for m in league_matches]
        features = [f for f in features if f]

        if not features:
            return {"count": 0}

        home_probs = [f.implied_home_prob for f in features]
        margins = [f.bookmaker_margin for f in features]

        home_wins = sum(1 for f in features if f.result == "H")
        draws = sum(1 for f in features if f.result == "D")
        away_wins = sum(1 for f in features if f.result == "A")
        total = len(features)

        return {
            "league": league_code,
            "total_matches": len(league_matches),
            "with_features": total,
            "avg_implied_home_prob": sum(home_probs) / len(home_probs),
            "avg_margin": sum(margins) / len(margins),
            "actual_home_win_rate": home_wins / total,
            "actual_draw_rate": draws / total,
            "actual_away_win_rate": away_wins / total,
            "home_value": home_wins / total - sum(home_probs) / len(home_probs),
            "seasons": list(set(f.season for f in features)),
        }

    def find_value_opportunities(
        self,
        matches: List,
        threshold: float = 0.05
    ) -> List[Dict]:
        """寻找价值机会"""
        opportunities = []

        for match in matches:
            features = self.extract_features(match)
            if not features:
                continue

            actual_home = 1.0 if features.result == "H" else 0.0
            implied = features.implied_home_prob
            value = actual_home - implied

            if abs(value) > threshold:
                opportunities.append({
                    "match_id": features.match_id,
                    "date": features.date,
                    "home_team": features.home_team,
                    "away_team": features.away_team,
                    "home_odds": features.home_odds,
                    "implied_prob": implied,
                    "actual_result": features.result,
                    "value": value,
                    "league": features.league,
                })

        return sorted(opportunities, key=lambda x: abs(x["value"]), reverse=True)

    def build_team_profile(self, team_name: str, matches: List) -> Dict[str, Any]:
        """构建球队画像"""
        team_matches = [
            m for m in matches
            if self._get_home_team(m).lower() == team_name.lower()
            or self._get_away_team(m).lower() == team_name.lower()
        ]

        if not team_matches:
            return {"name": team_name, "matches": 0}

        features = [self.extract_features(m) for m in team_matches]
        features = [f for f in features if f]

        home_matches = [f for f in features if f.home_team.lower() == team_name.lower()]
        away_matches = [f for f in features if f.away_team.lower() == team_name.lower()]

        def calc_stats(matches_list, is_home):
            if not matches_list:
                return {}
            wins = sum(1 for f in matches_list if (
                (is_home and f.result == "H") or (not is_home and f.result == "A")
            ))
            draws = sum(1 for f in matches_list if f.result == "D")
            total = len(matches_list)

            avg_shots = sum(f.home_shots if is_home else f.away_shots for f in matches_list) / total
            avg_corners = sum(f.home_corners if is_home else f.away_corners for f in matches_list) / total

            avg_odds = sum(f.home_odds if is_home else f.away_odds for f in matches_list) / total
            implied_prob = sum(f.implied_home_prob if is_home else f.implied_away_prob for f in matches_list) / total

            return {
                "total": total,
                "wins": wins,
                "draws": draws,
                "win_rate": wins / total,
                "avg_shots": avg_shots,
                "avg_corners": avg_corners,
                "avg_odds": avg_odds,
                "implied_prob": implied_prob,
                "value": wins / total - implied_prob,
            }

        return {
            "name": team_name,
            "total_matches": len(team_matches),
            "home": calc_stats(home_matches, True),
            "away": calc_stats(away_matches, False),
        }

    def get_odds_distribution(self, league_code: str, matches: List) -> Dict[str, Any]:
        """获取赔率分布"""
        league_matches = [m for m in matches if self._get_league(m) == league_code]

        features = [self.extract_features(m) for m in league_matches]
        features = [f for f in features if f]

        if not features:
            return {"count": 0}

        home_odds = sorted([f.home_odds for f in features])
        away_odds = sorted([f.away_odds for f in features])

        def percentiles(data, ps):
            result = {}
            for p in ps:
                idx = int(len(data) * p / 100)
                result[f"p{p}"] = data[idx] if idx < len(data) else data[-1]
            return result

        return {
            "league": league_code,
            "count": len(features),
            "home_odds": {
                "min": min(home_odds),
                "max": max(home_odds),
                "median": home_odds[len(home_odds) // 2],
                **percentiles(home_odds, [25, 75, 90])
            },
            "away_odds": {
                "min": min(away_odds),
                "max": max(away_odds),
                "median": away_odds[len(away_odds) // 2],
                **percentiles(away_odds, [25, 75, 90])
            },
        }


class FeatureVectorizer:
    """
    特征向量化器

    将比赛转换为向量用于相似度搜索
    """

    def __init__(self):
        self.feature_dim = 10

    def vectorize_match(self, features: MatchFeatures) -> List[float]:
        """向量化比赛"""
        return features.to_vector()

    def vectorize_query(
        self,
        implied_home_prob: float = 0.5,
        implied_draw_prob: float = 0.25,
        implied_away_prob: float = 0.25,
        bookmaker_margin: float = 0.1,
        odds_range: str = "medium",
    ) -> List[float]:
        """向量化查询"""
        margin_map = {"low": 0.05, "medium": 0.1, "high": 0.15}

        return [
            implied_home_prob,
            implied_draw_prob,
            implied_away_prob,
            margin_map.get(odds_range, 0.1),
            0.5,
            0.5,
            0.5,
            0.5,
            0.0,
            0.0,
        ]

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """余弦相似度"""
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot / (norm1 * norm2)
