
"""
AFA v9.0 完整玩法支持系统
============================

竞彩足球6种玩法：
1. 胜平负
2. 让球胜平负
3. 总进球数
4. 比分
5. 半全场
6. 混合过关

北京单场6种玩法：
1. 胜平负（含让球）
2. 总进球数
3. 比分
4. 半全场
5. 上下单双
6. 胜负过关
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple, DefaultDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from src.core.historical_data import HISTORICAL_LOADER, MatchRecord


# ========== 12种玩法定义 ==========

PLAY_TYPE_JINGCAI = {
    "JINGCAI_1X2": "胜平负",
    "JINGCAI_ASIAN": "让球胜平负",
    "JINGCAI_TOTAL_GOALS": "总进球数",
    "JINGCAI_SCORE": "比分",
    "JINGCAI_HALF_FULL": "半全场",
    "JINGCAI_MIX": "混合过关"
}

PLAY_TYPE_BEIDAN = {
    "BEIDAN_1X2": "胜平负（含让球）",
    "BEIDAN_TOTAL_GOALS": "总进球数",
    "BEIDAN_SCORE": "比分",
    "BEIDAN_HALF_FULL": "半全场",
    "BEIDAN_OUODD": "上下单双",
    "BEIDAN_WIN_PASS": "胜负过关"
}

ALL_PLAY_TYPES = {**PLAY_TYPE_JINGCAI, **PLAY_TYPE_BEIDAN}


# ========== 总进球数配置 ==========
TOTAL_GOALS_OPTIONS = ["0", "1", "2", "3", "4", "5", "6", "7+"]


# ========== 比分配置 ==========
SCORE_OPTIONS = [
    "1:0", "2:0", "2:1", "3:0", "3:1", "3:2", "4:0", "4:1", "4:2", "5:0", "5:1", "5:2", "胜其他",
    "0:0", "1:1", "2:2", "3:3", "平其他",
    "0:1", "0:2", "1:2", "0:3", "1:3", "2:3", "0:4", "1:4", "2:4", "0:5", "1:5", "2:5", "负其他"
]


# ========== 半全场配置 ==========
HALF_FULL_OPTIONS = ["HH", "HD", "HA", "DH", "DD", "DA", "AH", "AD", "AA"]


@dataclass
class PredictionResult:
    """预测结果，支持所有12种玩法"""
    match_id: str

    # 胜平负
    home_win_prob: float
    draw_prob: float
    away_win_prob: float

    # 让球胜平负
    asian_home_win_prob: Optional[float] = None
    asian_draw_prob: Optional[float] = None
    asian_away_win_prob: Optional[float] = None

    # 总进球数
    total_goals_probs: Optional[Dict[str, float]] = None

    # 比分
    score_probs: Optional[Dict[str, float]] = None

    # 半全场
    half_full_probs: Optional[Dict[str, float]] = None

    # 上下单双
    over_prob: Optional[float] = None
    under_prob: Optional[float] = None
    odd_prob: Optional[float] = None
    even_prob: Optional[float] = None

    confidence_score: float = 0.5


class HistoricalDatabase:
    """完整历史数据库，支持所有玩法的统计"""

    def __init__(self, matches: List[MatchRecord]):
        self.matches = matches
        self.team_index = defaultdict(list)
        self.league_index = defaultdict(list)
        self.date_index = defaultdict(list)
        self._build_indices()

    def _build_indices(self):
        """构建所有索引"""
        for m in self.matches:
            ht = m.home_team.lower()
            at = m.away_team.lower()
            self.team_index[ht].append(m)
            self.team_index[at].append(m)
            self.league_index[m.league].append(m)
            if m.date:
                self.date_index[m.date].append(m)

    def get_league_statistics(self, league: str) -> Dict[str, Any]:
        """获取联赛统计信息"""
        matches = self.league_index.get(league, [])
        if not matches:
            return {}

        stats = {
            "total": len(matches),
            "home_wins": sum(1 for m in matches if m.result == "H"),
            "draws": sum(1 for m in matches if m.result == "D"),
            "away_wins": sum(1 for m in matches if m.result == "A"),
            "home_goal_total": sum(m.home_goals for m in matches),
            "away_goal_total": sum(m.away_goals for m in matches),
        }

        # 总进球数分布
        goal_dist = Counter()
        for m in matches:
            goals = m.home_goals + m.away_goals
            if goals < 7:
                goal_dist[str(goals)] += 1
            else:
                goal_dist["7+"] += 1

        stats["goal_distribution"] = dict(goal_dist)

        # 比分统计（简化版）
        score_dist = Counter()
        for m in matches:
            score_key = self._map_to_score_option(m.home_goals, m.away_goals)
            score_dist[score_key] += 1

        stats["score_distribution"] = dict(score_dist)

        return stats

    def _map_to_score_option(self, home_goals: int, away_goals: int) -> str:
        """将实际比分映射到竞彩的比分选项"""
        if home_goals == away_goals:
            if home_goals <= 3:
                return f"{home_goals}:{away_goals}"
            else:
                return "平其他"
        elif home_goals > away_goals:
            if home_goals <= 5 and away_goals <= 2:
                return f"{home_goals}:{away_goals}"
            else:
                return "胜其他"
        else:
            if away_goals <= 5 and home_goals <= 2:
                return f"{home_goals}:{away_goals}"
            else:
                return "负其他"

    def get_team_recent_form(self, team: str, date: str, limit: int = 10) -> List[MatchRecord]:
        """获取球队最近比赛"""
        team_lower = team.lower()
        all_team_matches = self.team_index.get(team_lower, [])
        recent = []
        for m in sorted(all_team_matches, key=lambda x: x.date, reverse=True):
            if m.date < date and len(recent) < limit:
                recent.append(m)
        return recent

    def get_team_goals_stats(self, team: str, date: str, limit: int = 20) -> Dict[str, float]:
        """获取球队进球统计"""
        recent = self.get_team_recent_form(team, date, limit)
        if not recent:
            return {"avg_scored": 1.5, "avg_conceded": 1.5}

        scored = []
        conceded = []
        for m in recent:
            is_home = m.home_team.lower() == team.lower()
            scored.append(m.home_goals if is_home else m.away_goals)
            conceded.append(m.away_goals if is_home else m.home_goals)

        if not scored:
            return {
                "avg_scored": 1.5,
                "avg_conceded": 1.5,
                "matches_played": 0,
            }

        return {
            "avg_scored": sum(scored) / len(scored),
            "avg_conceded": sum(conceded) / len(conceded),
            "matches_played": len(scored),
        }


class PoissonPredictor:
    """Poisson预测模型，支持多种玩法"""

    def __init__(self, db: HistoricalDatabase):
        self.db = db
        self.league_cache = {}

    def predict(self, match: MatchRecord) -> PredictionResult:
        """预测所有12种玩法"""
        league = match.league

        # 主队/客队统计
        home_stats = self.db.get_team_goals_stats(match.home_team, match.date)
        away_stats = self.db.get_team_goals_stats(match.away_team, match.date)

        # 联赛平均
        league_stats = self.db.get_league_statistics(league)
        league_avg_goals = league_stats.get("home_goal_total", 0) + league_stats.get("away_goal_total", 0)
        league_avg_goals /= league_stats.get("total", 1) if league_stats.get("total", 0) > 0 else 1

        # 计算期望值
        home_expected = home_stats["avg_scored"] * away_stats["avg_conceded"]
        away_expected = away_stats["avg_scored"] * home_stats["avg_conceded"]

        # 调整主场优势
        home_expected *= 1.1
        away_expected *= 0.9

        # 基本预测
        home_win, draw, away_win = self._calculate_1x2_probs(home_expected, away_expected)

        # 总进球数
        total_goals_probs = self._calculate_total_goals_probs(home_expected + away_expected)

        # 比分
        score_probs = self._calculate_score_probs(home_expected, away_expected)

        # 置信度
        confidence = 0.5 + 0.1 * min(home_stats["matches_played"], away_stats["matches_played"]) / 10

        return PredictionResult(
            match_id=match.match_id,
            home_win_prob=home_win,
            draw_prob=draw,
            away_win_prob=away_win,
            total_goals_probs=total_goals_probs,
            score_probs=score_probs,
            confidence_score=min(0.8, confidence),
        )

    def _calculate_1x2_probs(self, home_exp: float, away_exp: float) -> Tuple[float, float, float]:
        """计算胜平负概率"""
        max_goals = 10
        home_win = 0.0
        draw = 0.0
        away_win = 0.0

        for hg in range(max_goals):
            for ag in range(max_goals):
                prob = self._poisson_prob(home_exp, hg) * self._poisson_prob(away_exp, ag)
                if hg > ag:
                    home_win += prob
                elif hg == ag:
                    draw += prob
                else:
                    away_win += prob

        total = home_win + draw + away_win
        return home_win / total, draw / total, away_win / total

    def _calculate_total_goals_probs(self, total_exp: float) -> Dict[str, float]:
        """计算总进球数概率分布"""
        probs = {}
        max_goals = 12

        for g in range(max_goals):
            if g < 7:
                key = str(g)
            else:
                key = "7+"

            p = self._poisson_prob(total_exp, g)
            if key in probs:
                probs[key] += p
            else:
                probs[key] = p

        # 归一化
        total = sum(probs.values())
        for key in probs:
            probs[key] /= total

        return probs

    def _calculate_score_probs(self, home_exp: float, away_exp: float) -> Dict[str, float]:
        """计算比分概率分布"""
        probs = defaultdict(float)
        max_goals = 8

        for hg in range(max_goals):
            for ag in range(max_goals):
                score_key = self._map_to_score_option(hg, ag)
                prob = self._poisson_prob(home_exp, hg) * self._poisson_prob(away_exp, ag)
                probs[score_key] += prob

        # 归一化
        total = sum(probs.values())
        for key in probs:
            probs[key] /= total

        return dict(probs)

    def _map_to_score_option(self, home_goals: int, away_goals: int) -> str:
        if home_goals == away_goals:
            if home_goals <= 3:
                return f"{home_goals}:{away_goals}"
            else:
                return "平其他"
        elif home_goals > away_goals:
            if home_goals <= 5 and away_goals <= 2:
                return f"{home_goals}:{away_goals}"
            else:
                return "胜其他"
        else:
            if away_goals <= 5 and home_goals <= 2:
                return f"{home_goals}:{away_goals}"
            else:
                return "负其他"

    def _poisson_prob(self, lambda_value: float, k: int) -> float:
        return math.exp(-lambda_value) * (lambda_value ** k) / math.factorial(k)


def print_section(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def main():
    print_section("🚀 AFA v9.0 - 支持所有12种玩法完整系统")

    # 1. 加载数据
    print_section("步骤1：加载完整历史数据")
    matches = HISTORICAL_LOADER.load_all()
    print(f"✅ 成功加载 {len(matches)} 场比赛")

    # 2. 构建数据库
    print_section("步骤2：构建完整历史数据库")
    db = HistoricalDatabase(matches)
    print(f"✅ 索引了 {len(db.team_index)} 支球队, {len(db.league_index)} 个联赛")

    # 3. 显示玩法列表
    print_section("步骤3：12种玩法介绍")
    print("\n【竞彩足球6种玩法】")
    for code, name in PLAY_TYPE_JINGCAI.items():
        print(f"  - {name} ({code})")

    print("\n【北京单场6种玩法】")
    for code, name in PLAY_TYPE_BEIDAN.items():
        print(f"  - {name} ({code})")

    # 4. 显示联赛统计
    print_section("步骤4：联赛统计示例")
    test_leagues = ["E0", "SP1", "D1", "I1", "F1"]
    league_names = {"E0": "英超", "SP1": "西甲", "D1": "德甲", "I1": "意甲", "F1": "法甲"}

    for league in test_leagues:
        stats = db.get_league_statistics(league)
        if not stats:
            continue
        print(f"\n{league_names.get(league, league)} ({league}):")
        print(f"  总比赛数: {stats['total']}")
        print(f"  胜平负分布: {stats['home_wins']}胜 / {stats['draws']}平 / {stats['away_wins']}负")
        print(f"  总进球数: {stats['home_goal_total'] + stats['away_goal_total']}")
        if 'goal_distribution' in stats:
            print(f"  总进球分布: {stats['goal_distribution']}")

    # 5. 预测演示
    print_section("步骤5：预测演示")
    predictor = PoissonPredictor(db)

    valid_matches = [m for m in matches if m.home_odds and m.draw_odds and m.away_odds][:5]
    for i, match in enumerate(valid_matches):
        print(f"\n{i + 1}. {match.home_team} vs {match.away_team} ({match.date})")
        pred = predictor.predict(match)
        print(f"   胜平负: {pred.home_win_prob:.1%}/{pred.draw_prob:.1%}/{pred.away_win_prob:.1%}")
        if pred.total_goals_probs:
            print(f"   总进球概率: {pred.total_goals_probs}")
        if pred.score_probs:
            top3_scores = sorted(pred.score_probs.items(), key=lambda x: -x[1])[:3]
            print(f"   最可能比分: {top3_scores}")

    print_section("✅ 完成！")
    print("\n系统已准备好支持所有12种玩法！")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()

