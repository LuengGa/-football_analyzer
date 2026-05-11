"""
Match Value Analyzer - 比赛价值分析器
负责：
1. 预筛选有价值的比赛
2. 智能推荐最佳玩法
3. 结合六层分析和量化分析
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import math
from datetime import datetime

from src.calculations.game_type_manager import get_game_type_manager, get_probability_engine


class GamePriority(Enum):
    """玩法优先级"""
    MUST_BET = "must_bet"    # 必玩
    HIGH = "high"            # 推荐
    MEDIUM = "medium"        # 可玩
    LOW = "low"              # 不推荐
    NO_BET = "no_bet"        # 弃玩


@dataclass
class GameRecommendation:
    """玩法推荐"""
    game_type_id: str
    game_type_name: str
    category: str
    priority: GamePriority
    confidence: float
    expected_value: float
    edge: float
    best_selection: str
    best_selection_odds: float
    reasoning: str


@dataclass
class MatchValueResult:
    """比赛价值分析结果"""
    has_value: bool
    value_score: float
    overall_confidence: float
    game_recommendations: List[GameRecommendation]
    top_3_recommendations: List[GameRecommendation]
    reasoning: str
    match_filters_passed: List[str]
    match_filters_failed: List[str]


class MatchFilter:
    """比赛筛选器"""
    
    def __init__(self):
        # 筛选阈值
        self.min_confidence = 0.55
        self.min_edge = 0.03
        self.min_odds = 1.4
        self.max_odds = 5.0
    
    def filter_match(
        self,
        match_data: Dict[str, Any]
    ) -> tuple[bool, List[str], List[str]]:
        """
        筛选比赛
        
        Returns:
            (是否通过, 通过的筛选, 失败的筛选)
        """
        passed = []
        failed = []
        
        # 1. 赔率范围检查
        odds_home = match_data.get("odds_home", 1.0)
        odds_away = match_data.get("odds_away", 1.0)
        odds_draw = match_data.get("odds_draw", 3.0)
        
        min_odds_match = min(odds_home, odds_away, odds_draw)
        max_odds_match = max(odds_home, odds_away, odds_draw)
        
        if min_odds_match >= self.min_odds:
            passed.append("最低赔率符合要求")
        else:
            failed.append(f"最低赔率({min_odds_match:.2f})低于阈值({self.min_odds})")
        
        if max_odds_match <= self.max_odds:
            passed.append("最高赔率符合要求")
        else:
            failed.append(f"最高赔率({max_odds_match:.2f})高于阈值({self.max_odds})")
        
        # 2. 非极端热门/冷门检查
        implied_probs = {
            "home": 1 / odds_home if odds_home > 0 else 0,
            "draw": 1 / odds_draw if odds_draw > 0 else 0,
            "away": 1 / odds_away if odds_away > 0 else 0
        }
        implied_probs = {k: v / sum(implied_probs.values()) for k, v in implied_probs.items()}
        
        max_implied = max(implied_probs.values())
        if max_implied < 0.75:
            passed.append("无极端热门")
        else:
            failed.append(f"过于热门(隐含概率{max_implied:.1%})")
        
        # 3. 价差检查（多机构一致性）
        bookmaker_count = len(match_data.get("bookmaker_data", []))
        if bookmaker_count >= 2:
            passed.append(f"有多机构数据({bookmaker_count}个)")
        else:
            failed.append("机构数据不足")
        
        return len(failed) == 0, passed, failed


class GameTypeAnalyzer:
    """玩法类型分析器"""
    
    def __init__(self):
        self.game_type_manager = get_game_type_manager()
        self.probability_engine = get_probability_engine()
    
    def analyze_game_type(
        self,
        game_type_id: str,
        match_data: Dict[str, Any],
        six_layer_data: Dict[str, Any] = None,
        market_odds: Dict[str, Any] = None
    ) -> Optional[GameRecommendation]:
        """分析单个玩法"""
        game_type = self.game_type_manager.get_game_type(game_type_id)
        if not game_type:
            return None
        
        # 获取xG（预期进球）
        home_xg = match_data.get("home_xg", 1.5)
        away_xg = match_data.get("away_xg", 1.2)
        handicap = match_data.get("handicap", 0.0)
        
        # 计算所有玩法概率
        all_probs = self.probability_engine.calculate_all_markets(home_xg, away_xg, handicap)
        
        # 根据玩法类型处理
        if game_type_id == "jingcai_wdl" or game_type_id == "european_odds":
            return self._analyze_wdl(game_type, all_probs, market_odds, six_layer_data)
        elif game_type_id == "jingcai_handicap" or game_type_id == "asian_handicap":
            return self._analyze_handicap(game_type, all_probs, market_odds, handicap, six_layer_data)
        elif game_type_id == "jingcai_total" or game_type_id == "over_under":
            return self._analyze_total_goals(game_type, all_probs, market_odds, six_layer_data)
        elif game_type_id == "both_teams_score":
            return self._analyze_both_teams_score(game_type, all_probs, market_odds, six_layer_data)
        elif game_type_id == "double_chance":
            return self._analyze_double_chance(game_type, all_probs, market_odds, six_layer_data)
        elif game_type_id == "jingcai_htft":
            return self._analyze_htft(game_type, all_probs, market_odds, six_layer_data)
        elif game_type_id == "jingcai_score" or game_type_id == "correct_score":
            return self._analyze_correct_score(game_type, all_probs, market_odds, six_layer_data)
        elif game_type_id == "beidan_bonus":
            return self._analyze_updown(game_type, all_probs, market_odds, six_layer_data)
        else:
            return self._analyze_generic(game_type, all_probs, market_odds, six_layer_data)
    
    def _analyze_wdl(
        self,
        game_type,
        all_probs: Dict,
        market_odds: Dict = None,
        six_layer_data: Dict = None
    ) -> GameRecommendation:
        """分析胜平负玩法"""
        wdl_probs = all_probs["wdl"]
        market_odds = market_odds or {"home": 2.0, "draw": 3.3, "away": 3.5}
        
        # 计算各选项的edge和EV
        options = [
            ("home", wdl_probs["胜"], market_odds.get("home", 2.0)),
            ("draw", wdl_probs["平"], market_odds.get("draw", 3.3)),
            ("away", wdl_probs["负"], market_odds.get("away", 3.5))
        ]
        
        return self._find_best_option(game_type, options, ["胜", "平", "负"], six_layer_data)
    
    def _analyze_handicap(
        self,
        game_type,
        all_probs: Dict,
        market_odds: Dict = None,
        handicap: float = 0.0,
        six_layer_data: Dict = None
    ) -> GameRecommendation:
        """分析让球玩法"""
        handicap_probs = all_probs["handicap"]
        market_odds = market_odds or {"home": 1.95, "draw": 3.3, "away": 1.95}
        
        options = [
            ("home", handicap_probs["胜"], market_odds.get("home", 1.95)),
            ("draw", handicap_probs["平"], market_odds.get("draw", 3.3)),
            ("away", handicap_probs["负"], market_odds.get("away", 1.95))
        ]
        
        return self._find_best_option(game_type, options, ["胜", "平", "负"], six_layer_data)
    
    def _analyze_total_goals(
        self,
        game_type,
        all_probs: Dict,
        market_odds: Dict = None,
        six_layer_data: Dict = None
    ) -> GameRecommendation:
        """分析总进球玩法"""
        total_probs = all_probs["total_goals"]
        
        # 简化为大小球模式分析
        line = 2.5
        over_prob = sum(v for k, v in total_probs.items() if k != "7+" and int(k) > line) + (total_probs.get("7+", 0) if line < 7 else 0)
        under_prob = 1 - over_prob
        
        options = [
            ("over", over_prob, 1.9),
            ("under", under_prob, 1.9)
        ]
        
        option_names = ["大", "小"]
        if game_type.category == "jingcai":
            option_names = ["0", "1", "2", "3", "4", "5", "6", "7+"]
            max_prob = -1
            best_option = "0"
            for option in option_names:
                if total_probs.get(option, 0) > max_prob:
                    max_prob = total_probs.get(option, 0)
                    best_option = option
            options = [(best_option, max_prob, 5.0)]
        
        return self._find_best_option(game_type, options, option_names, six_layer_data)
    
    def _analyze_both_teams_score(
        self,
        game_type,
        all_probs: Dict,
        market_odds: Dict = None,
        six_layer_data: Dict = None
    ) -> GameRecommendation:
        """分析双方进球玩法"""
        bts_probs = self.probability_engine.calculate_both_teams_score(1.5, 1.2)
        
        options = [
            ("yes", bts_probs["是"], 1.9),
            ("no", bts_probs["否"], 1.9)
        ]
        
        return self._find_best_option(game_type, options, ["是", "否"], six_layer_data)
    
    def _analyze_double_chance(
        self,
        game_type,
        all_probs: Dict,
        market_odds: Dict = None,
        six_layer_data: Dict = None
    ) -> GameRecommendation:
        """分析双重机会玩法"""
        wdl_probs = all_probs["wdl"]
        
        options = [
            ("home_or_draw", wdl_probs["胜"] + wdl_probs["平"], 1.4),
            ("home_or_away", wdl_probs["胜"] + wdl_probs["负"], 1.2),
            ("draw_or_away", wdl_probs["平"] + wdl_probs["负"], 1.4)
        ]
        
        return self._find_best_option(game_type, options, ["胜/平", "胜/负", "平/负"], six_layer_data)
    
    def _analyze_htft(
        self,
        game_type,
        all_probs: Dict,
        market_odds: Dict = None,
        six_layer_data: Dict = None
    ) -> GameRecommendation:
        """分析半全场玩法"""
        htft_probs = all_probs["htft"]
        
        max_prob = -1
        best_option = "胜胜"
        for option, prob in htft_probs.items():
            if prob > max_prob:
                max_prob = prob
                best_option = option
        
        options = [(best_option, max_prob, 8.0)]
        return self._find_best_option(game_type, options, list(htft_probs.keys()), six_layer_data)
    
    def _analyze_correct_score(
        self,
        game_type,
        all_probs: Dict,
        market_odds: Dict = None,
        six_layer_data: Dict = None
    ) -> GameRecommendation:
        """分析比分玩法"""
        score_probs = all_probs["score"]
        
        max_prob = -1
        best_option = "1:0"
        for option, prob in score_probs.items():
            if prob > max_prob:
                max_prob = prob
                best_option = option
        
        options = [(best_option, max_prob, 6.5)]
        return self._find_best_option(game_type, options, list(score_probs.keys()), six_layer_data)
    
    def _analyze_updown(
        self,
        game_type,
        all_probs: Dict,
        market_odds: Dict = None,
        six_layer_data: Dict = None
    ) -> GameRecommendation:
        """分析上下单双玩法"""
        bd_probs = all_probs["bd_up_down"]
        
        max_prob = -1
        best_option = "上单"
        for option, prob in bd_probs.items():
            if prob > max_prob:
                max_prob = prob
                best_option = option
        
        options = [(best_option, max_prob, 3.5)]
        return self._find_best_option(game_type, options, list(bd_probs.keys()), six_layer_data)
    
    def _analyze_generic(
        self,
        game_type,
        all_probs: Dict,
        market_odds: Dict = None,
        six_layer_data: Dict = None
    ) -> GameRecommendation:
        """通用玩法分析"""
        wdl_probs = all_probs["wdl"]
        
        options = [
            ("home", wdl_probs["胜"], 2.0),
            ("draw", wdl_probs["平"], 3.3),
            ("away", wdl_probs["负"], 3.5)
        ]
        
        return self._find_best_option(game_type, options, ["胜", "平", "负"], six_layer_data)
    
    def _find_best_option(
        self,
        game_type,
        options: List[tuple],
        option_names: List[str],
        six_layer_data: Dict = None
    ) -> GameRecommendation:
        """找出最佳选项"""
        best_opt = None
        best_ev = -float('inf')
        best_edge = -float('inf')
        
        for opt_id, prob, odds in options:
            if odds <= 1.0:
                continue
            
            implied_prob = 1 / odds
            edge = prob - implied_prob
            ev = (prob * (odds - 1)) - ((1 - prob) * 1)
            
            if ev > best_ev:
                best_ev = ev
                best_edge = edge
                best_opt = (opt_id, prob, odds)
        
        if not best_opt:
            best_opt = options[0] if options else ("unknown", 0.5, 2.0)
        
        # 确定优先级
        priority = self._determine_priority(best_edge, best_ev, best_opt[1])
        
        # 结合六层分析增强信心
        confidence = best_opt[1]
        if six_layer_data:
            layer6 = six_layer_data.get("layer6", {})
            six_layer_conf = layer6.get("overall_confidence", 0)
            confidence = 0.6 * confidence + 0.4 * six_layer_conf
        
        opt_idx = option_names.index(best_opt[0]) if best_opt[0] in option_names else 0
        
        return GameRecommendation(
            game_type_id=game_type.id,
            game_type_name=game_type.name,
            category=game_type.category,
            priority=priority,
            confidence=confidence,
            expected_value=best_ev,
            edge=best_edge,
            best_selection=option_names[opt_idx],
            best_selection_odds=best_opt[2],
            reasoning=f"选择{option_names[opt_idx]}，概率{best_opt[1]:.1%}，EV={best_ev:.3f}"
        )
    
    def _determine_priority(
        self,
        edge: float,
        expected_value: float,
        confidence: float
    ) -> GamePriority:
        """确定优先级"""
        if edge > 0.1 and confidence > 0.65 and expected_value > 0.15:
            return GamePriority.MUST_BET
        elif edge > 0.05 and confidence > 0.60 and expected_value > 0.05:
            return GamePriority.HIGH
        elif edge > 0.02 and confidence > 0.55 and expected_value > 0:
            return GamePriority.MEDIUM
        elif edge > -0.03:
            return GamePriority.LOW
        else:
            return GamePriority.NO_BET


class MatchValueAnalyzer:
    """比赛价值分析器"""
    
    def __init__(self):
        self.match_filter = MatchFilter()
        self.game_analyzer = GameTypeAnalyzer()
        
        # 主要玩法列表（优先分析）
        self.primary_game_types = [
            "jingcai_wdl",
            "jingcai_handicap",
            "asian_handicap",
            "european_odds",
            "over_under",
            "jingcai_total",
            "both_teams_score",
            "double_chance"
        ]
        
        # 次要玩法列表
        self.secondary_game_types = [
            "jingcai_score",
            "jingcai_htft",
            "beidan_wdl",
            "beidan_handicap",
            "beidan_total"
        ]
    
    def analyze_match(
        self,
        match_data: Dict[str, Any],
        six_layer_data: Dict[str, Any] = None,
        market_odds: Dict[str, Any] = None
    ) -> MatchValueResult:
        """
        分析比赛价值并推荐玩法
        
        Args:
            match_data: 比赛数据
            six_layer_data: 六层分析结果
            market_odds: 市场赔率
        
        Returns:
            MatchValueResult
        """
        # 1. 先筛选比赛
        has_value, passed_filters, failed_filters = self.match_filter.filter_match(match_data)
        
        # 2. 分析所有玩法
        all_recommendations = []
        
        # 分析主要玩法
        for game_type_id in self.primary_game_types:
            recommendation = self.game_analyzer.analyze_game_type(
                game_type_id, match_data, six_layer_data, market_odds
            )
            if recommendation:
                all_recommendations.append(recommendation)
        
        # 分析次要玩法（仅当比赛有价值时）
        if has_value:
            for game_type_id in self.secondary_game_types:
                recommendation = self.game_analyzer.analyze_game_type(
                    game_type_id, match_data, six_layer_data, market_odds
                )
                if recommendation:
                    all_recommendations.append(recommendation)
        
        # 3. 排序和选择Top3
        all_recommendations.sort(
            key=lambda x: (x.priority.value, -x.expected_value, -x.confidence),
            reverse=False
        )
        
        # 按优先级排序：MUST_BET > HIGH > MEDIUM > LOW > NO_BET
        priority_order = {
            GamePriority.MUST_BET: 0,
            GamePriority.HIGH: 1,
            GamePriority.MEDIUM: 2,
            GamePriority.LOW: 3,
            GamePriority.NO_BET: 4
        }
        
        all_recommendations.sort(
            key=lambda x: (priority_order[x.priority], -x.expected_value)
        )
        
        top_3 = all_recommendations[:3]
        
        # 4. 计算整体价值分数
        value_score = 0.0
        if has_value:
            # 结合Top3推荐的质量
            for rec in top_3:
                if rec.priority == GamePriority.MUST_BET:
                    value_score += 0.4
                elif rec.priority == GamePriority.HIGH:
                    value_score += 0.25
                elif rec.priority == GamePriority.MEDIUM:
                    value_score += 0.1
        
        # 六层分析加成
        if six_layer_data:
            layer6 = six_layer_data.get("layer6", {})
            opportunities = layer6.get("opportunities", [])
            if opportunities:
                value_score += 0.2
        
        value_score = min(1.0, value_score)
        
        # 5. 确定是否有价值
        has_value = value_score >= 0.15
        
        # 6. 生成理由
        reasoning = self._generate_reasoning(
            has_value, value_score, all_recommendations, passed_filters, failed_filters
        )
        
        return MatchValueResult(
            has_value=has_value,
            value_score=value_score,
            overall_confidence=top_3[0].confidence if top_3 else 0.5,
            game_recommendations=all_recommendations,
            top_3_recommendations=top_3,
            reasoning=reasoning,
            match_filters_passed=passed_filters,
            match_filters_failed=failed_filters
        )
    
    def _generate_reasoning(
        self,
        has_value: bool,
        value_score: float,
        recommendations: List[GameRecommendation],
        passed: List[str],
        failed: List[str]
    ) -> str:
        """生成分析理由"""
        if not has_value:
            return f"比赛价值不足(得分{value_score:.2f})，不推荐分析。"
        
        parts = [f"比赛价值评估得分为{value_score:.2f}。"]
        
        # 筛选情况
        if passed:
            parts.append(f"通过筛选: {', '.join(passed)}。")
        if failed:
            parts.append(f"未通过筛选: {', '.join(failed)}。")
        
        # 推荐玩法
        if recommendations:
            must_bet = [r for r in recommendations if r.priority == GamePriority.MUST_BET]
            high_recommend = [r for r in recommendations if r.priority == GamePriority.HIGH]
            
            if must_bet:
                parts.append(f"发现{len(must_bet)}个必玩玩法！")
            if high_recommend:
                parts.append(f"发现{len(high_recommend)}个高推荐玩法。")
        
        return " ".join(parts)
    
    def analyze_daily_matches(
        self,
        matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """分析当日所有比赛"""
        results = []
        
        for match in matches:
            result = self.analyze_match(match)
            results.append({
                "match": match,
                "value_result": result,
                "is_valuable": result.has_value
            })
        
        # 按价值排序
        results.sort(
            key=lambda x: (x["is_valuable"], x["value_result"].value_score),
            reverse=True
        )
        
        return results


# 全局实例
_match_value_analyzer = None

def get_match_value_analyzer() -> MatchValueAnalyzer:
    """获取比赛价值分析器实例"""
    global _match_value_analyzer
    if _match_value_analyzer is None:
        _match_value_analyzer = MatchValueAnalyzer()
    return _match_value_analyzer
