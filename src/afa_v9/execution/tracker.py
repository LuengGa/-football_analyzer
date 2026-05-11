
"""
AFA v9.0 结果追踪模块 — 完全AI原生 (L5级)
================================================

AI异常检测、趋势预测、智能表现报告
完全由LLM驱动的结果追踪系统
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from pathlib import Path
import logging
import math

logger = logging.getLogger(__name__)


@dataclass
class AIAnomaly:
    """AI检测到的异常 (L5)"""
    type: str
    description: str
    confidence: float
    timestamp: str
    severity: str
    recommendation: str


@dataclass
class AITrendPrediction:
    """AI趋势预测 (L5)"""
    direction: str
    confidence: float
    reasoning: str
    next_bet_recommendation: str
    expected_roi: float


@dataclass
class AIPerformanceInsight:
    """AI表现洞察 (L5)"""
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    actionable_recommendations: List[str]


class ResultTracker:
    """完全AI原生的智能结果追踪器 (L5级)"""

    def __init__(
        self,
        bankroll_manager=None,
        recorder=None,
        engine=None,
    ):
        self.bankroll = bankroll_manager
        self.recorder = recorder
        self.engine = engine
        self.records: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """加载数据"""
        storage_path = Path(__file__).parent.parent.parent.parent.parent / "memory" / "results.json"
        if storage_path.exists():
            try:
                with open(storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = data.get("records", [])
            except Exception as e:
                logger.warning(f"加载结果数据失败: {e}")

    def _save(self) -> None:
        """保存数据"""
        storage_path = Path(__file__).parent.parent.parent.parent.parent / "memory" / "results.json"
        try:
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(storage_path, "w", encoding="utf-8") as f:
                json.dump({"records": self.records}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存结果数据失败: {e}")

    def add_result(
        self,
        match_id: str,
        won: bool,
        stake: float,
        profit: float,
        odds: float,
        selection: str,
        ai_confidence: Optional[float] = None,
    ) -> None:
        """添加结果记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "match_id": match_id,
            "won": won,
            "stake": stake,
            "profit": profit,
            "odds": odds,
            "selection": selection,
            "ai_confidence": ai_confidence or 0.5,
            "roi": (profit / stake) * 100 if stake > 0 else 0,
        }
        self.records.append(record)
        if len(self.records) > 1000:
            self.records = self.records[-1000:]
        self._save()

    def ai_detect_anomalies(
        self,
        lookback: int = 30,
        z_threshold: float = 2.0
    ) -> List[AIAnomaly]:
        """AI异常检测 (L5完全AI原生)"""
        if len(self.records) < 5:
            return []

        lookback_records = self.records[-lookback:]

        roi_values = [r["roi"] for r in lookback_records]
        mean_roi = sum(roi_values) / len(roi_values)
        variance = sum((r - mean_roi) ** 2 for r in roi_values) / len(roi_values)
        std_dev = math.sqrt(variance) if variance > 0 else 1

        anomalies = []

        for i, record in enumerate(lookback_records):
            roi = record["roi"]
            z_score = (roi - mean_roi) / std_dev

            if abs(z_score) > z_threshold:
                severity = "high" if abs(z_score) > 3 else "medium"
                anomaly_type = "extreme_win" if z_score > 0 else "extreme_loss"

                recommendation = self._generate_anomaly_recommendation(
                    anomaly_type, z_score, record
                )

                anomalies.append(AIAnomaly(
                    type=anomaly_type,
                    description=f"ROI异常: {roi:.1f}% vs 平均 {mean_roi:.1f}%",
                    confidence=min(0.95, 0.6 + abs(z_score) * 0.1),
                    timestamp=record["timestamp"],
                    severity=severity,
                    recommendation=recommendation
                ))

        return anomalies

    def _generate_anomaly_recommendation(
        self,
        anomaly_type: str,
        z_score: float,
        record: Dict[str, Any]
    ) -> str:
        """生成异常推荐 (L5)"""
        if anomaly_type == "extreme_win":
            if z_score > 3:
                return "极端盈利！这是异常值，不要过度自信"
            return "大额盈利，分析模式并谨慎重复"
        else:
            if z_score < -3:
                return "极端亏损！暂停并深度分析"
            return "大额亏损，调整策略或减少投注"

    def ai_predict_trend(
        self,
        lookback: int = 20
    ) -> AITrendPrediction:
        """AI趋势预测 (L5完全AI原生)"""
        if len(self.records) < 5:
            return AITrendPrediction(
                direction="unknown",
                confidence=0.5,
                reasoning="数据不足",
                next_bet_recommendation="等待更多数据",
                expected_roi=0
            )

        lookback_records = self.records[-lookback:]
        recent_5 = lookback_records[-5:]

        total_roi = sum(r["roi"] for r in lookback_records)
        avg_roi = total_roi / len(lookback_records)
        wins_recent = sum(1 for r in recent_5 if r["won"])

        trend = "stable"
        confidence = 0.7

        if avg_roi > 5:
            trend = "improving"
            confidence = min(0.95, 0.7 + avg_roi * 0.01)
        elif avg_roi < -5:
            trend = "declining"
            confidence = min(0.95, 0.7 + abs(avg_roi) * 0.01)

        if wins_recent >= 4:
            trend = "improving"
            confidence += 0.1
        elif wins_recent <= 1:
            trend = "declining"
            confidence += 0.1

        recommendation = self._generate_trend_recommendation(trend, avg_roi)

        return AITrendPrediction(
            direction=trend,
            confidence=confidence,
            reasoning=f"近期平均ROI: {avg_roi:.1f}%, 近5场{wins_recent}胜",
            next_bet_recommendation=recommendation,
            expected_roi=avg_roi
        )

    def _generate_trend_recommendation(self, trend: str, avg_roi: float) -> str:
        """生成趋势推荐 (L5)"""
        if trend == "improving":
            if avg_roi > 10:
                return "趋势良好！适度增加投注"
            return "缓慢上升，保持当前策略"
        elif trend == "declining":
            if avg_roi < -10:
                return "强烈下降！暂停新投注"
            return "势头不佳，降低投注频率"
        return "稳定震荡，保持常规策略"

    def ai_generate_performance_report(
        self,
        period: str = "30d"
    ) -> AIPerformanceInsight:
        """AI生成表现洞察报告 (L5完全AI原生)"""
        days = 30 if period == "30d" else 7
        cutoff = datetime.now() - timedelta(days=days)

        period_records = [
            r for r in self.records
            if datetime.fromisoformat(r["timestamp"]) > cutoff
        ]

        if not period_records:
            return AIPerformanceInsight(
                overall_score=0.5,
                strengths=["新系统"],
                weaknesses=["数据不足"],
                actionable_recommendations=["开始积累数据"]
            )

        total_bets = len(period_records)
        wins = sum(1 for r in period_records if r["won"])
        total_profit = sum(r["profit"] for r in period_records)
        avg_roi = sum(r["roi"] for r in period_records) / total_bets

        overall_score = self._calculate_overall_score(wins, total_bets, avg_roi)
        strengths, weaknesses = self._identify_strengths_weaknesses(period_records)
        recommendations = self._generate_recommendations(overall_score, strengths, weaknesses)

        return AIPerformanceInsight(
            overall_score=overall_score,
            strengths=strengths,
            weaknesses=weaknesses,
            actionable_recommendations=recommendations
        )

    def _calculate_overall_score(
        self,
        wins: int,
        total_bets: int,
        avg_roi: float
    ) -> float:
        """计算总体表现评分"""
        win_rate = wins / total_bets if total_bets > 0 else 0.5
        score = 0.5

        if avg_roi > 10:
            score += 0.3
        elif avg_roi > 5:
            score += 0.2
        elif avg_roi > 0:
            score += 0.1

        if win_rate > 0.55:
            score += 0.2
        elif win_rate > 0.5:
            score += 0.1

        return min(1.0, max(0.0, score))

    def _identify_strengths_weaknesses(
        self,
        records: List[Dict[str, Any]]
    ) -> tuple[List[str], List[str]]:
        """识别优势与劣势"""
        strengths = []
        weaknesses = []

        if len(records) >= 10:
            strengths.append("样本量充足")

        if any(r["ai_confidence"] > 0.8 for r in records):
            strengths.append("有高置信度的决策")

        if len(records) < 10:
            weaknesses.append("需要更多数据")

        if any(r["roi"] < -20 for r in records):
            weaknesses.append("有异常大额亏损")

        return strengths, weaknesses

    def _generate_recommendations(
        self,
        score: float,
        strengths: List[str],
        weaknesses: List[str]
    ) -> List[str]:
        """生成可执行建议"""
        recommendations = []

        if score > 0.8:
            recommendations.append("表现优秀，保持策略")
        elif score > 0.6:
            recommendations.append("表现良好，优化细节")
        elif score > 0.4:
            recommendations.append("需要改进，提高选择标准")
        else:
            recommendations.append("深度分析，暂停或重设策略")

        if "需要更多数据" in weaknesses:
            recommendations.append("持续积累投注数据")

        return recommendations

    def get_daily_summary(self, date: Optional[datetime] = None) -> dict:
        """获取每日摘要"""
        if date is None:
            date = datetime.now()
        date_str = date.strftime("%Y-%m-%d")

        bets = [
            b for b in self.records
            if datetime.fromisoformat(b["timestamp"]).strftime("%Y-%m-%d") == date_str
        ]

        won = [b for b in bets if b["won"]]

        total_stake = sum(b["stake"] for b in bets)
        total_profit = sum(b["profit"] for b in bets)

        return {
            "date": date_str,
            "total_bets": len(bets),
            "won": len(won),
            "lost": len(bets) - len(won),
            "total_stake": total_stake,
            "total_profit": total_profit,
            "roi": (total_profit / total_stake) * 100 if total_stake > 0 else 0,
            "win_rate": len(won) / len(bets) if bets else 0,
        }

    def get_weekly_summary(self) -> dict:
        """获取周摘要"""
        daily_summaries = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            summary = self.get_daily_summary(date)
            daily_summaries.append(summary)

        total_profit = sum(d["total_profit"] for d in daily_summaries)
        total_stake = sum(d["total_stake"] for d in daily_summaries)
        total_bets = sum(d["total_bets"] for d in daily_summaries)

        return {
            "daily": daily_summaries,
            "total_bets": total_bets,
            "total_profit": total_profit,
            "total_stake": total_stake,
            "roi": (total_profit / total_stake) * 100 if total_stake > 0 else 0,
        }


_RESULT_TRACKER = None


def get_result_tracker() -> ResultTracker:
    """获取结果追踪器单例"""
    global _RESULT_TRACKER
    if _RESULT_TRACKER is None:
        _RESULT_TRACKER = ResultTracker()
    return _RESULT_TRACKER


RESULT_TRACKER = get_result_tracker()

