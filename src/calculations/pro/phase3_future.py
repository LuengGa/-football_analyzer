#!/usr/bin/env python3
"""
AFA v8.3 - Phase 3 未来功能框架
实现：
 1. 进球时序模型框架
 2. 实时滚球深度模型框架
 3. 高级组合玩法框架
"""
import math
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.calculations.pro.domain_models import BetType
from src.calculations.pro.phase2_enhancements import AccumulatorEngine, BetLeg


# =============================================================================
# 1. 进球时序模型框架
# =============================================================================

@dataclass
class GoalEvent:
    minute: int
    team: str
    home_score: int
    away_score: int


@dataclass
class MatchTimeline:
    events: List[GoalEvent]
    total_home_goals: int
    total_away_goals: int
    minutes: List[int]


class GoalTimeModel:
    def __init__(self):
        self.minutes = 90
        self.injury_time_factor = 1.07
        self.shape_param = 0.9
        self.home_goal_intensity = 0.018
        self.away_goal_intensity = 0.014
    
    def simulate_goals(self, expected_home: float, expected_away: float, num_simulations: int = 1000) -> List[MatchTimeline]:
        timelines = []
        home_rate = expected_home / self.minutes
        away_rate = expected_away / self.minutes
        
        for _ in range(num_simulations):
            timeline = self._simulate_single_match(home_rate, away_rate)
            timelines.append(timeline)
        
        return timelines
    
    def _simulate_single_match(self, home_rate: float, away_rate: float) -> MatchTimeline:
        events = []
        home_goals = 0
        away_goals = 0
        minutes = []
        
        minute = 0
        while minute < self.minutes * self.injury_time_factor:
            time_to_next_home = random.expovariate(home_rate) if home_rate > 0 else float('inf')
            time_to_next_away = random.expovariate(away_rate) if away_rate > 0 else float('inf')
            
            next_goal_time = min(time_to_next_home, time_to_next_away)
            
            if minute + next_goal_time > self.minutes * self.injury_time_factor:
                break
            
            for m in range(len(minutes), int(minute + next_goal_time) + 1):
                minutes.append((home_goals, away_goals))
            
            if time_to_next_home < time_to_next_away:
                home_goals += 1
                events.append(GoalEvent(
                    minute=int(minute + next_goal_time),
                    team="home",
                    home_score=home_goals,
                    away_score=away_goals
                ))
            else:
                away_goals += 1
                events.append(GoalEvent(
                    minute=int(minute + next_goal_time),
                    team="away",
                    home_score=home_goals,
                    away_score=away_goals
                ))
            
            minute += next_goal_time
        
        for m in range(len(minutes), int(self.minutes * self.injury_time_factor) + 1):
            minutes.append((home_goals, away_goals))
        
        return MatchTimeline(
            events=events,
            total_home_goals=home_goals,
            total_away_goals=away_goals,
            minutes=minutes
        )
    
    def calculate_first_goal_probs(self, expected_home: float, expected_away: float, num_simulations: int = 5000) -> Dict[str, float]:
        timelines = self.simulate_goals(expected_home, expected_away, num_simulations)
        
        home_first = 0.0
        away_first = 0.0
        no_goals = 0.0
        
        for tl in timelines:
            if len(tl.events) == 0:
                no_goals += 1
            elif tl.events[0].team == "home":
                home_first += 1
            else:
                away_first += 1
        
        total = len(timelines)
        return {
            "home_first": home_first / total,
            "away_first": away_first / total,
            "no_goals": no_goals / total
        }
    
    def calculate_goal_in_minute_range(self, expected_home: float, expected_away: float, start_min: int, end_min: int, num_simulations: int = 3000) -> float:
        timelines = self.simulate_goals(expected_home, expected_away, num_simulations)
        
        goal_count = 0
        for tl in timelines:
            for event in tl.events:
                if start_min <= event.minute <= end_min:
                    goal_count += 1
                    break
        
        return goal_count / len(timelines)


# =============================================================================
# 2. 实时滚球深度模型框架
# =============================================================================

class GameState(Enum):
    NOT_STARTED = "not_started"
    FIRST_HALF = "first_half"
    HALF_TIME = "half_time"
    SECOND_HALF = "second_half"
    FINISHED = "finished"


@dataclass
class LiveMatchState:
    minute: int
    home_goals: int
    away_goals: int
    state: GameState
    time_remaining: int
    momentum_score: float
    red_cards_home: int = 0
    red_cards_away: int = 0


@dataclass
class LivePrediction:
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    expected_home_goals: float
    expected_away_goals: float
    expected_total_goals: float
    probability_updates: List[Dict[str, float]]


class LivePredictor:
    def __init__(self):
        self.goal_model = GoalTimeModel()
        self.time_decay_factor = 0.015
    
    def update_prediction(self, initial_home: float, initial_away: float, current_state: LiveMatchState) -> LivePrediction:
        time_remaining = max(0, 90 - current_state.minute)
        time_fraction_remaining = time_remaining / 90
        
        goals_scored_home = current_state.home_goals
        goals_scored_away = current_state.away_goals
        
        remaining_home = initial_home * time_fraction_remaining
        remaining_away = initial_away * time_fraction_remaining
        
        momentum = current_state.momentum_score
        momentum_adjustment = 0.1 * (momentum - 50) / 50
        
        remaining_home *= (1 + momentum_adjustment)
        remaining_away *= (1 - momentum_adjustment)
        
        final_home = goals_scored_home + remaining_home
        final_away = goals_scored_away + remaining_away
        
        probs = self._calculate_result_probs(goals_scored_home, goals_scored_away, remaining_home, remaining_away)
        
        return LivePrediction(
            home_win_prob=probs["home"],
            draw_prob=probs["draw"],
            away_win_prob=probs["away"],
            expected_home_goals=final_home,
            expected_away_goals=final_away,
            expected_total_goals=final_home + final_away,
            probability_updates=[]
        )
    
    def _calculate_result_probs(self, current_h: int, current_a: int, rem_h: float, rem_a: float) -> Dict[str, float]:
        home_total = 0.0
        draw_total = 0.0
        away_total = 0.0
        
        max_goals = 10
        for add_h in range(max_goals + 1):
            for add_a in range(max_goals + 1):
                prob_h = self._poisson(rem_h, add_h)
                prob_a = self._poisson(rem_a, add_a)
                joint_prob = prob_h * prob_a
                
                final_h = current_h + add_h
                final_a = current_a + add_a
                
                if final_h > final_a:
                    home_total += joint_prob
                elif final_h == final_a:
                    draw_total += joint_prob
                else:
                    away_total += joint_prob
        
        total = home_total + draw_total + away_total
        return {
            "home": home_total / total,
            "draw": draw_total / total,
            "away": away_total / total
        }
    
    def _poisson(self, lam: float, k: int) -> float:
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam ** k)) / math.factorial(k)


# =============================================================================
# 3. 高级组合玩法框架
# =============================================================================

class ComboType(Enum):
    DOUBLE_CHANCE = "double_chance"
    WIN_BOTH_HALVES = "win_both_halves"
    SCORE_GOAL_FIRST = "score_first_and_win"
    CORRECT_SCORE_RANGE = "correct_score_range"


@dataclass
class ComboBetLeg:
    combo_type: ComboType
    parameters: Dict[str, Any]
    odds: float
    predicted_prob: float


@dataclass
class ComboBet:
    legs: List[ComboBetLeg]
    total_odds: float
    win_probability: float
    ev_ratio: float


class ComboEngine:
    def __init__(self):
        self.accumulator_engine = AccumulatorEngine()
        self.goal_model = GoalTimeModel()
    
    def create_double_chance_and_ou(self, home_prob: float, draw_prob: float, away_prob: float, ou_prob: float, odds_home_draw: float, odds_ou: float) -> ComboBet:
        home_draw_prob = home_prob + draw_prob
        joint_prob = home_draw_prob * ou_prob
        
        total_odds = odds_home_draw * odds_ou
        
        return ComboBet(
            legs=[
                ComboBetLeg(
                    combo_type=ComboType.DOUBLE_CHANCE,
                    parameters={"type": "home_draw"},
                    odds=odds_home_draw,
                    predicted_prob=home_draw_prob
                ),
                ComboBetLeg(
                    combo_type=ComboType.DOUBLE_CHANCE,
                    parameters={"type": "over_under"},
                    odds=odds_ou,
                    predicted_prob=ou_prob
                )
            ],
            total_odds=total_odds,
            win_probability=joint_prob,
            ev_ratio=(joint_prob * total_odds) - 1.0
        )
    
    def calculate_win_both_halves_prob(self, exp_h_1h: float, exp_a_1h: float, exp_h_2h: float, exp_a_2h: float) -> float:
        prob_1h = self._prob_win_half(exp_h_1h, exp_a_1h)
        prob_2h = self._prob_win_half(exp_h_2h, exp_a_2h)
        return prob_1h * prob_2h
    
    def _prob_win_half(self, exp_h: float, exp_a: float) -> float:
        win_prob = 0.0
        max_g = 8
        for h in range(max_g + 1):
            for a in range(max_g + 1):
                if h > a:
                    prob_h = self._poisson(exp_h, h)
                    prob_a = self._poisson(exp_a, a)
                    win_prob += prob_h * prob_a
        return win_prob
    
    def calculate_score_first_and_win_prob(self, expected_home: float, expected_away: float, num_sims: int = 2000) -> float:
        timelines = self.goal_model.simulate_goals(expected_home, expected_away, num_sims)
        
        success = 0
        for tl in timelines:
            if len(tl.events) > 0:
                first_team = tl.events[0].team
                if first_team == "home" and tl.total_home_goals > tl.total_away_goals:
                    success += 1
                elif first_team == "away" and tl.total_away_goals > tl.total_home_goals:
                    success += 1
        
        return success / len(timelines)
    
    def _poisson(self, lam: float, k: int) -> float:
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam ** k)) / math.factorial(k)


# =============================================================================
# 综合演示
# =============================================================================

def demo_phase3_future():
    print("="*80)
    print("🔮 AFA v8.3 - Phase 3 未来功能框架演示")
    print("="*80)
    
    home_exp, away_exp = 1.8, 1.2
    print(f"\n📊 测试场景: 主队预期进球 {home_exp}, 客队预期进球 {away_exp}")
    
    print("\n" + "="*60)
    print("1️⃣  进球时序模型框架")
    print("="*60)
    goal_model = GoalTimeModel()
    
    first_goal = goal_model.calculate_first_goal_probs(home_exp, away_exp, num_simulations=2000)
    print(f"  首个进球概率:")
    print(f"    主队先进球: {first_goal['home_first']*100:.1f}%")
    print(f"    客队先进球: {first_goal['away_first']*100:.1f}%")
    print(f"    无进球: {first_goal['no_goals']*100:.1f}%")
    
    goal_75_90 = goal_model.calculate_goal_in_minute_range(home_exp, away_exp, 75, 90, num_simulations=1500)
    print(f"\n  75-90分钟进球概率: {goal_75_90*100:.1f}%")
    
    print("\n" + "="*60)
    print("2️⃣  实时滚球深度模型框架")
    print("="*60)
    live_predictor = LivePredictor()
    
    scenarios = [
        ("赛前 (0:0)", LiveMatchState(minute=0, home_goals=0, away_goals=0, state=GameState.NOT_STARTED, time_remaining=90, momentum_score=50)),
        ("中场 (1:0)", LiveMatchState(minute=45, home_goals=1, away_goals=0, state=GameState.HALF_TIME, time_remaining=45, momentum_score=65)),
        ("75分钟 (1:1)", LiveMatchState(minute=75, home_goals=1, away_goals=1, state=GameState.SECOND_HALF, time_remaining=15, momentum_score=45)),
    ]
    
    for desc, state in scenarios:
        pred = live_predictor.update_prediction(home_exp, away_exp, state)
        print(f"\n  {desc}:")
        print(f"    胜平负: 主 {pred.home_win_prob*100:.1f}% / 平 {pred.draw_prob*100:.1f}% / 客 {pred.away_win_prob*100:.1f}%")
        print(f"    预期进球: 主 {pred.expected_home_goals:.1f} / 客 {pred.expected_away_goals:.1f}")
    
    print("\n" + "="*60)
    print("3️⃣  高级组合玩法框架")
    print("="*60)
    combo_engine = ComboEngine()
    
    home_p, draw_p, away_p = 0.52, 0.24, 0.24
    ou_p = 0.58
    odds_hd = 1.35
    odds_ou = 1.75
    
    combo = combo_engine.create_double_chance_and_ou(home_p, draw_p, away_p, ou_p, odds_hd, odds_ou)
    print(f"  双胜+大小球组合:")
    print(f"    组合赔率: {combo.total_odds:.2f}")
    print(f"    胜率: {combo.win_probability*100:.1f}%")
    print(f"    EV比: {combo.ev_ratio*100:+.1f}%")
    
    first_and_win = combo_engine.calculate_score_first_and_win_prob(home_exp, away_exp, num_sims=1500)
    print(f"\n  先进球且获胜概率: {first_and_win*100:.1f}%")
    
    print("\n" + "="*80)
    print("✅ Phase 3 框架演示完成！")
    print("="*80)


if __name__ == '__main__':
    demo_phase3_future()
