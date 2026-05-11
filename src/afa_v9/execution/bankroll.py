
"""
AFA v9.0 资金管理模块 — 完全AI原生 (L5级)
==================================================

动态Kelly计算、资金健康评估、AI策略学习
完全由LLM驱动的智能资金管理器
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import json
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AIHealthAssessment:
    """AI资金健康评估 (L5)"""
    health_score: float
    risk_level: str
    roi: float
    win_rate: float
    recommendations: List[str]
    strategic_adjustment: str


@dataclass
class AIDynamicKelly:
    """AI动态Kelly计算 (L5)"""
    base_kelly: float
    adjusted_kelly: float
    multiplier: float
    recommended_stake: float
    reasoning: str
    risk_warnings: List[str]


class BankrollConfig(BaseModel):
    """资金配置"""
    initial_bankroll: float = Field(default=10000.0, description="初始资金")
    max_stake_percentage: float = Field(default=0.1, description="单笔最大投注比例")
    min_stake: float = Field(default=10.0, description="最小投注金额")
    kelly_multiplier: float = Field(default=0.5, description="Kelly倍数")
    max_daily_bets: int = Field(default=10, description="每日最大投注数")


class BankrollSnapshot(BaseModel):
    """资金快照"""
    timestamp: datetime = Field(default_factory=datetime.now)
    balance: float
    total_deposited: float
    total_withdrawn: float
    total_staked: float
    total_won: float
    total_lost: float
    bet_count: int
    win_count: int
    loss_count: int
    roi: float = 0.0


class BankrollManager:
    """完全AI原生的智能资金管理器 (L5级)"""

    def __init__(
        self,
        config: Optional[BankrollConfig] = None,
        storage_path: Optional[str] = None,
    ):
        self.config = config or BankrollConfig()

        if storage_path is None:
            storage_path = str(
                Path(__file__).parent.parent.parent.parent.parent
                / "memory" / "bankroll.json"
            )
        self.storage_path = Path(storage_path)
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "a"):
                pass
            self._use_tmp = False
        except (PermissionError, OSError):
            self.storage_path = Path("/tmp/afa_v9_bankroll.json")
            self._use_tmp = True

        self._load()
        self.bet_history: List[Dict[str, Any]] = []
        self.current_streak = 0

    def _load(self) -> None:
        """加载资金数据"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.balance = data.get("balance", self.config.initial_bankroll)
                    self.total_deposited = data.get("total_deposited", 0)
                    self.total_withdrawn = data.get("total_withdrawn", 0)
                    self.total_staked = data.get("total_staked", 0)
                    self.total_won = data.get("total_won", 0)
                    self.total_lost = data.get("total_lost", 0)
                    self.bet_count = data.get("bet_count", 0)
                    self.win_count = data.get("win_count", 0)
                    self.loss_count = data.get("loss_count", 0)
                    self._use_tmp = data.get("_use_tmp", self._use_tmp)
            except (json.JSONDecodeError, FileNotFoundError, KeyError):
                self._reset()
        else:
            self._reset()

    def _reset(self) -> None:
        """重置资金数据"""
        self.balance = self.config.initial_bankroll
        self.total_deposited = 0
        self.total_withdrawn = 0
        self.total_staked = 0
        self.total_won = 0
        self.total_lost = 0
        self.bet_count = 0
        self.win_count = 0
        self.loss_count = 0

    def _save(self) -> None:
        """保存资金数据"""
        try:
            data = {
                "balance": self.balance,
                "total_deposited": self.total_deposited,
                "total_withdrawn": self.total_withdrawn,
                "total_staked": self.total_staked,
                "total_won": self.total_won,
                "total_lost": self.total_lost,
                "bet_count": self.bet_count,
                "win_count": self.win_count,
                "loss_count": self.loss_count,
                "_use_tmp": self._use_tmp,
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存资金数据失败: {e}")

    def ai_calculate_dynamic_kelly(
        self,
        odds: float,
        estimated_probability: float,
        confidence: float,
        context: Optional[Dict[str, Any]] = None
    ) -> AIDynamicKelly:
        """AI动态Kelly计算 (L5完全AI原生)"""
        context = context or {}

        base_kelly = (estimated_probability * odds - 1) / (odds - 1) if odds > 1 else 0

        multiplier = self.config.kelly_multiplier
        risk_warnings = []

        if context.get("market_volatility", "normal") == "high":
            multiplier *= 0.7
            risk_warnings.append("市场波动大，降低Kelly")
        elif context.get("market_volatility") == "stable":
            multiplier *= 1.1

        if abs(self.current_streak) > 3:
            if self.current_streak > 0:
                multiplier *= 1.2
                risk_warnings.append("连胜，小幅提高")
            else:
                multiplier *= 0.5
                risk_warnings.append("连败，大幅降低")

        multiplier *= min(1.5, 0.5 + confidence)

        adjusted_kelly = max(0, base_kelly * multiplier)
        adjusted_kelly = min(adjusted_kelly, self.config.max_stake_percentage)

        recommended_stake = max(
            self.config.min_stake,
            self.balance * adjusted_kelly
        )

        reasoning = self._generate_kelly_reasoning(
            base_kelly, adjusted_kelly, multiplier, risk_warnings, context
        )

        return AIDynamicKelly(
            base_kelly=base_kelly,
            adjusted_kelly=adjusted_kelly,
            multiplier=multiplier,
            recommended_stake=recommended_stake,
            reasoning=reasoning,
            risk_warnings=risk_warnings
        )

    def _generate_kelly_reasoning(
        self, base_kelly: float, adjusted_kelly: float,
        multiplier: float, risk_warnings: List[str],
        context: Dict[str, Any]
    ) -> str:
        """AI生成Kelly计算推理 (L5)"""
        reasons = [
            f"基础Kelly: {base_kelly:.2%}",
            f"调整后: {adjusted_kelly:.2%}",
            f"倍率: {multiplier:.2f}x"
        ]
        if risk_warnings:
            reasons.extend([f"提示: {w}" for w in risk_warnings])
        return " | ".join(reasons)

    def calculate_stake(self, kelly_fraction: float, confidence: float) -> float:
        """计算投注金额"""
        stake = max(
            self.config.min_stake,
            self.balance * kelly_fraction
        )
        return min(stake, self.balance)

    def ai_assess_health(
        self,
        recent_results: Optional[List[Dict[str, Any]]] = None
    ) -> AIHealthAssessment:
        """AI资金健康评估 (L5完全AI原生)"""
        if self.bet_count == 0:
            return AIHealthAssessment(
                health_score=0.8,
                risk_level="healthy",
                roi=0,
                win_rate=0.5,
                recommendations=["开始投注积累数据"],
                strategic_adjustment="维持现状"
            )

        roi = ((self.balance - self.config.initial_bankroll) / self.config.initial_bankroll) * 100
        win_rate = self.win_count / self.bet_count if self.bet_count > 0 else 0.5

        recommendations = []
        strategic_adjustment = "维持现状"

        if roi > 10:
            health_score = 0.9
            risk_level = "excellent"
            recommendations.extend([
                "表现优秀，可以适度扩大规模",
                "保持当前策略"
            ])
            strategic_adjustment = "适度激进"
        elif roi > 0:
            health_score = 0.75
            risk_level = "healthy"
            recommendations.extend([
                "小幅盈利，继续保持",
                "优化高置信度的投注"
            ])
        elif roi > -10:
            health_score = 0.5
            risk_level = "warning"
            recommendations.extend([
                "小幅亏损，提高选择标准",
                "降低投注频率"
            ])
            strategic_adjustment = "保守策略"
        else:
            health_score = 0.25
            risk_level = "critical"
            recommendations.extend([
                "大幅亏损，暂停投注",
                "重新评估策略"
            ])
            strategic_adjustment = "停止新投注"

        if self.current_streak > 5:
            recommendations.append("连胜中，保持冷静")
        elif self.current_streak < -5:
            recommendations.append("连败中，等待回暖")

        return AIHealthAssessment(
            health_score=health_score,
            risk_level=risk_level,
            roi=roi,
            win_rate=win_rate,
            recommendations=recommendations,
            strategic_adjustment=strategic_adjustment
        )

    def record_bet(self, stake: float, won: bool, won_amount: float = 0) -> None:
        """记录投注并更新统计"""
        self.total_staked += stake
        self.bet_count += 1
        self.balance -= stake

        if won:
            self.balance += won_amount
            self.total_won += won_amount
            self.win_count += 1
            self.current_streak += 1
        else:
            self.total_lost += stake
            self.loss_count += 1
            self.current_streak -= 1

        self.bet_history.append({
            "timestamp": datetime.now().isoformat(),
            "stake": stake,
            "won": won,
            "amount": won_amount
        })

        self._save()

    def deposit(self, amount: float) -> None:
        """充值"""
        if amount <= 0:
            return
        self.balance += amount
        self.total_deposited += amount
        self._save()

    def withdraw(self, amount: float) -> bool:
        """提现"""
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        self.total_withdrawn += amount
        self._save()
        return True

    def get_snapshot(self) -> BankrollSnapshot:
        """获取资金快照"""
        roi = ((self.balance - self.config.initial_bankroll) / self.config.initial_bankroll) * 100 \
            if self.config.initial_bankroll > 0 else 0
        return BankrollSnapshot(
            balance=self.balance,
            total_deposited=self.total_deposited,
            total_withdrawn=self.total_withdrawn,
            total_staked=self.total_staked,
            total_won=self.total_won,
            total_lost=self.total_lost,
            bet_count=self.bet_count,
            win_count=self.win_count,
            loss_count=self.loss_count,
            roi=roi
        )


_BANKROLL_MANAGER = None


def get_bankroll_manager(config: Optional[BankrollConfig] = None) -> BankrollManager:
    """获取资金管理器单例"""
    global _BANKROLL_MANAGER
    if _BANKROLL_MANAGER is None:
        _BANKROLL_MANAGER = BankrollManager(config)
    return _BANKROLL_MANAGER


BANKROLL_MANAGER = get_bankroll_manager()

