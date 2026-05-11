"""
中国体育彩票官方规则统一模块

这个模块包含竞彩足球和北京单场的所有官方规则、奖金计算、路由逻辑等。

主要组件:
- lottery_knowledge: 官方规则知识库 (单一真实来源)
- lottery_queries: 查询接口
- lottery_router: 彩种路由
- chinese_lottery_official_calc: 官方奖金计算
"""

from .lottery_knowledge import (
    LotteryKnowledge,
    LOTTERY_KNOWLEDGE,
    get_lottery_knowledge,
)
from .lottery_queries import (
    LotteryQuery,
    LOTTERY_QUERY,
    get_lottery_query,
)
from .lottery_router import (
    LotteryRouter,
)
from .chinese_lottery_official_calc import (
    ChineseLotteryOfficialCalculator,
)

__all__ = [
    "LotteryKnowledge",
    "LOTTERY_KNOWLEDGE",
    "get_lottery_knowledge",
    "LotteryQuery",
    "LOTTERY_QUERY",
    "get_lottery_query",
    "LotteryRouter",
    "ChineseLotteryOfficialCalculator",
]
