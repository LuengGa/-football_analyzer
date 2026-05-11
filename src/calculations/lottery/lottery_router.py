import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LotteryRouter:
    """
    体育彩票三大玩法物理隔离路由器 (Lottery Physical Firewall Router).
    绝对禁止"串台"！根据不同彩种的底层逻辑，强制分流到独立的校验和计算引擎中。

    竞彩足球 (JINGCAI):
    - 5种核心玩法 + 混合过关 = 6种玩法
    - 让球胜平负是独立玩法，与胜平负并列
    - 整数让球（如让1球、让2球）
    - 固定赔率（过关投注）、浮动赔率（单关投注）
    - 返奖率69%（68%返奖奖金 + 1%调节基金）
    - 最大8串1
    - 奖金公式: 2元 × 各场赔率连乘 × 倍数
    - M串1: 标准串关（如3串1、4串1）
    - M串N: 容错过关（如3串4含3个2串1+1个3串1）
    - 复式投注: 同一场次选择多个选项
    - 自由过关: 任选2-8场比赛，选择过关数自动生成M串1组合

    北京单场 (BEIDAN):
    - 6种玩法: 胜平负（含让球选项）、总进球、比分、半全场、上下单双、胜负过关
    - 让球是胜平负的选项，不是独立玩法
    - 小数让球（含0.5，如让0/0.5球、让0.5球）
    - 浮动SP值（根据销售额计算）
    - 固定65%返奖率
    - 最大15串1
    - 奖金公式: 2元 × 各场SP值连乘 × 65% × 倍数
    - 胜负过关: 只有胜负两个选项，无平局
    """

    def __init__(self):
        self.supported_types = ["JINGCAI", "BEIDAN", "ZUCAI"]

        self.JINGCAI_PLAY_TYPES = {
            "胜平负": {"options": ["胜", "平", "负"], "description": "竞猜全场90分钟（含伤停补时）主队胜平负"},
            "让球胜平负": {"options": ["胜", "平", "负"], "description": "竞猜主队加减让球数后的胜平负，让球为整数", "is_independent": True},
            "比分": {"options": ["具体比分选项"], "description": "竞猜具体比分，最多31种选项"},
            "总进球": {"options": ["0", "1", "2", "3", "4", "5", "6", "7+"], "description": "竞猜全场总进球数"},
            "半全场": {"options": ["胜胜", "胜平", "胜负", "平胜", "平平", "平负", "负胜", "负平", "负负"], "description": "竞猜半全场组合"},
            "混合过关": {"options": ["混合"], "description": "将5种核心玩法混合串关"},
        }

        self.BEIDAN_PLAY_TYPES = {
            "胜平负": {"options": ["胜", "平", "负"], "description": "不含让球", "has_handicap_option": True},
            "让球胜平负": {"options": ["胜", "平", "负"], "description": "含让球选项（让0.5、让1/1.5等小数让球）", "is_handicap_option": True},
            "总进球": {"options": ["0", "1", "2", "3", "4", "5", "6", "7+"], "description": "竞猜全场总进球数"},
            "比分": {"options": ["具体比分选项"], "description": "竞猜具体比分"},
            "半全场": {"options": ["胜胜", "胜平", "胜负", "平胜", "平平", "平负", "负胜", "负平", "负负"], "description": "竞猜半全场组合"},
            "上下单双": {"options": ["上单", "上双", "下单", "下双"], "description": "竞猜总进球数奇偶和上下盘"},
            "胜负过关": {"options": ["胜", "负"], "description": "只有胜负两个选项，无平局", "no_draw": True},
        }

    def _normalize_play_type(self, lottery_type: str, play_type: Any) -> str:
        lt = str(lottery_type or "").upper()
        s = str(play_type or "").strip()
        up = s.upper()
        if lt == "JINGCAI":
            if up in {"JINGCAI_WDL", "WDL", "1X2", "胜平负"}:
                return "胜平负"
            if up in {"JINGCAI_HANDICAP_WDL", "HANDICAP_WDL", "HANDICAP", "RQ", "让球胜平负"}:
                return "让球胜平负"
            if up in {"JINGCAI_GOALS", "GOALS", "TOTAL_GOALS", "总进球"}:
                return "总进球"
            if up in {"JINGCAI_CS", "CS", "CORRECT_SCORE", "比分"}:
                return "比分"
            if up in {"JINGCAI_HTFT", "HTFT", "半全场"}:
                return "半全场"
            if up in {"JINGCAI_MIXED_PARLAY", "MIXED_PARLAY", "MIXED", "混合过关"}:
                return "混合过关"
            return up or "胜平负"
        if lt == "BEIDAN":
            if up in {"BEIDAN_WDL", "WDL", "1X2", "胜平负", "BEIDAN_HANDICAP_WDL"}:
                return "胜平负(含让球)"
            if up in {"BEIDAN_SFGG", "SFGG", "胜负过关", "SHOU_FU_GUAN_GUO"}:
                return "胜负过关"
            if up in {"BEIDAN_UP_DOWN_ODD_EVEN", "UP_DOWN_ODD_EVEN", "SXDS", "UDOE", "上下单双"}:
                return "上下单双"
            if up in {"BEIDAN_GOALS", "GOALS", "TOTAL_GOALS", "总进球"}:
                return "总进球"
            if up in {"BEIDAN_HTFT", "HTFT", "半全场"}:
                return "半全场"
            if up in {"BEIDAN_CS", "CS", "CORRECT_SCORE", "比分"}:
                return "比分"
            return up or "胜平负(含让球)"
        if lt == "ZUCAI":
            if up in {"ZUCAI_14_MATCH", "14_MATCH", "14MATCH", "14"}:
                return "14_match"
            if up in {"ZUCAI_RENJIU", "RENJIU", "RX9", "9"}:
                return "renjiu"
            if up in {"ZUCAI_6_HTFT", "6_HTFT", "6HTFT"}:
                return "6_htft"
            if up in {"ZUCAI_4_GOALS", "4_GOALS", "4GOALS"}:
                return "4_goals"
            low = s.lower()
            if low in {"14_match", "renjiu", "6_htft", "4_goals"}:
                return low
            return low or "renjiu"
        return up or "WDL"

    def route_and_validate(self, lottery_type: str, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        核心路由网关。所有 Agent 生成的打票策略必须经过此网关。
        """
        lt = str(lottery_type or "").upper()
        if lt not in self.supported_types:
            raise ValueError(f"🚨 致命错误：未知的彩票类型 {lottery_type}。必须是 {self.supported_types} 之一。")

        normalized_ticket = dict(ticket_data or {})
        normalized_ticket["play_type"] = self._normalize_play_type(lt, normalized_ticket.get("play_type"))
        logger.info(f"[LotteryRouter] 正在进入 {lt} 专属处理通道...")

        if lt == "JINGCAI":
            return self._process_jingcai(normalized_ticket)
        if lt == "BEIDAN":
            return self._process_beidan(normalized_ticket)
        if lt == "ZUCAI":
            return self._process_zucai(normalized_ticket)
        raise ValueError(f"🚨 致命错误：未知的彩票类型 {lottery_type}。必须是 {self.supported_types} 之一。")

    def _process_jingcai(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        【竞彩专属通道】
        竞彩6种玩法: 胜平负、让球胜平负、比分、总进球、半全场、混合过关
        特征: 固定赔率(Fixed Odds)，整数让球，最大8串1。
        """
        legs = ticket_data.get("legs", [])
        if len(legs) > 8:
            raise ValueError("❌ 竞彩拦截: 串关数超过物理上限(8场)。")

        for leg in legs:
            if "0.5" in str(leg.get("handicap", "0")):
                raise ValueError(f"❌ 竞彩拦截: 竞彩绝对不存在小数让球(如 {leg.get('handicap')})。")

        for leg in legs:
            if "odds" not in leg:
                raise ValueError("❌ 竞彩拦截: 缺少固定赔率(Odds)参数。")
            odds = leg["odds"]
            if not isinstance(odds, (int, float)) or odds <= 1.0 or odds == float('inf'):
                raise ValueError(f"❌ 竞彩风控拦截: 检测到非法赔率数值({odds})。")

        return {"status": "SUCCESS", "channel": "JINGCAI", "message": "竞彩固定赔率校验通过。"}

    def _process_beidan(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        【北单专属通道】
        北单6种玩法: 胜平负(含让球)、上下单双、比分、半全场、总进球、胜负过关
        特征: 浮动奖池，65%返奖率，胜负过关消除平局，最大15串1。
        """
        legs = ticket_data.get("legs", [])
        play_type = ticket_data.get("play_type", "胜平负(含让球)")

        if len(legs) > 15:
            raise ValueError("❌ 北单拦截: 串关数超过物理上限(15场)。")

        if play_type == "胜负过关":
            for leg in legs:
                if "0.5" not in str(leg.get("handicap", "0")):
                    raise ValueError("❌ 北单拦截: 胜负过关必须带有0.5小数让球，消除平局。")

        return {"status": "SUCCESS", "channel": "BEIDAN", "message": "北单浮动奖池校验通过。"}

    def _process_zucai(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        【传统足彩专属通道】
        特征: 绝对没有赔率(No Odds)！只有全国投注比例。固定14场或9场。
        """
        legs = ticket_data.get("legs", [])
        play_type = ticket_data.get("play_type", "任九")

        for leg in legs:
            if "odds" in leg:
                logger.warning("⚠️ 警告: 传统足彩没有固定赔率！传入的Odds将被忽略。")

        if play_type == "14场胜负彩" and len(legs) != 14:
            raise ValueError(f"❌ 足彩拦截: 14场必须且只能包含14场比赛，当前为{len(legs)}场。")

        if play_type == "任九" and (len(legs) < 9 or len(legs) > 14):
            raise ValueError(f"❌ 足彩拦截: 任九必须包含9-14场比赛，当前为{len(legs)}场。")

        return {"status": "SUCCESS", "channel": "ZUCAI", "message": "传统足彩奖池共享模式校验通过。"}
