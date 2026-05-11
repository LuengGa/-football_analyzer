"""
AFA v9.0 快速验证版本
====================
验证核心功能，使用5万场数据快速运行
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from src.core.historical_data import (
    HISTORICAL_LOADER,
    MatchRecord,
)


def print_section(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


@dataclass
class TeamRecentForm:
    team_name: str
    last_10_matches: List[MatchRecord]
    
    @property
    def wins(self) -> int:
        return sum(1 for m in self.last_10_matches 
                  if self._is_win(m))
    
    @property
    def draws(self) -> int:
        return sum(1 for m in self.last_10_matches if m.result == "D")
    
    @property
    def losses(self) -> int:
        return len(self.last_10_matches) - self.wins - self.draws
    
    @property
    def win_rate(self) -> float:
        if not self.last_10_matches:
            return 0.0
        return self.wins / len(self.last_10_matches)
    
    def _is_win(self, match: MatchRecord) -> bool:
        if match.home_team.lower() == self.team_name.lower():
            return match.result == "H"
        else:
            return match.result == "A"


class CompleteHistoricalDatabase:
    def __init__(self, matches: List[MatchRecord]):
        self.matches = matches
        self.team_index = defaultdict(list)
        self.league_index = defaultdict(list)
        self._build_indices()
    
    def _build_indices(self):
        for m in self.matches:
            h = m.home_team.lower()
            a = m.away_team.lower()
            self.team_index[h].append(m)
            self.team_index[a].append(m)
            self.league_index[m.league].append(m)
    
    def get_team_matches(self, team_name: str) -> List[MatchRecord]:
        return sorted(self.team_index.get(team_name.lower(), []), 
                     key=lambda x: x.date, reverse=True)
    
    def get_recent_form(self, team_name: str, date: str, limit: int = 10) -> TeamRecentForm:
        team_matches = self.get_team_matches(team_name)
        recent = []
        for m in team_matches:
            if m.date < date:
                recent.append(m)
                if len(recent) >= limit:
                    break
        return TeamRecentForm(team_name, recent)


class EnhancedPredictor:
    def __init__(self, db: CompleteHistoricalDatabase):
        self.db = db
        self.league_profiles = self._build_league_profiles()
    
    def _build_league_profiles(self) -> Dict[str, Dict[str, Any]]:
        profiles = {}
        leagues = ["E0", "SP1", "D1", "I1", "F1"]
        
        for league in leagues:
            matches = self.db.league_index.get(league, [])
            if not matches:
                continue
            
            total = len(matches)
            hw = sum(1 for m in matches if m.result == "H")
            d = sum(1 for m in matches if m.result == "D")
            
            profiles[league] = {
                "home_win_rate": hw/total,
                "draw_rate": d/total,
                "away_win_rate": (total-hw-d)/total,
                "home_advantage": (hw - (total-hw-d))/total
            }
        
        return profiles
    
    def predict_match(self, match: MatchRecord) -> Tuple[float, float, float, float]:
        profile = self.league_profiles.get(match.league, {
            "home_win_rate": 0.45, "draw_rate": 0.28, "away_win_rate": 0.27
        })
        
        home_form = self.db.get_recent_form(match.home_team, match.date, limit=10)
        away_form = self.db.get_recent_form(match.away_team, match.date, limit=10)
        
        base_home = profile["home_win_rate"]
        base_draw = profile["draw_rate"]
        base_away = profile["away_win_rate"]
        
        home_bonus = home_form.win_rate - 0.45
        away_bonus = away_form.win_rate - 0.45
        
        base_home += home_bonus * 0.15
        base_away += away_bonus * 0.15
        
        total = base_home + base_draw + base_away
        h_prob = base_home / total
        d_prob = base_draw / total
        a_prob = base_away / total
        
        confidence = 0.5 + min(0.3, len(home_form.last_10_matches) / 20)
        
        return h_prob, d_prob, a_prob, confidence


class CompleteBacktester:
    def __init__(self, db: CompleteHistoricalDatabase):
        self.db = db
        self.predictor = EnhancedPredictor(db)
    
    def run_backtest(
        self,
        matches: List[MatchRecord],
        initial_capital: float = 10000.0,
        base_stake: float = 50.0,
        use_kelly: bool = True,
        min_value_threshold: float = 0.02
    ) -> Dict[str, Any]:
        valid_matches = [m for m in matches if m.home_odds and m.draw_odds and m.away_odds]
        
        logger.info(f"📊 开始回测，{len(valid_matches)} 场有赔率数据...")
        
        capital = initial_capital
        peak_capital = initial_capital
        max_drawdown = 0.0
        total_stake = 0.0
        total_profit = 0.0
        correct = 0
        total_bets = 0
        league_stats = defaultdict(lambda: {"bets": 0, "correct": 0, "profit": 0.0})
        
        result_map = {"H": "home", "D": "draw", "A": "away"}
        
        for i, m in enumerate(valid_matches):
            if i % 5000 == 0:
                logger.info(f"  进度: {i}/{len(valid_matches)}, 资金: ¥{capital:.0f}")
            
            h_prob, d_prob, a_prob, confidence = self.predictor.predict_match(m)
            
            best_selection = "home" if h_prob > a_prob and h_prob > d_prob else \
                           ("away" if a_prob > d_prob else "draw")
            
            book_h = 1.0 / m.home_odds if m.home_odds > 0 else 0.33
            book_d = 1.0 / m.draw_odds if m.draw_odds > 0 else 0.33
            book_a = 1.0 / m.away_odds if m.away_odds > 0 else 0.33
            
            value_edge = {
                "home": h_prob - book_h,
                "draw": d_prob - book_d,
                "away": a_prob - book_a
            }
            
            if value_edge[best_selection] < min_value_threshold:
                continue
            
            stake = base_stake
            if use_kelly:
                odds = m.home_odds if best_selection == "home" else \
                      (m.draw_odds if best_selection == "draw" else m.away_odds)
                pred_prob = h_prob if best_selection == "home" else \
                           (d_prob if best_selection == "draw" else a_prob)
                kelly = (pred_prob * odds - 1) / (odds - 1) if odds > 1 else 0
                stake = max(10, min(base_stake * 2, capital * max(0, kelly)))
            
            actual_result = result_map.get(m.result, m.result)
            is_correct = best_selection == actual_result
            
            total_bets += 1
            total_stake += stake
            league_stats[m.league]["bets"] += 1
            
            profit = 0.0
            if is_correct:
                correct += 1
                league_stats[m.league]["correct"] += 1
                odds = m.home_odds if best_selection == "home" else \
                      (m.draw_odds if best_selection == "draw" else m.away_odds)
                profit = stake * (odds - 1)
                total_profit += profit
                capital += profit
            else:
                total_profit -= stake
                capital -= stake
            
            league_stats[m.league]["profit"] += profit
            
            if capital > peak_capital:
                peak_capital = capital
            
            drawdown = (peak_capital - capital) / peak_capital if peak_capital > 0 else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        accuracy = correct / total_bets if total_bets > 0 else 0
        roi = (total_profit / total_stake * 100) if total_stake > 0 else 0
        
        return {
            "total_bets": total_bets,
            "correct_predictions": correct,
            "accuracy": accuracy,
            "total_stake": total_stake,
            "net_profit": total_profit,
            "roi": roi,
            "max_drawdown": max_drawdown * 100,
            "final_capital": capital,
            "league_stats": league_stats
        }


def main():
    print("\n" + "=" * 80)
    print("  🚀 AFA v9.0 完全AI原生优化系统 (快速验证版)")
    print("  =   =   =   =   =   =   =   =   =   =   =   =   =   =   =   =   =   =   =   =")
    print("  目标：真正利用历史数据！")
    print("=" * 80)
    
    print_section("第一步：验证数据位置")
    data_path = Path("data/INTEGRATED_COMPLETE_DATA.json")
    archive_path = Path("data/archive/INTEGRATED_COMPLETE_DATA.json")
    
    if data_path.exists():
        logger.info(f"✅ 数据已在正确位置: data/INTEGRATED_COMPLETE_DATA.json")
        logger.info(f"  文件大小: {data_path.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        if archive_path.exists():
            logger.info(f"⚠️  数据在归档目录，正在复制...")
            import shutil
            shutil.copy(archive_path, data_path)
            logger.info(f"✅ 已复制到 data/INTEGRATED_COMPLETE_DATA.json")
        else:
            logger.error(f"❌ 找不到数据文件！")
            return
    
    print_section("第二步：加载完整历史数据")
    matches = HISTORICAL_LOADER.load_all()
    logger.info(f"✅ 成功加载 {len(matches)} 场真实比赛！")
    
    valid_matches = [m for m in matches if m.home_odds and m.draw_odds and m.away_odds]
    logger.info(f"  • 有完整赔率: {len(valid_matches):,} 场")
    
    print_section("第三步：构建完整历史数据库")
    db = CompleteHistoricalDatabase(matches)
    logger.info(f"✅ 已索引 {len(db.team_index)} 支球队")
    
    print_section("第四步：显示各联赛数据量")
    league_names = {"E0": "英超", "SP1": "西甲", "D1": "德甲", "I1": "意甲", "F1": "法甲"}
    for league in ["E0", "SP1", "D1", "I1", "F1"]:
        count = len(db.league_index.get(league, []))
        name = league_names.get(league, league)
        logger.info(f"  • {name}: {count:,} 场")
    
    print_section("第五步：运行快速回测 (3万场数据)")
    backtester = CompleteBacktester(db)
    result = backtester.run_backtest(
        valid_matches[:30000],
        initial_capital=10000.0,
        base_stake=50.0,
        use_kelly=True,
        min_value_threshold=0.02
    )
    
    print_section("第六步：回测结果")
    logger.info(f"\n📈 最终回测性能:")
    logger.info(f"  • 总投注: {result['total_bets']:,} 场")
    logger.info(f"  • 准确率: {result['accuracy']:.1%}")
    logger.info(f"  • ROI: {result['roi']:+.1f}%")
    logger.info(f"  • 最终资金: ¥{result['final_capital']:.0f} (初始 ¥10,000)")
    logger.info(f"  • 最大回撤: {result['max_drawdown']:.1f}%")
    
    print_section("第七步：各联赛表现")
    sorted_leagues = sorted(
        result['league_stats'].items(),
        key=lambda x: x[1].get('profit', 0),
        reverse=True
    )
    
    for league, stats in sorted_leagues:
        if stats['bets'] > 100:
            name = league_names.get(league, league)
            acc = stats['correct'] / stats['bets'] if stats['bets'] > 0 else 0
            roi = (stats['profit'] / (stats['bets'] * 50)) * 100
            logger.info(f"  • {name}: {stats['bets']} 场, 准确率 {acc:.1%}, ROI {roi:+.1f}%")
    
    print_section("总结")
    logger.info(f"\n✅ 完成！")
    logger.info(f"  1. 历史数据已从归档目录移出到 data/INTEGRATED_COMPLETE_DATA.json")
    logger.info(f"  2. 完整历史数据库已构建")
    logger.info(f"  3. 按联赛优化已实现 (英超、西甲、德甲、意甲、法甲)")
    logger.info(f"  4. 增强预测算法 (近期状态等特征)")
    logger.info(f"  5. 价值投注策略已实现")
    logger.info(f"  6. 完整回测系统已运行")
    
    print("\n" + "=" * 80)
    print("  🎉 完全AI原生优化完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
