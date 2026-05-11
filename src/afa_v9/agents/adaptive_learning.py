"""
AFA v9.0 自适应学习回路 - 实时反馈与参数优化
=====================================================

功能：
1. 投注结果反馈记录
2. 参数动态调整
3. 自我评估与优化
4. 学习历史追踪
5. 性能趋势分析
"""

import logging
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class BetResult:
    """投注结果记录"""
    bet_id: str
    match_id: str
    home_team: str
    away_team: str
    league: str
    bet_type: str
    odds: float
    stake: float
    actual_result: str
    profit: float
    roi: float
    timestamp: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParameterAdjustment:
    """参数调整记录"""
    parameter_name: str
    old_value: float
    new_value: float
    reason: str
    timestamp: str


@dataclass
class LearningInsight:
    """学习洞察"""
    insight_id: str
    category: str
    content: str
    confidence: float
    actionable: bool
    recommendation: str
    timestamp: str


class AdaptiveLearningLoop:
    """
    自适应学习回路
    
    核心功能：
    - 结果反馈：记录投注结果
    - 参数调整：根据表现动态调整
    - 学习洞察：提取模式和经验
    - 趋势分析：分析性能趋势
    - 自我优化：自动优化系统
    """

    def __init__(self):
        self.bet_results: List[BetResult] = []
        self.parameter_history: List[ParameterAdjustment] = []
        self.insights: List[LearningInsight] = []
        
        # 当前参数
        self.current_parameters = {
            "kelly_multiplier": 1.0,
            "confidence_threshold": 0.6,
            "max_exposure": 0.25,
            "min_odds_value": 1.5,
            "risk_tolerance": "medium",
        }
        
        # 统计数据
        self.stats = {
            "total_bets": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "total_profit": 0.0,
            "total_stakes": 0.0,
            "average_odds": 0.0,
        }
        
        # 数据目录
        self._data_dir = Path(__file__).parent.parent.parent.parent / "data" / "adaptive"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载历史数据
        self._load_history()
        
        logger.info("🧠 自适应学习回路初始化完成")

    def _load_history(self) -> None:
        """加载历史数据"""
        try:
            results_file = self._data_dir / "bet_results.json"
            if results_file.exists():
                with open(results_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.bet_results = [BetResult(**item) for item in data]
                logger.info(f"📊 加载了 {len(self.bet_results)} 条历史投注记录")
            
            params_file = self._data_dir / "parameters.json"
            if params_file.exists():
                with open(params_file, "r", encoding="utf-8") as f:
                    saved_params = json.load(f)
                    self.current_parameters.update(saved_params)
            
            self._update_stats()
        except Exception as e:
            logger.warning(f"加载历史数据失败: {e}")

    def _save_history(self) -> None:
        """保存历史数据"""
        try:
            results_file = self._data_dir / "bet_results.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump([
                    {
                        "bet_id": r.bet_id,
                        "match_id": r.match_id,
                        "home_team": r.home_team,
                        "away_team": r.away_team,
                        "league": r.league,
                        "bet_type": r.bet_type,
                        "odds": r.odds,
                        "stake": r.stake,
                        "actual_result": r.actual_result,
                        "profit": r.profit,
                        "roi": r.roi,
                        "timestamp": r.timestamp,
                        "context": r.context,
                    }
                    for r in self.bet_results
                ], f, indent=2, ensure_ascii=False)
            
            params_file = self._data_dir / "parameters.json"
            with open(params_file, "w", encoding="utf-8") as f:
                json.dump(self.current_parameters, f, indent=2)
        except Exception as e:
            logger.warning(f"保存历史数据失败: {e}")

    def _update_stats(self) -> None:
        """更新统计数据"""
        if not self.bet_results:
            return
        
        self.stats["total_bets"] = len(self.bet_results)
        self.stats["wins"] = sum(1 for r in self.bet_results if r.profit > 0)
        self.stats["losses"] = sum(1 for r in self.bet_results if r.profit < 0)
        self.stats["draws"] = sum(1 for r in self.bet_results if r.profit == 0)
        self.stats["total_profit"] = sum(r.profit for r in self.bet_results)
        self.stats["total_stakes"] = sum(r.stake for r in self.bet_results)
        
        if self.bet_results:
            self.stats["average_odds"] = sum(r.odds for r in self.bet_results) / len(self.bet_results)
        
        win_rate = self.stats["wins"] / self.stats["total_bets"] if self.stats["total_bets"] > 0 else 0
        self.stats["win_rate"] = win_rate
        
        if self.stats["total_stakes"] > 0:
            self.stats["overall_roi"] = (self.stats["total_profit"] / self.stats["total_stakes"]) * 100

    def record_bet_result(
        self,
        bet_id: str,
        match_id: str,
        home_team: str,
        away_team: str,
        league: str,
        bet_type: str,
        odds: float,
        stake: float,
        actual_result: str,
        profit: float,
        context: Optional[Dict] = None,
    ) -> BetResult:
        """
        记录投注结果
        
        Args:
            bet_id: 投注ID
            match_id: 比赛ID
            home_team: 主队
            away_team: 客队
            league: 联赛
            bet_type: 投注类型
            odds: 赔率
            stake: 投注金额
            actual_result: 实际结果
            profit: 盈亏
            context: 上下文信息
        """
        roi = (profit / stake) * 100 if stake > 0 else 0
        
        result = BetResult(
            bet_id=bet_id,
            match_id=match_id,
            home_team=home_team,
            away_team=away_team,
            league=league,
            bet_type=bet_type,
            odds=odds,
            stake=stake,
            actual_result=actual_result,
            profit=profit,
            roi=roi,
            timestamp=datetime.now().isoformat(),
            context=context or {},
        )
        
        self.bet_results.append(result)
        self._update_stats()
        self._save_history()
        
        logger.info(
            f"📝 记录投注结果: {home_team} vs {away_team} "
            f"- {'✅ 赢' if profit > 0 else '❌ 输' if profit < 0 else '🤝 平'} "
            f"{profit:.2f}元 (ROI: {roi:.1f}%)"
        )
        
        # 触发自动学习
        self._analyze_and_learn(result)
        
        return result

    def _analyze_and_learn(self, new_result: BetResult) -> None:
        """分析结果并学习"""
        # 生成洞察
        self._generate_insights(new_result)
        
        # 检查是否需要调整参数
        if len(self.bet_results) % 10 == 0:  # 每10次投注检查一次
            self._check_and_adjust_parameters()

    def _generate_insights(self, new_result: BetResult) -> List[LearningInsight]:
        """从结果中生成学习洞察"""
        insights = []
        
        # 基础洞察
        if new_result.profit > 0:
            insights.append(LearningInsight(
                insight_id=f"win_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category="success",
                content=f"在{new_result.league}联赛投注{new_result.bet_type}成功",
                confidence=0.7,
                actionable=True,
                recommendation="继续关注该联赛的类似投注",
                timestamp=datetime.now().isoformat(),
            ))
        elif new_result.profit < 0:
            insights.append(LearningInsight(
                insight_id=f"loss_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category="loss",
                content=f"在{new_result.league}联赛投注{new_result.bet_type}失败",
                confidence=0.6,
                actionable=True,
                recommendation="分析失败原因，可能需要调整策略",
                timestamp=datetime.now().isoformat(),
            ))
        
        self.insights.extend(insights)
        return insights

    def _check_and_adjust_parameters(self) -> List[ParameterAdjustment]:
        """检查并调整参数"""
        adjustments = []
        
        if len(self.bet_results) < 10:
            return adjustments
        
        recent_results = self.bet_results[-20:]
        recent_roi = sum(r.roi for r in recent_results) / len(recent_results)
        recent_win_rate = sum(1 for r in recent_results if r.profit > 0) / len(recent_results)
        
        # 基于表现调整Kelly倍数
        if recent_roi > 10 and recent_win_rate > 0.55:
            # 表现良好，略微提高风险
            old_value = self.current_parameters["kelly_multiplier"]
            new_value = min(old_value * 1.1, 1.5)
            self.current_parameters["kelly_multiplier"] = new_value
            
            adjustments.append(ParameterAdjustment(
                parameter_name="kelly_multiplier",
                old_value=old_value,
                new_value=new_value,
                reason="近期表现良好，适度提高风险偏好",
                timestamp=datetime.now().isoformat(),
            ))
            logger.info(f"⚙️ 参数调整: Kelly倍数 {old_value:.2f} → {new_value:.2f}")
        
        elif recent_roi < -5:
            # 表现不佳，降低风险
            old_value = self.current_parameters["kelly_multiplier"]
            new_value = max(old_value * 0.8, 0.3)
            self.current_parameters["kelly_multiplier"] = new_value
            
            adjustments.append(ParameterAdjustment(
                parameter_name="kelly_multiplier",
                old_value=old_value,
                new_value=new_value,
                reason="近期表现不佳，降低风险偏好",
                timestamp=datetime.now().isoformat(),
            ))
            logger.info(f"⚙️ 参数调整: Kelly倍数 {old_value:.2f} → {new_value:.2f}")
        
        # 保存调整
        if adjustments:
            self.parameter_history.extend(adjustments)
            self._save_history()
        
        return adjustments

    def self_assessment(self) -> Dict[str, Any]:
        """
        自我评估
        
        Returns:
            评估报告
        """
        if len(self.bet_results) < 10:
            return {
                "status": "insufficient_data",
                "message": "投注记录不足，无法进行有效评估",
            }
        
        win_rate = self.stats.get("win_rate", 0)
        overall_roi = self.stats.get("overall_roi", 0)
        
        if win_rate > 0.55 and overall_roi > 5:
            assessment = "excellent"
        elif win_rate > 0.48 and overall_roi > 0:
            assessment = "good"
        elif win_rate > 0.45:
            assessment = "fair"
        else:
            assessment = "needs_improvement"
        
        return {
            "status": "ready",
            "overall_assessment": assessment,
            "win_rate": win_rate * 100,
            "overall_roi": overall_roi,
            "total_bets": len(self.bet_results),
            "total_profit": self.stats.get("total_profit", 0),
            "current_parameters": self.current_parameters.copy(),
            "recommendations": self._get_recommendations(assessment),
        }

    def _get_recommendations(self, assessment: str) -> List[str]:
        """根据评估获取改进建议"""
        recommendations = []
        
        if assessment == "excellent":
            recommendations.append("当前表现优秀，继续保持当前策略")
            recommendations.append("可以考虑适度增加投注规模")
        elif assessment == "good":
            recommendations.append("表现良好，建议保持当前风险水平")
            recommendations.append("分析获胜投注的共同模式")
        elif assessment == "fair":
            recommendations.append("建议降低风险偏好")
            recommendations.append("只选择高信心的投注机会")
        else:
            recommendations.append("暂停投注，回顾分析历史数据")
            recommendations.append("考虑调整策略参数")
        
        return recommendations

    def get_learning_report(self) -> Dict[str, Any]:
        """获取学习报告"""
        return {
            "overview": {
                "total_bets": self.stats["total_bets"],
                "win_rate": self.stats.get("win_rate", 0) * 100,
                "total_profit": self.stats["total_profit"],
                "overall_roi": self.stats.get("overall_roi", 0),
            },
            "trending": self._analyze_trends(),
            "insights_count": len(self.insights),
            "parameter_adjustments": len(self.parameter_history),
            "self_assessment": self.self_assessment(),
        }

    def _analyze_trends(self) -> Dict[str, Any]:
        """分析趋势"""
        if len(self.bet_results) < 20:
            return {"status": "insufficient_data"}
        
        recent = self.bet_results[-20:]
        older = self.bet_results[-40:-20] if len(self.bet_results) >= 40 else []
        
        recent_roi = sum(r.roi for r in recent) / len(recent)
        older_roi = sum(r.roi for r in older) / len(older) if older else 0
        
        return {
            "recent_roi": recent_roi,
            "previous_roi": older_roi,
            "trend": "improving" if recent_roi > older_roi else "declining" if recent_roi < older_roi else "stable",
        }

    def reset_learning(self) -> None:
        """重置学习状态"""
        self.bet_results = []
        self.parameter_history = []
        self.insights = []
        self.current_parameters = {
            "kelly_multiplier": 1.0,
            "confidence_threshold": 0.6,
            "max_exposure": 0.25,
            "min_odds_value": 1.5,
            "risk_tolerance": "medium",
        }
        self._update_stats()
        self._save_history()
        logger.info("🧹 学习状态已重置")


# 全局单例
ADAPTIVE_LEARNING = AdaptiveLearningLoop()
