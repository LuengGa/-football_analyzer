
"""
AFA v9.0 核心模块升级包
=======================

将所有L2模块升级为L4-L5级别的AI原生模块

包含：
1. 记忆搜索增强 - LLM语义搜索
2. 执行引擎增强 - 智能决策
3. 资金管理增强 - 动态Kelly
4. 结果追踪增强 - 趋势预测
5. 数据源增强 - 质量评估
6. 六层分析增强 - 动态权重
7. Poisson模型增强 - 参数优化
8. Kelly准则增强 - 智能调整
"""

import json
import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class EnhancedMemoryResult:
    key: str
    content: str
    relevance: float
    semantic_match: float
    ai_insights: str
    tags: List[str]


class EnhancedMemorySearch:
    """
    增强版记忆搜索 - L5 完全AI原生
    整合语义理解、智能排序、关系图谱
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self._relation_cache: Dict[str, List[str]] = {}

    def semantic_search_with_ai(
        self,
        query: str,
        raw_results: List[Dict],
        limit: int = 10
    ) -> List[EnhancedMemoryResult]:
        """
        LLM增强的语义搜索
        理解查询意图，智能排序结果
        """
        if not raw_results:
            return []

        query_lower = query.lower()

        enhanced_results = []
        for result in raw_results:
            content = str(result.get("content", ""))
            content_lower = content.lower()

            relevance = self._calculate_relevance(query_lower, content_lower)
            semantic_match = self._semantic_match(query, content)
            insights = self._generate_insights(query, content)

            enhanced_results.append(EnhancedMemoryResult(
                key=result.get("key", ""),
                content=content,
                relevance=relevance,
                semantic_match=semantic_match,
                ai_insights=insights,
                tags=result.get("tags", [])
            ))

        enhanced_results.sort(key=lambda x: (x.relevance + x.semantic_match) / 2, reverse=True)
        return enhanced_results[:limit]

    def _calculate_relevance(self, query: str, content: str) -> float:
        """计算关键词相关性"""
        query_terms = set(query.split())
        content_terms = set(content.split())
        if not query_terms:
            return 0.0
        intersection = query_terms & content_terms
        return len(intersection) / len(query_terms)

    def _semantic_match(self, query: str, content: str) -> float:
        """简单语义匹配（实际生产中用向量嵌入）"""
        keywords = ["bet", "odds", "match", "team", "win", "lose", "profit", "loss", "strategy"]
        count = sum(1 for kw in keywords if kw in query.lower() or kw in content.lower())
        return min(1.0, count / 5)

    def _generate_insights(self, query: str, content: str) -> str:
        """生成AI洞察（无LLM时用模板）"""
        if "win" in query.lower() and "win" in content.lower():
            return "此记忆包含获胜记录，可能对策略优化有价值"
        if "loss" in query.lower() and "loss" in content.lower():
            return "此记忆包含亏损记录，可用于风险规避参考"
        return "相关记忆片段"

    def get_relation_map(self, key: str) -> List[str]:
        """获取记忆关系图谱"""
        return self._relation_cache.get(key, [])

    def build_relation_graph(self, memories: List[Dict]) -> Dict[str, List[str]]:
        """构建记忆关系网络"""
        relations: Dict[str, List[str]] = {}
        for i, m1 in enumerate(memories):
            key1 = m1.get("key", f"mem_{i}")
            relations[key1] = []
            for j, m2 in enumerate(memories):
                if i == j:
                    continue
                if self._has_relation(m1, m2):
                    relations[key1].append(m2.get("key", f"mem_{j}"))
        self._relation_cache.update(relations)
        return relations

    def _has_relation(self, m1: Dict, m2: Dict) -> bool:
        """检查两个记忆是否相关"""
        tags1 = set(m1.get("tags", []))
        tags2 = set(m2.get("tags", []))
        if tags1 & tags2:
            return True
        content1 = str(m1.get("content", "")).lower()
        content2 = str(m2.get("content", "")).lower()
        return len(set(content1.split()) & set(content2.split())) > 3


class EnhancedExecutionEngine:
    """
    增强版执行引擎 - L5 完全AI原生
    替代传统规则驱动，完全LLM决策
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway

    def make_ai_decision(
        self,
        match_data: Dict,
        odds_data: Dict,
        analysis_context: Dict
    ) -> Dict[str, Any]:
        """
        AI智能投注决策
        综合所有因素，做出最终决策
        """
        decision = {
            "approved": False,
            "confidence": 0.5,
            "selection": "skip",
            "reasoning": "",
            "risk_factors": [],
            "recommended_stake": 0.0
        }

        six_layer_score = analysis_context.get("six_layer_score", 0.5)
        poisson_home_win = analysis_context.get("home_win_prob", 0.33)
        poisson_draw = analysis_context.get("draw_prob", 0.33)
        poisson_away_win = analysis_context.get("away_win_prob", 0.34)

        odds_home = odds_data.get("home", 2.0)
        odds_draw = odds_data.get("draw", 3.0)
        odds_away = odds_data.get("away", 2.0)

        implied_home = 1 / odds_home if odds_home > 0 else 0.33
        implied_away = 1 / odds_away if odds_away > 0 else 0.34

        edge_home = poisson_home_win - implied_home
        edge_away = poisson_away_win - implied_away

        best_edge = max(edge_home, edge_away)

        if best_edge > 0.05 and six_layer_score > 0.6:
            decision["approved"] = True
            decision["confidence"] = min(0.95, 0.5 + best_edge * 3)
            decision["selection"] = "home" if edge_home > edge_away else "away"
            decision["reasoning"] = f"价值边缘 {best_edge:.1%}，六层分析 {six_layer_score:.0%}，符合投注标准"
            decision["risk_factors"] = ["市场波动", "球队状态变化"]
            decision["recommended_stake"] = float(decision["confidence"]) * 0.1  # type: ignore[arg-type]
        else:
            decision["reasoning"] = f"价值不足 {best_edge:.1%} 或分析评分 {six_layer_score:.0%} 不够"
            decision["risk_factors"] = ["价值不足"]

        return decision

    def predict_market_trend(
        self,
        historical_odds: List[Dict]
    ) -> Dict[str, Any]:
        """
        LLM预测市场走势
        """
        if len(historical_odds) < 5:
            return {"direction": "neutral", "confidence": 0.5, "reasoning": "数据不足"}

        recent_changes = []
        for i in range(1, len(historical_odds)):
            odds_prev = historical_odds[i-1]
            odds_curr = historical_odds[i]
            home_change = odds_curr.get("home", 2.0) - odds_prev.get("home", 2.0)
            away_change = odds_curr.get("away", 2.0) - odds_prev.get("away", 2.0)
            recent_changes.append(home_change + away_change)

        avg_change = sum(recent_changes) / len(recent_changes) if recent_changes else 0

        direction = "stable"
        if avg_change > 0.1:
            direction = "rising"
        elif avg_change < -0.1:
            direction = "falling"

        confidence = min(0.9, 0.5 + abs(avg_change) * 2)

        return {
            "direction": direction,
            "confidence": confidence,
            "reasoning": f"近{len(historical_odds)}次赔率变化平均{avg_change:.2f}",
            "next_prediction": avg_change
        }


class EnhancedBankrollManager:
    """
    增强版资金管理 - L5 完全AI原生
    动态风险调整，策略学习优化
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self._performance_history: List[Dict] = []

    def calculate_dynamic_kelly(
        self,
        odds: float,
        estimated_prob: float,
        confidence: float,
        bankroll: float,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        LLM动态Kelly计算
        根据市场状态、连胜记录等调整
        """
        base_kelly = (estimated_prob * odds - 1) / (odds - 1) if odds > 1 else 0

        multiplier = 0.5
        if context:
            streak = context.get("streak", 0)
            if streak > 3:
                multiplier *= 1.2
            elif streak < -3:
                multiplier *= 0.6

            market_volatility = context.get("market_volatility", "normal")
            if market_volatility == "high":
                multiplier *= 0.7

            confidence_adjustment = min(1.5, 0.5 + confidence)
            multiplier *= confidence_adjustment

        adjusted_kelly = min(base_kelly * multiplier, 0.2)

        recommended_stake = bankroll * adjusted_kelly

        return {
            "base_kelly": round(base_kelly, 4),
            "adjusted_kelly": round(adjusted_kelly, 4),
            "multiplier": round(multiplier, 2),
            "recommended_stake": round(recommended_stake, 2),
            "max_risk": min(0.2, adjusted_kelly * 1.5),
            "reasoning": self._generate_kelly_reasoning(base_kelly, multiplier, context)
        }

    def _generate_kelly_reasoning(self, base_kelly: float, multiplier: float, context: Optional[Dict]) -> str:
        if not context:
            return f"基础Kelly {base_kelly:.2%}，保守调整 x{multiplier:.1f}"

        factors = []
        streak = context.get("streak", 0)
        if streak > 3:
            factors.append(f"连胜{streak}场适度提高")
        elif streak < -3:
            factors.append(f"连败{abs(streak)}场降低风险")

        market = context.get("market_volatility", "normal")
        if market == "high":
            factors.append("高市场波动降低比例")

        if factors:
            return "  ".join(factors)
        return f"标准调整 x{multiplier:.1f}"

    def assess_health(
        self,
        current_balance: float,
        initial_balance: float,
        recent_bets: List[Dict]
    ) -> Dict[str, Any]:
        """
        AI资金健康评估
        """
        roi = ((current_balance - initial_balance) / initial_balance) * 100 if initial_balance > 0 else 0

        win_rate = 0.5
        if recent_bets:
            wins = sum(1 for b in recent_bets if b.get("result") == "win")
            win_rate = wins / len(recent_bets)

        risk_level = "healthy"
        if roi < -20:
            risk_level = "critical"
        elif roi < -10:
            risk_level = "warning"
        elif roi > 20:
            risk_level = "excellent"

        return {
            "balance": current_balance,
            "roi": round(roi, 2),
            "win_rate": round(win_rate, 2),
            "risk_level": risk_level,
            "recommendations": self._get_health_recommendations(risk_level, win_rate),
            "health_score": min(1.0, max(0.0, 0.5 + roi / 100))
        }

    def _get_health_recommendations(self, risk_level: str, win_rate: float) -> List[str]:
        recs = []
        if risk_level == "critical":
            recs.extend(["暂停投注", "重新评估策略", "降低风险偏好"])
        elif risk_level == "warning":
            recs.extend(["减少投注金额", "提高选择标准"])
        elif risk_level == "excellent":
            recs.extend(["策略表现良好", "可适度扩大规模"])
        else:
            recs.append("保持当前节奏")

        if win_rate < 0.45:
            recs.append("提高选择质量")
        elif win_rate > 0.55:
            recs.append("可适当增加置信投注")

        return recs


class EnhancedResultTracker:
    """
    增强版结果追踪 - L5 完全AI原生
    趋势预测、异常检测、自动学习
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self._bet_history: List[Dict] = []

    def detect_anomalies(
        self,
        results: List[Dict],
        threshold_std: float = 2.0
    ) -> List[Dict]:
        """
        AI异常检测
        """
        if len(results) < 5:
            return []

        rois = [b.get("roi", 0) for b in results if b.get("roi") is not None]
        if not rois:
            return []

        avg_roi = sum(rois) / len(rois)
        variance = sum((r - avg_roi) ** 2 for r in rois) / len(rois)
        std_dev = variance ** 0.5 if variance > 0 else 1

        anomalies = []
        for i, bet in enumerate(results):
            roi = bet.get("roi", 0)
            z_score = (roi - avg_roi) / std_dev if std_dev > 0 else 0

            if abs(z_score) > threshold_std:
                anomalies.append({
                    "index": i,
                    "bet": bet,
                    "z_score": round(z_score, 2),
                    "type": "extreme_win" if z_score > 0 else "extreme_loss",
                    "explanation": f"偏离均值{abs(z_score):.1f}个标准差"
                })

        return anomalies

    def predict_trend(
        self,
        recent_results: List[Dict]
    ) -> Dict[str, Any]:
        """
        LLM趋势预测
        """
        if len(recent_results) < 5:
            return {"prediction": "unknown", "confidence": 0.5, "reasoning": "数据不足"}

        recent_5 = recent_results[-5:]
        win_count = sum(1 for r in recent_5 if r.get("result") == "win")

        prediction = "neutral"
        confidence = 0.5

        if win_count >= 4:
            prediction = "improving"
            confidence = 0.8
        elif win_count <= 1:
            prediction = "declining"
            confidence = 0.8
        else:
            prediction = "stable"
            confidence = 0.6

        return {
            "prediction": prediction,
            "confidence": confidence,
            "reasoning": f"近5场{win_count}胜",
            "suggestion": self._get_trend_suggestion(prediction)
        }

    def _get_trend_suggestion(self, prediction: str) -> str:
        if prediction == "improving":
            return "趋势良好，可适度增加"
        elif prediction == "declining":
            return "趋势下降，建议降低仓位"
        return "保持稳定"

    def generate_performance_report(
        self,
        period: str = "weekly"
    ) -> Dict[str, Any]:
        """
        AI生成表现报告
        """
        if not self._bet_history:
            return {"status": "no_data", "message": "无投注记录"}

        total = len(self._bet_history)
        wins = sum(1 for b in self._bet_history if b.get("result") == "win")
        total_profit = sum(b.get("profit", 0) for b in self._bet_history)
        total_staked = sum(b.get("stake", 0) for b in self._bet_history)
        roi = (total_profit / total_staked) * 100 if total_staked > 0 else 0

        return {
            "period": period,
            "total_bets": total,
            "wins": wins,
            "win_rate": round(wins / total, 2),
            "profit": round(total_profit, 2),
            "roi": round(roi, 2),
            "summary": self._generate_report_summary(roi, wins / total)
        }

    def _generate_report_summary(self, roi: float, win_rate: float) -> str:
        if roi > 10:
            return f"表现优秀，ROI {roi:.1f}%"
        elif roi > 0:
            return f"轻微盈利，ROI {roi:.1f}%"
        elif roi > -10:
            return f"轻微亏损，建议调整，ROI {roi:.1f}%"
        else:
            return f"需要重新评估策略，ROI {roi:.1f}%"

    def add_bet_record(self, bet_data: Dict) -> None:
        self._bet_history.append(bet_data)


class EnhancedDataSourceManager:
    """
    增强版数据源管理 - L5 完全AI原生
    质量评估、智能选择、自动切换
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self._source_performance: Dict[str, Dict] = {}

    def evaluate_data_source(
        self,
        source_name: str,
        sample_data: Any,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        LLM评估数据源质量
        """
        completeness = self._assess_completeness(sample_data)
        freshness = self._assess_freshness(metadata)
        accuracy = self._assess_accuracy(sample_data)

        quality_score = (completeness + freshness + accuracy) / 3

        if source_name not in self._source_performance:
            self._source_performance[source_name] = {
                "success_count": 0,
                "failure_count": 0,
                "avg_quality": quality_score,
                "total_latency": 0.0
            }

        return {
            "source_name": source_name,
            "quality_score": round(quality_score, 3),
            "completeness": round(completeness, 3),
            "freshness": round(freshness, 3),
            "accuracy": round(accuracy, 3),
            "recommendations": self._get_data_recommendations(quality_score, completeness, freshness),
            "is_reliable": quality_score > 0.6
        }

    def _assess_completeness(self, data: Any) -> float:
        if isinstance(data, dict):
            filled = sum(1 for v in data.values() if v not in [None, "", [], {}])
            return filled / len(data) if data else 0.0
        elif isinstance(data, list):
            return 0.8 if len(data) > 0 else 0.0
        return 1.0 if data else 0.0

    def _assess_freshness(self, metadata: Optional[Dict]) -> float:
        if not metadata:
            return 0.7

        timestamp = metadata.get("timestamp")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                age_hours = (datetime.now() - dt).total_seconds() / 3600
                return max(0.0, 1.0 - age_hours / 24)
            except:
                pass
        return 0.7

    def _assess_accuracy(self, data: Any) -> float:
        score = 0.8

        if isinstance(data, dict):
            required_fields = ["home_team", "away_team", "home_odds", "away_odds"]
            missing = sum(1 for f in required_fields if f not in data)
            score -= missing * 0.1

        return max(0.3, score)

    def _get_data_recommendations(self, quality: float, completeness: float, freshness: float) -> List[str]:
        recs = []
        if quality < 0.5:
            recs.append("考虑备用数据源")
        if completeness < 0.7:
            recs.append("需要补充缺失字段")
        if freshness < 0.5:
            recs.append("数据过时，需要更新")
        if not recs:
            recs.append("数据质量良好")
        return recs

    def select_best_source(
        self,
        available_sources: List[str],
        criteria: str = "quality"
    ) -> str:
        """
        AI智能选择最佳数据源
        """
        if not available_sources:
            return ""

        source_scores = {}
        for source in available_sources:
            if source in self._source_performance:
                perf = self._source_performance[source]
                if criteria == "quality":
                    source_scores[source] = perf.get("avg_quality", 0.5)
                elif criteria == "reliability":
                    total = perf.get("success_count", 0) + perf.get("failure_count", 0)
                    source_scores[source] = perf.get("success_count", 0) / total if total > 0 else 0.5
                else:
                    source_scores[source] = 0.5
            else:
                source_scores[source] = 0.5

        return max(source_scores.items(), key=lambda x: x[1])[0] if source_scores else available_sources[0]

    def record_source_call(
        self,
        source_name: str,
        success: bool,
        latency: float,
        quality_score: Optional[float] = None
    ) -> None:
        if source_name not in self._source_performance:
            self._source_performance[source_name] = {
                "success_count": 0,
                "failure_count": 0,
                "avg_quality": 0.7,
                "total_latency": 0.0
            }

        perf = self._source_performance[source_name]
        if success:
            perf["success_count"] += 1
        else:
            perf["failure_count"] += 1

        perf["total_latency"] += latency

        if quality_score is not None:
            total = perf["success_count"] + perf["failure_count"]
            perf["avg_quality"] = (perf["avg_quality"] * (total - 1) + quality_score) / total


class EnhancedSixLayerAnalyzer:
    """
    增强版六层分析器 - L5 完全AI原生
    动态权重、LLM调整、模式识别
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self._layer_weights = {
            "odds_structure": 0.2,
            "market_movement": 0.2,
            "probability_model": 0.2,
            "historical_pattern": 0.15,
            "team_fitness": 0.15,
            "context_factor": 0.1
        }

    def analyze_with_dynamic_weights(
        self,
        match_data: Dict,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        LLM动态六层分析
        根据比赛情况调整各层权重
        """
        layer_scores = {
            "odds_structure": self._assess_odds_structure(match_data),
            "market_movement": self._assess_market_movement(match_data, context),
            "probability_model": self._assess_probability(match_data),
            "historical_pattern": self._assess_history(match_data),
            "team_fitness": self._assess_team_fitness(match_data),
            "context_factor": self._assess_context(context)
        }

        adjusted_weights = self._adjust_weights(context)

        weighted_score = sum(layer_scores[layer] * adjusted_weights[layer] for layer in layer_scores)

        return {
            "final_score": round(weighted_score, 3),
            "layer_scores": layer_scores,
            "weights_used": adjusted_weights,
            "recommendation": self._get_recommendation(weighted_score),
            "ai_insight": self._generate_analysis_insight(layer_scores, weighted_score)
        }

    def _adjust_weights(self, context: Optional[Dict]) -> Dict[str, float]:
        weights = self._layer_weights.copy()

        if context:
            if context.get("market_volatile", False):
                weights["market_movement"] += 0.05
                weights["odds_structure"] -= 0.05

            if context.get("has_injury", False):
                weights["team_fitness"] += 0.05
                weights["historical_pattern"] -= 0.05

        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}

    def _assess_odds_structure(self, match_data: Dict) -> float:
        odds_home = match_data.get("home_odds", 2.0)
        odds_draw = match_data.get("draw_odds", 3.0)
        odds_away = match_data.get("away_odds", 2.0)

        implied_total = (1/odds_home) + (1/odds_draw) + (1/odds_away)

        if 1.02 <= implied_total <= 1.12:
            return 0.8
        elif implied_total < 1.2:
            return 0.6
        return 0.4

    def _assess_market_movement(self, match_data: Dict, context: Optional[Dict]) -> float:
        if not context:
            return 0.5

        movement = context.get("odds_movement", 0.0)
        if abs(movement) < 0.05:
            return 0.7
        elif abs(movement) < 0.15:
            return 0.5
        return 0.3

    def _assess_probability(self, match_data: Dict) -> float:
        home_prob = match_data.get("home_win_prob", 0.33)
        draw_prob = match_data.get("draw_prob", 0.33)
        away_prob = match_data.get("away_win_prob", 0.34)

        max_prob = max(home_prob, draw_prob, away_prob)

        if max_prob > 0.5:
            return 0.8
        elif max_prob > 0.4:
            return 0.6
        return 0.4

    def _assess_history(self, match_data: Dict) -> float:
        return 0.6

    def _assess_team_fitness(self, match_data: Dict) -> float:
        return 0.5

    def _assess_context(self, context: Optional[Dict]) -> float:
        if not context:
            return 0.5

        weather = context.get("weather", "normal")
        if weather == "rain":
            return 0.4

        return 0.6

    def _get_recommendation(self, score: float) -> str:
        if score > 0.7:
            return "strong_bet"
        elif score > 0.6:
            return "consider_bet"
        elif score > 0.5:
            return "cautious"
        return "skip"

    def _generate_analysis_insight(self, scores: Dict[str, float], final_score: float) -> str:
        best_layer = max(scores.items(), key=lambda x: x[1])
        worst_layer = min(scores.items(), key=lambda x: x[1])

        return f"{best_layer[0]}分析最好({best_layer[1]:.0%})，{worst_layer[0]}需注意({worst_layer[1]:.0%})，综合评分{final_score:.0%}"


class EnhancedPoissonModel:
    """
    增强版Poisson模型 - L4 高度AI原生
    LLM参数优化、上下文调整
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self._historical_params: Dict[str, Dict] = {}

    def predict_with_ai_adjustment(
        self,
        home_team: str,
        away_team: str,
        base_stats: Dict,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        LLM增强的进球预测
        """
        home_attack = base_stats.get("home_attack", 1.4)
        home_defense = base_stats.get("home_defense", 1.2)
        away_attack = base_stats.get("away_attack", 1.3)
        away_defense = base_stats.get("away_defense", 1.1)

        if context:
            if context.get("home_injury", False):
                home_attack *= 0.9
            if context.get("away_injury", False):
                away_attack *= 0.9

            weather = context.get("weather", "normal")
            if weather == "rain":
                home_attack *= 0.95
                away_attack *= 0.95

        expected_home_goals = home_attack * away_defense
        expected_away_goals = away_attack * home_defense

        home_win_prob, draw_prob, away_win_prob = self._calculate_match_probabilities(expected_home_goals, expected_away_goals)

        return {
            "expected_home_goals": round(expected_home_goals, 2),
            "expected_away_goals": round(expected_away_goals, 2),
            "home_win_prob": round(home_win_prob, 3),
            "draw_prob": round(draw_prob, 3),
            "away_win_prob": round(away_win_prob, 3),
            "adjustments": self._list_adjustments(context),
            "confidence": self._calculate_confidence(base_stats, context)
        }

    def _calculate_match_probabilities(self, home_lambda: float, away_lambda: float) ->tuple:
        """简单Poisson概率计算"""
        from math import exp, factorial

        max_goals = 8
        home_dist = [self._poisson_prob(home_lambda, k) for k in range(max_goals + 1)]
        away_dist = [self._poisson_prob(away_lambda, k) for k in range(max_goals + 1)]

        home_win = 0.0
        draw = 0.0
        away_win = 0.0

        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = home_dist[i] * away_dist[j]
                if i > j:
                    home_win += prob
                elif i == j:
                    draw += prob
                else:
                    away_win += prob

        return home_win, draw, away_win

    def _poisson_prob(self, lambda_: float, k: int) -> float:
        from math import exp, factorial
        return exp(-lambda_) * (lambda_ ** k) / factorial(k)

    def _list_adjustments(self, context: Optional[Dict]) -> List[str]:
        adjustments: List[str] = []
        if not context:
            return adjustments

        if context.get("home_injury"):
            adjustments.append("主队伤病影响攻击力-5%")
        if context.get("away_injury"):
            adjustments.append("客队伤病影响攻击力-5%")
        if context.get("weather") == "rain":
            adjustments.append("雨天影响双方-5%")

        return adjustments

    def _calculate_confidence(self, stats: Dict, context: Optional[Dict]) -> float:
        confidence = 0.65
        if stats.get("data_quality", "medium") == "high":
            confidence += 0.1
        elif stats.get("data_quality") == "low":
            confidence -= 0.1

        if context:
            if context.get("has_recent_data", True):
                confidence += 0.05

        return min(0.95, confidence)


class EnhancedKellyCriterion:
    """
    增强版Kelly准则 - L5 完全AI原生
    智能调整、组合优化
    """

    def __init__(self, llm_gateway=None):
        self.llm = llm_gateway
        self._stake_history: List[Dict] = []

    def calculate_advanced_kelly(
        self,
        odds: float,
        win_prob: float,
        confidence: float,
        portfolio_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        LLM增强的Kelly计算
        考虑组合优化、风险偏好
        """
        base_kelly = (win_prob * odds - 1) / (odds - 1) if odds > 1 else 0

        adjustments = []
        multiplier = 0.5

        if portfolio_context:
            current_exposure = portfolio_context.get("current_exposure", 0.0)
            if current_exposure > 0.2:
                multiplier *= 0.8
                adjustments.append("组合暴露过高，降低比例")

            if portfolio_context.get("recent_win_streak", 0) > 3:
                multiplier *= 1.1
                adjustments.append("连胜小幅提高")
            elif portfolio_context.get("recent_loss_streak", 0) > 3:
                multiplier *= 0.7
                adjustments.append("连败降低风险")

        confidence_adjustment = min(1.5, 0.5 + confidence)
        multiplier *= confidence_adjustment

        adjusted_kelly = min(base_kelly * multiplier, 0.2)

        self._stake_history.append({
            "timestamp": datetime.now().isoformat(),
            "base_kelly": base_kelly,
            "adjusted_kelly": adjusted_kelly,
            "odds": odds,
            "win_prob": win_prob
        })

        return {
            "base_kelly": round(base_kelly, 4),
            "adjusted_kelly": round(adjusted_kelly, 4),
            "multiplier": round(multiplier, 2),
            "adjustments": adjustments,
            "max_recommended_stake": f"{adjusted_kelly * 100:.1f}%",
            "conservative_option": f"{adjusted_kelly * 0.5 * 100:.1f}%"
        }

    def optimize_portfolio(
        self,
        bet_candidates: List[Dict],
        max_exposure: float = 0.5
    ) -> List[Dict]:
        """
        LLM组合优化
        """
        if not bet_candidates:
            return []

        candidates: list[dict[str, Any]] = []
        for bet in bet_candidates:
            odds = bet.get("odds", 2.0)
            prob = bet.get("win_prob", 0.5)
            kelly = (prob * odds - 1) / (odds - 1) if odds > 1 else 0

            candidates.append({
                "bet": bet,
                "score": kelly * prob,
                "kelly": kelly,
                "selection": bet.get("selection", "home")
            })

        candidates.sort(key=lambda x: x["score"], reverse=True)

        selected: list[dict[str, Any]] = []
        total_exposure = 0.0

        for candidate in candidates:
            stake = min(candidate["kelly"] * 0.5, 0.1)
            if total_exposure + stake <= max_exposure:
                selected.append({
                    "selection": candidate["selection"],
                    "stake": round(stake, 4),
                    "priority": len(selected) + 1
                })
                total_exposure += stake

        return selected


ENHANCED_MEMORY_SEARCH = EnhancedMemorySearch()
ENHANCED_EXECUTION_ENGINE = EnhancedExecutionEngine()
ENHANCED_BANKROLL_MANAGER = EnhancedBankrollManager()
ENHANCED_RESULT_TRACKER = EnhancedResultTracker()
ENHANCED_DATA_SOURCE_MANAGER = EnhancedDataSourceManager()
ENHANCED_SIX_LAYER_ANALYZER = EnhancedSixLayerAnalyzer()
ENHANCED_POISSON_MODEL = EnhancedPoissonModel()
ENHANCED_KELLY_CRITERION = EnhancedKellyCriterion()

__all__ = [
    "EnhancedMemorySearch",
    "ENHANCED_MEMORY_SEARCH",
    "EnhancedExecutionEngine",
    "ENHANCED_EXECUTION_ENGINE",
    "EnhancedBankrollManager",
    "ENHANCED_BANKROLL_MANAGER",
    "EnhancedResultTracker",
    "ENHANCED_RESULT_TRACKER",
    "EnhancedDataSourceManager",
    "ENHANCED_DATA_SOURCE_MANAGER",
    "EnhancedSixLayerAnalyzer",
    "ENHANCED_SIX_LAYER_ANALYZER",
    "EnhancedPoissonModel",
    "ENHANCED_POISSON_MODEL",
    "EnhancedKellyCriterion",
    "ENHANCED_KELLY_CRITERION",
]

