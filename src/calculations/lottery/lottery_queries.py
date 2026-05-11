"""
彩票规则查询接口
===================

提供结构化的规则查询能力
"""

from typing import Dict, Any, List, Optional
from .lottery_knowledge import LotteryKnowledge, LOTTERY_KNOWLEDGE


class LotteryQuery:
    """
    彩票规则查询接口

    提供智能查询能力，支持:
    - 按彩种查询
    - 按玩法查询
    - 规则对比
    - 合法性校验
    """

    def __init__(self, knowledge: LotteryKnowledge = None):
        self.knowledge = knowledge or LOTTERY_KNOWLEDGE

    def get_lottery_info(self, lottery_type: str) -> Dict[str, Any]:
        """获取彩种完整信息"""
        return self.knowledge.get_lottery(lottery_type)

    def get_play_type_rules(self, lottery_type: str, play_type: str) -> Dict[str, Any]:
        """获取玩法的具体规则"""
        return self.knowledge.query_rules(lottery_type, play_type)

    def list_play_types(self, lottery_type: str) -> List[str]:
        """列出指定彩种的所有玩法"""
        lottery = self.knowledge.get_lottery(lottery_type)
        return list(lottery.get("play_types", {}).keys())

    def validate_bet(
        self,
        lottery_type: str,
        play_type: str,
        legs: int,
        options: List[str] = None,
    ) -> Dict[str, Any]:
        """
        校验投注是否合法

        Returns:
            {"valid": bool, "errors": [], "warnings": []}
        """
        errors = []
        warnings = []

        try:
            lottery = self.knowledge.get_lottery(lottery_type)
        except ValueError as e:
            return {"valid": False, "errors": [str(e)], "warnings": []}

        if legs > lottery["max_legs"]:
            errors.append(
                f"串关数超过限制: {legs}关 > {lottery['max_legs']}关(最大)"
            )

        try:
            play_rules = self.knowledge.query_rules(lottery_type, play_type)
        except ValueError as e:
            errors.append(str(e))
            return {"valid": False, "errors": errors, "warnings": warnings}

        if options:
            valid_options = play_rules.get("options", [])
            for opt in options:
                if opt not in valid_options:
                    errors.append(f"无效选项: '{opt}'，有效选项: {valid_options}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "lottery": lottery["name"],
            "play_type": play_type,
            "legs": legs,
        }

    def calculate_bonus(
        self,
        lottery_type: str,
        odds_or_sp: List[float],
        bet_amount: float = 2.0,
        bet_count: int = 1,
    ) -> Dict[str, Any]:
        """
        计算理论奖金

        Args:
            lottery_type: JINGCAI 或 BEIDAN
            odds_or_sp: 赔率列表(竞彩)或SP值列表(北单)
            bet_amount: 投注金额
            bet_count: 投注注数
        """
        lottery = self.knowledge.get_lottery(lottery_type)
        return_rate = lottery["return_rate"]

        product = 1.0
        for val in odds_or_sp:
            product *= val

        if lottery_type == "JINGCAI":
            raw_bonus = bet_amount * product * bet_count
        else:
            raw_bonus = bet_amount * product * return_rate * bet_count

        return {
            "lottery": lottery["name"],
            "odds_product": round(product, 4),
            "bet_amount": bet_amount,
            "bet_count": bet_count,
            "return_rate": f"{return_rate*100}%",
            "raw_bonus": round(raw_bonus, 2),
            "formula": lottery["betting_rules"]["奖金公式"],
        }

    def get_allowed_handicaps(self, lottery_type: str) -> List[str]:
        """获取允许的让球类型"""
        lottery = self.knowledge.get_lottery(lottery_type)
        return lottery.get("handicap_type_detail", "")

    def compare_lotteries(self) -> Dict[str, Any]:
        """对比两种彩种"""
        return self.knowledge.compare_lotteries()

    def explain_difference(self, topic: str) -> str:
        """
        解释两种彩种的差异

        Args:
            topic: 差异主题，如 "让球"、"玩法"、"联赛"
        """
        comparison = self.knowledge.compare_lotteries()

        explanations = {
            "让球": f"""
竞彩足球 vs 北京单场 - 让球规则差异:

• 竞彩足球: {comparison['差异说明']['让球'].split('，')[0].replace('竞彩=', '')}
  - 使用整数让球: 让1球、让2球、让3球
  - 让球胜平负是独立玩法

• 北京单场: {comparison['差异说明']['让球'].split('，')[1].replace('北单=', '')}
  - 使用小数让球: 让0.5球、让0/0.5球、让0.5/1球
  - 让球胜平负是独立玩法
  - 胜负过关必须带0.5让球消除平局
""",
            "玩法": f"""
竞彩足球 vs 北京单场 - 玩法差异:

竞彩足球({len(comparison['竞彩足球']['独有玩法'])}种独有):
  {', '.join(comparison['竞彩足球']['独有玩法'])}

北京单场({len(comparison['北京单场']['独有玩法'])}种独有):
  {', '.join(comparison['北京单场']['独有玩法'])}

共同玩法:
  胜平负、让球胜平负、比分、半全场、总进球
""",
            "联赛": f"""
竞彩足球 vs 北京单场 - 联赛差异:

竞彩独有联赛({len(comparison['竞彩足球']['独有联赛'])}个):
  {', '.join(comparison['竞彩足球']['独有联赛'][:10])}{'...' if len(comparison['竞彩足球']['独有联赛']) > 10 else ''}

北单独有联赛({len(comparison['北京单场']['独有联赛'])}个):
  {', '.join(comparison['北京单场']['独有联赛'][:10])}{'...' if len(comparison['北京单场']['独有联赛']) > 10 else ''}

重叠联赛({len(comparison['重叠联赛'])}个):
  {', '.join(comparison['重叠联赛'][:10])}{'...' if len(comparison['重叠联赛']) > 10 else ''}
""",
        }

        return explanations.get(topic, "未知主题，有效主题: 让球、玩法、联赛")


LOTTERY_QUERY = LotteryQuery()


def get_lottery_query() -> LotteryQuery:
    """获取查询接口单例"""
    return LOTTERY_QUERY
