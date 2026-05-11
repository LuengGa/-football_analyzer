"""
AFA v9.0 交易记录模块

记录所有投注交易、追踪历史、分析绩效
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import json
from pathlib import Path


class BetStatus(str, Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    VOID = "void"
    CANCELLED = "cancelled"


class BetRecord(BaseModel):
    """投注记录"""
    bet_id: str
    match_id: str
    home_team: str
    away_team: str
    market: str
    selection: str
    odds: float
    stake: float
    kelly_fraction: float
    confidence: float
    status: BetStatus = BetStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    settled_at: Optional[datetime] = None
    profit: float = 0.0
    notes: str = ""

    def settle(self, won: bool, profit: float = 0) -> None:
        """结算投注"""
        self.status = BetStatus.WON if won else BetStatus.LOST
        self.settled_at = datetime.now()
        self.profit = profit if won else -self.stake


class BetRecorder:
    """交易记录器"""

    def __init__(self, storage_path: Optional[str] = None):
        if storage_path is None:
            storage_path = str(
                Path(__file__).parent.parent.parent.parent.parent
                / "memory" / "bet_records.json"
            )
        self.storage_path = Path(storage_path)
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "a"):
                pass
            self._use_tmp = False
        except (PermissionError, OSError):
            self.storage_path = Path("/tmp/afa_v9_bet_records.json")
            self._use_tmp = True
        
        self.records: List[BetRecord] = []
        self._load()

    def _load(self) -> None:
        """加载记录"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for rec in data.get("records", []):
                        rec["created_at"] = datetime.fromisoformat(rec["created_at"])
                        if rec.get("settled_at"):
                            rec["settled_at"] = datetime.fromisoformat(rec["settled_at"])
                        self.records.append(BetRecord(**rec))
            except (json.JSONDecodeError, KeyError):
                self.records = []
        else:
            self.records = []

    def _save(self) -> None:
        """保存记录"""
        if self._use_tmp:
            return
        try:
            data = {
                "records": [
                    {
                        **rec.model_dump(),
                        "created_at": rec.created_at.isoformat(),
                        "settled_at": rec.settled_at.isoformat() if rec.settled_at else None,
                    }
                    for rec in self.records[-500:]
                ]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (PermissionError, OSError):
            self._use_tmp = True

    def create_bet(
        self,
        match_id: str,
        home_team: str,
        away_team: str,
        market: str,
        selection: str,
        odds: float,
        stake: float,
        kelly_fraction: float,
        confidence: float,
    ) -> BetRecord:
        """创建投注记录"""
        bet_id = f"bet_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        record = BetRecord(
            bet_id=bet_id,
            match_id=match_id,
            home_team=home_team,
            away_team=away_team,
            market=market,
            selection=selection,
            odds=odds,
            stake=stake,
            kelly_fraction=kelly_fraction,
            confidence=confidence,
        )
        
        self.records.append(record)
        self._save()
        return record

    def settle_bet(self, bet_id: str, won: bool) -> Optional[BetRecord]:
        """结算投注"""
        for record in self.records:
            if record.bet_id == bet_id and record.status == BetStatus.PENDING:
                profit = record.stake * (record.odds - 1) if won else 0
                record.settle(won, profit)
                self._save()
                return record
        return None

    def cancel_bet(self, bet_id: str) -> bool:
        """取消投注"""
        for record in self.records:
            if record.bet_id == bet_id and record.status == BetStatus.PENDING:
                record.status = BetStatus.CANCELLED
                self._save()
                return True
        return False

    def get_pending_bets(self) -> List[BetRecord]:
        """获取待结算投注"""
        return [r for r in self.records if r.status == BetStatus.PENDING]

    def get_recent_bets(self, count: int = 20) -> List[BetRecord]:
        """获取最近投注"""
        return sorted(self.records, key=lambda x: x.created_at, reverse=True)[:count]

    def get_stats(
        self,
        days: Optional[int] = None,
        market: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取统计数据"""
        bets = self.records
        
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            bets = [b for b in bets if b.created_at >= cutoff]
        
        if market:
            bets = [b for b in bets if b.market == market]
        
        settled = [b for b in bets if b.status in [BetStatus.WON, BetStatus.LOST]]
        won = [b for b in settled if b.status == BetStatus.WON]
        
        total_stake = sum(b.stake for b in settled)
        total_profit = sum(b.profit for b in settled)
        roi = (total_profit / total_stake) if total_stake > 0 else 0
        win_rate = len(won) / len(settled) if settled else 0
        
        return {
            "total_bets": len(settled),
            "won": len(won),
            "lost": len(settled) - len(won),
            "pending": len([b for b in bets if b.status == BetStatus.PENDING]),
            "total_stake": total_stake,
            "total_profit": total_profit,
            "roi": roi,
            "win_rate": win_rate,
            "avg_odds": sum(b.odds for b in settled) / len(settled) if settled else 0,
            "avg_stake": total_stake / len(settled) if settled else 0,
        }


BET_RECORDER = BetRecorder()
